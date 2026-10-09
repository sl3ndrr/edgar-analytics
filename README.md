# Edgars Depot

Eine private, sachliche Rückschau auf Handelsaktivität. Die statische Website zeigt ausschließlich anonymisierte Auswertungen. Sie benötigt keinen Build, keine externen Laufzeitdienste und kein Tracking. Alle Diagrammdateien liegen im Repository; uPlot 1.6.32 wird unter seiner MIT-Lizenz mitgeliefert.

## Start in fünf Schritten

1. UTF-8-Exportdateien in `raw/` ablegen. Python 3.10 oder neuer verwenden; einmalig `python -m pip install -r scripts/requirements.txt` ausführen. Die Rohdaten niemals committen.
2. `python scripts/anonymize.py` ausführen. Mehrere Dateien werden zusammengeführt, nach Transaktions-ID dedupliziert und in Berliner Zeit sortiert. Widersprüchliche Duplikate führen zum Abbruch. Die private, allowlist-basierte Zwischendatei liegt in `.private/`.
3. `python scripts/analyze.py` ausführen. Das erstellt `data/summary.json` und prüft anschließend Namen und Leak-Muster. Beide Schritte benötigen die Quelldateien in `raw/`. Nach Änderungen an HTML, JS oder README abschließend `python scripts/anonymize.py --check-only` ausführen.
4. `python -m http.server 8000 --bind 127.0.0.1` im Repository starten und `http://localhost:8000` öffnen. Eine direkt geöffnete HTML-Datei kann das JSON wegen Browserbeschränkungen nicht laden. Optional `python scripts/test_analysis.py` und `python scripts/validate_public.py` ausführen.
5. Nur die geprüften öffentlichen Dateien pushen und unter **Settings → Pages → Build and deployment → Source: GitHub Actions** aktivieren. Der Workflow `pages.yml` veröffentlicht eine explizite Auswahl: HTML, Konfiguration, aggregierte Zusammenfassung, `src/` und `vendor/`. Rohdaten, private Zwischenstände, Python-Skripte und Tests werden nicht als Pages-Dateien veröffentlicht.

## Datenschutz

`scripts/anonymize.py` entfernt Gegenparteien, IBANs, Verwendungszwecke, MCC, Beschreibungen, ursprüngliche Transaktions-IDs und Kontotypen vollständig. Stattdessen entstehen laufende IDs wie `t000001`. Transfers enthalten ausschließlich anonyme ID, Datum, Richtung und Betrag. Wertpapiernamen und ISIN bleiben als öffentliche Informationen erhalten; im gelieferten Export steht die ISIN in `symbol`.

Der Leak-Check scannt JSON, HTML, JavaScript und Markdown einschließlich README nach IBAN-Mustern, E-Mail-Adressen, UUIDs und vollständigen Gegenparteinamen sowie deren Namensbestandteilen aus den Rohdaten. Der Name Edgar ist die ausdrückliche Ausnahme. Die Namensliste wird nicht gespeichert oder veröffentlicht. Ein Treffer beendet das Skript; die erzeugte Ergebnisdatei wird bei Fehlern entfernt. `.gitignore` schützt `raw/`, alle CSV-Dateien und `.private/`. Der öffentliche CI-Check kann mangels Rohdaten nur generische Muster, verbotene Datenfelder und den dokumentierten lokalen Check prüfen; er ersetzt den lokalen Namensabgleich nicht.

Die Website zeigt standardmäßig nur den Vornamen Edgar. `config.json` steuert `display_name`, `show_age` (false), einen optionalen expliziten Alterswert (null) und `spread_default_percent` (0). Änderungen an der öffentlichen Konfiguration ebenfalls auf Datenschutz prüfen. Es gibt keine automatische Veröffentlichung der Rohdaten und keinen Browser-Dateiupload.

## Methodik

