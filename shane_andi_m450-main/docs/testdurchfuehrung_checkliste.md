# Checkliste Testdurchführung – Smart-Parking-System

Grundlage: Testkonzept v1.2 (Kap. 7). Bitte **das tatsächliche Ergebnis** notieren, nicht nur ✔/✘. Bei einer Abweichung: Mangel-Nr. vergeben (fortlaufend M-01, M-02 …) und auf dem Mängelblatt am Ende beschreiben.

| Adressen | |
|---|---|
| Kamera-Sim-UI (Pico 2) | http://192.168.4.2/ |
| Kassen-UI (Pico 1) | http://192.168.4.1/ |
| Admin-Seite (Pico 1) | http://192.168.4.1/admin |

## Vor dem Start: Grundzustand G0

| Prüfpunkt | ☐ |
|---|---|
| Beide Picos an Powerbanks, nicht am Laptop; Onboard-LED leuchtet dauernd (WLAN verbunden) | ☐ |
| Pico 2 zuerst einschalten, dann Pico 1 | ☐ |
| Tablets/Smartphone mit WLAN «__________» (von Pico 2) verbunden, **mobile Daten aus** | ☐ |
| Admin-Seite: Uhrzeit stimmt (sonst «Uhrzeit übernehmen») | ☐ |
| Admin-Seite: «Alle Daten zurücksetzen» → «Kein Fahrzeug im System», freie Plätze 3 von 3 | ☐ |
| Beide Schranken geschlossen (LED rot / Servo zu) | ☐ |
| Kamera-Sim-UI, Kassen-UI und Admin-Seite je in einem Tab offen | ☐ |
| Stoppuhr bereit | ☐ |

Session-Start: ______ Uhr · Testmanager: __________ · Tester B (Kamera-Sim): __________ · Tester C (Kasse): __________

---

## TC-01 – Einfahrt · Prio Hoch

- **Vorbedingung:** G0. Tester B auf der Kamera-Sim-UI.
- **Schritte:** 1. Im Feld «Einfahrt» «ZH-123» eingeben, «Bestätigen», Zeit bis zum Öffnen stoppen. 2. Schranke beobachten (offen wie lange?). 3. Admin-Seite neu laden.
- **Erwartet:** «Einfahrt registriert: ZH-123 (Datum, Uhrzeit)»; Schranke öffnet ≤ 2 s, bleibt 5 s (± 1 s) offen, schliesst; Admin: ZH-123 mit Einfahrtszeit, Status «Offen», freie Plätze 2.

| Tatsächliches Ergebnis | |
|---|---|
| Meldung (Wortlaut) | |
| Zeit bis Öffnen / Offen-Dauer | ____ s / ____ s |
| Admin-Seite | |
| Uhrzeit · Browser/Gerät | ______ · ____________ |
| Status | ☐ Passed ☐ Failed · Mangel-Nr.: ____ |

## TC-02 – Doppelte Einfahrt · Prio Mittel

- **Vorbedingung:** TC-01 erfolgreich.
- **Schritte:** Sofort erneut «ZH-123» als Einfahrt bestätigen. Admin-Seite neu laden.
- **Erwartet:** «Fahrzeug bereits im Parkhaus»; Schranke bleibt ZU; Admin: genau ein Eintrag ZH-123.

| Tatsächliches Ergebnis | |
|---|---|
| Meldung / Schranke | |
| Admin-Seite | |
| Uhrzeit · Browser/Gerät | ______ · ____________ |
| Status | ☐ Passed ☐ Failed · Mangel-Nr.: ____ |

## TC-03 – Preis abfragen · Prio Hoch

- **Vorbedingung:** ZH-123 seit ca. 2 Minuten im System.
- **Schritte:** Tester C: Kassen-UI, «ZH-123» eingeben, «Preis abfragen».
- **Erwartet:** Einfahrtszeit, Parkdauer (z. B. 0:02 h), CHF 2.00 gut lesbar, Status «Offen».

| Tatsächliches Ergebnis | |
|---|---|
| Einfahrt / Dauer / Betrag / Status | |
| Uhrzeit · Browser/Gerät | ______ · ____________ |
| Status | ☐ Passed ☐ Failed · Mangel-Nr.: ____ |

