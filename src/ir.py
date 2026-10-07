#!/usr/bin/env python3
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Optional

@dataclass
class ComparisonIR:
    degree: str='positive'          # positive|comparative|superlative
    standard: Optional['NPIR']=None # than X
    marker: Optional[str]=None      # more|less|better etc.

@dataclass
class ParticipialModifierIR:
    lemma: str
    object: Optional['NPIR']=None

@dataclass
class NPIR:
    tokens: list[str]
    head: Optional[str]=None
    determiner: Optional[str]=None
    number: str='singular'
    adjectives: list[str]=field(default_factory=list)
    noun_modifiers: list[str]=field(default_factory=list)
    participial_modifiers: list[ParticipialModifierIR]=field(default_factory=list)
    proper_name: bool=False
    quantifier: Optional[str]=None
    numeral: Optional[str]=None
    possessor: Optional['NPIR']=None
    person: Optional[str]=None
    conjunction: Optional[str]=None
    coordinated: list['NPIR']=field(default_factory=list)
    comparison: Optional[ComparisonIR]=None

@dataclass
class PPIR:
    adposition: str
    object: NPIR

@dataclass
class ModifierIR:
    lemma: str
    kind: str='manner' # manner|frequency|temporal|degree|discourse
    source: Optional[str]=None

@dataclass
class PredicateIR:
    lemma: str
    tense: str='present'
    aspect: list[str]=field(default_factory=list)
    mood: str='indicative'
    negative: bool=False
    modal: Optional[str]=None
    object: Optional[NPIR]=None
    indirect_object: Optional[NPIR]=None
    complement: Optional[NPIR]=None
    complement_kind: Optional[str]=None # adjective|nominal
    modifiers: list[ModifierIR]=field(default_factory=list)
    particles: list[str]=field(default_factory=list)
    pps: list[PPIR]=field(default_factory=list)
    comparison: Optional[ComparisonIR]=None
    conjunction: Optional[str]=None
    coordinated: list['PredicateIR']=field(default_factory=list)

    @property
    def adverbs(self):
        # Backward-compatible view used by pre-v6.5 callers/tests.
        return [m.source or m.lemma for m in self.modifiers]

@dataclass
class ClauseIR:
    subject: Optional[NPIR]
    predicate: PredicateIR
    clause_type: str='declarative'
    conjunction: Optional[str]=None
    coordinated: Optional['ClauseIR']=None
    source_tokens: list[str]=field(default_factory=list)

    def to_dict(self): return asdict(self)
