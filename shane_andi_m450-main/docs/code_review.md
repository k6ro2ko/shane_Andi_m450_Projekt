# Code-Review gegen das Testkonzept v1.1

| | |
|---|---|
| Geprüfter Stand | Commit `0efc97a` («Teacher Version»), Ordner `shane_andi_m450-main/` |
| Grundlage | [Testkonzept_und_Auftrag.md](Testkonzept_und_Auftrag.md), Teil B, v1.1 |
| Datum | 05.11.2026 |
| Methode | Statische Prüfung: jeder Testfall und jedes Akzeptanzkriterium wurde gegen den Quellcode gehalten. |

## 1 Befund zum geprüften Stand

Der Code im Repository ist **nicht das Smart-Parking-System**, sondern eine Countdown-Firmware:

| Datei | Inhalt |
|---|---|
| `src/main.cpp`, `lib/countdown/*` | C++/Arduino-Firmware (PlatformIO): Countdown mit zwei Tastern, Status-LEDs, serielles Befehlsprotokoll |
| `webapp/Program.cs` | leeres ASP.NET-Projekt, liefert nur «Hello World!» |
| `tools/countdown_control.py` | PC-Skript, steuert den Countdown über USB |

Nicht vorhanden sind: MicroPython-Code, ein Webserver auf dem Pico, die Kasse (Pico 1), die Schranken mit Kamera-Sim-UI (Pico 2), die M2M-Kommunikation, die Admin-Seite, das Tarifmodell und die Kennzeichenprüfung. Deshalb steht unten bei **jedem** Testfall und **jedem** Akzeptanzkriterium der Status «fehlt».

Darum wurde das System gemäss Testkonzept neu umgesetzt (Ordner `parking/`, siehe [aenderungen.md](aenderungen.md)). Die Spalte «Umsetzung» verweist auf die Stelle im neuen Code, mit der das Kriterium jetzt erfüllt wird. **Ob ein Testfall auf der Hardware besteht, zeigt erst die Testsession.**

## 2 Testfälle TC-01 bis TC-15

