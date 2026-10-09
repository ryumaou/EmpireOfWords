import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from semantic_audit import inspect,realization_probe
class AttachmentTests(unittest.TestCase):
    def test_recursive_attachment(self):
        by={x:[(p,x+'x')] for x,p in [('girl','n'),('wreath','n'),('flower','n'),('dance','v'),('with','prep'),('of','prep')]}
        r=inspect('The girls with wreaths of flowers danced.',by)
        self.assertEqual([(x['owner'],x['object']) for x in r['attachments']],[('girl','wreath'),('wreath','flower')])
    def test_realization_probe_failure_is_explicit(self):
        by={'dog':[('n','dogx')],'see':[('v','seex')]}
        r=realization_probe('The dog sees.',by,{})
        self.assertIn('missing_predicates',r)
        self.assertFalse(r['realized'])
