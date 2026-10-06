#!/usr/bin/env python3
"""Shared language-package I/O and validation."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import json

SCHEMA_VERSION=2
TOOL_VERSION='6.1'

@dataclass(frozen=True)
class EntryKey:
    gloss:str
    pos:str
@dataclass
class Entry:
    key:EntryKey
    expr:str|None=None
    line_no:int=0

def resolve_project_path(project:Path,value:Path)->Path:
    return value.resolve() if value.is_absolute() else (project/value).resolve()

def resolve_language_path(project:Path,value:Path)->Path:
    p=resolve_project_path(project,value)
    return p/'language.json' if p.is_dir() else p

def load_language(path:Path):
    raw=path.read_bytes()
    text=raw.decode('utf-8-sig') if raw.startswith(b'\xef\xbb\xbf') else raw.decode('utf-8')
    data=json.loads(text)
    if not isinstance(data,dict): raise ValueError('language.json must contain a JSON object')
    grammar=data.get('grammar'); lexicon=data.get('lexicon')
    if not isinstance(grammar,dict): raise ValueError("language.json does not contain a usable 'grammar' object")
    if not isinstance(lexicon,list): raise ValueError("language.json does not contain a usable 'lexicon' array")
    entries=[]; forms={}
    for i,item in enumerate(lexicon,1):
        if not isinstance(item,dict): continue
        gloss=str(item.get('gloss','')).strip(); pos=str(item.get('pos','')).strip(); form=str(item.get('form','')).strip()
        if not gloss or not pos: continue
        e=Entry(EntryKey(gloss,pos),item.get('derivation'),i); entries.append(e)
        if form: forms[e.key]=form
    if not entries: raise ValueError('language.json contains no usable lexical entries')
    return data,grammar,entries,forms

def validate_package(data,entries,forms):
    issues=[]; warnings=[]
    schema=data.get('schema_version',1)
    if not isinstance(schema,int): issues.append('schema_version must be an integer')
    elif schema>SCHEMA_VERSION: warnings.append(f'package schema {schema} is newer than this tool supports ({SCHEMA_VERSION})')
    seen_forms={}
    for e in entries:
        f=forms.get(e.key,'')
        if not f: issues.append(f'missing form: {e.key.gloss}:{e.key.pos}'); continue
        label=f'{e.key.gloss}:{e.key.pos}'
        if f in seen_forms and seen_forms[f]!=label: warnings.append(f'homophone: {label} = {seen_forms[f]} = {f}')
        else: seen_forms[f]=label
    for key in ('word_order','morphemes','pronouns','verb'):
        if key not in data.get('grammar',{}): issues.append(f'grammar missing required key: {key}')
    return issues,warnings