| TC/AK | erwartet | Status im Code (0efc97a) | Datei:Zeile (Umsetzung) | Problem → Lösung |
|---|---|---|---|---|
| TC-01 | «Einfahrt registriert: ZH-123» mit Datum/Uhrzeit; Schranke öffnet innert 2 s für 5 s; Admin: ZH-123, Status «Offen», freie Plätze 2 | fehlt | `parking/pico2_schranke/schranken_app.py:33`, `ablauf.py:14`, `pico1_kasse/kasse_app.py:104`, `parkhaus.py:24` | Keine Einfahrt vorhanden → Einfahrt über Pico 2, Meldung an Pico 1 per HTTP, Schranke öffnet *vor* der Antwort an den Browser |
| TC-02 | «Fahrzeug bereits im Parkhaus», Schranke zu, genau ein Eintrag | fehlt | `parkhaus.py:27`, `ablauf.py:3` | Duplikatprüfung serverseitig auf Pico 1 |
| TC-03 | Einfahrtszeit, Dauer (z. B. 0:02), CHF 2.00 gut lesbar, Status «Offen» | fehlt | `kasse_app.py:152`, `tarif.py:11`, `tarif.py:29`, `webutil.py:161` | Kassen-UI mit Betrag in grosser Schrift |
| TC-04 | Zahlungsart «Karte», «Gebühr bezahlen» → «Bezahlung erfolgreich – bitte innert 15 Minuten ausfahren»; Status «Bezahlt»; Admin: Zahlungszeit, Karte, CHF 2.00 | fehlt | `kasse_app.py:13`, `kasse_app.py:125`, `kasse_app.py:186`, `parkhaus.py:60` | Zahlung simuliert, Zahlungsart Pflichtfeld (auch serverseitig geprüft) |
| TC-05 | «Bitte an Kasse bezahlen», Schranke zu | fehlt | `parkhaus.py:88`, `ablauf.py:6`, `ablauf.py:38` | Entscheidungstabelle R2 |
| TC-06 | Schranke öffnet innert 2 s für 5 s, Kennzeichen gelöscht, freie Plätze 2 | fehlt | `parkhaus.py:88`, `schranken_app.py:44`, `config.py` (Pico 2) `SCHRANKE_OFFEN_S = 5` | R3; abgeschlossener Vorgang wandert in den Verlauf der Admin-Seite (Konzept präzisiert, s. Protokoll Kap. 7) |
| TC-07 | «XX-000» und bereits ausgefahrenes «ZH-123»: beide Male «Kennzeichen nicht gefunden», Schranke zu, kein Absturz | fehlt | `schranken_app.py:44` | «XX-000» ist formal ungültig (kein Kanton, führende Null). Bei der *Ausfahrt* wird deshalb bewusst «Kennzeichen nicht gefunden» gemeldet, nicht «Ungültiges Kennzeichen» |
| TC-08 | Ungültige Eingaben → «Ungültiges Kennzeichen», kein Eintrag; 60 × «A» und `<b>ZH-1</b>` abgewiesen, nicht fett, kein Absturz; JU-1, VD-999999, ag-9999 → gespeichert als JU-1, VD-999999, AG-9999 | fehlt | `common/kennzeichen.py:16`, `webutil.py:14`, `webutil.py:122`, `schranken_app.py:33` | Validierung ohne `re` (MicroPython kennt `{1,6}` nicht); alle Ausgaben über `esc()`; Anfragen > 2 KB werden mit 413 abgewiesen |
| TC-09 | Kapazität 3; bei 0 «Bestätigen» deaktiviert + «Parkhaus voll»; Tab 2 → serverseitig «Parkhaus voll»; nach Ausfahrt wieder aktiv | fehlt | `parkhaus.py:29`, `schranken_app.py:65`, `schranken_app.py:79` | Button-Sperre in der UI **und** Prüfung auf Pico 1 |
| TC-10 | 0/59/61/659/661/1439/1441 min → 2/2/4/22/24/24/26 CHF, Dauer h:mm bis 24:01 | fehlt | `tarif.py:11`, `tarif.py:29`, `kasse_app.py:269` | Tarif in Rappen (int, keine float-Rundung); «Einfahrt vor n Minuten» auf der Admin-Seite |
| TC-11 | 14 min → öffnet; 16 min → «Kulanzzeit überschritten – Nachzahlung CHF 2.00»; Nachgebühr bar bezahlen → öffnet | fehlt | `tarif.py:21`, `parkhaus.py:34`, `ablauf.py:10` | Kulanz ≤ 15 min; Nachzahlung ab Zahlungszeitpunkt je angefangene Stunde |
| TC-12 | «Kennzeichen nicht gefunden» + Option «Ticket verloren»; Pauschale CHF 24.00; «Bezahlt – Ausfahrt bis hh:mm»; Ausfahrt öffnet | fehlt | `kasse_app.py:158`, `kasse_app.py:208`, `parkhaus.py:75` | Ticket verloren nur für Kennzeichen ohne Parkvorgang |
| TC-13 | Pico 1 aus: nach ≤ 5 s «Kasse nicht erreichbar – bitte Personal rufen», Schranke zu (Aus- und Einfahrt); danach ohne Neustart von Pico 2 wieder funktionsfähig | fehlt | `pico2_schranke/m2m.py:45`, `config.py` (Pico 2) `M2M_TIMEOUT_MS = 4000`, `ablauf.py:7` | Eigener nicht-blockierender HTTP-Client mit hartem Timeout. Timeout 4 s, damit die Meldung inkl. Seitenaufbau sicher innert 5 s erscheint. Nach einem Timeout keine zweite M2M-Anfrage |
| TC-14 | Nach Neustart Pico 2 beide Schranken zu; Parkvorgang auf Pico 1 unverändert | fehlt | `pico2_schranke/main.py:5`, `schranke.py:31` | Schranken werden als erste Anweisung geschlossen, noch vor WLAN/Webserver |
| TC-15 | Schranke ≤ 2 s; Seiten ≤ 3 s bedienbar; Smartphone: Betrag ohne Zoom lesbar, kein horizontales Scrollen, Touch | fehlt | `webutil.py:175` (Viewport), `webutil.py:147` (CSS), `config.py` (Pico 2) `STATUS_TIMEOUT_MS` | Responsives CSS, Buttons ≥ 44 px, Energiesparmodus WLAN aus (`common/netz.py`) |