## TC-04 – Bezahlen (Karte) · Prio Hoch

- **Vorbedingung:** Preis von ZH-123 wird angezeigt (TC-03).
- **Schritte:** Zahlungsart «Karte» wählen, «Gebühr bezahlen». Admin-Seite neu laden.
- **Erwartet:** «Bezahlung erfolgreich – bitte innert 15 Minuten ausfahren»; Status «Bezahlt»; Admin: Zahlungszeit, «Karte», CHF 2.00.

| Tatsächliches Ergebnis | |
|---|---|
| Meldung / Status | |
| Admin-Seite | |
| Uhrzeit · Browser/Gerät | ______ · ____________ |
| Status | ☐ Passed ☐ Failed · Mangel-Nr.: ____ |

## TC-05 – Ausfahrt ohne Zahlung · Prio Hoch

- **Vorbedingung:** «BE-999» eingefahren (wie TC-01), nicht bezahlt.
- **Schritte:** Tester B: Feld «Ausfahrt» «BE-999», «Bestätigen».
- **Erwartet:** «Bitte an Kasse bezahlen»; Ausfahrtsschranke bleibt ZU.

| Tatsächliches Ergebnis | |
|---|---|
| Meldung / Schranke | |
| Uhrzeit · Browser/Gerät | ______ · ____________ |
| Status | ☐ Passed ☐ Failed · Mangel-Nr.: ____ |

## TC-06 – Ausfahrt nach Zahlung · Prio Hoch

- **Vorbedingung:** ZH-123 hat bezahlt (TC-04), Zahlung < 15 min her.
- **Schritte:** Feld «Ausfahrt» «ZH-123», «Bestätigen», Zeit stoppen. Admin-Seite neu laden.
- **Erwartet:** Ausfahrtsschranke öffnet ≤ 2 s für 5 s; Admin: ZH-123 nicht mehr unter «Im Parkhaus» (nur noch unter «Abgeschlossene Parkvorgänge»), freie Plätze 2 (BE-999 ist noch drin).

| Tatsächliches Ergebnis | |
|---|---|
| Meldung / Zeit bis Öffnen / Offen-Dauer | ____ s / ____ s |
| Admin-Seite | |
| Uhrzeit · Browser/Gerät | ______ · ____________ |
| Status | ☐ Passed ☐ Failed · Mangel-Nr.: ____ |

## TC-07 – Unbekanntes Kennzeichen · Prio Hoch

- **Vorbedingung:** nach TC-06.
- **Schritte:** Ausfahrt «XX-000», danach Ausfahrt «ZH-123».
- **Erwartet:** beide Male «Kennzeichen nicht gefunden»; Schranke ZU; kein Absturz (Seite weiter bedienbar).

| Tatsächliches Ergebnis | |
|---|---|
| XX-000 | |
| ZH-123 | |
| Uhrzeit · Browser/Gerät | ______ · ____________ |
| Status | ☐ Passed ☐ Failed · Mangel-Nr.: ____ |

## TC-08 – Kennzeichen-Validierung · Prio Mittel

- **Vorbedingung:** G0 (Admin: «Alle Daten zurücksetzen»).
- **Schritte / Erwartet:**

| Schritt | Eingabe (Einfahrt) | Erwartet | Tatsächlich | ✔/✘ |
|---|---|---|---|---|
| 1a | ZH- | «Ungültiges Kennzeichen», Schranke zu | | |
| 1b | ZH-1234567 | dito | | |
| 1c | ZH-0123 | dito | | |
| 1d | XX-123 | dito | | |
| 1e | ZH123 | dito | | |
| 1f | (leer) | dito | | |
| 2a | 60 × «A» | dito, kein Absturz | | |
| 2b | `<b>ZH-1</b>` | dito, Text nicht fett | | |
| 3a | JU-1 | registriert als JU-1, Schranke öffnet | | |
| 3b | VD-999999 | registriert als VD-999999, öffnet | | |
| 3c | ag-9999 | registriert als AG-9999, öffnet | | |
| – | Admin-Seite | nur JU-1, VD-999999, AG-9999 | | |

