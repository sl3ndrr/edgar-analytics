"""Public-side defensive check. Personal-name check additionally requires raw input locally."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = [r'(?<![A-Z0-9])[A-Z]{2}\d{2}[A-Z0-9]{10,30}(?![A-Z0-9])',
            r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}',
            r'\b[0-9a-fA-F]{8}-(?:[0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12}\b']
def main():
    summary = json.loads((ROOT/'data/summary.json').read_text())
    assert summary['checks']['leak_check'] == 'passed', 'Lokaler Leak-Check fehlt.'
    for directory in ['data','config','src','vendor']:
        for p in (ROOT/directory).rglob('*'):
            if p.suffix in {'.json','.js','.html','.md'}:
                text=p.read_text()
                assert not any(re.search(pattern,text) for pattern in PATTERNS), 'Leak-Muster im öffentlichen Inhalt.'
    for p in [ROOT/'index.html',ROOT/'config.json',ROOT/'README.md']:
        assert not any(re.search(pattern,p.read_text()) for pattern in PATTERNS), 'Leak-Muster im öffentlichen Inhalt.'
    forbidden={'counterparty_name','counterparty_iban','payment_reference','mcc_code','description','transaction_id','account_type'}
    def walk(v):
        if isinstance(v,dict):
            assert not forbidden & set(v), 'Persönliches Datenfeld im JSON.'
            for item in v.values():walk(item)
        elif isinstance(v,list):
            for item in v:walk(item)
    walk(summary)
    for p in summary['periods'].values():
        assert abs(p['capital']['unexplained_difference']) < .01, 'Bilanz nicht erklärt.'
    print('Public payload: privacy patterns, forbidden fields and period balances passed.')
if __name__=='__main__':main()
