#!/usr/bin/env python3
"""Compare actual generated packages and test their grammar behavior."""
import argparse, csv, hashlib, json, sys
from pathlib import Path
from itertools import combinations
from language_io import load_language, resolve_language_path, validate_package
from grammar_engine import analyze_translation

PROBES = [
 'The dog sees the cat.', 'The small dog sees the cat.',
 'The dog sees the small cat.', 'The dogs see the cat.',
 'The dog does not see the cat.', 'Will the dog see the cat?',
 'The dog saw the cat.', 'The dog will see the cat.',
 'The dog sees the cat and the bird.', 'The dog sees the cats and the bird.', 'The dog is happy.',
 'The dog sees the cat in the house.', 'The cat sees the dog.', 'The dog never sees the cat.', 'The dog sees no cat.', 'The dog will not see the cat.', 'The dog sees the cats.', 'The dog sees the cat and the birds.'
]
FIELDS = ['word_order','adposition_type','adjective_position','possessor_position','plural_strategy','comparison_strategy','question_strategy','negation_strategy','morphology_type','future','progressive','perfect','imperative']

def sha(obj): return hashlib.sha256(json.dumps(obj,sort_keys=True,ensure_ascii=False).encode('utf-8')).hexdigest()
def main():
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument('--languages',nargs='+',required=True,type=Path)
 ap.add_argument('--output',type=Path,default=Path('output/language_audit'))
 ap.add_argument('--corpus',type=Path,help='optional English sentence file to compare status and surface')
 a=ap.parse_args(); a.output.mkdir(parents=True,exist_ok=True)
 packs=[]
 for item in a.languages:
  path=resolve_language_path(Path.cwd(),item); data,g,entries,forms=load_language(path)
  errors,warnings=validate_package(data,entries,forms)
  manifest_path=path.parent/'manifest.json'; manifest=json.loads(manifest_path.read_text(encoding='utf-8')) if manifest_path.exists() else {}
  lex={(e.key.gloss,e.key.pos):forms[e.key] for e in entries if e.key in forms}
  packs.append(dict(name=data.get('name',path.parent.name),path=str(path),grammar=g,lex=lex,entries=entries,forms=forms,errors=errors,warnings=warnings,manifest=manifest,sha=hashlib.sha256(path.read_bytes()).hexdigest()))
 if len(packs)<2: ap.error('provide at least two language packages')
 lines=['# Empire Of Words — language diversity and realization audit','', '## Package provenance and validity','']
 for p in packs:
  lines += [f"- **{p['name']}**: {len(p['lex'])} lexical entries; build version {p['manifest'].get('tool_version','unknown')}; package SHA256 `{p['sha']}`; validation errors {len(p['errors'])}; warnings {len(p['warnings'])}"]
  for e in p['errors'][:5]: lines.append(f'  - ERROR: {e}')
 lines += ['','## Declared grammatical contrasts','', '| Feature | '+' | '.join(p['name'] for p in packs)+' |','|---|'+'---|'*len(packs)]
 for key in FIELDS:
  vals=[str(p['grammar'].get('realization_profile',{}).get(key,'(not declared)')) for p in packs]
  lines.append('| '+key+' | '+' | '.join(vals)+' |')
 lines += ['','## Pairwise lexical and grammatical overlap','']
 for x,y in combinations(packs,2):
  common=x['lex'].keys() & y['lex'].keys(); same=sum(x['lex'][k]==y['lex'][k] for k in common)
  union_forms=set(x['lex'].values())|set(y['lex'].values()); intersect_forms=set(x['lex'].values())&set(y['lex'].values())
  diff=sum(x['grammar'].get('realization_profile',{}).get(k)!=y['grammar'].get('realization_profile',{}).get(k) for k in FIELDS)
  lines += [f"- **{x['name']} vs {y['name']}**: {len(common)} shared lemma/POS keys; {same} identical forms ({same/max(1,len(common)):.1%}); {len(intersect_forms)} shared surface types out of {len(union_forms)} unique combined surface types ({len(intersect_forms)/max(1,len(union_forms)):.1%}); {diff}/{len(FIELDS)} differing profile fields; grammar fingerprints {'identical' if sha(x['grammar'])==sha(y['grammar']) else 'different'}."]
 lines += ['','## Contrast probes','', 'A matching success flag does not prove equivalent grammatical behavior. Inspect surface output and semantic receipts in the CSV.','']
 probes=PROBES[:]
 if a.corpus:
  from grammar_engine import load_translation_sentences
  probes=load_translation_sentences(a.corpus)
 rows=[]
 for idx,sentence in enumerate(probes,1):
  row={'number':idx,'english':sentence}
  for p in packs:
   r=analyze_translation(sentence,p['grammar'],p['entries'],p['forms']); prefix=p['name']
   row[prefix+'_status']=r['status']; row[prefix+'_surface']=r['surface']; row[prefix+'_reason']=r['reason']; row[prefix+'_gloss']=r.get('gloss','')
  rows.append(row)
 with (a.output/'contrast_probes.csv').open('w',newline='',encoding='utf-8-sig') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
 n=len(rows); same_status=sum(len({row[p['name']+'_status'] for p in packs})==1 for row in rows)
 complete=[r for r in rows if all(r[p['name']+'_status']=='ok' for p in packs)]
 same_surface=sum(len({r[p['name']+'_surface'] for p in packs})==1 for r in complete)
 # Within-language minimal-pair invariants: identical surfaces are not proof of an error
 # for all typologies, but our v7 contract promises an overt past distinction.
 lines += ['', '## Grammatical fidelity checks', '']
 for p in packs:
  name=p['name']
  def probe(s):
   return next((r for r in rows if r['english']==s),None)
  present=probe('The dog sees the cat.'); past=probe('The dog saw the cat.')
  if present and past:
   both=all(r[name+'_status']=='ok' for r in (present,past))
   distinct=present[name+'_surface']!=past[name+'_surface'] if both else False
   lines.append(f"- **{name} past/present contrast**: {'PASS' if distinct else 'FAIL' if both else 'INCONCLUSIVE'}; both complete={both}; distinct surface={distinct}.")
  singular=probe('The dog sees the cat.'); coord=probe('The dog sees the cat and the bird.')
  if singular and coord and coord[name+'_status']=='ok':
   # A coordination must preserve the number of each child noun, even if the
   # conjunction as a whole is plural in agreement.
   gloss=coord[name+'_gloss']
   bad=('CAT.PL' in gloss or 'BIRD.PL' in gloss)
   lines.append(f"- **{name} coordinated singular nouns**: {'FAIL' if bad else 'PASS'}; CAT/BIRD unexpectedly plural={bad}.")
  neg=probe('The dog does not see the cat.')
  if neg and neg[name+'_status']=='ok':
   strategy=p['grammar'].get('verb',{}).get('negation','unknown')
   particle=p['grammar'].get('particles',{}).get('negative')
   surface=neg[name+'_surface'].split()
   observed=surface.count(particle) if particle else 0
   if strategy=='particle':
    result='PASS' if observed==1 else 'FAIL'
   elif strategy=='affix':
    result='PASS' if observed==0 else 'FAIL'
   else:
    result='INCONCLUSIVE'  # Mixed requires per-clause strategy receipts.
   lines.append(f"- **{name} negation strategy surface**: {result}; particle tokens={observed}; strategy={strategy}. The gloss NEG is a semantic label, not an additional surface marker.")
  future=probe('The dog will see the cat.')
  if present and future and present[name+'_status']=='ok' and future[name+'_status']=='ok':
   different=present[name+'_surface']!=future[name+'_surface']
   lines.append(f"- **{name} future/present contrast**: {'PASS' if different else 'FAIL'}; distinct surface={different}.")
  plural=probe('The dog sees the cats.')
  if singular and plural and singular[name+'_status']=='ok' and plural[name+'_status']=='ok':
   different=singular[name+'_surface']!=plural[name+'_surface']
   lines.append(f"- **{name} singular/plural object contrast**: {'PASS' if different else 'INCONCLUSIVE'}; distinct surface={different}.")
 lines += [f'- Probe sentences: {n}',f'- Same status across all languages: {same_status}/{n}',f'- All-language complete probes: {len(complete)}',f'- Identical surface among all-language complete probes: {same_surface}/{len(complete)}','', '## Interpretation', '', 'Identical completion rates alone do not imply identical languages. Distinct surface forms alone do not prove correct syntax. Manually inspect contrast_probes.csv for grammatical order, morphology, agreement, and semantic fidelity. This audit does not claim to certify translation correctness.']
 (a.output/'language_audit.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
 print('\n'.join(lines[:8])); print('Audit:',a.output/'language_audit.md'); print('Contrasts:',a.output/'contrast_probes.csv')
 return 1 if any(p['errors'] for p in packs) else 0
if __name__=='__main__': sys.exit(main())
