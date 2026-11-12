# Testprotokoll – Smart-Parking-System

## 1 Identifikation

| | |
|---|---|
| Testobjekt | Smart-Parking-System: Pico 1 Kasse (192.168.4.1) und Pico 2 Schranken + Kamera-Sim-UI (192.168.4.2), MicroPython, TEST-Build mit Admin-Seite |
| Version | Git-Commit [OFFEN – Hash des geflashten Stands eintragen, `git rev-parse --short HEAD`]; Basis: `0efc97a` + Änderungen Ä-01 bis Ä-10 ([aenderungen.md](aenderungen.md)) |
| MicroPython-Version auf den Picos | [OFFEN] |
| Bezug | Testkonzept v1.1 (Shane & Andreas, 24.09.2026), ergänzt zu v1.2 (siehe Kap. 7) – [Testkonzept_und_Auftrag.md](Testkonzept_und_Auftrag.md) |
| Testart | Systemtest und Abnahmetest, manuell, Black-Box |

## 2 Datum und Zeitpunkt der Durchführung

| | |
|---|---|
| Datum | [OFFEN] |
| Beginn / Ende | [OFFEN] / [OFFEN] |
| Klasse / Ort | [OFFEN] |
| Retest-Session | [OFFEN] |

## 3 Testumgebung (gemäss Kap. 2 Testkonzept)

| Element | Soll | Ist |
|---|---|---|
| Netzwerk | v1.1: eigener WLAN-Router; **v1.2: WPA2-WLAN von Pico 2 (Access Point), ohne Internet**, Netz 192.168.4.0/24 | [OFFEN – SSID eintragen] |
| Pico 1 Kasse | Raspberry Pi Pico W, Powerbank, 192.168.4.1 | [OFFEN] |
| Pico 2 Schranken | Raspberry Pi Pico W, Powerbank, 192.168.4.2, je Schranke Servo SG90 oder LED rot/grün | [OFFEN] |
| Clients | Tablet (Kamera-Sim-UI, Kassen-UI), Smartphone (TC-15), Laptop (Admin-Seite) | [OFFEN – Gerät und Browser mit Version] |
| Testdaten | nur fiktive Kennzeichen aus den Testfällen | |
| Grundzustand G0 | Admin «Alle Daten zurücksetzen», 3 freie Plätze, Uhrzeit gesetzt, Schranken zu | [OFFEN] |
| Hilfsmittel | Stoppuhr (Smartphone), Toleranz ± 1 s | |

## 4 Tester und Rollen

| Rolle | Name | Aufgabe |
|---|---|---|
| Testmanager (Mitschüler/in A) | [OFFEN] | leitet die Session, bedient die Admin-Seite, klassifiziert Mängel, führt das Protokoll |
| Fachtester B | [OFFEN] | Kamera-Sim-UI (Pico 2) |
| Fachtester C | [OFFEN] | Kassen-UI (Pico 1) |
| Entwickler | Shane, Andreas | Aufbau, Hotfixes, sonst passiv |
| Auftraggeber | [OFFEN] (Lehrperson) | Go/No-Go-Entscheid |

## 5 Übersicht der Testfälle (Erstdurchführung)

