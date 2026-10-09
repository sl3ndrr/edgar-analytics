#!/usr/bin/env python3
"""Allowlist anonymization; raw personal fields never enter published data."""
import argparse
import json
import re
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
REMOVED = {'counterparty_name', 'counterparty_iban', 'payment_reference', 'mcc_code',
           'description', 'transaction_id', 'account_type'}
KEEP = ['datetime', 'date', 'category', 'type', 'asset_class', 'name', 'symbol',
        'shares', 'price', 'amount', 'fee', 'tax', 'currency']
PATTERNS = {'IBAN': r'(?<![A-Z0-9])[A-Z]{2}\d{2}[A-Z0-9]{10,30}(?![A-Z0-9])',
            'email': r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}',
            'UUID': r'\b[0-9a-fA-F]{8}-(?:[0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12}\b'}

def read_raw(paths):
    frames = [pd.read_csv(p, dtype=str, keep_default_na=False) for p in paths]
    if not frames:
        raise ValueError('Keine CSV-Dateien in raw/.')
    df = pd.concat(frames, ignore_index=True)
    required = set(KEEP + ['transaction_id', 'counterparty_name'])
    if required - set(df.columns):
        raise ValueError('Erforderliche Spalten fehlen.')
    if df.transaction_id.eq('').any():
        raise ValueError('Leere transaction_id: sichere Deduplizierung nicht möglich.')
    conflicts = df.groupby('transaction_id').filter(lambda g: len(g.drop_duplicates()) > 1)
    if len(conflicts):
        raise ValueError('Widersprüchliche Zeilen mit gleicher transaction_id.')
    return df

def names_from(df):
    # Full counterparty names and all constituent words, including surnames.
    names = set(df.counterparty_name[df.counterparty_name.ne('')])
    for field in ['counterparty_name', 'description', 'payment_reference']:
        if field in df:
            for value in df[field]:
                names.update(re.findall(r'(?i)(?:kontoinhaber|account holder|empfänger|sender)\s*[:=]\s*([^;\n]+)', value))
    for name in list(names):
        names.update(re.findall(r"[^\W\d_]+(?:[-'][^\W\d_]+)*", name))
    return names - {'Edgar'}

def leak_check(root, names):
    checked = 0
    for path in root.rglob('*'):
        if not path.is_file() or path.suffix.lower() not in {'.json', '.html', '.js', '.md'}:
            continue
        if {'raw', '.git', '.private', 'node_modules'} & set(path.relative_to(root).parts):
            continue
        value = path.read_text(encoding='utf-8')
        checked += 1
        for kind, pattern in PATTERNS.items():
            if re.search(pattern, value):
                raise ValueError(f'Leak-Check fehlgeschlagen: {kind} in {path.relative_to(root)}')
        for name in names:
            if re.search(r'(?<!\w)' + re.escape(name) + r'(?!\w)', value, re.I):
                raise ValueError(f'Leak-Check fehlgeschlagen: persönlicher Name in {path.relative_to(root)}')
    return checked

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('files', nargs='*', type=Path)
    parser.add_argument('--check-only', action='store_true')
    args = parser.parse_args()
    df = read_raw(args.files or sorted((ROOT / 'raw').glob('*.csv')))
    names = names_from(df)
    if args.check_only:
        print(f'Leak-Check bestanden ({leak_check(ROOT, names)} veröffentlichbare Textdateien).')
        return
    raw_count = len(df)
    df = df.drop_duplicates('transaction_id', keep='first').copy()
    times = pd.to_datetime(df.datetime, format='ISO8601', utc=True, errors='raise').dt.tz_convert('Europe/Berlin')
    df['_time'] = times
    df = df.sort_values('_time', kind='stable')
    df.datetime = df._time.map(lambda t: t.isoformat())
    date_mismatches = int((df.date != df._time.dt.strftime('%Y-%m-%d')).sum())
    df.date = df._time.dt.strftime('%Y-%m-%d')
    if set(df.currency) != {'EUR'}:
        raise ValueError('Nur EUR unterstützt; keine implizite Währungsumrechnung.')
    records = []
    for i, row in enumerate(df.to_dict('records'), 1):
        transfer = row['type'].startswith('TRANSFER_')
        out = {'id': f't{i:06d}'}
        if transfer:
            if any(float(row[k] or 0) != 0 for k in ['fee','tax']):
                raise ValueError('Transfer enthält separate Gebühren/Steuern: Buchungslogik muss zuerst geklärt werden.')
            out.update(date=row['date'], type='TRANSFER', direction='in' if 'INBOUND' in row['type'] else 'out', amount=float(row['amount']))
        else:
            out.update({k: row[k] for k in KEEP if k not in {'date'}})
            for key in ['shares', 'price', 'amount', 'fee', 'tax']:
                out[key] = None if row[key] == '' else float(row[key])
        records.append(out)
    payload = {'schema_version': 1, 'records': records, 'checks': {
        'input_rows': raw_count, 'rows': len(df), 'duplicates_removed': raw_count - len(df),
        'rows_by_type': df.type.value_counts().to_dict(), 'date_mismatches_corrected': date_mismatches,
        'missing_by_column': {k: int(df[k].eq('').sum()) for k in KEEP},
        'timezone': 'Europe/Berlin', 'currency': 'EUR'}}
    ignore_path = ROOT / '.gitignore'
    existing = ignore_path.read_text(encoding='utf-8').splitlines() if ignore_path.exists() else []
    required = ['raw/','*.csv','.private/','__pycache__/','*.pyc','*.tmp','.DS_Store','qa/','node_modules/','test-results/','public/','package-lock.json']
    ignore_path.write_text('\n'.join(existing + [line for line in required if line not in existing]) + '\n', encoding='utf-8')
    private = ROOT / '.private'
    private.mkdir(exist_ok=True)
    output = private / 'transactions.json'
    output.write_text(json.dumps(payload, ensure_ascii=False, allow_nan=False), encoding='utf-8')
    # Private output is checked too, without exposing the name list itself.
    temp = ROOT / 'data' / '_anonymized_check.json'
    temp.parent.mkdir(exist_ok=True)
    temp.write_text(output.read_text(), encoding='utf-8')
    try:
        checked = leak_check(ROOT, names)
    except Exception:
        output.unlink(missing_ok=True)
        raise
    finally:
        temp.unlink(missing_ok=True)
    print(f'Anonymisiert: {len(df)} Zeilen. Leak-Check bestanden ({checked} Textdateien).')

if __name__ == '__main__':
    main()
