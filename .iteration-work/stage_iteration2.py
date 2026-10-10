import difflib
from pathlib import Path
import subprocess

path = 'src/grammar_engine.py'
head = subprocess.check_output(['git', 'show', 'HEAD:' + path]).decode('utf-8')
work = Path(path).read_text(encoding='utf-8')
start = work.index('    # Punctuation inside this fixed discourse expression')
end = work.index('    # Discourse expressions are independent', start)
anchor = '    by=_lexicon(entries,forms); raw=sentence.strip()\n'
assert head.count(anchor) == 1
staged = head.replace(anchor, anchor + work[start:end])
patch = ''.join(difflib.unified_diff(head.splitlines(True), staged.splitlines(True),
                                   fromfile='a/' + path, tofile='b/' + path))
Path('.iteration-work/iteration2.patch').write_text(patch, encoding='utf-8', newline='\n')
