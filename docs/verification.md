# Prüfstatus

Der Anwendungscode wurde im GitHub-Workflow „Analysis and browser checks“ erfolgreich geprüft: https://github.com/sl3ndrr/edgar-analytics/actions/runs/37957052508

Getesteter Code-Commit: `ed4b20fb6d8be5526c8acaa6f8498428cfa87c4d`. Danach wurden ausschließlich dieser Prüfbericht und die README-Prüfzusammenfassung ergänzt.

## Ergebnisse

| Ansicht | Seitenüberlauf | axe hell | axe dunkel | Funktionen |
|---|---|---|---|---|
| 360 × 640 | keiner | 0 Verstöße | 0 Verstöße | bestanden |
| 390 × 844 | keiner | 0 Verstöße | 0 Verstöße | bestanden |
| 768 × 1024 | keiner | 0 Verstöße | 0 Verstöße | bestanden |
| 1440 × 900 | keiner | 0 Verstöße | 0 Verstöße | bestanden |

Lighthouse (mobil, Standard-Drosselung, lokaler Server im GitHub Runner): **Performance 99 / Accessibility 100 / Best Practices 100**. Dies ist eine Messung dieses Laufs; Hosting, Gerät und Netzwerk können Werte verändern.

Getestet wurden alle 13 einzelnen Modulschalter, alle Presets, Monats-/Jahresfilter, Periodenpfeile, Hash-Kurzformen, gespeicherte Auswahl, blockiertes localStorage, Ladefehler, Spread-Regler, keine externen HTTP-Requests, helle/dunkle Darstellung und reduzierte Bewegung. Zusätzlich wurde eine Ansicht mit aktivierten Animationen aufgenommen. Screenshots aller Größen und axe-/Lighthouse-Berichte liegen im Actions-Artefakt „browser-and-lighthouse-results“. Die Layoutprüfung war automatisiert; eine manuelle Sichtprüfung der Screenshots konnte in dieser Umgebung nicht abgeschlossen werden.

Lokale und GitHub-seitige Python-Tests: bestanden (6 Tests). Die optionale prices.csv wurde zusätzlich durch die gesamte Skriptverarbeitung getestet; sie verändert keine realisierten Ergebnisse. Unabhängiger Cash-plus-Einstands-Abgleich für alle 170 Instrumente: bestanden. Gesamtergebnis und alle Monats-/Jahresbilanzen stimmen auf Cent-Niveau; keine unzuordenbaren Verkäufe. Öffentlicher Payload-Check, Rohdaten-Namensabgleich und JavaScript-Syntaxprüfung sind bestanden.

## Veröffentlichung

Das vollständige Repo liegt auf GitHub. **GitHub Pages ist noch nicht aktiviert.** Der Pages-Workflow scheitert bei configure-pages mit „Not Found“. Unter Settings → Pages → Build and deployment muss **GitHub Actions** als Source aktiviert werden. Anschließend den Workflow „GitHub Pages“ über Run workflow erneut ausführen.

Die GitHub-Einstellungsseite und der lokale Testserver sind vom verfügbaren Cloud-Browser aus nicht erreichbar. Die verbundene GitHub-App stellt keine Pages-Verwaltungsaktion bereit. Deshalb ist diese einmalige Einstellung noch erforderlich; es wurde keine erfolgreiche Veröffentlichung behauptet.