| | |
|---|---|
| Uhrzeit · Browser/Gerät | ______ · ____________ |
| Status | ☐ Passed ☐ Failed · Mangel-Nr.: ____ |

## TC-09 – Parkhaus voll · Prio Mittel

- **Vorbedingung:** G0. Kamera-Sim-UI in zwei Tabs offen.

| Schritt | Aktion | Erwartet | Tatsächlich | ✔/✘ |
|---|---|---|---|---|
| 1 | Einfahrten FR-101, FR-102, FR-103 | Schranke öffnet jeweils; freie Plätze 0 | | |
| 2 | Tab 1 neu laden | «Bestätigen» (Einfahrt) deaktiviert, «Parkhaus voll» | | |
| 3 | Tab 2 (nicht neu geladen): Einfahrt FR-104 | «Parkhaus voll», Schranke ZU | | |
| 4 | FR-101 an der Kasse bezahlen, ausfahren; Tab 1 neu laden; Einfahrt FR-104 | Ausfahrt öffnet; «Bestätigen» aktiv; FR-104 registriert, Schranke öffnet | | |

| | |
|---|---|
| Uhrzeit · Browser/Gerät | ______ · ____________ |
| Status | ☐ Passed ☐ Failed · Mangel-Nr.: ____ |

## TC-10 – Tarifgrenzen · Prio Hoch

- **Vorbedingung:** G0; Einfahrt «TG-500».
- **Schritte:** Je Spalte: Testmanager setzt auf der Admin-Seite bei TG-500 n ein und klickt «Einfahrt vor n Minuten»; Tester C fragt **innert 30 s** in der Kassen-UI den Preis ab.

| n (min) | 0 | 59 | 61 | 659 | 661 | 1439 | 1441 |
|---|---|---|---|---|---|---|---|
| Erwartet Dauer | 0:00 | 0:59 | 1:01 | 10:59 | 11:01 | 23:59 | 24:01 |
| Erwartet CHF | 2.00 | 2.00 | 4.00 | 22.00 | 24.00 | 24.00 | 26.00 |
| Tatsächlich Dauer | | | | | | | |
| Tatsächlich CHF | | | | | | | |
| ✔/✘ | | | | | | | |

| | |
|---|---|
| Uhrzeit · Browser/Gerät | ______ · ____________ |
| Status | ☐ Passed ☐ Failed · Mangel-Nr.: ____ |

## TC-11 – Kulanzzeit · Prio Hoch

- **Vorbedingung:** G0; SZ-710 und SZ-711 eingefahren und mit je CHF 2.00 bezahlt.

| Schritt | Aktion | Erwartet | Tatsächlich | ✔/✘ |
|---|---|---|---|---|
| 1 | Admin: Zahlung SZ-710 «vor 14 Minuten»; Ausfahrt SZ-710 | Schranke öffnet | | |
| 2 | Admin: Zahlung SZ-711 «vor 16 Minuten»; Ausfahrt SZ-711 | ZU; «Kulanzzeit überschritten – Nachzahlung CHF 2.00» | | |
| 3 | Kasse: SZ-711 abfragen, Nachgebühr mit «Bargeld» bezahlen; Ausfahrt SZ-711 | Nachgebühr CHF 2.00; danach öffnet die Schranke | | |

| | |
|---|---|
| Uhrzeit · Browser/Gerät | ______ · ____________ |
| Status | ☐ Passed ☐ Failed · Mangel-Nr.: ____ |

## TC-12 – Ticket verloren · Prio Mittel

- **Vorbedingung:** G0; «GL-4040» nie registriert.

| Schritt | Aktion | Erwartet | Tatsächlich | ✔/✘ |
|---|---|---|---|---|
| 1 | Kasse: GL-4040 abfragen | «Kennzeichen nicht gefunden» + «Ticket verloren» | | |
| 2 | «Ticket verloren», «Bargeld», «Gebühr bezahlen» | CHF 24.00; «Bezahlt – Ausfahrt bis hh:mm» (= Zahlung + 15 min) | | |
| 3 | Innert 15 min Ausfahrt GL-4040 | Schranke öffnet | | |

| | |
|---|---|
| Uhrzeit · Browser/Gerät | ______ · ____________ |
| Status | ☐ Passed ☐ Failed · Mangel-Nr.: ____ |