- FIFO läuft je ISIN chronologisch über alle Käufe und Verkäufe, auch über Monats- und Jahresgrenzen hinweg. Verkaufsmengen werden absolut verarbeitet. Teilverkäufe teilen Lots und Kaufgebühren anteilig. Die gebuchten Beträge bestimmen Einstand und Erlös; `price` dient der Plausibilitätsprüfung.
- **Brutto:** zugeordneter Verkaufserlös minus Kaufbetrag. **Netto:** Brutto minus zugeordnete Kauf- und Verkaufsgebühren. **Unter dem Strich:** Netto plus Dividenden, Zinsen und signierte Steuerbuchungen einschließlich `TAX_OPTIMIZATION`. Positive Steuerwerte sind Erstattungen; negative Werte sind Belastungen. Kaufsteuern werden im Buchungsmonat als Steuern berücksichtigt, nicht nochmals im FIFO-Einstand.
- Ein Closed Trade ist eine Verkaufszeile mit zuordenbaren Lots. Ganze Stücke und Bruchstücke sind im Export häufig getrennte Zeilen. Ohne verlässliche Order-ID zählen wir Exportzeilen als Orders und führen sie nicht heuristisch zusammen. Netto-% bezieht sich auf den zugeordneten Einstand inklusive Kaufgebühren. Instrument-% ist ein Quotient über alle zugeordneten Einstandskosten und keine Depotrendite.
- Bei fehlenden Kauf-Lots werden unzuordenbare Mengen, Erlöse und anteilige Verkaufsgebühren getrennt ausgewiesen. Nur der bekannte Anteil geht in das realisierte Ergebnis ein. Teilweise zugeordnete Verkäufe sind markiert; ein vollständiger Depotgewinn ist bei unbekanntem Anfangsbestand nicht rekonstruierbar.
- Monats- und Jahresergebnisse werden nach Berliner Verkaufs- beziehungsweise Cash-Buchungstag ausgewiesen. Offene Positionen und Cash sind Bestände am jeweiligen Periodenende. Die Bilanz für Teilperioden berücksichtigt Anfangsbestände und Anfangs-Cash. Für die Gesamtrechnung wird der Exportanfang mit null angesetzt; Erlöse ohne Kauf-Lot erklären eine mögliche Bilanzdifferenz.
- Kaufgebühren bleiben bei offenen Lots im Einstand. Daher können **insgesamt gezahlte Gebühren** und **bereits realisierte Gebühren** voneinander abweichen. Cash ist die Summe aus `amount + fee + tax`; die Bilanz verwendet offenen Einstand einschließlich Kaufgebühren. Die Algebra ist ein Konsistenzcheck des Exports, keine unabhängige Bestätigung durch einen Kontoauszug.
- Daytrade: alle zugeordneten Kauf-Lots liegen am Berliner Verkaufstag. Haltedauer ist je Verkaufszeile nach Stückzahl gewichtet. Die Verteilung umfasst `<1 h`, `1 h–<1 Tag`, `1–7 Tage` und `>7 Tage`. Serien basieren auf der Reihenfolge zugeordneter Verkaufszeilen; Ergebnisse innerhalb ±0,005 € zählen als nahe null und unterbrechen Serien. Handelstage sind Tage mit mindestens einem Kauf oder Verkauf; profitable Tage beziehen sich auf das realisierte Netto-Handelsergebnis.
- Die Equity-Kurve enthält kumuliertes realisiertes Handelsergebnis nach Gebühren und beginnt im gewählten Zeitraum bei null. Sie ist kein Depotwert. Maximaler Drawdown ist der größte Euro-Rückgang vom bisherigen Hoch zum nachfolgenden Tief; kein Prozentwert. Einzahlungen, Dividenden, Zinsen und Steuern sind nicht in dieser Kurve enthalten.
- Rendite auf Netto-Einzahlung und Umschlag sind einfache Quotienten. Bei Netto-Einzahlung ≤ 0 sind sie nicht definiert. Sie berücksichtigen keine zeitliche Kapitalbindung.

## Befunde zum gelieferten Export

6.889 Zeilen, 6.775 Handelszeilen, 170 Instrumente, 16.04.2025 bis 02.10.2026. Keine doppelten Transaktions-IDs. 2.727 Handelszeilen haben leere Gebühren; diese werden als null behandelt. Alle nicht leeren Handelsgebühren betragen −1,00 €. Verkaufsmengen sind negativ gespeichert.

Bei sechs Commerzbank-Zeilen ist der Kurs um Faktor 1.000 skaliert, eine Tesla-Kleinbetragszeile weicht um mehr als 0,011 € von Stückzahl × Kurs ab. Für die Ergebnisrechnung sind deshalb die gebuchten Beträge maßgeblich. Eine Datumsangabe weicht vom Berliner Kalendertag ab und wird korrigiert. Gemischte ISO-Zeitstempel werden mit pandas `format="ISO8601"`, UTC und anschließender Umrechnung nach Europe/Berlin verarbeitet.

Die einzige besteuerte Verkaufszeile entspricht auf Cent-Niveau Stückzahl × Kurs; `amount` ist dort nicht steuerbereinigt. `TAX_OPTIMIZATION` enthält sowohl positive Erstattungen als auch negative Nachbelastungen und hat jeweils `amount=0`. Die Gesamtsumme `amount + fee + tax` ergibt 0,00 € Schluss-Cash. Das stützt die separate Verbuchung, ersetzt aber keinen unabhängigen Kontostand.

