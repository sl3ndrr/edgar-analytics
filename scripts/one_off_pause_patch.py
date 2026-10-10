#!/usr/bin/env python3
"""Reconstruct public pause fields without raw data; assert all other data unchanged."""
import copy
import json
from analyze import ROOT, longest_pauses

def main():
    path = ROOT/'data/summary.json'
    before = json.loads(path.read_text(encoding='utf-8'))
    after = copy.deepcopy(before)
    config = json.loads((ROOT/'config.json').read_text(encoding='utf-8'))
    window = {'from': config.get('pause_analysis_start'), 'to': config.get('pause_analysis_end')}
    after['metadata']['pause_window'] = window
    for key, period in after['periods'].items():
        days = [d['date'] for d in period['equity']['daily'] if d['orders'] > 0]
        pauses = longest_pauses(days, window['from'], window['to'])
        period['activity']['longest_pauses'] = pauses
        period['activity']['longest_pause'] = pauses[0] if pauses else {'full_days': 0, 'from': None, 'to': None}
    unchanged = copy.deepcopy(after)
    for key, period in unchanged['periods'].items():
        for field in ['longest_pause', 'longest_pauses']:
            original = before['periods'][key]['activity']
            if field in original:
                period['activity'][field] = original[field]
            else:
                period['activity'].pop(field, None)
    if 'pause_window' in before['metadata']:
        unchanged['metadata']['pause_window'] = before['metadata']['pause_window']
    else:
        unchanged['metadata'].pop('pause_window', None)
    assert unchanged == before, 'Unexpected change outside pause fields and metadata.pause_window'
    path.write_text(json.dumps(after, ensure_ascii=False, allow_nan=False, separators=(',',':')), encoding='utf-8')
    print('All other JSON fields unchanged.')
    print(json.dumps(after['periods']['all']['activity']['longest_pauses'], ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