## TC-13 – Kasse offline · Prio Hoch

- **Vorbedingung:** G0; OW-1313 eingefahren und bezahlt.

| Schritt | Aktion | Erwartet | Tatsächlich | ✔/✘ |
|---|---|---|---|---|
| 1 | Pico 1 von der Powerbank trennen | Kassen-UI nicht erreichbar | | |
| 2 | Ausfahrt OW-1313, Zeit bis zur Meldung stoppen | ≤ 5 s «Kasse nicht erreichbar – bitte Personal rufen»; ZU | ____ s | |
| 3 | Einfahrt NE-2020 | gleiche Meldung; ZU; keine Registrierung | | |
| 4 | Pico 1 anschliessen, ca. 15 s warten, Admin-Seite: Uhrzeit prüfen; Einfahrt NE-2020 (Pico 2 **nicht** neu starten) | NE-2020 registriert, Schranke öffnet | | |

| | |
|---|---|
| Uhrzeit · Browser/Gerät | ______ · ____________ |
| Status | ☐ Passed ☐ Failed · Mangel-Nr.: ____ |

## TC-14 – Neustart Pico 2 · Prio Mittel

- **Vorbedingung:** G0.

| Schritt | Aktion | Erwartet | Tatsächlich | ✔/✘ |
|---|---|---|---|---|
| 1 | Einfahrt AI-900; während die Schranke offen ist, Pico 2 trennen, nach 10 s wieder anschliessen | Nach dem Aufstarten beide Schranken geschlossen | | |
| 2 | ca. 20 s warten (Tablet und Pico 1 verbinden neu mit dem WLAN von Pico 2); Kamera-Sim-UI neu laden; Ausfahrt AI-900 | UI erreichbar; «Bitte an Kasse bezahlen»; ZU | | |

| | |
|---|---|
| Uhrzeit · Browser/Gerät | ______ · ____________ |
| Status | ☐ Passed ☐ Failed · Mangel-Nr.: ____ |

## TC-15 – Zeiten und UI · Prio Mittel

- **Vorbedingung:** G0; Tablet und Smartphone im Test-WLAN.

| Schritt | Aktion | Erwartet | Gemessen | ✔/✘ |
|---|---|---|---|---|
| 1 | Einfahrten SG-321 / SG-322 / SG-323, Zeit bis Öffnen | je ≤ 2 s | ___ / ___ / ___ s | |
| 2a | Kamera-Sim-UI 3 × neu laden | je ≤ 3 s bedienbar | ___ / ___ / ___ s | |
| 2b | Kassen-UI 3 × neu laden | je ≤ 3 s | ___ / ___ / ___ s | |
| 2c | Admin-Seite 3 × neu laden | je ≤ 3 s | ___ / ___ / ___ s | |
| 3 | Smartphone: Kassen-UI, SG-321 abfragen | Betrag ohne Zoom lesbar, kein horizontales Scrollen, Touch-Bedienung | | |

| | |
|---|---|
| Uhrzeit · Browser/Gerät (Tablet / Smartphone) | ______ · ____________ / ____________ |
| Status | ☐ Passed ☐ Failed · Mangel-Nr.: ____ |

---

## Mängelblatt

Fehlerklassen (Kap. 6): **Kritisch** (Kernfunktion defekt, Absturz, Schranke öffnet grundlos, falscher Preis) · **Hoch** (wichtige Funktion eingeschränkt, Workaround vorhanden) · **Mittel** (ohne Einfluss auf die Geschäftslogik, z. B. Tippfehler) · **Tief** (CSS/Kosmetik).

| Nr. | TC / Schritt | Eingabe (Kennzeichen) | Beobachtung (was genau passierte) | Uhrzeit | Browser/Gerät | Klasse |
|---|---|---|---|---|---|---|
| M-01 | | | | | | |
| M-02 | | | | | | |
| M-03 | | | | | | |
| M-04 | | | | | | |
| M-05 | | | | | | |

## Retests / Regressionstests während der Session

| TC | Anlass (Mangel-Nr. / Hotfix) | Uhrzeit | Ergebnis | Status |
|---|---|---|---|---|
| | | | | |
| | | | | |
