# summary.json – Schema v1

UTF-8 JSON. Geldwerte in EUR, Prozente als 0–100-Werte, Haltedauern in Stunden, Stückzahlen und finanzielle Quotienten als Zahlen. Fehlende oder mathematisch nicht definierte Werte sind `null`. Zahlen werden in Python auf acht Nachkommastellen serialisiert; die UI zeigt Geld in Cent. Alle Datumswerte sind ISO-Kalendertage; datetime enthält den Offset für Europe/Berlin. Keine Original-Transaktions-IDs.

## Struktur

`periods` enthält `all`, jeden Exportmonat (`YYYY-MM`) und jedes Exportjahr (`YYYY`). Alle Perioden besitzen dieselbe Struktur. Monats-/Jahreskennzahlen sind auf Verkaufs- und Cash-Buchungsdatum bezogen. Bestände gehören zum Periodenende. `months` und `years` sind chronologisch sortierte Schlüsselarrays.

## Felder

| JSON-Pfad | Typ |
|---|---|
| `schema_version` | Zahl |
| `metadata.prices_provided` | Boolean |
| `metadata.timezone` | Zeichenfolge |
| `metadata.currency` | Zeichenfolge |
| `metadata.row_is_order` | Boolean |
| `metadata.methodology` | Zeichenfolge |
| `metadata.limits` | Array, leer möglich |
| `metadata.limits[]` | Zeichenfolge |
| `checks.input_rows` | Zahl |
| `checks.rows` | Zahl |
| `checks.duplicates_removed` | Zahl |
| `checks.rows_by_type.TRANSFER` | Zahl |
| `checks.rows_by_type.BUY` | Zahl |
| `checks.rows_by_type.DIVIDEND` | Zahl |
| `checks.rows_by_type.TAX_OPTIMIZATION` | Zahl |
| `checks.rows_by_type.SELL` | Zahl |
| `checks.rows_by_type.INTEREST_PAYMENT` | Zahl |
| `checks.date_mismatches_corrected` | Zahl |
| `checks.missing_by_column.datetime` | Zahl |
| `checks.missing_by_column.date` | Zahl |
| `checks.missing_by_column.category` | Zahl |
| `checks.missing_by_column.type` | Zahl |
| `checks.missing_by_column.asset_class` | Zahl |
| `checks.missing_by_column.name` | Zahl |
| `checks.missing_by_column.symbol` | Zahl |
| `checks.missing_by_column.shares` | Zahl |
| `checks.missing_by_column.price` | Zahl |
| `checks.missing_by_column.amount` | Zahl |
| `checks.missing_by_column.fee` | Zahl |
| `checks.missing_by_column.tax` | Zahl |
| `checks.missing_by_column.currency` | Zahl |
| `checks.timezone` | Zeichenfolge |
| `checks.currency` | Zeichenfolge |
| `checks.missing_fee_trades` | Zahl |
| `checks.missing_fee_percent` | Zahl |
| `checks.unmatched_sales` | Zahl |
| `checks.unmatched_volume` | Zahl |
| `checks.unmatched_details` | Array, leer möglich |
| `checks.price_mismatches` | Zahl |
| `checks.price_mismatch_ids` | Array, leer möglich |
| `checks.price_mismatch_ids[]` | Zeichenfolge |
| `checks.cash_ledger_delta` | Zahl |
| `checks.cash_balance_verified` | Boolean |
| `checks.start` | Zeichenfolge |
| `checks.end` | Zeichenfolge |
| `checks.raw_rows_by_type.BUY` | Zahl |
| `checks.raw_rows_by_type.SELL` | Zahl |
| `checks.raw_rows_by_type.TRANSFER_INBOUND` | Zahl |
| `checks.raw_rows_by_type.TRANSFER_INSTANT_OUTBOUND` | Zahl |
| `checks.raw_rows_by_type.INTEREST_PAYMENT` | Zahl |
| `checks.raw_rows_by_type.TRANSFER_OUTBOUND` | Zahl |
| `checks.raw_rows_by_type.DIVIDEND` | Zahl |
| `checks.raw_rows_by_type.TRANSFER_INSTANT_INBOUND` | Zahl |
| `checks.raw_rows_by_type.TAX_OPTIMIZATION` | Zahl |
| `checks.cash_balance` | Zahl |
| `checks.amount_matches_quantity_price_rows` | Zahl |
| `checks.sell_with_tax_count` | Zahl |
| `checks.tax_evidence` | Zeichenfolge |
| `checks.leak_check` | Zeichenfolge |
| `months` | Array, leer möglich |
| `months[]` | Zeichenfolge |
| `years` | Array, leer möglich |
| `years[]` | Zeichenfolge |
| `periods.<period>.id` | Zeichenfolge |
| `periods.<period>.start` | Zeichenfolge |
| `periods.<period>.end` | Zeichenfolge |
| `periods.<period>.core.buy_volume` | Zahl |
| `periods.<period>.core.sell_volume` | Zahl |
| `periods.<period>.core.total_volume` | Zahl |
| `periods.<period>.core.buy_orders` | Zahl |
| `periods.<period>.core.sell_orders` | Zahl |
| `periods.<period>.core.orders` | Zahl |
| `periods.<period>.core.gross` | Zahl |
| `periods.<period>.core.net` | Zahl |
| `periods.<period>.core.result` | Zahl |
| `periods.<period>.core.dividends` | Zahl |
| `periods.<period>.core.interest` | Zahl |
| `periods.<period>.core.tax_signed` | Zahl |
| `periods.<period>.core.taxes_net` | Zahl |
| `periods.<period>.core.tax_optimization_signed` | Zahl |
| `periods.<period>.costs.fees` | Zahl |
| `periods.<period>.costs.fees_per_order` | Zahl |
| `periods.<period>.costs.basis_points` | Zahl |
| `periods.<period>.costs.realized_fees` | Zahl |
| `periods.<period>.costs.fees_share_gross_percent` | null / optionale Zahl oder Zeichenfolge |
| `periods.<period>.costs.fee_caused_losses` | Zahl |
| `periods.<period>.quality.closed_trades` | Zahl |
| `periods.<period>.quality.wins` | Zahl |
| `periods.<period>.quality.losses` | Zahl |
| `periods.<period>.quality.breakeven` | Zahl |
| `periods.<period>.quality.hit_rate` | Zahl |
| `periods.<period>.quality.average_win` | Zahl |
| `periods.<period>.quality.average_loss` | Zahl |
| `periods.<period>.quality.win_loss_ratio` | Zahl |
| `periods.<period>.quality.profit_factor` | Zahl |
| `periods.<period>.quality.expected_value` | Zahl |
| `periods.<period>.quality.net_per_trading_day` | Zahl |
| `periods.<period>.quality.profitable_days_percent` | Zahl |
| `periods.<period>.quality.winning_streak` | Zahl |
| `periods.<period>.quality.losing_streak` | Zahl |
| `periods.<period>.holding.daytrades` | Zahl |
| `periods.<period>.holding.daytrade_percent` | Zahl |
| `periods.<period>.holding.median_hours` | Zahl |
| `periods.<period>.holding.mean_hours` | Zahl |
| `periods.<period>.holding.buckets.<1 h` | Zahl |
| `periods.<period>.holding.buckets.1 h–<1 Tag` | Zahl |
| `periods.<period>.holding.buckets.1–7 Tage` | Zahl |
| `periods.<period>.holding.buckets.>7 Tage` | Zahl |
| `periods.<period>.activity.heatmap` | Array, leer möglich |
| `periods.<period>.activity.heatmap[]` | Array, leer möglich |
| `periods.<period>.activity.heatmap[][]` | Zahl |
| `periods.<period>.activity.daily` | Array, leer möglich |
| `periods.<period>.activity.daily[].date` | Zeichenfolge |
| `periods.<period>.activity.daily[].orders` | Zahl |
| `periods.<period>.activity.trading_days` | Zahl |
| `periods.<period>.activity.active_days` | Array, leer möglich |
| `periods.<period>.activity.active_days[].date` | Zeichenfolge |
| `periods.<period>.activity.active_days[].orders` | Zahl |
| `periods.<period>.activity.longest_pause.full_days` | Zahl |
| `periods.<period>.activity.longest_pause.from` | Zeichenfolge |
| `periods.<period>.activity.longest_pause.to` | Zeichenfolge |
| `periods.<period>.equity.daily` | Array, leer möglich |
| `periods.<period>.equity.daily[].date` | Zeichenfolge |
| `periods.<period>.equity.daily[].net_cumulative` | Zahl |
| `periods.<period>.equity.daily[].result_daily` | Zahl |
| `periods.<period>.equity.daily[].net_daily` | Zahl |
| `periods.<period>.equity.daily[].orders` | Zahl |
| `periods.<period>.equity.max_drawdown` | Zahl |
| `periods.<period>.equity.drawdown_start` | Zeichenfolge |
| `periods.<period>.equity.drawdown_end` | Zeichenfolge |
| `periods.<period>.capital.deposited` | Zahl |
| `periods.<period>.capital.withdrawn` | Zahl |
| `periods.<period>.capital.net_deposited` | Zahl |
| `periods.<period>.capital.return_on_net_deposit_percent` | Zahl |
| `periods.<period>.capital.turnover` | Zahl |
| `periods.<period>.capital.cash_start` | Zahl |
| `periods.<period>.capital.cash_end` | Zahl |
| `periods.<period>.capital.open_cost_start` | Zahl |
| `periods.<period>.capital.open_cost_end` | Zahl |
| `periods.<period>.capital.cumulative_net_deposited` | Zahl |
| `periods.<period>.capital.balance_lhs` | Zahl |
| `periods.<period>.capital.balance_difference` | Zahl |
| `periods.<period>.capital.unmatched_effect` | Zahl |
| `periods.<period>.capital.unexplained_difference` | Zahl |
| `periods.<period>.capital.positions` | Array, leer möglich |
| `periods.<period>.capital.positions[].isin` | Zeichenfolge |
| `periods.<period>.capital.positions[].name` | Zeichenfolge |
| `periods.<period>.capital.positions[].asset_class` | Zeichenfolge |
| `periods.<period>.capital.positions[].shares` | Zahl |
| `periods.<period>.capital.positions[].cost` | Zahl |
| `periods.<period>.capital.positions[].buy_fees` | Zahl |
| `periods.<period>.capital.positions[].cost_including_fees` | Zahl |
| `periods.<period>.capital.positions[].market_value` | null / optionale Zahl oder Zeichenfolge |
| `periods.<period>.capital.positions[].unrealized` | null / optionale Zahl oder Zeichenfolge |
| `periods.<period>.capital.valuation` | Zeichenfolge |
| `periods.<period>.capital.unrealized` | null / optionale Zahl oder Zeichenfolge |
| `periods.<period>.titles` | Array, leer möglich |
| `periods.<period>.titles[].isin` | Zeichenfolge |
| `periods.<period>.titles[].name` | Zeichenfolge |
| `periods.<period>.titles[].asset_class` | Zeichenfolge |
| `periods.<period>.titles[].volume` | Zahl |
| `periods.<period>.titles[].orders` | Zahl |
| `periods.<period>.titles[].net` | Zahl |
| `periods.<period>.titles[].gross` | Zahl |
| `periods.<period>.titles[].fees` | Zahl |
| `periods.<period>.titles[].cost` | Zahl |
| `periods.<period>.titles[].closed` | Zahl |
| `periods.<period>.titles[].net_percent` | Zahl |
| `periods.<period>.classes.STOCK.volume` | Zahl |
| `periods.<period>.classes.STOCK.orders` | Zahl |
| `periods.<period>.classes.STOCK.net` | Zahl |
| `periods.<period>.classes.CRYPTO.volume` | Zahl |
| `periods.<period>.classes.CRYPTO.orders` | Zahl |
| `periods.<period>.classes.CRYPTO.net` | Zahl |
| `periods.<period>.classes.FUND.volume` | Zahl |
| `periods.<period>.classes.FUND.orders` | Zahl |
| `periods.<period>.classes.FUND.net` | Zahl |
| `periods.<period>.concentration_top10_percent` | Zahl |
| `periods.<period>.top.wins` | Array, leer möglich |
| `periods.<period>.top.wins[].id` | Zeichenfolge |
| `periods.<period>.top.wins[].name` | Zeichenfolge |
| `periods.<period>.top.wins[].isin` | Zeichenfolge |
| `periods.<period>.top.wins[].date` | Zeichenfolge |
| `periods.<period>.top.wins[].shares` | Zahl |
| `periods.<period>.top.wins[].proceeds` | Zahl |
| `periods.<period>.top.wins[].cost` | Zahl |
| `periods.<period>.top.wins[].gross` | Zahl |
| `periods.<period>.top.wins[].buy_fees` | Zahl |
| `periods.<period>.top.wins[].sell_fees` | Zahl |
| `periods.<period>.top.wins[].fees` | Zahl |
| `periods.<period>.top.wins[].net` | Zahl |
| `periods.<period>.top.wins[].net_percent` | Zahl |
| `periods.<period>.top.wins[].hours` | Zahl |
| `periods.<period>.top.wins[].daytrade` | Boolean |
| `periods.<period>.top.wins[].partial` | Boolean |
| `periods.<period>.top.losses` | Array, leer möglich |
| `periods.<period>.top.losses[].id` | Zeichenfolge |
| `periods.<period>.top.losses[].name` | Zeichenfolge |
| `periods.<period>.top.losses[].isin` | Zeichenfolge |
| `periods.<period>.top.losses[].date` | Zeichenfolge |
| `periods.<period>.top.losses[].shares` | Zahl |
| `periods.<period>.top.losses[].proceeds` | Zahl |
| `periods.<period>.top.losses[].cost` | Zahl |
| `periods.<period>.top.losses[].gross` | Zahl |
| `periods.<period>.top.losses[].buy_fees` | Zahl |
| `periods.<period>.top.losses[].sell_fees` | Zahl |
| `periods.<period>.top.losses[].fees` | Zahl |
| `periods.<period>.top.losses[].net` | Zahl |
| `periods.<period>.top.losses[].net_percent` | Zahl |
| `periods.<period>.top.losses[].hours` | Zahl |
| `periods.<period>.top.losses[].daytrade` | Boolean |
| `periods.<period>.top.losses[].partial` | Boolean |
| `periods.<period>.top.titles_wins` | Array, leer möglich |
| `periods.<period>.top.titles_wins[].isin` | Zeichenfolge |
| `periods.<period>.top.titles_wins[].name` | Zeichenfolge |
| `periods.<period>.top.titles_wins[].asset_class` | Zeichenfolge |
| `periods.<period>.top.titles_wins[].volume` | Zahl |
| `periods.<period>.top.titles_wins[].orders` | Zahl |
| `periods.<period>.top.titles_wins[].net` | Zahl |
| `periods.<period>.top.titles_wins[].gross` | Zahl |
| `periods.<period>.top.titles_wins[].fees` | Zahl |
| `periods.<period>.top.titles_wins[].cost` | Zahl |
| `periods.<period>.top.titles_wins[].closed` | Zahl |
| `periods.<period>.top.titles_wins[].net_percent` | Zahl |
| `periods.<period>.top.titles_losses` | Array, leer möglich |
| `periods.<period>.top.titles_losses[].isin` | Zeichenfolge |
| `periods.<period>.top.titles_losses[].name` | Zeichenfolge |
| `periods.<period>.top.titles_losses[].asset_class` | Zeichenfolge |
| `periods.<period>.top.titles_losses[].volume` | Zahl |
| `periods.<period>.top.titles_losses[].orders` | Zahl |
| `periods.<period>.top.titles_losses[].net` | Zahl |
| `periods.<period>.top.titles_losses[].gross` | Zahl |
| `periods.<period>.top.titles_losses[].fees` | Zahl |
| `periods.<period>.top.titles_losses[].cost` | Zahl |
| `periods.<period>.top.titles_losses[].closed` | Zahl |
| `periods.<period>.top.titles_losses[].net_percent` | Zahl |
| `periods.<period>.top.wins_percent` | Array, leer möglich |
| `periods.<period>.top.wins_percent[].id` | Zeichenfolge |
| `periods.<period>.top.wins_percent[].name` | Zeichenfolge |
| `periods.<period>.top.wins_percent[].isin` | Zeichenfolge |
| `periods.<period>.top.wins_percent[].date` | Zeichenfolge |
| `periods.<period>.top.wins_percent[].shares` | Zahl |
| `periods.<period>.top.wins_percent[].proceeds` | Zahl |
| `periods.<period>.top.wins_percent[].cost` | Zahl |
| `periods.<period>.top.wins_percent[].gross` | Zahl |
| `periods.<period>.top.wins_percent[].buy_fees` | Zahl |
| `periods.<period>.top.wins_percent[].sell_fees` | Zahl |
| `periods.<period>.top.wins_percent[].fees` | Zahl |
| `periods.<period>.top.wins_percent[].net` | Zahl |
| `periods.<period>.top.wins_percent[].net_percent` | Zahl |
| `periods.<period>.top.wins_percent[].hours` | Zahl |
| `periods.<period>.top.wins_percent[].daytrade` | Boolean |
| `periods.<period>.top.wins_percent[].partial` | Boolean |
| `periods.<period>.top.losses_percent` | Array, leer möglich |
| `periods.<period>.top.losses_percent[].id` | Zeichenfolge |
| `periods.<period>.top.losses_percent[].name` | Zeichenfolge |
| `periods.<period>.top.losses_percent[].isin` | Zeichenfolge |
| `periods.<period>.top.losses_percent[].date` | Zeichenfolge |
| `periods.<period>.top.losses_percent[].shares` | Zahl |
| `periods.<period>.top.losses_percent[].proceeds` | Zahl |
| `periods.<period>.top.losses_percent[].cost` | Zahl |
| `periods.<period>.top.losses_percent[].gross` | Zahl |
| `periods.<period>.top.losses_percent[].buy_fees` | Zahl |
| `periods.<period>.top.losses_percent[].sell_fees` | Zahl |
| `periods.<period>.top.losses_percent[].fees` | Zahl |
| `periods.<period>.top.losses_percent[].net` | Zahl |
| `periods.<period>.top.losses_percent[].net_percent` | Zahl |
| `periods.<period>.top.losses_percent[].hours` | Zahl |
| `periods.<period>.top.losses_percent[].daytrade` | Boolean |
| `periods.<period>.top.losses_percent[].partial` | Boolean |
| `periods.<period>.top.titles_wins_percent` | Array, leer möglich |
| `periods.<period>.top.titles_wins_percent[].isin` | Zeichenfolge |
| `periods.<period>.top.titles_wins_percent[].name` | Zeichenfolge |
| `periods.<period>.top.titles_wins_percent[].asset_class` | Zeichenfolge |
| `periods.<period>.top.titles_wins_percent[].volume` | Zahl |
| `periods.<period>.top.titles_wins_percent[].orders` | Zahl |
| `periods.<period>.top.titles_wins_percent[].net` | Zahl |
| `periods.<period>.top.titles_wins_percent[].gross` | Zahl |
| `periods.<period>.top.titles_wins_percent[].fees` | Zahl |
| `periods.<period>.top.titles_wins_percent[].cost` | Zahl |
| `periods.<period>.top.titles_wins_percent[].closed` | Zahl |
| `periods.<period>.top.titles_wins_percent[].net_percent` | Zahl |
| `periods.<period>.top.titles_losses_percent` | Array, leer möglich |
| `periods.<period>.top.titles_losses_percent[].isin` | Zeichenfolge |
| `periods.<period>.top.titles_losses_percent[].name` | Zeichenfolge |
| `periods.<period>.top.titles_losses_percent[].asset_class` | Zeichenfolge |
| `periods.<period>.top.titles_losses_percent[].volume` | Zahl |
| `periods.<period>.top.titles_losses_percent[].orders` | Zahl |
| `periods.<period>.top.titles_losses_percent[].net` | Zahl |
| `periods.<period>.top.titles_losses_percent[].gross` | Zahl |
| `periods.<period>.top.titles_losses_percent[].fees` | Zahl |
| `periods.<period>.top.titles_losses_percent[].cost` | Zahl |
| `periods.<period>.top.titles_losses_percent[].closed` | Zahl |
| `periods.<period>.top.titles_losses_percent[].net_percent` | Zahl |
| `periods.<period>.checks.rows` | Zahl |
| `periods.<period>.checks.rows_by_type.TRANSFER` | Zahl |
| `periods.<period>.checks.rows_by_type.BUY` | Zahl |
| `periods.<period>.checks.rows_by_type.DIVIDEND` | Zahl |
| `periods.<period>.checks.rows_by_type.TAX_OPTIMIZATION` | Zahl |
| `periods.<period>.checks.rows_by_type.SELL` | Zahl |
| `periods.<period>.checks.rows_by_type.INTEREST_PAYMENT` | Zahl |
| `periods.<period>.checks.missing_fee_trades` | Zahl |
| `periods.<period>.checks.missing_fee_percent` | Zahl |
| `periods.<period>.checks.unmatched_sales` | Zahl |
| `periods.<period>.checks.unmatched_volume` | Zahl |
| `periods.<period>.checks.unmatched_details` | Array, leer möglich |
| `periods.<period>.checks.price_mismatches` | Zahl |
| `periods.<period>.checks.price_mismatch_ids` | Array, leer möglich |
| `periods.<period>.checks.price_mismatch_ids[]` | Zeichenfolge |
| `periods.<period>.checks.cash_ledger_delta` | Zahl |
| `periods.<period>.checks.cash_balance_verified` | Boolean |
| `periods.<period>.checks.start` | Zeichenfolge |
| `periods.<period>.checks.end` | Zeichenfolge |
| `periods.<period>.broker.visible_fees` | Zahl |
| `periods.<period>.broker.interest_paid` | Zahl |
| `periods.<period>.broker.fees_less_interest` | Zahl |
| `periods.<period>.broker.spread_observable` | Boolean |
| `periods.<period>.conclusions` | Array, leer möglich |
| `periods.<period>.conclusions[]` | Zeichenfolge |

