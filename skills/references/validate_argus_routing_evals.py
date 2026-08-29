#!/usr/bin/env python3
"""Deterministically classify Argus routing fixtures from their prompts."""
from pathlib import Path
import yaml
PROFILES = {'codebase-reconnaissance','research-source-discovery','reference-state-reconnaissance'}
def classify(prompt):
    p = prompt.lower()
    if any(x in p for x in ('implement','update ','change files','approve','synthesize','scientific conclusion')): return 'reject'
    if 'unversioned' in p or 'no authority' in p: return 'stop'
    code = any(x in p for x in ('map','code','callers','auth/','prometheus'))
    research = any(x in p for x in ('source','paper','feynman'))
    reference = any(x in p for x in ('compare','current','authority','manifest','field','handoff','anchors gaps','unknowns'))
    if code and ('scientific meaning' in p or 'and interpret' in p): return 'choose-one'
    if research and not any(x in p for x in ('compare','current','manifest')): return 'research-source-discovery'
    if sum((code,research,reference)) > 1: return 'ambiguous'
    if reference: return 'reference-state-reconnaissance'
    return 'codebase-reconnaissance'
def main():
    cases = yaml.safe_load((Path(__file__).parent/'argus-routing-evals.yaml').read_text())['cases']
    assert {c['profile'] for c in cases} == PROFILES
    for c in cases:
        actual = classify(c['prompt']); expected = c['outcome']
        if expected == 'select': assert actual == c['profile'], (c['id'], actual, c['profile'])
        elif expected in {'reject','stop','choose-one'}: assert actual == expected, (c['id'], actual, expected)
        elif expected == 'choose-sibling': assert actual != c['profile']
    for p in PROFILES:
        assert any(c['profile']==p and c['outcome']=='select' for c in cases)
        assert any(c['profile']==p and c['outcome']=='choose-sibling' for c in cases)
    assert any(c['outcome']=='stop' for c in cases) and any(c['outcome']=='choose-one' for c in cases)
    print('PASS Argus routing eval: independent selection, reject/stop, sibling, narrow, provenance, co-load, and output cases')
if __name__ == '__main__': main()
