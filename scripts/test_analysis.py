import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import pandas as pd
from analyze import prepare, fifo, run
from anonymize import leak_check, names_from

def order(i,typ,qty,amount,fee=-1,time='2026-03-01T09:00:00Z'):
    return {'id':f't{i:06d}','datetime':time,'type':typ,'symbol':'XX0000000001','name':'Example',
            'asset_class':'STOCK','shares':qty,'amount':amount,'fee':fee,'tax':None,'price':abs(amount/qty)}

class FifoTests(unittest.TestCase):
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