| TC | Prio | erwartet (Kurzform) | tatsächlich | Status | Mangel-Nr. |
|---|---|---|---|---|---|
| TC-01 Einfahrt | Hoch | «Einfahrt registriert: ZH-123» mit Datum/Uhrzeit; Schranke ≤ 2 s offen für 5 s; Admin: Offen, 2 frei | [OFFEN] | [OFFEN] | |
| TC-02 Doppelte Einfahrt | Mittel | «Fahrzeug bereits im Parkhaus»; zu; 1 Eintrag | [OFFEN] | [OFFEN] | |
| TC-03 Preis abfragen | Hoch | Einfahrtszeit, Dauer 0:02, CHF 2.00, «Offen» | [OFFEN] | [OFFEN] | |
| TC-04 Bezahlen (Karte) | Hoch | «Bezahlung erfolgreich – bitte innert 15 Minuten ausfahren»; «Bezahlt»; Admin: Zeit, Karte, 2.00 | [OFFEN] | [OFFEN] | |
| TC-05 Ausfahrt ohne Zahlung | Hoch | «Bitte an Kasse bezahlen»; zu | [OFFEN] | [OFFEN] | |
| TC-06 Ausfahrt nach Zahlung | Hoch | öffnet ≤ 2 s für 5 s; ZH-123 gelöscht; 2 frei | [OFFEN] | [OFFEN] | |
| TC-07 Unbekanntes Kennzeichen | Hoch | 2 × «Kennzeichen nicht gefunden»; zu; kein Absturz | [OFFEN] | [OFFEN] | |
| TC-08 Kennzeichen-Validierung | Mittel | Ungültige → «Ungültiges Kennzeichen»; kein HTML; JU-1, VD-999999, AG-9999 registriert | [OFFEN] | [OFFEN] | |
| TC-09 Parkhaus voll | Mittel | 0 frei → Button deaktiviert, «Parkhaus voll»; Tab 2 abgewiesen; nach Ausfahrt wieder aktiv | [OFFEN] | [OFFEN] | |
| TC-10 Tarifgrenzen | Hoch | 2.00 / 2.00 / 4.00 / 22.00 / 24.00 / 24.00 / 26.00 | [OFFEN] | [OFFEN] | |
| TC-11 Kulanzzeit | Hoch | 14 min öffnet; 16 min «Kulanzzeit überschritten – Nachzahlung CHF 2.00»; nach Nachzahlung öffnet | [OFFEN] | [OFFEN] | |
| TC-12 Ticket verloren | Mittel | «Kennzeichen nicht gefunden» + Option; CHF 24.00; «Bezahlt – Ausfahrt bis hh:mm»; öffnet | [OFFEN] | [OFFEN] | |
| TC-13 Kasse offline | Hoch | ≤ 5 s «Kasse nicht erreichbar – bitte Personal rufen»; zu; danach ohne Neustart wieder ok | [OFFEN] | [OFFEN] | |
| TC-14 Neustart Pico 2 | Mittel | beide Schranken zu; «Bitte an Kasse bezahlen» | [OFFEN] | [OFFEN] | |
| TC-15 Zeiten und UI | Mittel | Schranke ≤ 2 s; Seiten ≤ 3 s; Smartphone lesbar ohne Zoom | [OFFEN] | [OFFEN] | |

Die Einzelresultate (Messzeiten, Uhrzeit, Browser) stehen auf der ausgefüllten Checkliste ([testdurchfuehrung_checkliste.md](testdurchfuehrung_checkliste.md)), die als Anhang zum Protokoll gehört.

## 6 Abweichungen

Fehlerklassen gemäss Kap. 6: **Kritisch** – Testabbruch, sofortiger Fix · **Hoch** – Fix vor Freigabe · **Mittel** – Fix nach der Session · **Tief** – bei Gelegenheit.

| Nr. | TC | Beschreibung (Schritte, Kennzeichen, Uhrzeit, Browser) | Fehlerklasse | Massnahme |
|---|---|---|---|---|
| [OFFEN] | | | | |

## 7 Änderungen am Testkonzept (v1.1 → v1.2)

Beim Code-Review vor der Session sind folgende Lücken und Unklarheiten aufgefallen. Sie sind im Testkonzept mit «[v1.2]» markiert.

| Nr. | Stelle | Problem in v1.1 | Änderung in v1.2 |
|---|---|---|---|
| K-01 | Kap. 2.3, Grundzustand G0 | Der Pico W hat keine gepufferte Uhr. Nach jedem Einschalten stimmt die Zeit nicht, und Einfahrtszeiten und Preise wären falsch. | G0 verlangt zusätzlich: Admin-Seite zeigt die richtige Uhrzeit (sonst «Uhrzeit übernehmen»). |
| K-02 | Kap. 2.1, Adressierung | Viele Router belegen selbst 192.168.4.1, das ergäbe einen Konflikt mit Pico 1. | Router auf einer anderen Adresse (z. B. .254), .1/.2 ausserhalb des DHCP-Bereichs. |
| K-03 | TC-01, erwartetes Ergebnis 1 | Format von Datum/Uhrzeit nicht festgelegt. | Format «Einfahrt registriert: ZH-123 (TT.MM.JJJJ, hh:mm Uhr)». |
| K-04 | TC-06 | Widerspruch: Kap. 2.3 verlangt die Anzeige der Ausfahrtszeit, TC-06 verlangt, dass ZH-123 nicht mehr aufgeführt ist. | ZH-123 erscheint nicht mehr unter «Im Parkhaus», aber unter «Abgeschlossene Parkvorgänge» mit Ausfahrtszeit. |
| K-05 | TC-07 | «XX-000» ist formal ungültig. Unklar war, ob «Ungültiges Kennzeichen» oder «Kennzeichen nicht gefunden» erwartet wird. | Bei der Ausfahrt gilt «Kennzeichen nicht gefunden». Die Formatmeldung gilt nur bei der Einfahrt. |
| K-06 | TC-13, Schritt 4 | «Uhrzeit übernehmen» war nicht beschrieben. | ca. 15 s warten (WLAN), Admin-Seite öffnen, Uhrzeit prüfen bzw. übernehmen. |
| K-07 | Kap. 2.1, 2.3 Hardware, TC-14 | Es gibt keinen separaten Router; das Netz der Entwickler wird aus Sicherheitsgründen nur per Kabel geteilt. Ohne gemeinsames WLAN erreichen sich die Picos nicht. | Pico 2 spannt ein eigenes WPA2-WLAN ohne Internet auf (Isolation wie gefordert). Pico 2 statt Pico 1, damit bei TC-13 die Schranken-UI erreichbar bleibt. TC-14: nach dem Neustart ca. 20 s warten, bis alle Geräte wieder verbunden sind. Mobile Daten auf den Test-Geräten aus. |
| K-08 | [OFFEN] | weitere Erkenntnisse aus der Testsession | [OFFEN] |