## 3 Akzeptanzkriterien

| TC/AK | erwartet | Status im Code (0efc97a) | Datei:Zeile (Umsetzung) | Problem → Lösung |
|---|---|---|---|---|
| 1.1 | Kennzeichen im Feld «Einfahrt», «Bestätigen» | fehlt | `schranken_app.py:70` | Kamera-Sim-UI mit Feldern «Einfahrt» und «Ausfahrt» |
| 1.2 | Pico 1 speichert Kennzeichen + Einfahrtszeit, UI zeigt Datum/Uhrzeit | fehlt | `parkhaus.py:24`, `kasse_app.py:104`, `common/zeitformat.py` | Uhr ohne Batterie: Zeit wird auf der Admin-Seite übernommen (`kasse_app.py:222`) |
| 1.3 | Schranke öffnet innert 2 s | fehlt | `schranken_app.py:40` | Schranke öffnet vor der HTTP-Antwort |
| 1.4 | Schranke schliesst nach 5 s | fehlt | `schranke.py:35`, `schranke.py:39` | Takt alle 50 ms schliesst nach Ablauf |
| 1.5 | Anzeige freie Plätze; bei 0 Button deaktiviert, «Parkhaus voll» | fehlt | `schranken_app.py:61` | siehe TC-09 |
| A1 | Kantonskürzel-1…6 Ziffern ohne führende Null, Kleinbuchstaben → gross, nur gültige Kantone | fehlt | `kennzeichen.py:2`, `kennzeichen.py:10`, `kennzeichen.py:16` | Liste der 26 Kantone |
| A2 | Keine doppelte Einfahrt | fehlt | `parkhaus.py:27` | siehe TC-02 |
| 2.1 | Kennzeichen in der Kassen-UI eingeben, Preis abfragen | fehlt | `kasse_app.py:119` | Formular «Preis abfragen» |
| 2.2 | Dauer und Preis gemäss Tarifmodell | fehlt | `tarif.py:11` | siehe TC-10 |
| 2.3 | CHF mit zwei Dezimalen, ohne Zoom lesbar | fehlt | `tarif.py:25`, `webutil.py:161` | |
| 2.4 | Zahlungsart Karte oder Bargeld | fehlt | `parkhaus.py:5`, `kasse_app.py:125` | |
| 2.5 | Status «Bezahlt» mit Zahlungszeit, Hinweis 15 Minuten | fehlt | `kasse_app.py:13`, `kasse_app.py:175` | |
| 3.1 | Kennzeichen im Feld «Ausfahrt» | fehlt | `schranken_app.py:71` | |
| 3.2 | Pico 2 fragt Pico 1 per HTTP (M2M), Status + Kulanz | fehlt | `m2m.py:45`, `kasse_app.py:111` | |
| 3.3 | Schranke öffnet 5 s, Kennzeichen gelöscht, Platz frei | fehlt | `parkhaus.py:88` | |
| 3.4 | «Bitte an Kasse bezahlen» bzw. «Kulanzzeit überschritten – Nachzahlung CHF …» | fehlt | `ablauf.py:6`, `ablauf.py:10` | |
| 3.5 | Rufsäule | nicht im Scope (Kap. 1.4) | – | – |
| A3 | Unbekanntes Kennzeichen: «Kennzeichen nicht gefunden» | fehlt | `ablauf.py:5`, `schranken_app.py:46` | |
| 4.1 | «Ticket verloren» für Kennzeichen ohne Parkvorgang | fehlt | `kasse_app.py:158`, `parkhaus.py:82` | |
| 4.2 | Pauschale CHF 24.00 | fehlt | `tarif.py` `PAUSCHALE_VERLOREN` | |
| 4.3 | Bezahlte Ausfahrtsberechtigung 15 min | fehlt | `parkhaus.py:75`, `kasse_app.py:208` | |
| NF1 | Schranke ≤ 2 s, UI ≤ 3 s | fehlt | `schranken_app.py:40`, `netz.py` (Energiesparmodus aus), `config.py` `STATUS_TIMEOUT_MS = 2000` | nur in der Session messbar |
| NF2 | Timeout 5 s → Meldung, Schranke zu (fail-safe) | fehlt | `m2m.py:45`, `ablauf.py:22`, `ablauf.py:38` | jede unklare Antwort = Schranke zu |
| NF3 | Nach Neustart Pico 2 beide Schranken zu | fehlt | `pico2_schranke/main.py:5` | |
| NF4 | Kein Absturz, Eingaben nie als HTML | fehlt | `webutil.py:14`, `webutil.py:122` | Fehler pro Anfrage abgefangen, Server läuft weiter |

