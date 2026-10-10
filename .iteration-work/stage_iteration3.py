import difflib
from pathlib import Path
import subprocess

patches = []
for path in ('src/structured_realizer.py', 'src/grammar_engine.py'):
    head = subprocess.check_output(['git', 'show', 'HEAD:' + path]).decode('utf-8')
    work = Path(path).read_text(encoding='utf-8')
    staged = head
    if path.endswith('structured_realizer.py'):
        begin = head.index('    # Without a comma, a nominative pronoun')
        end = head.index('    # Degree questions', begin)
        start_new = work.index('    # A nominative pronoun supplies')
        end_new = work.index('    # Fronted adjunct PP:', start_new)
        staged = staged[:begin] + work[start_new:end_new] + staged[end:]
        begin = staged.index("    if ',' in raw and re.search")
        end = staged.index('        if len(segments)>=3:', begin)
        start_new = work.index("    if (',' in raw or ';' in raw) and re.search")
        end_new = work.index('        if len(segments)>=3:', start_new)
        staged = staged[:begin] + work[start_new:end_new] + staged[end:]
    else:
        begin = head.index('    # Punctuation inside this fixed discourse expression')
        end = head.index('    base_ir=_analyze_english', begin)
        start_new = work.index('    # Retain both lexical interjections')
        end_new = work.index('    # Discourse expressions are independent', start_new)
        staged = staged[:begin] + work[start_new:end_new] + staged[end:]
    patches.append(''.join(difflib.unified_diff(head.splitlines(True), staged.splitlines(True),
                                             fromfile='a/' + path, tofile='b/' + path)))
Path('.iteration-work/iteration3.patch').write_text(''.join(patches), encoding='utf-8', newline='\n')
