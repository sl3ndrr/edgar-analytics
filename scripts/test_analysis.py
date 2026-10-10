import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import pandas as pd
from analyze import prepare, fifo, run, evaluate, longest_pause, longest_pauses, shortest_holds
from anonymize import leak_check, names_from

def order(i,typ,qty,amount,fee=-1,time='2026-03-01T09:00:00Z'):
    return {'id':f't{i:06d}','datetime':time,'type':typ,'symbol':'XX0000000001','name':'Example',
            'asset_class':'STOCK','shares':qty,'amount':amount,'fee':fee,'tax':None,'price':abs(amount/qty)}

class FifoTests(unittest.TestCase):
    def test_pause_cutoff_only_changes_pause(self):
        events=prepare([order(1,'BUY',1,-10,time='2025-04-16T09:00:00Z'),
                        order(2,'BUY',1,-10,time='2025-05-05T09:00:00Z'),
                        order(3,'BUY',1,-10,time='2025-05-13T09:00:00Z')])
        closed,unknown,snaps=fifo(events,{})
        args=('all','2025-04-16','2025-05-13',events,closed,unknown,snaps,{'prices_provided':False})
        before=evaluate(*args)
        after=evaluate(*args,pause_analysis_start='2025-05-01')
        self.assertEqual(after['activity']['longest_pause'],{'full_days':7,'from':'2025-05-05','to':'2025-05-13'})
        before['activity']['longest_pause']=after['activity']['longest_pause']
        before['activity']['longest_pauses']=after['activity']['longest_pauses']
        self.assertEqual(before,after)
        april=evaluate('2025-04','2025-04-16','2025-04-30',events,closed,unknown,snaps,{'prices_provided':False},'2025-05-01')
        self.assertEqual(april['activity']['longest_pause'],{'full_days':0,'from':None,'to':None})
        self.assertEqual(april['activity']['trading_days'],1)

    def test_pause_without_cutoff(self):
        self.assertEqual(longest_pause(['2025-05-05','2025-04-16']),
                         {'full_days':18,'from':'2025-04-16','to':'2025-05-05'})

    def test_pause_window_and_top_five(self):
        days = ['2025-04-16', '2025-05-05', '2025-05-13', '2025-05-19',
                '2025-05-24', '2025-05-29', '2025-06-02', '2025-06-06',
                '2026-08-21', '2026-09-02']
        pauses = longest_pauses(days, '2025-05-01', '2025-06-06')
        self.assertEqual([p['full_days'] for p in pauses], [7, 5, 4, 4, 3])
        self.assertEqual([p['from'] for p in pauses], days[1:6])
        self.assertEqual(longest_pause(days, '2025-05-01', '2025-06-06'), pauses[0])
        self.assertEqual(longest_pauses(['2026-08-21', '2026-09-02'], None, '2026-08-21'), [])
        self.assertEqual(longest_pauses(['2025-05-01', '2025-05-02']), [])
        for start, end in [('2025-04-01', '2025-04-30'), ('2026-09-01', '2026-09-30')]:
            events = prepare([order(1, 'BUY', 1, -10, time=start+'T09:00:00Z'),
                              order(2, 'BUY', 1, -10, time=end+'T09:00:00Z')])
            closed, unknown, snaps = fifo(events, {})
            args = ('test', start, end, events, closed, unknown, snaps, {'prices_provided': False})
            before = evaluate(*args)
            after = evaluate(*args, pause_analysis_start='2025-05-01', pause_analysis_end='2026-08-21')
            self.assertEqual(after['activity']['longest_pauses'], [])
            self.assertEqual(after['activity']['longest_pause'], {'full_days': 0, 'from': None, 'to': None})
            for field in ['longest_pause', 'longest_pauses']:
                before['activity'][field] = after['activity'][field]
            self.assertEqual(before, after)

    def test_shortest_filter_sort_ties_and_limit(self):
        def trade(i, hours, proceeds, date='2026-03-02'):
            return dict(id=str(i), name='Example', isin='XX0000000001', date=date,
                        hours=hours, proceeds=proceeds, net=1, net_percent=10)
        rows = [trade('cent', 0, .01), trade('late', 1, 20), trade('early', 1, 20, '2026-03-01'),
                trade('five', .5, 5), trade('low', 1, 10), trade('slow', 2, 30), trade('last', 3, 40)]
        self.assertEqual([t['id'] for t in shortest_holds(rows)], ['five', 'early', 'late', 'low', 'slow'])
        self.assertEqual(shortest_holds(rows, 0)[0]['id'], 'cent')
        self.assertEqual(shortest_holds(rows, 35), [rows[-1]])
        self.assertEqual(shortest_holds([], 0), [])
        self.assertEqual(shortest_holds(rows, 100), [])

    def test_shortest_weighted_lots_and_empty_period(self):
        events = prepare([order(1, 'BUY', 1, -10, time='2026-03-01T08:00:00Z'),
                          order(2, 'BUY', 3, -30, time='2026-03-01T09:00:00Z'),
                          order(3, 'SELL', -4, 48, time='2026-03-01T10:00:00Z')])
        closed, unknown, snaps = fifo(events, {})
        p = evaluate('all', '2026-03-01', '2026-03-01', events, closed, unknown, snaps, {'prices_provided': False})
        self.assertEqual(p['holding']['shortest'][0]['hours'], 1.25)
        self.assertEqual(set(p['holding']['shortest'][0]), {'id','name','isin','date','hours','proceeds','net','net_percent'})
        empty = evaluate('empty', '2026-04-01', '2026-04-30', events, closed, unknown, snaps, {'prices_provided': False})
        self.assertEqual(empty['holding']['shortest'], [])

    def test_waterfall_reconciles_all_periods(self):
        summary=json.loads((Path(__file__).resolve().parents[1]/'data/summary.json').read_text())
        for key,p in summary['periods'].items():
            with self.subTest(period=key):
                c=p['core']
                self.assertLessEqual(abs(c['gross']-p['costs']['realized_fees']-c['net']),.01)
                self.assertLessEqual(abs(c['net']+c['dividends']+c['interest']+c['tax_signed']-c['result']),.01)
                self.assertLessEqual(abs(c['gross']-p['costs']['realized_fees']+c['dividends']+c['interest']+c['tax_signed']-c['result']),.01)

    def test_partial_lots_and_fee_allocation(self):
        events=prepare([order(1,'BUY',10,-100),order(2,'BUY',10,-200),order(3,'SELL',-15,300,time='2026-03-02T10:00:00Z')])
        closed,unknown,snaps=fifo(events,{})
        self.assertFalse(unknown)
        self.assertAlmostEqual(closed[0]['cost'],200)
        self.assertAlmostEqual(closed[0]['buy_fees'],1.5)
        self.assertAlmostEqual(closed[0]['net'],97.5)
        self.assertAlmostEqual(snaps['2026-03-02']['open_cost'],100.5)
    def test_unmatched_sale_only_allocates_known_part(self):
        closed,unknown,_=fifo(prepare([order(1,'BUY',5,-50),order(2,'SELL',-10,120)]),{})
        self.assertAlmostEqual(closed[0]['net'],8.5)
        self.assertAlmostEqual(unknown[0]['proceeds'],60)
        self.assertAlmostEqual(unknown[0]['sell_fees'],.5)
        self.assertTrue(closed[0]['partial'])
    def test_berlin_day_and_mixed_iso(self):
        events=prepare([order(1,'BUY',1,-10,time='2026-03-01T23:30:00.123456Z'),order(2,'SELL',-1,12,time='2026-03-02T08:00:00Z')])
        closed,_,_=fifo(events,{})
        self.assertEqual(events[0]['day'],'2026-03-02')
        self.assertTrue(closed[0]['daytrade'])
    def test_missing_fee_and_optional_valuation(self):
        _,_,snaps=fifo(prepare([order(1,'BUY',10,-100,fee=None)]),{'XX0000000001':12})
        self.assertAlmostEqual(snaps['2026-03-01']['positions'][0]['unrealized'],20)
    def test_name_and_generic_leaks_fail(self):
        with TemporaryDirectory() as directory:
            p=Path(directory)/'sample.json';p.write_text('{"name":"TestSurname"}')
            with self.assertRaises(ValueError):leak_check(Path(directory),{'TestSurname'})
            p.write_text('{"contact":"test@example.invalid"}')
            with self.assertRaises(ValueError):leak_check(Path(directory),set())
    def test_export_reconciles_all_periods(self):
        path=Path(__file__).resolve().parents[1]/'data/summary.json'
        if not path.exists():self.skipTest('Kein Ergebnisexport vorhanden.')
        s=json.loads(path.read_text());p=s['periods']['all']
        for item in s['periods'].values():
            self.assertAlmostEqual(item['capital']['unexplained_difference'],0,places=2)
        for field in ['buy_volume','sell_volume','gross','net','result','orders']:
            self.assertAlmostEqual(sum(s['periods'][k]['core'][field] for k in s['months']),p['core'][field],places=2)
        self.assertAlmostEqual(p['core']['net']+p['core']['dividends']+p['core']['interest']+p['core']['tax_signed'],p['core']['result'],places=2)

if __name__=='__main__':unittest.main()