Alle Verkäufe sind durch Kauf-Lots gedeckt. Die Gesamtrechnung ist auf Cent-Niveau konsistent: berechnetes Cash 0,00 € + offener Einstand 2.001,00 € − Netto-Einzahlungen 28.547,68 € = −26.546,68 €. Die offene Alibaba-Position hat 2.000,00 € Kaufbetrag und 1,00 € Kaufgebühr. Diese Gebühr ist noch nicht realisiert: 4.048,00 € insgesamt gezahlte gegenüber 4.047,00 € realisierten Gebühren. Die offene Position ist ohne Kursdaten nicht bewertet.

## Kurse und Grenzen

Optional lokal `data/prices.csv` mit den Spalten `isin,price` und positiven EUR-Kursen ablegen und die Analyse erneut ausführen. Dann kommen Marktwert und unrealisierter Gewinn nach Kaufgebühren hinzu. Fehlende Kurse bleiben als nicht bewertet markiert. Die Datei wird durch `.gitignore` ausgeschlossen. Ein einheitlicher bereitgestellter Kursstand ist keine historische Kursreihe; Bewertungen historischer Monatsbestände damit sind nur ein Szenario. Ohne diese Datei gibt es keinen aktuellen Gesamtdepotwert und keine Aussage über den endgültigen wirtschaftlichen Verlust offener Positionen.

Sichtbare Gebühren sind gezahlte Kosten, keine nachgewiesenen Gewinne von Trade Republic. Guthabenzinsen sind im Export sichtbar. Spreads, Rückvergütungen, Fremdkosten und weitere Anbieteraufwendungen sind nicht sichtbar. Der Regler 0–0,3 % zeigt ausschließlich einen angenommenen Spreadbetrag auf das Kauf- und Verkaufsvolumen. Dieser Betrag wird nicht zusätzlich vom historischen Ergebnis abgezogen, weil tatsächliche Ausführungspreise bereits gebucht sind.

## Module und Bedienung

Alle 13 Module in `src/modules/` exportieren `{ id, title, render(data, period) }`. `render` liefert einen DOM-Knoten. `data` ist die gesamte Zusammenfassung; `period` ist `all`, ein Jahr (`2026`) oder ein Monat (`2026-03`). `config/features.json` setzt die Standardauswahl. „Ansicht anpassen“ bietet einzelne Schalter sowie Alles, Nur Kernzahlen und Nur Trade Republic. Auswahl und Farbmodus werden mit Fehler-Fallback im Browser gespeichert.

Der URL-Hash überschreibt die gespeicherte Ansicht: `#modules=kernzahlen,kosten&period=2026-03`. Die Kurzformen `core` und `fees` werden ebenfalls akzeptiert. Jahr und Monat können per Auswahl, Pfeilen oder horizontaler Touch-Geste auf dem freien Bereich der Zeitraumleiste geändert werden. Monatskarten und Tabellenzeilen setzen den globalen Filter. Dunkler Modus folgt zunächst dem System und kann manuell gewechselt werden.

Count-up, Diagramm-Reveal, Balken und Heatmap verwenden ausschließlich transform/opacity für Animationen. Bei `prefers-reduced-motion: reduce` werden sie deaktiviert. Diagramme reagieren per ResizeObserver auf Größenänderungen, unterstützen Tap-Informationen und Pfeiltasten und besitzen Tabellenalternativen. Tabellen scrollen nur in ihren eigenen Containern; Monatsdaten werden auf Mobilgeräten als Karten dargestellt.

## Prüfung und Reproduktion

Die lokalen Python-Tests prüfen FIFO-Teil-Lots, anteilige Gebühren, Verkäufe ohne Lot, Berliner Daytrades, leere Gebühren, Kursbewertung, Leak-Abbrüche, Summen über Monate und die Bilanz in allen Perioden. `python scripts/test_analysis.py` und `python scripts/validate_public.py` laufen ohne Rohdaten auf dem gelieferten öffentlichen Ergebnis.

Der optionale Workflow `validate.yml` installiert Playwright, axe und Lighthouse ausschließlich für QA. Kein Website-Build ist nötig. Er prüft **360×640, 390×844, 768×1024 und 1440×900**, helle/dunkle Ansicht, Overflow, alle Modulschalter, Presets, Filter, Hash, blockiertes localStorage, Ladefehler, externe Requests und reduzierte Bewegung. Screenshots, axe-Reports und Lighthouse-Berichte werden als Actions-Artefakt gespeichert. Lighthouse-Ziel: Performance, Accessibility und Best Practices jeweils ≥ 90. Der tatsächliche Status steht in [docs/verification.md](docs/verification.md); ein vorbereiteter Test ist kein bestandener Test.

Das JSON-Schema ist in [docs/schema.md](docs/schema.md) beschrieben. Alle Ergebnissätze werden in Python aus festen Vorlagen erzeugt. Keine freie Textgenerierung und keine erfundenen Kennzahlen.

Private Auswertung. Keine Anlageberatung. Alle persönlichen Daten entfernt.
