# Prüfstatus

- Lokale FIFO-, Gebühren-, Zeitzonen-, Bewertungs- und Leak-Tests: bestanden (6 Tests).
- Optionale prices.csv: vollständige Skriptverarbeitung getestet; realisierte Ergebnisse bleiben unverändert, zusätzliche Kursbewertung ist getrennt.
- Gesamtergebnis und Monats-/Jahresbilanzen: auf Cent-Niveau konsistent; keine unzuordenbaren Verkäufe.
- Öffentlicher Payload-Check, Rohdaten-Namensabgleich und JavaScript-Syntaxprüfung: bestanden.
- GitHub-Workflow: Python-Tests und öffentlicher Payload-Check ebenfalls bestanden.
- Browserprüfung bei 360×640, 390×844, 768×1024 und 1440×900: Testlauf gestartet; noch kein bestätigter erfolgreicher Lauf.
- Lighthouse ≥ 90: Ziel, bisher nicht gemessen.
- Pages-Veröffentlichung: noch nicht aktiviert. Der Pages-Workflow scheitert bei configure-pages mit „Not Found“. Unter Settings → Pages muss GitHub Actions als Source aktiviert werden; anschließend den Pages-Workflow erneut ausführen.

Der lokale Testserver und die GitHub-Einstellungsseite sind vom verfügbaren Cloud-Browser aus nicht erreichbar. Der Testworkflow enthält reproduzierbare Browserprüfungen und speichert die tatsächlichen Berichte als Actions-Artefakt. Ein gestarteter Test ist kein bestandener Test.
