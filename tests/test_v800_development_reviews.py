"""Changed complete outputs require exact, scoped development review."""
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from acceptance_gate import digest
from run_acceptance import reviewed_development_change


class DevelopmentReviewTests(unittest.TestCase):
    def test_exact_hash_and_semantic_dimensions_are_required(self):
        item={'language':'Fixture','corpus':'development','id':2}
        before={'english':'A dog sees a cat.','status':'ok','surface':'old','gloss':'OLD'}
        after={'english':before['english'],'status':'ok','surface':'new','gloss':'NEW'}
        review={**item,'english':before['english'],'old_sha256':digest(before),
                'new_sha256':digest(after),'scope':'development_only',
                'reviewer':'fixture reviewer','notes':'All roles and target forms checked.',
                'dimensions':{key:True for key in ('roles','tense_aspect_mood','scope','reference',
                                                   'lexical_content','target_grammar')}}
        self.assertTrue(reviewed_development_change(item,before,after,[review]))
        self.assertFalse(reviewed_development_change(item,before,{**after,'surface':'altered'},[review]))
        self.assertFalse(reviewed_development_change(item,before,after,[{**review,'scope':'holdout'}]))
        self.assertFalse(reviewed_development_change(item,before,after,[{**review,'dimensions':{'roles':True}}]))


if __name__=='__main__':unittest.main()
