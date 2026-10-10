"""Stage only this iteration's source edits, preserving the dirty baseline."""
import difflib
from pathlib import Path
import subprocess

path = 'src/structured_realizer.py'
head = subprocess.check_output(['git', 'show', 'HEAD:' + path]).decode('utf-8')
work = Path(path).read_text(encoding='utf-8')
old = "        if _pos(by,vl,'v'):\n"
start = work.index('        # A postnominal participle needs a nominal host.')
end = work.index('\n', work.index("        if _pos(by,vl,'v')", start)) + 1
assert head.count(old) == 1
staged = head.replace(old, work[start:end], 1)
anchor = "    if any(c in constructions for c in ('relative_clause','appositive','conditional_clause','passive','quotation','complement_clause')): return None\n"
start = work.index('    # Without a comma, a nominative pronoun supplies the adjunct boundary.')
end = work.index('    # Fronted adjunct PP:', start)
assert staged.count(anchor) == 1
staged = staged.replace(anchor, anchor + work[start:end], 1)
patch = ''.join(difflib.unified_diff(head.splitlines(True), staged.splitlines(True),
                                   fromfile='a/' + path, tofile='b/' + path))
Path('.iteration-work/iteration1.patch').write_text(patch, encoding='utf-8', newline='\n')
print(patch)
