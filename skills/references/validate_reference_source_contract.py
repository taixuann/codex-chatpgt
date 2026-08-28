#!/usr/bin/env python3
from pathlib import Path
import yaml
REQUIRED = set(yaml.safe_load((Path(__file__).parent/'argus-reference-source-contract.yaml').read_text())['required'])
def check(item):
    if not REQUIRED <= set(item): return False
    b, s = item['bounded_path_source_service'], item['scope']
    return any(b.get(k) for k in ('paths','sources','services')) and bool(s.get('include')) and 'exclude' in s and bool(item['authority']) and bool(item['priority']) and item['load_strategy'] in {'minimum-first','controlled-expansion','saturation-stop'} and bool(item['freshness'].get('required')) and isinstance(item['validated'], bool)
def main():
    d = yaml.safe_load((Path(__file__).parent/'argus-reference-source-fixtures.yaml').read_text())
    assert all(check(d[k]) for k in ('multi_source_current','stale_conflict','narrow_source'))
    assert len(d['multi_source_current']['bounded_path_source_service']['paths']) == 1
    assert d['stale_conflict']['validated'] is False and d['stale_conflict']['supersession']['status'] == 'conflict'
    assert d['narrow_source']['scope']['exclude'] == ['all-other-paths']
    print('PASS reference-source map: multi-source priority, stale/conflict, and narrow-scope fixtures validated')
if __name__ == '__main__': main()