## 4 Testinfrastruktur (Kap. 2.3)

| Anforderung | Status im Code (0efc97a) | Umsetzung |
|---|---|---|
| Admin-Seite `/admin` nur im TEST-Build | fehlt | `kasse_app.py:215`; Schalter `ADMIN_AKTIV` in `pico1_kasse/config.py` |
| «Alle Daten zurücksetzen» (G0) | fehlt | `kasse_app.py:269` |
| «Einfahrt vor n Minuten», «Zahlung vor n Minuten» | fehlt | `kasse_app.py:269`, `parkhaus.py:107`, `parkhaus.py:114` |
| Feste IPs 192.168.4.1 / .2 | fehlt | `config.py` je Pico, `common/netz.py` |

## 5 Weitere Beobachtungen (nicht im Konzept, aber relevant)

| Nr. | Beobachtung | Entscheid |
|---|---|---|
| B1 | Der Pico W hat keine batteriegepufferte Uhr. Nach jedem Start von Pico 1 stimmt die Uhrzeit nicht. | Uhrzeit wird beim Öffnen der Admin-Seite automatisch vom Browser übernommen, zusätzlich Button «Uhrzeit übernehmen». Warnung in der Kassen-UI, solange die Zeit fehlt. In G0 aufgenommen. |
| B2 | Ohne Speicherung gehen bei einem Stromausfall von Pico 1 alle Parkvorgänge verloren. | Parkvorgänge werden in `daten.json` im Flash gespeichert. |
| B3 | Das Konzept fordert «M2M-Timeout 5 s» **und** «Meldung nach höchstens 5 s». Bei genau 5 s Timeout käme die Meldung knapp danach. | Timeout 4 s (`M2M_TIMEOUT_MS`). |

## 6 Automatisierte Tests (pytest)

`python -m pytest tests` – 16 Tests, alle grün:

| Datei | prüft | Bezug |
|---|---|---|
| `tests/test_kennzeichen.py` | gültige/ungültige Kennzeichen, Kleinbuchstaben | A1, TC-08 |
| `tests/test_tarif.py` | Mindestgebühr, angefangene Stunde, Tagespauschale, Anzeige h:mm | 2.2, TC-03, TC-10 |
| `tests/test_ausfahrt.py` | Kulanzzeit 14/16 min, Ticket verloren, Parkhaus voll, Entscheidungstabelle R1–R5 | TC-05–TC-07, TC-09, TC-11–TC-13 |
