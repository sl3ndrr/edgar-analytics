#!/usr/bin/env python3
"""FIFO analysis of allowlisted transactions, no raw personal fields required."""
import argparse
import json
from collections import defaultdict, deque, Counter
from datetime import timedelta
from pathlib import Path
import statistics
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EPS = 1e-9

def ratio(a, b, factor=1):
    return a / b * factor if b else None

def stamp(value):
    return pd.Timestamp(value).tz_convert('Europe/Berlin')

def money(v):
    return f'{v:,.2f}'.replace(',', '_').replace('.', ',').replace('_', '.') + ' €'

def tidy(value):
    if isinstance(value, dict):
        return {str(k): tidy(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [tidy(v) for v in value]
    if isinstance(value, float):
        return round(value, 8)
    return value

def prepare(records):
    events = []
    for r in records:
        r = dict(r)
        r['time'] = stamp(r['datetime']) if 'datetime' in r else pd.Timestamp(r['date'], tz='Europe/Berlin')
        r['day'] = r['time'].strftime('%Y-%m-%d')
        r['fee_missing'] = r.get('fee') is None
        r['fee'] = float(r.get('fee') or 0)
        r['tax'] = float(r.get('tax') or 0)
        r['amount'] = float(r['amount'])
        if r['type'] in {'BUY', 'SELL'}:
            if not r.get('symbol') or not r.get('shares'):
                raise ValueError('Handelszeile ohne Instrument oder Stückzahl.')
            if (r['type'] == 'BUY' and r['amount'] >= 0) or (r['type'] == 'SELL' and r['amount'] <= 0):
                raise ValueError('Unerwartetes Betragsvorzeichen.')
            r['qty'] = abs(float(r['shares']))
        events.append(r)
    return sorted(events, key=lambda r: (r['time'], r['id']))

def snapshot(lots, prices):
    positions = []
    for isin, ls in lots.items():
        q = sum(l['qty'] for l in ls)
        if q <= EPS:
            continue
        cost = sum(l['cost'] for l in ls)
        fees = sum(l['fees'] for l in ls)
        name = ls[0]['name']
        position = {'isin': isin, 'name': name, 'asset_class': ls[0]['asset_class'], 'shares': q,
                    'cost': cost, 'buy_fees': fees, 'cost_including_fees': cost + fees,
                    'market_value': q * prices[isin] if isin in prices else None,
                    'unrealized': q * prices[isin] - cost - fees if isin in prices else None}
        positions.append(position)
    return sorted(positions, key=lambda r: -r['cost'])

def fifo(events, prices):
    lots = defaultdict(deque)
    closed, unmatched, snapshots = [], [], {}
    cash = deposited = 0.
    for i, r in enumerate(events):
        typ = r['type']
        cash += r['amount'] + r['fee'] + r['tax']
        if typ == 'TRANSFER':
            deposited += r['amount']
        if typ == 'BUY':
            lots[r['symbol']].append({'qty': r['qty'], 'cost': -r['amount'], 'fees': -r['fee'],
                                      'time': r['time'], 'name': r['name'], 'asset_class': r['asset_class']})
        elif typ == 'SELL':
            left = r['qty']
            cost = fees = matched = weighted_hours = day_qty = 0.
            pieces = []
            while left > EPS and lots[r['symbol']]:
                lot = lots[r['symbol']][0]
                qty = min(left, lot['qty'])
                fraction = qty / lot['qty']
                c, f = lot['cost'] * fraction, lot['fees'] * fraction
                hours = (r['time'] - lot['time']).total_seconds() / 3600
                same_day = r['day'] == lot['time'].strftime('%Y-%m-%d')
                pieces.append({'shares': qty, 'hours': hours, 'daytrade': same_day})
                cost += c; fees += f; matched += qty; weighted_hours += qty * hours
                day_qty += qty if same_day else 0
                lot['qty'] -= qty; lot['cost'] -= c; lot['fees'] -= f; left -= qty
                if lot['qty'] <= EPS:
                    lots[r['symbol']].popleft()
            matched_fraction = matched / r['qty']
            if left > EPS:
                unmatched.append({'id': r['id'], 'name': r['name'], 'isin': r['symbol'], 'date': r['day'],
                                  'shares': left, 'proceeds': r['amount'] * (1 - matched_fraction),
                                  'sell_fees': -r['fee'] * (1 - matched_fraction)})
            if matched > EPS:
                proceeds = r['amount'] * matched_fraction
                sale_fee = -r['fee'] * matched_fraction
                gross = proceeds - cost
                net = gross - fees - sale_fee
                closed.append({'id': r['id'], 'name': r['name'], 'isin': r['symbol'], 'date': r['day'],
                               'datetime': r['time'].isoformat(), 'shares': matched,
                               'proceeds': proceeds, 'cost': cost, 'gross': gross, 'buy_fees': fees,
                               'sell_fees': sale_fee, 'fees': fees + sale_fee, 'net': net,
                               'net_percent': ratio(net, cost + fees, 100),
                               'hours': weighted_hours / matched, 'daytrade': day_qty >= matched - EPS,
                               'daytrade_share': day_qty / matched, 'partial': left > EPS, 'lots': pieces})
        if i == len(events) - 1 or events[i + 1]['day'] != r['day']:
            pos = snapshot(lots, prices)
            snapshots[r['day']] = {'cash': cash, 'net_deposited': deposited, 'positions': pos,
                                    'open_cost': sum(p['cost_including_fees'] for p in pos)}
    return closed, unmatched, snapshots

def streaks(trades):
    best = {'win': 0, 'loss': 0}
    active = None; count = 0
    for t in trades:
        sign = 'win' if t['net'] > 0.005 else 'loss' if t['net'] < -0.005 else None
        count = count + 1 if sign and sign == active else 1 if sign else 0
        active = sign
        if sign:
            best[sign] = max(best[sign], count)
    return best

def evaluate(key, start, end, events, all_closed, unmatched, snapshots, metadata):
    rows = [r for r in events if start <= r['day'] <= end]
    trades = [t for t in all_closed if start <= t['date'] <= end]
    unknown = [t for t in unmatched if start <= t['date'] <= end]
    orders = [r for r in rows if r['type'] in {'BUY', 'SELL'}]
    buys = [r for r in orders if r['type'] == 'BUY']; sells = [r for r in orders if r['type'] == 'SELL']
    purchase = sum(-r['amount'] for r in buys); sale = sum(r['amount'] for r in sells); volume = purchase + sale
    charges = sum(-r['fee'] for r in rows); gross = sum(t['gross'] for t in trades); net = sum(t['net'] for t in trades)
    dividends = sum(r['amount'] for r in rows if r['type'] == 'DIVIDEND')
    interest = sum(r['amount'] for r in rows if r['type'] == 'INTEREST_PAYMENT')
    tax_signed = sum(r['tax'] for r in rows)
    tax_optimization = sum(r['amount'] + r['tax'] for r in rows if r['type'] == 'TAX_OPTIMIZATION')
    result = net + dividends + interest + tax_signed + sum(r['amount'] for r in rows if r['type'] == 'TAX_OPTIMIZATION')
    transfers = [r for r in rows if r['type'] == 'TRANSFER']
    inbound = sum(r['amount'] for r in transfers if r['direction'] == 'in')
    outbound = sum(-r['amount'] for r in transfers if r['direction'] == 'out')
    deposited = inbound - outbound
    winning = [t['net'] for t in trades if t['net'] > .005]; losing = [t['net'] for t in trades if t['net'] < -.005]
    avgwin = statistics.mean(winning) if winning else None
    avgloss = statistics.mean(losing) if losing else None
    hours = [t['hours'] for t in trades]
    buckets = {'<1 h': 0, '1 h–<1 Tag': 0, '1–7 Tage': 0, '>7 Tage': 0}
    for h in hours:
        buckets['<1 h' if h < 1 else '1 h–<1 Tag' if h < 24 else '1–7 Tage' if h <= 168 else '>7 Tage'] += 1
    order_days = Counter(r['day'] for r in orders)
    daily_net = defaultdict(float); daily_result = defaultdict(float)
    for t in trades:
        daily_net[t['date']] += t['net']; daily_result[t['date']] += t['net']
    for r in rows:
        daily_result[r['day']] += r['tax']
        if r['type'] in {'DIVIDEND', 'INTEREST_PAYMENT', 'TAX_OPTIMIZATION'}:
            daily_result[r['day']] += r['amount']
    equity = []; running = peak = drawdown = 0.; peak_day = start; dd_start = dd_end = start
    for day in pd.date_range(start, end):
        date = day.strftime('%Y-%m-%d'); running += daily_net[date]
        if running >= peak:
            peak = running; peak_day = date
        if peak - running > drawdown:
            drawdown = peak - running; dd_start = peak_day; dd_end = date
        equity.append({'date': date, 'net_cumulative': running, 'result_daily': daily_result[date], 'net_daily': daily_net[date], 'orders': order_days[date]})
    heatmap = [[0] * 24 for _ in range(7)]
    for r in orders:
        heatmap[r['time'].weekday()][r['time'].hour] += 1
    days = sorted(k for k,v in order_days.items() if v)
    pauses = [(max(0, (pd.Timestamp(b) - pd.Timestamp(a)).days - 1), a, b) for a,b in zip(days, days[1:])]
    pause = max(pauses, default=(0, None, None))
    titles = {}; classes = defaultdict(lambda: {'volume': 0., 'orders': 0, 'net': 0.})
    for r in orders:
        s = titles.setdefault(r['symbol'], {'isin': r['symbol'], 'name': r['name'], 'asset_class': r['asset_class'], 'volume': 0., 'orders': 0, 'net': 0., 'gross': 0., 'fees': 0., 'cost': 0., 'closed': 0})
        s['volume'] += abs(r['amount']); s['orders'] += 1
        classes[r['asset_class']]['volume'] += abs(r['amount']); classes[r['asset_class']]['orders'] += 1
    for t in trades:
        s = titles[t['isin']]
        for field in ['net', 'gross', 'fees', 'cost']:
            s[field] += t[field]
        s['closed'] += 1; classes[s['asset_class']]['net'] += t['net']
    for s in titles.values():
        s['net_percent'] = ratio(s['net'], s['cost'] + sum(t['buy_fees'] for t in trades if t['isin'] == s['isin']), 100)
    title_list = sorted(titles.values(), key=lambda s: -s['volume'])
    prior_days = sorted(d for d in snapshots if d < start); end_days = sorted(d for d in snapshots if d <= end)
    before = snapshots[prior_days[-1]] if prior_days else {'cash': 0., 'open_cost': 0., 'net_deposited': 0., 'positions': []}
    after = snapshots[end_days[-1]] if end_days else before
    lhs = after['cash'] - before['cash'] + after['open_cost'] - before['open_cost'] - deposited
    difference = lhs - result
    unknown_effect = sum(t['proceeds'] - t['sell_fees'] for t in unknown)
    clean_rows = [{k: t[k] for k in ['id','name','isin','date','shares','proceeds','cost','gross','buy_fees','sell_fees','fees','net','net_percent','hours','daytrade','partial']} for t in trades]
    best = sorted(clean_rows, key=lambda t: -t['net']); worst = sorted(clean_rows, key=lambda t: t['net'])
    period = {'id': key, 'start': start, 'end': end, 'core': {
        'buy_volume': purchase, 'sell_volume': sale, 'total_volume': volume,
        'buy_orders': len(buys), 'sell_orders': len(sells), 'orders': len(orders),
        'gross': gross, 'net': net, 'result': result, 'dividends': dividends, 'interest': interest,
        'tax_signed': tax_signed, 'taxes_net': -tax_signed, 'tax_optimization_signed': tax_optimization},
        'costs': {'fees': charges, 'fees_per_order': ratio(charges,len(orders)), 'basis_points': ratio(charges, volume,10000),
                  'realized_fees': sum(t['fees'] for t in trades), 'fees_share_gross_percent': ratio(sum(t['fees'] for t in trades),gross,100) if gross > 0 else None,
                  'fee_caused_losses': sum(t['gross'] >= 0 and t['net'] < -.005 for t in trades)},
        'quality': {'closed_trades': len(trades), 'wins': len(winning), 'losses': len(losing), 'breakeven': len(trades)-len(winning)-len(losing),
                    'hit_rate': ratio(len(winning),len(trades),100), 'average_win': avgwin, 'average_loss': avgloss,
                    'win_loss_ratio': ratio(avgwin,abs(avgloss)) if avgwin is not None and avgloss else None,
                    'profit_factor': ratio(sum(winning),-sum(losing)), 'expected_value': ratio(net,len(trades)),
                    'net_per_trading_day': ratio(net,len(days)), 'profitable_days_percent': ratio(sum(daily_net[d] > .005 for d in days),len(days),100),
                    'winning_streak': streaks(trades)['win'], 'losing_streak': streaks(trades)['loss']},
        'holding': {'daytrades': sum(t['daytrade'] for t in trades), 'daytrade_percent': ratio(sum(t['daytrade'] for t in trades),len(trades),100),
                    'median_hours': statistics.median(hours) if hours else None, 'mean_hours': statistics.mean(hours) if hours else None, 'buckets': buckets},
        'activity': {'heatmap': heatmap, 'daily': [{'date': d, 'orders': order_days[d]} for d in days], 'trading_days': len(days),
                     'active_days': sorted([{'date':d,'orders':order_days[d]} for d in days],key=lambda d: -d['orders'])[:10],
                     'longest_pause': {'full_days': pause[0], 'from':pause[1], 'to':pause[2]}},
        'equity': {'daily': equity, 'max_drawdown': drawdown, 'drawdown_start': dd_start, 'drawdown_end': dd_end},
        'capital': {'deposited': inbound, 'withdrawn': outbound, 'net_deposited': deposited,
                    'return_on_net_deposit_percent': ratio(result,deposited,100) if deposited > 0 else None,
                    'turnover': ratio(volume,deposited) if deposited > 0 else None,
                    'cash_start': before['cash'], 'cash_end': after['cash'], 'open_cost_start': before['open_cost'], 'open_cost_end': after['open_cost'],
                    'cumulative_net_deposited': after['net_deposited'], 'balance_lhs': lhs, 'balance_difference': difference,
                    'unmatched_effect': unknown_effect, 'unexplained_difference': difference - unknown_effect,
                    'positions': after['positions'], 'valuation': 'not_valued' if not metadata['prices_provided'] else 'partial' if any(p['unrealized'] is None for p in after['positions']) else 'prices_provided',
                    'unrealized': sum(p['unrealized'] for p in after['positions']) if metadata['prices_provided'] and all(p['unrealized'] is not None for p in after['positions']) else None},
        'titles': title_list, 'classes': dict(classes), 'concentration_top10_percent': ratio(sum(s['volume'] for s in title_list[:10]),volume,100),
        'top': {'wins': [t for t in best if t['net'] > .005][:5], 'losses': [t for t in worst if t['net'] < -.005][:5],
                'titles_wins': sorted([s for s in title_list if s['net'] > .005],key=lambda s:-s['net'])[:5],
                'titles_losses': sorted([s for s in title_list if s['net'] < -.005],key=lambda s:s['net'])[:5],
                'wins_percent': sorted([t for t in clean_rows if t['net_percent'] is not None and t['net_percent'] > 0],key=lambda t:-t['net_percent'])[:5],
                'losses_percent': sorted([t for t in clean_rows if t['net_percent'] is not None and t['net_percent'] < 0],key=lambda t:t['net_percent'])[:5],
                'titles_wins_percent': sorted([s for s in title_list if s['net_percent'] is not None and s['net_percent'] > 0],key=lambda s:-s['net_percent'])[:5],
                'titles_losses_percent': sorted([s for s in title_list if s['net_percent'] is not None and s['net_percent'] < 0],key=lambda s:s['net_percent'])[:5]},
        'checks': {'rows': len(rows), 'rows_by_type': dict(Counter(r['type'] for r in rows)), 'missing_fee_trades': sum(r['fee_missing'] for r in orders),
                   'missing_fee_percent': ratio(sum(r['fee_missing'] for r in orders),len(orders),100), 'unmatched_sales': len(unknown),
                   'unmatched_volume': sum(t['proceeds'] for t in unknown), 'unmatched_details': unknown,
                   'price_mismatches': sum(abs(abs(r['amount'])-r['qty']*r['price']) > .011 for r in orders),
                   'price_mismatch_ids': [r['id'] for r in orders if abs(abs(r['amount'])-r['qty']*r['price']) > .011],
                   'cash_ledger_delta': sum(r['amount']+r['fee']+r['tax'] for r in rows),
                   'cash_balance_verified': False, 'start':start, 'end':end},
        'broker': {'visible_fees': charges, 'interest_paid': interest, 'fees_less_interest': charges-interest, 'spread_observable': False}}
    texts = [f'Das zuordenbare Ergebnis nach Gebühren und ausgewiesenen Steuern beträgt {money(result)}.',
             f'Für {len(orders):,} Handelszeilen wurden {money(charges)} Gebühren ausgewiesen.'.replace(',', '.'),
             f'{len(winning)} von {len(trades)} zuordenbaren Verkaufszeilen endeten nach Gebühren im Plus.',
             f'{sum(t["gross"] >= 0 and t["net"] < -.005 for t in trades)} Verkaufszeilen wurden erst durch Gebühren negativ.',
             f'{len(unknown)} Verkäufe enthalten Mengen ohne Kauf-Lot im Export; ihr Erlös wird getrennt ausgewiesen.',
             f'Der Export zeigt {money(interest)} Guthabenzinsen. Spreads und der tatsächliche Anbietergewinn sind nicht ermittelbar.']
    period['conclusions'] = texts
    return period

def run(input_path, prices_path):
    payload = json.loads(input_path.read_text(encoding='utf-8'))
    events = prepare(payload['records'])
    allowed = {'BUY','SELL','DIVIDEND','INTEREST_PAYMENT','TAX_OPTIMIZATION','TRANSFER'}
    if set(r['type'] for r in events) - allowed:
        raise ValueError('Nicht unterstützter Transaktionstyp.')
    prices = {}
    if prices_path.exists():
        p = pd.read_csv(prices_path)
        if not {'isin','price'} <= set(p.columns) or p['isin'].duplicated().any() or p['price'].isna().any() or (p['price'] <= 0).any():
            raise ValueError('Preise müssen eindeutig und positiv sein.')
        prices = dict(zip(p['isin'], p['price']))
    closed, unmatched, snapshots = fifo(events, prices)
    start, end = events[0]['day'], events[-1]['day']
    metadata = {'prices_provided': bool(prices), 'timezone': 'Europe/Berlin', 'currency':'EUR', 'row_is_order':True,
                'methodology': 'FIFO je ISIN über den gesamten Export. Gebuchte Beträge sind maßgeblich; Kaufgebühren werden anteilig realisierten Lots zugeordnet. Gebühren und Steuern sind separate Cash-Buchungen. Keine Bewertung offener Positionen ohne bereitgestellte Kurse.',
                'limits': ['Exportzeilen sind keine sicher identifizierbaren Börsenorders; Bruchstücke können separate Ausführungen derselben Order sein.',
                           'Realisierte Ergebnisse schließen Erlöse ohne Kauf-Lot aus. Anfangsbestand und dessen Einstand sind nicht rekonstruierbar.',
                           'Cash ist aus dem Export berechnet. Ein unabhängiger Kontoauszug zur Bestätigung liegt nicht vor.',
                           'Steuern werden als signierte Cash-Buchungen im Buchungsmonat berücksichtigt, auch Kaufsteuern und TAX_OPTIMIZATION.',
                           'Rendite auf Netto-Einzahlung ist ein einfacher Quotient, keine zeitgewichtete oder kapitalgewichtete Depotrendite.',
                           'Historische offene Positionen werden zu ihren jeweiligen Monatsenden gezeigt; optionale Preise sind ein einheitlicher, vom Nutzer gelieferter Kursstand.']}
    periods = {'all': evaluate('all',start,end,events,closed,unmatched,snapshots,metadata)}
    for prefix in sorted(set(r['day'][:7] for r in events)):
        s = max(start,prefix+'-01'); e = min(end,(pd.Timestamp(prefix+'-01')+pd.offsets.MonthEnd(0)).strftime('%Y-%m-%d'))
        periods[prefix] = evaluate(prefix,s,e,events,closed,unmatched,snapshots,metadata)
    for year in sorted(set(r['day'][:4] for r in events)):
        periods[year] = evaluate(year,max(start,year+'-01-01'),min(end,year+'-12-31'),events,closed,unmatched,snapshots,metadata)
    checks = dict(payload['checks'])
    checks.update(periods['all']['checks'])
    checks['raw_rows_by_type'] = payload['checks']['rows_by_type']
    checks['cash_balance'] = periods['all']['capital']['cash_end']
    checks['amount_matches_quantity_price_rows'] = periods['all']['core']['orders'] - checks['price_mismatches']
    checks['sell_with_tax_count'] = sum(r['type']=='SELL' and r['tax']!=0 for r in events)
    taxed_sales = [r for r in events if r['type']=='SELL' and r['tax'] != 0]
    taxed_matches = sum(abs(r['amount'] - r['qty'] * r['price']) <= .011 for r in taxed_sales)
    if taxed_matches != len(taxed_sales):
        raise ValueError('Besteuerte Verkaufsbeträge weichen von Stückzahl × Kurs ab. Steuerbereinigung muss vor der Analyse geklärt werden.')
    checks['taxed_sell_matches_product'] = taxed_matches
    checks['tax_evidence'] = (f'{taxed_matches} von {len(taxed_sales)} besteuerten Verkaufszeilen entsprechen Stückzahl × Kurs innerhalb von 0,011 €. amount ist in diesen Zeilen nicht um die separat ausgewiesene Steuer vermindert. ' if taxed_sales else 'Keine besteuerten Verkäufe zur direkten Prüfung vorhanden. ') + 'Cash wird als amount + fee + tax gebucht; Ertragsbuchungen mit Steuerfeldern werden als separate Buchungen behandelt. Ein unabhängiger Kontoauszug liegt nicht vor.'
    orders = [r for r in events if r['type'] in {'BUY','SELL'}]
    checks['price_scale1000_count'] = sum(abs(r['amount']) > 0 and abs(abs(r['amount']) - r['qty'] * r['price']) > .011 and abs(abs(r['amount']) - r['qty'] * r['price']/1000) <= .011 for r in orders)
    checks['other_price_mismatch_count'] = checks['price_mismatches'] - checks['price_scale1000_count']
    checks['leak_check'] = 'pending'
    summary = {'schema_version': 1, 'metadata': metadata, 'checks':checks, 'periods':periods,
               'months': [k for k in periods if len(k)==7], 'years':[k for k in periods if len(k)==4]}
    return tidy(summary), closed

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=Path, default=ROOT/'.private/transactions.json')
    parser.add_argument('--prices', type=Path, default=ROOT/'data/prices.csv')
    args = parser.parse_args()
    summary, _ = run(args.input,args.prices)
    target = ROOT/'data/summary.json'
    target.write_text(json.dumps(summary, ensure_ascii=False,allow_nan=False,separators=(',',':')),encoding='utf-8')
    # Enforce the raw-name check after generation whenever the raw source is present.
    from anonymize import read_raw, names_from, leak_check
    raw = sorted((ROOT/'raw').glob('*.csv'))
    try:
        if not raw:
            raise ValueError('Für den abschließenden Namens-Leak-Check müssen die CSV-Quelldateien in raw/ liegen.')
        leak_check(ROOT,names_from(read_raw(raw)))
        summary['checks']['leak_check'] = 'passed'
        target.write_text(json.dumps(summary, ensure_ascii=False,allow_nan=False,separators=(',',':')),encoding='utf-8')
        leak_check(ROOT,names_from(read_raw(raw)))
    except Exception:
        target.unlink(missing_ok=True)
        raise
    p = summary['periods']['all']
    print('Methodik: FIFO je ISIN; Beträge maßgeblich; Gebühren anteilig; separate signierte Steuerbuchungen.')
    print(json.dumps({'core':p['core'],'costs':p['costs'],'balance':p['capital'],'top':{k:v[:1] for k,v in p['top'].items()},'checks':summary['checks']},ensure_ascii=False,indent=2))

if __name__ == '__main__':
    main()