## 8 Retest und Regressionstest

Die Resultate aus Kap. 5 bleiben unverändert stehen. Wiederholungen werden hier ergänzt.

**Regel (Kap. 3 Testkonzept):** Nach einem Hotfix wird der betroffene Testfall als Retest wiederholt. Sind mehrere Testfälle betroffen, werden alle Testfälle mit Priorität «Hoch» (TC-01, 03, 04, 05, 06, 07, 10, 11, 13) als Regressionstest wiederholt. Welche Testfälle von welcher Code-Änderung betroffen sein können, steht in [aenderungen.md](aenderungen.md).

| Lauf | Datum/Uhrzeit | Anlass (Mangel-Nr. / Änderung Ä-xx) | TC | Art (Retest/Regression) | Begründung | tatsächlich | Status |
|---|---|---|---|---|---|---|---|
| [OFFEN] | | | | | | | |

## 9 Zusammenfassung

| | Erstdurchführung | nach Retest |
|---|---|---|
| Ausgeführt (von 15) | [OFFEN] | [OFFEN] |
| Passed | [OFFEN] | [OFFEN] |
| Failed | [OFFEN] | [OFFEN] |
| Nicht ausgeführt | [OFFEN] | [OFFEN] |
| Prio «Hoch» bestanden (von 9) | [OFFEN] | [OFFEN] |
| Offene Mängel kritisch / hoch / mittel / tief | [OFFEN] | [OFFEN] |

## 10 Fazit für den Parkhausbesitzer

**Empfehlung: [OFFEN – Go / No-Go]**

Prüfung gegen die Endekriterien (Kap. 5.3):

| Endekriterium | erfüllt? |
|---|---|
| Alle 9 Testfälle mit Priorität «Hoch» ausgeführt und bestanden | [OFFEN] |
| Mindestens 80 % aller Testfälle bestanden (12 von 15) | [OFFEN] |
| Kein kritischer und kein hoher Mangel offen | [OFFEN] |
| Protokoll unterschrieben | [OFFEN] |

**In einfachen Worten:** [OFFEN – nach der Session ausformulieren: Kommen zahlende Gäste zuverlässig hinaus? Kommt niemand ohne Bezahlung hinaus? Stimmen die Preise? Was passiert, wenn die Kasse ausfällt? Welche Einschränkungen bleiben?]

## 11 Genehmigung

| Rolle | Name | Ort, Datum | Unterschrift |
|---|---|---|---|
| Testmanager | | | |
| Tester 1 | | | |
| Tester 2 | | | |
| Auftraggeber | | | |

## 12 Mitwirkende

| Person | Beitrag |
|---|---|
| Shane | [OFFEN – z. B. Testkonzept, Umsetzung Pico 1, Testaufbau, Hotfixes] |
| Andreas | [OFFEN – z. B. Testkonzept, Umsetzung Pico 2, Testaufbau, Protokoll] |
| Testmanager [OFFEN] | Leitung der Testsession, Klassifizierung, Protokoll |
| Tester B [OFFEN] | Durchführung Kamera-Sim-UI |
| Tester C [OFFEN] | Durchführung Kassen-UI |
