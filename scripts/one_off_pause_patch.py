#!/usr/bin/env python3
"""One-off public summary patch; only activity.longest_pause may change."""
import copy
import json
from analyze import ROOT, longest_pause

def main():
    path = ROOT/'data/summary.json'
    before = json.loads(path.read_text(encoding='utf-8'))
    after = copy.deepcopy(before)
    cutoff = json.loads((ROOT/'config.json').read_text(encoding='utf-8')).get('pause_analysis_start')
    for key, period in after['periods'].items():
        days = [d['date'] for d in period['equity']['daily'] if d['orders'] > 0]
        pause = longest_pause(days, cutoff)
        old = before['periods'][key]['activity']['longest_pause']
        period['activity']['longest_pause'] = pause
        if old != pause:
            print(f'periods.{key}.activity.longest_pause: {old} -> {pause}')
    unchanged = copy.deepcopy(after)
    for key, period in unchanged['periods'].items():
        period['activity']['longest_pause'] = before['periods'][key]['activity']['longest_pause']
    assert unchanged == before, 'Unexpected change outside activity.longest_pause'
    path.write_text(json.dumps(after, ensure_ascii=False, allow_nan=False, separators=(',',':')), encoding='utf-8')
    print('All other JSON fields unchanged.')

if __name__ == '__main__':
    main()
