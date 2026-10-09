# Prüfstatus

- Lokale FIFO-, Gebühren-, Zeitzonen-, Bewertungs- und Leak-Tests: bestanden (6 Tests).
- Gesamtergebnis und Monats-/Jahresbilanzen: auf Cent-Niveau konsistent; keine unzuordenbaren Verkäufe.
- Öffentlicher Payload-Check und Rohdaten-Namensabgleich werden vor dem Upload erneut ausgeführt.
- JavaScript-Syntaxprüfung: wird vor dem Upload ausgeführt.
- Browserprüfung bei 360×640, 390×844, 768×1024 und 1440×900: im GitHub-Workflow vorbereitet; noch kein bestätigter erfolgreicher Lauf.
- Lighthouse ≥ 90: Ziel, bisher nicht gemessen.

Der lokale Testserver ist vom verfügbaren Cloud-Browser aus nicht erreichbar. Der Testworkflow enthält deshalb reproduzierbare Browserprüfungen und speichert die tatsächlichen Berichte als Actions-Artefakt. Diese Datei wird aktualisiert, sobald ein Lauf auswertbar ist.
