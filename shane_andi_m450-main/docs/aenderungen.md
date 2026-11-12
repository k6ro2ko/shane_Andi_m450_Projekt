# Änderungen am Testobjekt (für Retest und Regressionstest)

Bezug: [code_review.md](code_review.md). Ausgangsstand: Commit `0efc97a`.

Jede Änderung: **was war falsch → was wurde geändert → Dateien → betroffene Testfälle**.
Änderungen nach der Testsession werden unten in Abschnitt B fortlaufend ergänzt (Ä-11 ff.).

## A Änderungen vor der Testsession (Aufgabe 2)

### Ä-01 Smart-Parking-System neu umgesetzt (MicroPython, Pico W)
- **Falsch:** Im Repository lag eine C++-Countdown-Firmware statt des Parksystems. Keine einzige Anforderung des Testkonzepts war umgesetzt (alle TC «fehlt», siehe Review).
- **Geändert:** Neues System im Ordner `parking/`: Pico 1 = Kasse mit Kassen-UI, Admin-Seite und M2M-API, Pico 2 = Schranken mit Kamera-Sim-UI. Die Logik ohne Hardware liegt in eigenen Modulen (`kennzeichen.py`, `tarif.py`, `parkhaus.py`, `ablauf.py`, `zeitformat.py`, `webutil.py`), die Hardware nur in `schranke.py`, `netz.py` und den beiden `main.py`.
- **Dateien:** `parking/common/*`, `parking/pico1_kasse/*`, `parking/pico2_schranke/*`
- **Betroffene TC:** alle (TC-01 bis TC-15)

### Ä-02 Kennzeichen-Validierung
- **Falsch:** fehlte.
- **Geändert:** Kantonskürzel (Liste der 26 Kantone) + «-» + 1–6 Ziffern ohne führende Null; Leerzeichen am Rand entfernt, Kleinbuchstaben → Grossbuchstaben. Ohne `re`, weil MicroPython keine `{1,6}`-Wiederholung kennt. Bei der Einfahrt wird lokal auf Pico 2 abgewiesen («Ungültiges Kennzeichen», keine M2M-Anfrage) und Pico 1 prüft zusätzlich. Bei der Ausfahrt meldet ein ungültiges Kennzeichen «Kennzeichen nicht gefunden» (TC-07 «XX-000»).
- **Dateien:** `parking/common/kennzeichen.py`, `pico2_schranke/schranken_app.py`, `pico1_kasse/parkhaus.py`
- **Betroffene TC:** TC-01, TC-07, TC-08, TC-12

### Ä-03 Tarifmodell und Kulanzzeit
- **Falsch:** fehlte.
- **Geändert:** Beträge in Rappen (int). Angefangene Stunde CHF 2.00, Mindestgebühr 2.00, höchstens 24.00 pro 24 h (24:01 h = 26.00). Kulanz ≤ 15 min ab Zahlung, danach Nachzahlung ab Zahlungszeitpunkt nach demselben Tarif. Ticket verloren: Pauschale 24.00.
- **Dateien:** `pico1_kasse/tarif.py`, `pico1_kasse/parkhaus.py`
- **Betroffene TC:** TC-03, TC-04, TC-10, TC-11, TC-12

### Ä-04 Kassen-UI mit Zahlungsart und «Ticket verloren»
- **Falsch:** fehlte.
- **Geändert:** Preis abfragen, Zahlungsart «Karte»/«Bargeld» (Pflichtfeld, auch serverseitig geprüft), «Gebühr bezahlen», Meldungen wörtlich nach Konzept. Bei unbekanntem Kennzeichen: «Kennzeichen nicht gefunden» + Button «Ticket verloren» → Pauschale → «Bezahlt – Ausfahrt bis hh:mm».
- **Dateien:** `pico1_kasse/kasse_app.py`
- **Betroffene TC:** TC-03, TC-04, TC-11, TC-12, TC-15

### Ä-05 M2M mit Timeout und fail-safe
- **Falsch:** fehlte.
- **Geändert:** Eigener nicht-blockierender HTTP-Client (statt `urequests`, das den ganzen Pico blockiert). Timeout 4 s, damit die Meldung «Kasse nicht erreichbar – bitte Personal rufen» inklusive Seitenaufbau innert 5 s sichtbar ist. Jede unklare Antwort (Timeout, Fehler, kein JSON, HTTP ≠ 200) lässt die Schranke zu. Nach einem fehlgeschlagenen Request folgt keine zweite Anfrage. Der Socket wird bei einem Timeout immer geschlossen, deshalb arbeitet Pico 2 nach dem Wiedereinschalten von Pico 1 ohne Neustart weiter.
- **Dateien:** `pico2_schranke/m2m.py`, `pico2_schranke/ablauf.py`, `pico2_schranke/schranken_app.py`, `pico2_schranke/config.py`
- **Betroffene TC:** TC-01, TC-05, TC-06, TC-07, TC-11, TC-13