## Sonderfälle

- `checks.rows_by_type` hat die normalisierten Typen (Transfers als TRANSFER); `checks.raw_rows_by_type` hält die ursprünglichen Typ-Anzahlen ohne Einzelinformationen. `missing_by_column` zählt leere Zellen nur für erlaubte Felder.
- `checks.unmatched_details[]` enthält anonyme id, name, isin, date, shares, proceeds und sell_fees. Wenn keine Fälle vorkommen, ist das Array leer. Der Erlös des nicht zuordenbaren Anteils ist ausgeschlossen; `capital.unmatched_effect` erklärt dessen Cash-Wirkung in der Bilanz.
- `activity.heatmap` ist eine 7×24-Matrix: Zeilen Montag bis Sonntag, Spalten 0 bis 23 Uhr in Berliner Zeit.
- `holding.buckets` enthält disjunkte Anzahlwerte; `daytrade_percent` bezieht sich auf Verkaufszeilen, deren gesamte bekannte Menge am selben Tag gekauft wurde.
- `top` enthält Gewinn- und Verlustlisten nach Euro sowie nach Prozent für Verkäufe und Instrumente. Trade-Gebühren teilen sich in buy_fees und sell_fees. `partial` markiert teilweise bekannte Verkaufszeilen. Instrumentlisten nutzen die gleiche aggregierte Titelstruktur.
- `capital.positions[]` enthält isin, name, asset_class, shares, cost (vor Gebühren), buy_fees, cost_including_fees, market_value und unrealized. Marktwert und unrealisierter Gewinn sind ohne passenden Nutzerkurs null. `valuation` ist not_valued, partial oder prices_provided.
- `equity.daily[]` enthält date, net_cumulative (Netto-Handel), net_daily, result_daily (inkl. Erträge und Steuern) und orders. Die kumulierte Kurve startet pro Zeitraum bei null.
- `activity.longest_pause` enthält full_days, from und to; leere Aktivität hat null-Daten.
- `titles[]` enthält jedes im Zeitraum gehandelte Instrument: isin, name, asset_class, volume, orders, net, gross, fees, cost, closed und net_percent. `classes` nutzt dynamische Anlageklassenschlüssel STOCK/CRYPTO/FUND mit volume, orders und net.
- `metadata.prices_provided` sagt nur aus, ob optionale Kurse vorhanden sind; es bestätigt weder Aktualität noch vollständige Abdeckung.
- `checks.cash_balance_verified` bleibt false: der Export liefert keinen unabhängigen Kontoauszug. `cash_ledger_delta` ist die Cash-Veränderung im jeweiligen Zeitraum.
- `conclusions[]` enthält sechs in Python erzeugte neutrale Template-Sätze. `broker.spread_observable` ist false; hypothetische Spreadbeträge werden ausschließlich als interaktives UI-Szenario berechnet.
