#!/usr/bin/env python3
"""build_language.py - generate a related conlang lexicon from MagicVocabulary-style files.

Uses the same two-character transition model as Christopher Pound's lc.pl (via lc.py)
for independent roots, then applies the vocabulary file's named derivational modifiers
consistently across the language.

Example:
  python build_language.py MagicVocabulary.txt corpus.txt --seed 12345 --output language.csv
"""
from __future__ import annotations
import argparse, csv, importlib.util, random, re, sys, json, hashlib
from grammar_engine import FAMILIES, generate_grammar, load_grammar, write_package, load_translation_sentences
from language_io import validate_grammar_contract
from dataclasses import dataclass
from pathlib import Path

VOWELS = set("aeiouyAEIOUY")

@dataclass(frozen=True)
class EntryKey:
    gloss: str
    pos: str

@dataclass
class Entry:
    key: EntryKey
    expr: str | None
    line_no: int

@dataclass
class Affix:
    name: str
    side: str
    form: str
    source_rule: str


def read_text(path: Path) -> str:
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        return raw.decode("utf-8-sig")
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("cp1252")


def load_lc_module(script: Path):
    spec = importlib.util.spec_from_file_location("pound_lc", script)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load lc module: {script}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def parse_vocab(path: Path, require_modifiers: bool = True):
    entries: list[Entry] = []
    modifiers: dict[str, str] = {}
    in_modifier_block = False
    for no, raw in enumerate(read_text(path).splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        mm = re.fullmatch(r"([A-Z][A-Z0-9.]*)\s*=\s*(.+)", line)
        if mm:
            in_modifier_block = True
            modifiers[mm.group(1)] = mm.group(2).strip()
            continue
        # Entries are gloss:pos, optionally " = derivation". Split on the first = only.
        left, sep, right = line.partition("=")
        left = left.strip()
        if ":" not in left:
            continue
        gloss, pos = left.rsplit(":", 1)
        gloss, pos = gloss.strip(), pos.strip()
        if not gloss or not pos:
            continue
        expr = right.strip() if sep else None
        entries.append(Entry(EntryKey(gloss, pos), expr, no))
    if require_modifiers and not modifiers:
        raise ValueError("no uppercase modifier definitions were found")
    return entries, modifiers


def visible_letters(s: str) -> int:
    return len(re.findall(r"[A-Za-z]", s))


def normalize_word(s: str) -> str:
    # Generated corpus may contain spaces at boundaries; lexical forms may not.
    return "".join(re.findall(r"[A-Za-z]", s)).lower()


def generate_unique_roots(lc, corpus: Path, count: int, rng: random.Random,
                          min_len: int, max_len: int) -> list[str]:
    data = lc.load_data(corpus)
    followers, starts = lc.build_tables(data)
    if not starts:
        raise ValueError("corpus has no usable word starts")
    used: set[str] = set()
    out: list[str] = []
    state = rng.choice(starts)
    attempts = 0
    while len(out) < count:
        attempts += 1
        if attempts > max(10000, count * 500):
            raise RuntimeError("could not generate enough unique roots; use a richer corpus or larger max length")
        state = lc.new_word(state[-2:], followers, rng, min_len)
        w = normalize_word(state[:max_len]).lower()
        if visible_letters(w) < 2 or w in used:
            continue
        used.add(w); out.append(w)
    return out


def make_affixes(names: list[str], lc, corpus: Path, rng: random.Random,
                  occupied: set[str], min_root: int, max_root: int,
                  source_rules: dict[str,str]) -> dict[str, Affix]:
    # Generate short language-native material, then keep 1-3 chars for bound morphology.
    raw = generate_unique_roots(lc, corpus, max(len(names)*3, 20), rng, min_root, max_root)
    idx = 0; affixes = {}
    for name in names:
        rule = source_rules[name]
        # Preserve an explicit literal IF...THEN...ELSE rule (currently DOER) as conditional morphology.
        m = re.fullmatch(r"IF\s+\\V\s+THEN\s+-([^\s]+)\s+ELSE\s+-([^\s]+)", rule, re.I)
        if m:
            affixes[name] = Affix(name, "conditional_suffix", f"{m.group(1)}/{m.group(2)}", rule)
            continue
        while True:
            if idx >= len(raw):
                raw.extend(generate_unique_roots(lc, corpus, len(names)*2, rng, min_root, max_root))
            base = raw[idx]; idx += 1
            # Bound morphemes may be one letter. Favor 2 chars, sometimes 1 or 3.
            n = rng.choices([1,2,3], weights=[2,6,2], k=1)[0]
            form = base[:n] if len(base) >= n else base
            if form and form not in occupied:
                break
        side = rng.choice(["prefix", "suffix"])
        affixes[name] = Affix(name, side, form, rule)
    return affixes


def join_parts(a: str, b: str) -> str:
    """Join compound/root material conservatively, smoothing duplicate boundary chars."""
    if not a: return b
    if not b: return a
    if a[-1].lower() == b[0].lower():
        return a + b[1:]
    return a + b


def apply_affix(word: str, aff: Affix) -> str:
    if aff.side == "conditional_suffix":
        yes, no = aff.form.split("/",1)
        suffix = yes if word and word[-1] in VOWELS else no
        return join_parts(word, suffix)
    if aff.side == "prefix":
        return join_parts(aff.form, word)
    return join_parts(word, aff.form)


def choose_key(ref: str, by_key: dict[EntryKey,Entry], by_gloss: dict[str,list[EntryKey]], current: EntryKey):
    ref = ref.strip()
    # POS-qualified reference, e.g. paint:v or copper:adj.
    if ":" in ref:
        g,p = ref.rsplit(":",1)
        k = EntryKey(g.strip(), p.strip())
        if k in by_key: return k
    candidates = by_gloss.get(ref, [])
    if not candidates:
        # Fallback for sense-qualified vocabulary entries.  A derivation may
        # refer to a bare gloss such as "hair" while the vocabulary contains
        # "hair (of body)" and "hair (of head)".  Preserve vocabulary-file
        # order and use the first matching sense by default.
        ref_base = re.sub(r"\s*\([^)]*\)\s*$", "", ref).strip()
        candidates = [
            k for k in by_key
            if re.sub(r"\s*\([^)]*\)\s*$", "", k.gloss).strip() == ref_base
        ]
    if not candidates:
        return None
    # An unqualified derivation such as attack:v = attack-NOUN.TO.VERB
    # means "the other lexical attack" (normally attack:n), not itself.
    others = [k for k in candidates if k != current]
    if not others:
        return None
    for k in others:
        if k.pos == current.pos:
            return k
    return others[0]


def tokenize_expr(expr: str, modifiers: set[str], by_key, by_gloss, current: EntryKey):
    """Dynamic-programming tokenizer. Hyphens may occur inside lexical glosses."""
    chunks = expr.split("-")
    memo = {}
    def rec(i):
        if i == len(chunks): return []
        if i in memo: return memo[i]
        # Prefer the longest lexical reference; modifiers are exact chunks.
        for j in range(len(chunks), i, -1):
            token = "-".join(chunks[i:j]).strip()
            if token in modifiers:
                rest = rec(j)
                if rest is not None:
                    memo[i] = [("mod", token)] + rest; return memo[i]
            k = choose_key(token, by_key, by_gloss, current)
            if k is not None:
                rest = rec(j)
                if rest is not None:
                    memo[i] = [("lex", k)] + rest; return memo[i]
        memo[i] = None
        return None
    return rec(0)


def main(argv=None):
    p=argparse.ArgumentParser(description="Build a related conlang lexicon from a MagicVocabulary-style list")
    root_default=Path(__file__).resolve().parent.parent
    p.add_argument("vocabulary", nargs="?", type=Path, help="legacy positional vocabulary file (prefer --vocabulary)")
    p.add_argument("corpus", nargs="?", type=Path, help="legacy positional source corpus (prefer --source)")
    p.add_argument("--vocabulary", dest="vocabulary_file", type=Path, help="vocabulary definition file; relative paths resolve from the project root")
    p.add_argument("--supplemental-vocabulary", dest="supplemental_vocabulary", action="append", type=Path, default=[], help="additional vocabulary file to merge after the main vocabulary; may be repeated")
    p.add_argument("--source", dest="source_file", type=Path, help="source/base language corpus to analyze; relative paths resolve from the project root")
    p.add_argument("--translations", dest="translations_file", type=Path, help="English sentence file under ./translations (or another project-relative path); replaces built-in examples")
    p.add_argument("--no-translation-vocabulary-preflight", action="store_true", help="do not seed safely inferred lexical roots required by --translations during initial language creation")
    p.add_argument("--project-root", type=Path, default=root_default)
    p.add_argument("--language-name", default="Generated Language")
    p.add_argument("--grammar", dest="legacy_grammar", choices=["naturalistic","random"], help="legacy alias for --grammar-family")
    p.add_argument("--grammar-family", choices=sorted(FAMILIES), default="naturalistic")
    p.add_argument("--grammar-file", type=Path, help="reuse an exact grammar.json; family/grammar overrides are ignored")
    p.add_argument("--word-order", choices=["SVO","SOV","VSO","VOS","OVS","OSV"])
    p.add_argument("--adjective-position", choices=["before","after"])
    p.add_argument("--adposition", choices=["preposition","postposition","pre","post"])
    p.add_argument("--possession", choices=["before","after","possessor-first","possessed-first"])
    p.add_argument("--gender", choices=["none","2","3","classes"])
    p.add_argument("--cases", type=int, choices=range(0,9), metavar="0-8")
    p.add_argument("--articles", choices=["none","definite","indefinite","both"])
    p.add_argument("--agreement", choices=["none","subject","subject-object"])
    p.add_argument("--tense", choices=["minimal","standard","rich"])
    p.add_argument("--aspect", choices=["minimal","standard","rich"])
    p.add_argument("--mood", choices=["minimal","standard","rich"])
    p.add_argument("--plural", choices=["none","suffix","prefix","mixed"])
    p.add_argument("--comparison", choices=["particle","affix","mixed"])
    p.add_argument("--questions", choices=["particle","word-order","verb","mixed"])
    p.add_argument("--negation", choices=["particle","affix","mixed"])
    p.add_argument("--grammar-morphology", choices=["analytic","agglutinative","fusional","mixed","isolating"], help="grammar morphology type")
    p.add_argument("--morphophonemics", default="auto", help="auto, none, or comma-separated rules (vowel_harmony, initial_mutation, lenition, elision, palatalization, consonant_assimilation, nasal_assimilation, epenthesis, reduplication, ablaut, templatic_light)")
    p.add_argument("--lc", type=Path, default=Path(__file__).with_name("lc.py"), help="path to tested lc.py")
    p.add_argument("--output", type=Path, default=Path("generated_language.csv"))
    p.add_argument("--etymology", type=Path, default=Path("generated_language_etymology.txt"))
    p.add_argument("--morphology", type=Path, default=Path("generated_language_morphology.txt"))
    p.add_argument("--seed", type=int, default=None)
    p.add_argument("--min-root", type=int, default=3, help="lc minimum threshold (faithful lc semantics produce > this)")
    p.add_argument("--max-root", type=int, default=7)
    args=p.parse_args(argv)
    project=args.project_root.resolve()

    # Explicit selectors win. Positional arguments remain supported for v1-v4 compatibility.
    if args.vocabulary_file is not None and args.vocabulary is not None:
        p.error("specify the vocabulary either with --vocabulary or as the legacy positional argument, not both")
    if args.source_file is not None and args.corpus is not None:
        p.error("specify the source either with --source or as the legacy positional argument, not both")

    selected_vocab = args.vocabulary_file if args.vocabulary_file is not None else args.vocabulary
    selected_source = args.source_file if args.source_file is not None else args.corpus

    def resolve_project_path(value):
        return value.resolve() if value.is_absolute() else (project / value).resolve()

    if selected_vocab is None:
        candidates = sorted(pth for pth in (project/'vocabulary').iterdir() if pth.is_file()) if (project/'vocabulary').exists() else []
        if not candidates:
            p.error("no vocabulary supplied and no files found in ./vocabulary; use --vocabulary FILE")
        if len(candidates) > 1:
            listing = "\n  ".join(str(x.relative_to(project)) for x in candidates)
            p.error(f"multiple vocabulary files found; select one with --vocabulary FILE:\n  {listing}")
        selected_vocab = candidates[0]
    else:
        selected_vocab = resolve_project_path(selected_vocab)

    if selected_source is None:
        candidates = sorted((project/'data').glob('*.txt'))
        if not candidates:
            p.error("no source supplied and no .txt files found in ./data; use --source FILE")
        if len(candidates) > 1:
            listing = "\n  ".join(str(x.relative_to(project)) for x in candidates)
            p.error(f"multiple source language files found; select one with --source FILE:\n  {listing}")
        selected_source = candidates[0]
    else:
        selected_source = resolve_project_path(selected_source)

    if not selected_vocab.is_file(): p.error(f"vocabulary file not found: {selected_vocab}")
    if not selected_source.is_file(): p.error(f"source language file not found: {selected_source}")
    args.vocabulary = selected_vocab
    args.corpus = selected_source
    translation_sentences=None; translation_source=None
    if args.translations_file is not None:
        translation_source=resolve_project_path(args.translations_file)
        if not translation_source.is_file(): p.error(f"translations file not found: {translation_source}")
        translation_sentences=load_translation_sentences(translation_source)
        if not translation_sentences: p.error(f"translations file contains no usable sentences: {translation_source}")
    # Defaults go under ./output/<safe-language-name>/
    safe=re.sub(r'[^A-Za-z0-9._-]+','_',args.language_name).strip('_') or 'language'
    package_dir=project/'output'/safe
    if args.output == Path('generated_language.csv'): args.output=package_dir/'dictionary.csv'
    if args.etymology == Path('generated_language_etymology.txt'): args.etymology=package_dir/'etymology.txt'
    if args.morphology == Path('generated_language_morphology.txt'): args.morphology=package_dir/'derivational_morphology.txt'
    rng=random.Random(args.seed)
    entries, mod_rules=parse_vocab(args.vocabulary)
    supplemental_paths=[]
    for sv in args.supplemental_vocabulary:
        sv=resolve_project_path(sv)
        if not sv.is_file(): p.error(f"supplemental vocabulary file not found: {sv}")
        supplemental_paths.append(sv)
        extra_entries, extra_mods=parse_vocab(sv, require_modifiers=False)
        existing={e.key for e in entries}
        duplicates=[e.key for e in extra_entries if e.key in existing]
        if duplicates:
            shown=', '.join(f'{k.gloss}:{k.pos}' for k in duplicates[:10])
            p.error(f"supplemental vocabulary duplicates existing entries: {shown}")
        for name,rule in extra_mods.items():
            if name in mod_rules and mod_rules[name] != rule:
                p.error(f"supplemental vocabulary redefines modifier {name} with a different rule")
            mod_rules.setdefault(name,rule)
        entries.extend(extra_entries)
    # When a translation corpus is supplied, seed safely inferable lexical concepts
    # before roots are generated. This makes the initial language translation-ready
    # without changing existing MagicVocabulary derivations or requiring add_words.py.
    preflight_entries=[]
    if translation_sentences and not args.no_translation_vocabulary_preflight:
        from translate import infer_missing_entry
        from english_analyzer import tokens as english_tokens, FUNCTION_WORDS
        by_pos={}
        for e in entries: by_pos.setdefault(e.key.gloss,[]).append((e.key.pos,None))
        existing={e.key for e in entries}
        seen_tokens=[]
        for sent in translation_sentences:
            for tok in english_tokens(sent):
                low=tok.lower().strip("'\"")
                if low and low not in FUNCTION_WORDS and low not in seen_tokens: seen_tokens.append(low)
        for tok in seen_tokens:
            inferred=infer_missing_entry(tok,translation_sentences,by_pos)
            if not inferred: continue
            lemma,pos=inferred; key=EntryKey(lemma,pos)
            if key in existing: continue
            e=Entry(key,None,0); entries.append(e); preflight_entries.append(e); existing.add(key)
            by_pos.setdefault(lemma,[]).append((pos,None))
    lc=load_lc_module(args.lc)
    by_key={e.key:e for e in entries}
    by_gloss={}
    for e in entries: by_gloss.setdefault(e.key.gloss,[]).append(e.key)
    base=[e for e in entries if e.expr is None]
    roots=generate_unique_roots(lc,args.corpus,len(base),rng,args.min_root,args.max_root)
    forms={e.key:w for e,w in zip(base,roots)}
    occupied=set(roots)
    affixes=make_affixes(list(mod_rules),lc,args.corpus,rng,occupied,args.min_root,args.max_root,mod_rules)
    unresolved=[]; deriv_tokens={}
    # Pre-tokenize so syntax problems are visible independently of recursive resolution.
    for e in entries:
        if e.expr:
            t=tokenize_expr(e.expr,set(mod_rules),by_key,by_gloss,e.key)
            if t is None: unresolved.append((e,"cannot tokenize expression"))
            else: deriv_tokens[e.key]=t
    resolving=set()
    def resolve(k):
        if k in forms: return forms[k]
        if k in resolving: raise RuntimeError(f"derivation cycle at {k.gloss}:{k.pos}")
        e=by_key[k]; toks=deriv_tokens.get(k)
        if toks is None: raise KeyError(k)
        resolving.add(k); word=""
        try:
            for typ,val in toks:
                if typ=="lex": word=join_parts(word,resolve(val))
                else: word=apply_affix(word,affixes[val])
        finally:
            resolving.remove(k)
        if visible_letters(word)<2:
            raise RuntimeError(f"derived independent word too short: {k.gloss}:{k.pos} -> {word!r}")
        forms[k]=word
        return word
    errors=[]
    for e in entries:
        if e.key in forms: continue
        try: resolve(e.key)
        except Exception as exc: errors.append((e,str(exc)))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open("w",encoding="utf-8",newline="") as f:
        w=csv.writer(f); w.writerow(["English","POS","Generated","Type","Derivation"])
        for e in entries:
            w.writerow([e.key.gloss,e.key.pos,forms.get(e.key,""),"derived" if e.expr else "root",e.expr or ""])
    with args.morphology.open("w",encoding="utf-8") as f:
        f.write(f"seed: {args.seed}\n")
        for name,a in affixes.items():
            shown=(a.form+"-") if a.side=="prefix" else ("-"+a.form)
            if a.side=="conditional_suffix": shown="conditional -"+a.form
            f.write(f"{name:24} {shown:16} source={a.source_rule}\n")
    args.etymology.parent.mkdir(parents=True,exist_ok=True)
    args.morphology.parent.mkdir(parents=True,exist_ok=True)
    with args.etymology.open("w",encoding="utf-8") as f:
        for e in entries:
            if e.expr:
                f.write(f"{e.key.gloss}:{e.key.pos} = {forms.get(e.key,'[UNRESOLVED]')} <- {e.expr}\n")
        if unresolved or errors:
            f.write("\nUNRESOLVED / ERRORS\n")
            for e,msg in unresolved+errors: f.write(f"line {e.line_no}: {e.key.gloss}:{e.key.pos}: {msg} [{e.expr}]\n")
    overrides={
        'word_order':args.word_order, 'adjective_position':args.adjective_position,
        'adposition': {'pre':'preposition','post':'postposition'}.get(args.adposition,args.adposition),
        'possession': {'possessor-first':'before','possessed-first':'after'}.get(args.possession,args.possession),
        'gender': ({'none':0,'2':2,'3':3,'classes':'classes'}.get(args.gender) if args.gender is not None else None),
        'cases':args.cases, 'articles':args.articles, 'agreement':args.agreement,
        'tense':args.tense, 'aspect':args.aspect, 'mood':args.mood, 'plural':args.plural,
        'comparison':args.comparison, 'questions':args.questions, 'negation':args.negation,
        'morphology':args.grammar_morphology, 'morphophonemics':args.morphophonemics,
    }
    overrides={k:v for k,v in overrides.items() if v is not None}
    if args.grammar_file:
        gp=args.grammar_file if args.grammar_file.is_absolute() else (project/args.grammar_file).resolve()
        grammar=load_grammar(gp)
    else:
        family=args.legacy_grammar or args.grammar_family
        grammar=generate_grammar(roots,rng,family,overrides)
    contract_errors,contract_warnings=validate_grammar_contract(grammar)
    if contract_errors:
        raise RuntimeError('generated grammar failed realization contract: '+ '; '.join(contract_errors))
    for warning in contract_warnings:
        print('Grammar warning:',warning)
    write_package(package_dir,args.language_name,grammar,entries,forms,affixes,args.seed,translation_sentences,translation_source)
    def sha256_file(path):
        h=hashlib.sha256()
        with Path(path).open('rb') as fh:
            for chunk in iter(lambda:fh.read(1024*1024),b''): h.update(chunk)
        return h.hexdigest()
    manifest={
        'schema_version':2,'tool_version':'7.6.6','language':args.language_name,'seed':args.seed,
        'source':{'path':str(args.corpus),'sha256':sha256_file(args.corpus)},
        'vocabulary':{'path':str(args.vocabulary),'sha256':sha256_file(args.vocabulary)},
        'supplemental_vocabulary':[{'path':str(x),'sha256':sha256_file(x)} for x in supplemental_paths],
        'translation_vocabulary_preflight':{'enabled':bool(translation_sentences and not args.no_translation_vocabulary_preflight),'added':len(preflight_entries)},
        'grammar_family':args.legacy_grammar or args.grammar_family,
        'grammar_file':str(args.grammar_file) if args.grammar_file else None,
        'translation_source':str(translation_source) if translation_source else None,
        'counts':{'entries':len(entries),'base_roots':len(base),'modifiers':len(mod_rules),
                  'derived_resolved':sum(1 for e in entries if e.expr and e.key in forms),
                  'unresolved_errors':len({(e.line_no,m) for e,m in unresolved+errors})}
    }
    (package_dir/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f"Entries: {len(entries)}")
    if preflight_entries: print(f"Translation preflight roots: {len(preflight_entries)}")
    print(f"Base roots: {len(base)}")
    print(f"Modifiers: {len(mod_rules)}")
    print(f"Derived resolved: {sum(1 for e in entries if e.expr and e.key in forms)}")
    print(f"Unresolved/errors: {len({(e.line_no,m) for e,m in unresolved+errors})}")
    print(f"Dictionary: {args.output}")
    print(f"Morphology: {args.morphology}")
    print(f"Etymology: {args.etymology}")
    print(f"Grammar package: {package_dir}")
    if translation_source: print(f"Translations: {translation_source} ({len(translation_sentences)} sentences; replaces built-in examples)")
    return 2 if errors or unresolved else 0

if __name__=="__main__":
    raise SystemExit(main())