### Ä-06 Schranken: 5 s offen, sicherer Zustand nach Neustart
- **Falsch:** fehlte.
- **Geändert:** Die Schranken werden in `main.py` als erste Anweisung geschlossen, noch vor WLAN und Webserver. Öffnen erfolgt vor der HTTP-Antwort; ein Takt alle 50 ms schliesst nach 5 s. Bei einem Absturz schliesst `finally` die Schranken.
- **Dateien:** `pico2_schranke/schranke.py`, `pico2_schranke/main.py`
- **Betroffene TC:** TC-01, TC-06, TC-14, TC-15

### Ä-07 Kapazität 3 mit deaktiviertem Button und Serverprüfung
- **Falsch:** fehlte.
- **Geändert:** Kamera-Sim-UI zeigt die freien Plätze; bei 0 erscheint «Parkhaus voll» und «Bestätigen» ist deaktiviert. Pico 1 lehnt zusätzlich jede Einfahrt bei vollem Parkhaus ab (für einen nicht neu geladenen Tab).
- **Dateien:** `pico1_kasse/parkhaus.py`, `pico2_schranke/schranken_app.py`
- **Betroffene TC:** TC-09

### Ä-08 Admin-Seite (TEST-Build)
- **Falsch:** fehlte. Ohne sie sind TC-10 und TC-11 in 90 Minuten nicht prüfbar.
- **Geändert:** `/admin` zeigt alle Parkvorgänge mit Einfahrt, Status, Zahlung, Zahlungsart und Betrag sowie den Verlauf der letzten 10 Ausfahrten. Funktionen: «Alle Daten zurücksetzen», «Einfahrt vor n Minuten», «Zahlung vor n Minuten», «Uhrzeit übernehmen» (beim Öffnen automatisch, wenn die Uhr nicht gesetzt ist). Im PROD-Build ist `ADMIN_AKTIV = False`, dann liefert `/admin` 404.
- **Dateien:** `pico1_kasse/kasse_app.py`, `pico1_kasse/config.py`
- **Betroffene TC:** G0 für alle TC, TC-01, TC-02, TC-04, TC-06, TC-10, TC-11, TC-13

### Ä-09 Robustheit und HTML-Escaping
- **Falsch:** fehlte.
- **Geändert:** Jede Benutzereingabe wird vor der Ausgabe maskiert (`esc`). Anfragen über 2 KB werden mit 413 abgewiesen. Ein Fehler in einer Anfrage wird abgefangen, und der Server läuft weiter. Lesen der Anfrage hat einen Timeout von 5 s. Lange Eingaben werden in der Anzeige gekürzt. Parkvorgänge werden in `daten.json` gespeichert und überleben so einen Neustart von Pico 1.
- **Dateien:** `parking/common/webutil.py`, `pico1_kasse/kasse_app.py`
- **Betroffene TC:** TC-07, TC-08, TC-13, TC-14

### Ä-10 Test-WLAN ohne Router: Pico 2 als Access Point
- **Falsch:** Das Testkonzept (Kap. 2.1) setzt einen eigenen WLAN-Router voraus. Den gibt es nicht, und das Netz der Entwickler wird aus Sicherheitsgründen nur per Kabel geteilt. Ohne gemeinsames WLAN erreichen sich die Picos nicht (gleiches Fehlerbild wie am Schranken-Pico beobachtet: `/api/status` Code -1).
- **Geändert:** Pico 2 spannt selbst ein WPA2-WLAN ohne Internet auf (IP 192.168.4.2), Pico 1 verbindet sich als Client (192.168.4.1) und prüft die Verbindung alle 3 s statt 10 s. Das Flash-Skript prüft die Passwortlänge (8–63 Zeichen).
- **Dateien:** `parking/common/netz.py`, `pico2_schranke/main.py`, `pico2_schranke/config.py`, `pico1_kasse/config.py`, `parking/flash_pico.py`
- **Betroffene TC:** alle (G0); besonders TC-13 (Pico 1 aus/ein) und TC-14 (Neustart Pico 2: das WLAN ist kurz weg, Pico 1 und die Tablets verbinden neu)

### Automatisierte Tests
`tests/` (pytest, auf dem PC): 16 Tests für Kennzeichen, Tarif, Kulanzzeit, Ticket verloren, Kapazität und die Entscheidungstabelle R1–R5. Alle grün (`python -m pytest tests`). Zusätzlich wurden alle Firmware-Dateien mit `mpy-cross` (MicroPython v1.29) fehlerfrei kompiliert.

**Nicht automatisiert prüfbar** (nur in der Testsession): Zeiten (2 s / 3 s / 5 s), Servo/LED, WLAN, echter Neustart, Smartphone-Darstellung.

## B Änderungen nach der Testsession (Aufgabe 5)

| Nr. | Mangel-Nr. | Was war falsch | Was wurde geändert | Dateien | Retest | Regressionstest |
|---|---|---|---|---|---|---|
| Ä-11 | [OFFEN] | [OFFEN] | [OFFEN] | [OFFEN] | [OFFEN] | [OFFEN] |
