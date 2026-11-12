# Smart-Parking-System – Auftrag und Testkonzept

Dieses Dokument enthält zwei Teile:

- **Teil A:** Auftrag «Testprotokoll Parksystem» (Vorgabe der Lehrperson)
- **Teil B:** Testkonzept v1.1 (Shane & Andreas)

---

# Teil A – Auftrag: Testprotokoll Parksystem

## Auftrag

Führt die Tests für euer Parksystem durch. Grundlage dafür ist das Testkonzept, welches ihr in der Aufgabe «A01-02-10-Testkonzept-Parksystem» erstellt habt, sowie die Umsetzung aus der Aufgabe «A01-03-umsetzung-parksystem».

Haltet die Durchführung und die Resultate in einem Testprotokoll fest. Das Testprotokoll soll so aufgebaut sein, dass der Auftraggeber (der Parkhausbesitzer) anhand des Protokolls entscheiden kann, ob das Parksystem in Betrieb genommen werden kann.

## Testdurchführung gemäss Konzept

Führt die Testfälle aus eurem Testkonzept auf der Umgebung (Pico 1 Kasse / Pico 2 Schranken) aus.

- Haltet euch an die Testumgebung, die Rollen und die Testfälle, die im Testkonzept definiert sind.
- Haltet für jeden Testfall das tatsächliche Ergebnis fest, nicht nur ob er bestanden wurde.
- Wird eine Abweichung festgestellt, klassifiziert diese gemäss der Fehlerklassifizierung aus eurem Testkonzept.
- Beschreibt Abweichungen so, dass sie von jemand anderem nachvollzogen werden können (Schritte, Eingaben, z. B. Kennzeichen, Uhrzeit, Browser).

Stellt ihr fest, dass im Testkonzept Testfälle fehlen oder nicht eindeutig formuliert sind, ergänzt bzw. korrigiert das Testkonzept und vermerkt dies im Testprotokoll.

## Testprotokoll erstellen

Erstellt ein Testprotokoll mit den durchgeführten Tests und deren Resultaten. Überlegt euch dabei, was ihr im Unterricht zum Inhalt eines Testprotokolls erarbeitet habt. Z. B.:

- Identifikation (Testobjekt, Version, Bezug zum Testkonzept)
- Datum / Zeitpunkt der Durchführung
- Testumgebung
- Tester
- Übersicht der ausgeführten Testfälle mit Resultat (erwartet / tatsächlich / Status)
- Gefundene Abweichungen inkl. Fehlerklasse
- Fazit: Kann das Parksystem in Betrieb genommen werden?
- Genehmigung

## Erweiterungen / Anpassungen

Behebt die gefundenen Fehler in eurer Umsetzung oder setzt fehlende Anforderungen um.

- Führt die betroffenen Testfälle anschliessend erneut aus (Retest).
- Überlegt, ob durch die Anpassung andere Funktionen beeinflusst werden könnten, und führt auch diese Testfälle nochmals aus (Regressionstest).
- Ergänzt das Testprotokoll um die erneuten Testausführungen. Die ursprünglichen Resultate bleiben im Protokoll erhalten.

## Abgabeform

Gebt das Testprotokoll als Dokument (PDF) ab. Im Dokument soll klar erkennbar sein, wer in der Gruppe mitgewirkt hat.

> *Hinweis: Der restliche Auftrag (Linksammlung, Bewertungskriterien, formale Kriterien, Notenskala, verspätete Abgabe) lag beim Konvertieren nicht vor.*

---

# Teil B – Testkonzept

**IoT-basiertes Parkraummanagementsystem (Raspberry Pi Pico 1 & 2)**

| | |
|---|---|
| Projekt | Smart-Parking-System |
| Autoren | Shane und Andreas (Informatiker 3. Lehrjahr) |
| Datum | 24. September 2026 |
| Version | 1.2 (Ergänzung während der Testvorbereitung, 05.11.2026; Änderungen gegenüber 1.1 sind mit «[v1.2]» markiert und im Testprotokoll Kap. 7 begründet) |
| Methodik | Angelehnt an HERMES 2022 / Black-Box-Testing |

## Management Summary

Dieses Dokument definiert die Strategie, Organisation und die spezifischen Testfälle für die Qualitätssicherung des entwickelten Parksystems. Ziel ist es, durch systematische manuelle Tests die Erfüllung aller formulierten User Stories und Akzeptanzkriterien nachzuweisen. Das Konzept ist so strukturiert, dass die Durchführung der Tests als «Black-Box-Test» von systemfremden Personen (z. B. Mitschülern) im Rahmen einer 90-minütigen Unterrichtseinheit übernommen werden kann.

Version 1.1 vervollständigt das Konzept: Testziele und Risiken, die vollständige Testbasis mit der Zuordnung von Akzeptanzkriterium zu Testfall, Teststufen und Testarten, die Planung der 90-minütigen Session sowie alle 15 Testfälle (TC-01 bis TC-15) – davon 9 mit Priorität «Hoch».

---

## 1 Einleitung und Testgegenstand

Das Projekt «Smart-Parking-System» automatisiert die Zufahrtskontrolle und Gebührenabrechnung eines Parkhauses mittels zweier Microcontroller (Raspberry Pi Pico). Dieses Testkonzept dient als verbindlicher Leitfaden zur Verifizierung der entwickelten Hard- und Softwarekomponenten. Es ist so geschrieben, dass eine fremde Testgruppe die Tests ohne Rückfragen durchführen kann: Kapitel 1 bis 6 legen Gegenstand, Umgebung, Vorgehen, Rollen, Zeitplan und Fehlerklassen fest, Kapitel 7 enthält die auszuführenden Testfälle und Kapitel 8 das Protokoll für die Abnahme.

### 1.1 Was wird getestet? (Test Objects)

Der Testfokus liegt auf der fehlerfreien Integration der Hardware, der Geschäftslogik und der M2M-Kommunikation (Machine-to-Machine) zwischen den Picos. Konkret werden folgende Komponenten geprüft:

- **Pico 1 (Kasse – Backend & UI):** Webserver-Funktionalität, Korrektheit der Preisberechnung anhand von Zeitstempeln (Aufenthaltsdauer) und Statusänderung nach dem Bezahlvorgang.
- **Pico 2 (Schranken & Kamera-Simulation):** GPIO-Steuerung der Servomotoren/LEDs (Ein- und Ausfahrtsschranken), Webschnittstelle zur manuellen Kennzeicheneingabe (Simulation der OCR-Kamera).
- **Schnittstellen (API):** Die bidirektionale Kommunikation über das lokale Netzwerk, insbesondere die Statusabfrage (Bezahlt/Nicht Bezahlt) des Ausfahrts-Picos an den Kassen-Pico.

### 1.2 Testziele und Produktrisiken

Getestet wird risikobasiert: Je grösser der Schaden bei einem Fehler, desto wichtiger der Testfall. Das System entscheidet selbständig über Ein- und Ausfahrt und rechnet mit Geld – ein Fehler kostet den Betreiber entweder Einnahmen oder Kunden. Die Tests weisen nach, dass die Akzeptanzkriterien erfüllt sind, und liefern der Testgruppe die Grundlage für die Freigabeempfehlung (Kapitel 8).

| Produktrisiko | Auswirkung | Priorität | Abgedeckt durch |
|---|---|---|---|
| Schranke öffnet ohne gültige Zahlung | Einnahmeverlust | Hoch | TC-05, TC-07, TC-11, TC-13 |
| Bezahlter Gast kommt nicht hinaus | Stau, verärgerte Gäste | Hoch | TC-06, TC-11, TC-12 |
| Falscher Preis an Tarifgrenzen oder bei der Pauschale | Reklamationen, Einnahmeverlust | Hoch | TC-03, TC-10, TC-12 |
| Ausfall der M2M-Verbindung | Schranken blockieren oder öffnen falsch | Hoch | TC-13, TC-14 |
| Doppel- oder Überbelegung | Falsche Anzeige der freien Plätze | Mittel | TC-02, TC-09 |
| Fehleingaben bringen einen Pico zum Absturz | Betriebsunterbruch | Mittel | TC-07, TC-08 |

### 1.3 Testbasis: User Stories und Akzeptanzkriterien

Grundlage sind die vier User Stories aus der Anforderungsaufgabe. Sie beschreiben ein klassisches Parkhaus mit Ticket; der Prototyp arbeitet stattdessen mit dem Kennzeichen als eindeutiger Kennung. Die Spalte «Umsetzung im Prototyp» hält fest, wie das Kriterium konkret geprüft wird – sie ist für die Tester verbindlich. Die letzte Spalte zeigt, welche Testfälle das Kriterium abdecken.

#### US01 – Ticket ziehen und einfahren (Priorität Hoch)

| AK | Anforderung (User Story) | Umsetzung im Prototyp – so wird geprüft | Testfälle |
|---|---|---|---|
| 1.1 | Sensor erkennt das Fahrzeug an der Schranke | Kennzeichen in der Kamera-Sim-UI (Pico 2) im Feld «Einfahrt» eingeben, «Bestätigen» | TC-01 |
| 1.2 | Ticket mit eindeutigem Code, Einfahrtsdatum und Uhrzeit | Das Kennzeichen ist die eindeutige ID; Pico 1 speichert Kennzeichen und Einfahrtszeit, die UI bestätigt «Einfahrt registriert» mit Datum und Uhrzeit | TC-01, TC-03 |
| 1.3 | Schranke öffnet nach der Ticketentnahme | Schranke öffnet nach erfolgreicher Registrierung innert 2 s | TC-01 |
| 1.4 | Schranke schliesst nach der Durchfahrt | Ohne Durchfahrtssensor: Schranke schliesst nach 5 s | TC-01 |
| 1.5 | Parkhaus voll: Knopf deaktiviert, Schranke bleibt zu | Anzeige der freien Plätze; bei 0: «Bestätigen» deaktiviert, «Parkhaus voll», Schranke zu | TC-09 |
| A1 | Nur gültige Kennzeichen (Ausgangslage) | Kantonskürzel, Bindestrich und 1–6 Ziffern ohne führende Null (z. B. ZH-123); Kleinbuchstaben werden umgewandelt | TC-01, TC-08 |
| A2 | Keine doppelte Einfahrt (Ausgangslage) | Kennzeichen bereits im Parkhaus: «Fahrzeug bereits im Parkhaus», Schranke zu | TC-02 |

#### US02 – Ticket am Kassenautomaten bezahlen (Priorität Hoch)

| AK | Anforderung (User Story) | Umsetzung im Prototyp – so wird geprüft | Testfälle |
|---|---|---|---|
| 2.1 | Automat liest den Code des Tickets | Kennzeichen in der Kassen-UI (Pico 1) eingeben und Preis abfragen | TC-03, TC-12 |
| 2.2 | Parkdauer aus dem Einfahrtszeitstempel, Tarif berechnet | Parkdauer und Preis gemäss Tarifmodell (unten) | TC-03, TC-10 |
| 2.3 | Betrag gut lesbar angezeigt | Betrag in CHF mit zwei Dezimalstellen, auf Tablet und Smartphone ohne Zoomen lesbar | TC-03, TC-15 |
| 2.4 | Kartenzahlung und/oder Bargeld | Zahlungsart «Karte» oder «Bargeld» wählen; die Zahlung wird simuliert | TC-04, TC-11, TC-12 |
| 2.5 | Status «Bezahlt», Ticket entwertet, 15 min Kulanzzeit | Status «Bezahlt» mit Zahlungszeit; Hinweis «bitte innert 15 Minuten ausfahren» | TC-04, TC-11 |

#### US03 – Ticket entwerten und ausfahren (Priorität Hoch)

| AK | Anforderung (User Story) | Umsetzung im Prototyp – so wird geprüft | Testfälle |
|---|---|---|---|
| 3.1 | Leser an der Ausfahrt erfasst das Ticket | Kennzeichen in der Kamera-Sim-UI im Feld «Ausfahrt» eingeben | TC-05, TC-06 |
| 3.2 | Prüfung: bezahlt und innerhalb der Kulanzzeit? | Pico 2 fragt Pico 1 per HTTP an (M2M); Pico 1 prüft Status und Kulanzzeit | TC-05, TC-06, TC-11 |
| 3.3 | Erfolg: Schranke öffnet, Parkvorgang geschlossen | Schranke öffnet für 5 s; Kennzeichen wird gelöscht, der Platz ist wieder frei | TC-06, TC-07, TC-09 |
| 3.4 | Nicht bezahlt oder Zeit überschritten: Aufforderung zur (Nach-)Zahlung | Schranke bleibt zu; «Bitte an Kasse bezahlen» bzw. «Kulanzzeit überschritten – Nachzahlung CHF …» | TC-05, TC-11 |
| 3.5 | Rufsäule/Sprechtaste für Notfälle | Im Prototyp nicht vorhanden (Kap. 1.4) | – (Kap. 1.4) |
| A3 | Nur registrierte Fahrzeuge fahren aus (Ausgangslage) | Unbekanntes Kennzeichen: «Kennzeichen nicht gefunden», Schranke zu | TC-07 |

#### US04 – Verlorenes Ticket ersetzen (Priorität Mittel)

| AK | Anforderung (User Story) | Umsetzung im Prototyp – so wird geprüft | Testfälle |
|---|---|---|---|
| 4.1 | Option «Ticket verloren» am Automaten | Button «Ticket verloren» in der Kassen-UI für Kennzeichen ohne Parkvorgang | TC-12 |
| 4.2 | Tageshöchstpauschale wird berechnet | Pauschale CHF 24.00 | TC-12 |
| 4.3 | Neues, bezahltes Ausfahrtsticket, 15 min gültig | Bezahlte Ausfahrtsberechtigung für das Kennzeichen, gültig 15 Minuten | TC-12 |

#### NF – Nicht-funktionale Anforderungen (ergänzt)

| AK | Anforderung | Umsetzung im Prototyp – so wird geprüft | Testfälle |
|---|---|---|---|
| NF1 | Reaktionszeit | Schranke öffnet innert 2 s; Web-UIs sind innert 3 s bedienbar | TC-01, TC-06, TC-15 |
| NF2 | Verbindungsausfall (fail-safe) | Antwortet Pico 1 nicht innert 5 s: Meldung, Schranke bleibt zu | TC-13 |
| NF3 | Sicherer Zustand nach Neustart | Nach dem Neustart von Pico 2 sind beide Schranken zu | TC-14 |
| NF4 | Robustheit bei Fehleingaben | Kein Absturz; Eingaben werden nie als HTML dargestellt | TC-07, TC-08 |

#### Tarifmodell (Testorakel für alle Preisprüfungen)

Die Parkdauer wird aus dem Einfahrtszeitstempel berechnet. Jede angefangene Stunde kostet **CHF 2.00**, die Mindestgebühr beträgt **CHF 2.00**. Pro 24 Stunden wird höchstens die **Tageshöchstpauschale von CHF 24.00** verrechnet; sie gilt auch als Gebühr für ein verlorenes Ticket. Nach der Zahlung läuft eine **Kulanzzeit von 15 Minuten**; wer später ausfährt, zahlt ab dem Zahlungszeitpunkt erneut CHF 2.00 je angefangene Stunde nach.

### 1.4 Abgrenzung (Out of Scope)

| Nicht Teil der Tests | Begründung |
|---|---|
| Ticketdrucker, Barcode-Scanner, Fahrzeugsensor, Rufsäule (AK 3.5) | Im Prototyp nicht vorhanden; ersetzt durch Kennzeichen-Eingabe in der Kamera-Sim-UI. Die zugehörigen Akzeptanzkriterien werden im Konzept auf die vorhandene Umsetzung abgebildet (Kap. 1.3). |
| Echte Kartenzahlung und echtes Bargeld | Die Zahlung wird in der Kassen-UI simuliert; geprüft wird nur die Statusänderung im System. |
| Mechanik einer realen Schranke, Dauerbetrieb, Lasttests | Servo/LED stellen die Schranke dar; im Unterrichtsrahmen wird nur ein Fahrzeug nach dem anderen abgefertigt. |
| Penetrationstests, Verschlüsselung, Benutzerverwaltung | Das Testnetz ist isoliert (Kap. 2.1); geprüft wird lediglich, dass Fehleingaben das System nicht zum Absturz bringen (TC-08). |
| Komponententests der einzelnen Funktionen | Werden von den Entwicklern in der DEV-Umgebung durchgeführt (Kap. 3) und sind Voraussetzung für den Start der Testsession. |

---

## 2 Testumgebung und Infrastruktur

Gemäss den Architekturvorgaben für IT-Projekte (Referenz: Unterlage «T02-Umgebungen») ist eine strikte Trennung von Entwicklung, Test und Produktion zwingend erforderlich, um Seiteneffekte zu vermeiden und die Datenhoheit zu gewährleisten.

### 2.1 Isolation und Netzwerkarchitektur

Die Tests werden ausschliesslich in einer dedizierten TEST-Umgebung durchgeführt.

- **Netzwerk (WLAN):** Es wird ein separater, lokaler WLAN-Router (ohne WAN/Internet-Uplink) im Schulzimmer aufgestellt. Dies verhindert störende Zugriffe aus dem Schulnetzwerk und isoliert die M2M-Kommunikation. **[v1.2]** Es steht kein Router zur Verfügung. Stattdessen spannt Pico 2 selbst ein WPA2-geschütztes WLAN ohne Internet auf; Pico 1 und die Test-Geräte verbinden sich damit. Die Isolation bleibt gleich. Auf den Test-Geräten werden mobile Daten ausgeschaltet.
- **Adressierung:** Beide Picos erhalten eine feste IP-Adresse (Pico 1 Kasse: `192.168.4.1`, Pico 2 Schranken: `192.168.4.2`). Die Tester rufen die Oberflächen direkt über diese Adressen auf; die Adressen sind am Testplatz angeschrieben. **[v1.2]** Der Router selbst liegt auf einer anderen Adresse (z. B. `192.168.4.254`), .1 und .2 liegen ausserhalb seines DHCP-Bereichs.
- **Datenhoheit & sensible Daten:** Da in der PROD-Umgebung echte Autokennzeichen (personenbezogene Daten) anfallen würden, arbeiten wir in der TEST-Umgebung ausschliesslich mit Dummy-Daten (z. B. ZH-123, BE-999). Es werden keine realen Daten in der Testumgebung gespeichert.

### 2.2 Abgrenzung der Umgebungen (DEV, TEST, PROD)

- **DEV (Development):** Die Laptops von Shane und Andreas. Hier wird der Python/MicroPython-Code geschrieben und via Thonny IDE direkt auf die Picos geflasht. Hier laufen auch die Komponenten- und Integrationstests der Entwickler (Kap. 3).
- **TEST (Testing):** Der physische Aufbau auf dem Schreibtisch. Zwei Picos, angebunden an Powerbanks (unabhängig vom Laptop), verbunden über den dedizierten Test-Router. Bedienung erfolgt über Tablets/Smartphones der Tester. Geladen ist der TEST-Build, der zusätzlich die Admin-Seite (Kap. 2.3) enthält.
- **PROD (Production):** Theoretischer Endzustand im realen Parkhaus. In diesem Projekt Out-of-Scope, jedoch simuliert durch die Abwesenheit von Debugging-Kabeln während des Tests. Im PROD-Build ist die Admin-Seite deaktiviert.

### 2.3 Testdaten, Admin-Seite und Grundzustand G0

Damit jeder Testfall reproduzierbar ist, starten die Tester ihn im **Grundzustand G0**: Beide Picos laufen mit dem TEST-Build am Test-Router, auf der Admin-Seite wurde «Alle Daten zurücksetzen» ausgeführt (kein Fahrzeug im System, 3 freie Plätze), **[v1.2]** die Admin-Seite zeigt die aktuelle Uhrzeit (sonst «Uhrzeit übernehmen» klicken – der Pico hat keine gepufferte Uhr), beide Schranken sind geschlossen, und Kamera-Sim-UI, Kassen-UI sowie Admin-Seite sind je in einem Browser-Tab geöffnet.

| | |
|---|---|
| **Hardware** | 2 × Raspberry Pi Pico W mit je einer Powerbank; pro Schranke ein Servo SG90 oder ein LED-Paar (rot = geschlossen, grün = offen); ~~Test-Router~~ **[v1.2]** Test-WLAN von Pico 2; Stoppuhr (Smartphone). |
| **Clients** | Tablet der Tester für Kamera-Sim-UI und Kassen-UI, Smartphone für die Prüfung der Bedienbarkeit (TC-15), Laptop des Testmanagers für die Admin-Seite. |
| **Admin-Seite (nur TEST-Build)** | `http://192.168.4.1/admin` – zeigt alle Parkvorgänge mit Ein-, Zahlungs- und Ausfahrtszeit. Sie erlaubt «Alle Daten zurücksetzen» sowie das Zurücksetzen einzelner Zeitstempel («Einfahrt vor n Minuten», «Zahlung vor n Minuten»). Ohne diese Funktion liessen sich Stundentarif, Tagespauschale und Kulanzzeit in 90 Minuten nicht prüfen. Bedient wird sie ausschliesslich vom Testmanager. |
| **Testdaten** | Fiktive Kennzeichen nach dem Muster «Kantonskürzel-Nummer», in den Testfällen fest vorgegeben (z. B. ZH-123, BE-999, FR-101). Keine realen Kennzeichen. |
| **Toleranzen** | Zeitmessungen mit der Stoppuhr: ± 1 Sekunde. Bei Prüfungen mit zurückgesetzten Zeitstempeln muss der Preis innert 30 Sekunden abgefragt werden, da die Uhr weiterläuft. |

---

## 3 Teststufen und Testarten

Die Teststufen folgen dem V-Modell: Die Entwickler prüfen zuerst die einzelnen Funktionen, danach das Zusammenspiel; erst ein lauffähiges Gesamtsystem geht in die Testsession. Alle Testfälle in Kapitel 7 sind manuelle Black-Box-Tests über die Web-Oberflächen – die Tester kennen den Quellcode nicht.

| Teststufe | Prüfgegenstand | Wer / Umgebung | Testfälle |
|---|---|---|---|
| Komponententest | Einzelne Funktionen: Kennzeichenprüfung, Preisfunktion, Servosteuerung | Shane & Andreas, DEV | nicht Teil dieses Konzepts |
| Integrationstest | M2M-Kommunikation Pico 2 → Pico 1 (Statusabfrage, Einfahrtsmeldung), Verhalten bei Timeout | Shane & Andreas, DEV/TEST | TC-05, TC-06, TC-13 |
| Systemtest | Gesamtes System gegen alle Akzeptanzkriterien inkl. Grenzwerte und Ausnahmefälle | Fachtester, TEST | TC-01 bis TC-15 |
| Abnahmetest | Eignung aus Sicht von Gast und Parkhausbetreiber; Entscheid Go/No-Go | Testmanager, Auftraggeber, TEST | TC-01 bis TC-07, TC-15 |

**Testarten und Testentwurf:** Die funktionalen Tests decken je Akzeptanzkriterium einen Positiv- und, wo sinnvoll, einen Negativfall ab. Die Testfälle entstehen mit Äquivalenzklassen (gültige und ungültige Kennzeichen, TC-08), Grenzwertanalyse (Tarifgrenzen bei 59/61 Minuten und 24 Stunden in TC-10, Kulanzzeit 14/16 Minuten in TC-11, letzter freier Platz in TC-09) und einer Entscheidungstabelle für die Ausfahrt. Die nicht-funktionalen Tests prüfen Reaktionszeit und Bedienbarkeit (TC-15) sowie die Robustheit bei Verbindungs- und Stromausfall (TC-13, TC-14).

Nach jedem Hotfix während der Session wird der betroffene Testfall als **Retest** wiederholt; sind mehrere Testfälle betroffen, werden alle Testfälle mit Priorität «Hoch» als **Regressionstest** erneut ausgeführt.

### Entscheidungstabelle Ausfahrt

| | R1 | R2 | R3 | R4 | R5 |
|---|---|---|---|---|---|
| Kennzeichen im System | nein | ja | ja | ja | ja |
| Gebühr bezahlt | – | nein | ja | ja | ja |
| Innerhalb Kulanzzeit | – | – | ja | nein | ja |
| Pico 1 erreichbar | ja | ja | ja | ja | nein |
| **Erwartete Reaktion** | zu | zu | öffnet | zu | zu |
| Geprüft durch | TC-07 | TC-05 | TC-06 | TC-11 | TC-13 |

---

## 4 Testorganisation (Wer testet?)

Um «Betriebsblindheit» auszuschliessen, setzen wir auf das Vier-Augen-Prinzip. Die Entwickler testen ihren Code nicht selbst in der finalen Abnahme. Für die Dauer der 90-minütigen Unterrichtsstunde werden folgende Rollen definiert:

| Rolle | Verantwortlichkeiten & Zuweisung |
|---|---|
| Entwickler / Test-Infrastruktur | Shane & Andreas: Aufbau der Hardware, Bereitstellung des WLANs, Initialisierung der Picos. Während der Tests agieren sie passiv im Hintergrund und stehen ausschliesslich für kritische Bugfixes (Hotfixes) zur Verfügung. |
| Testmanager | Delegiert an Mitschüler/in A: Leitet die Testsession, überwacht das Timeboxing (max. 90 Min.), klassifiziert auftretende Mängel und führt das offizielle Testprotokoll (Sign-off). Bedient die Admin-Seite, wenn ein Testfall Zeitstempel verlangt (TC-10, TC-11), und gibt nach einem Hotfix die Retests frei. |
| Fachtester (Black-Box) | Delegiert an Mitschüler/in B & C: Führen die Testfälle strikt nach Vorgabe (Kapitel 7) durch. Sie kennen den Quellcode nicht und prüfen das System rein über die Web-UIs aus der Perspektive eines Kunden bzw. Parkhausbetreibers. B bedient die Kamera-Sim-UI (Schranken), C die Kassen-UI; beide tragen das Ergebnis je Testfall in die Status-Spalte ein. |
| Auftraggeber | Lehrperson: Vertritt den Parkhausbetreiber, nimmt die Freigabeempfehlung des Testmanagers entgegen und entscheidet über Go/No-Go (Kap. 8). |

---

## 5 Testplanung (Wann wird getestet?)

### 5.1 Termine

«Tag X» ist die Unterrichtsstunde, in der die Testsession stattfindet. Die Vorbereitung liegt vollständig bei den Entwicklern, damit die 90 Minuten ausschliesslich zum Testen genutzt werden.

| Termin | Aufgabe | Wer |
|---|---|---|
| bis Tag X − 2 | Komponenten- und Integrationstests in DEV; TEST-Build mit Admin-Seite auf beide Picos laden | Shane, Andreas |
| Tag X − 1 | Testaufbau probeweise in Betrieb nehmen, Protokoll (Kap. 8) drucken, Mitschüler/innen A–C bestimmen | Shane, Andreas |
| Tag X (90 Min.) | Testsession gemäss Kap. 5.2 | Testgruppe |
| bis Tag X + 7 | Mängel beheben; Retests und nicht ausgeführte Testfälle in einer Folgesession nachholen | Shane, Andreas, Testmanager |
| Tag X + 7 | Präsentation der Resultate vor der Klasse, Abgabe des unterschriebenen Protokolls | alle |

### 5.2 Ablauf der Testsession (90 Minuten)

| Zeit | Inhalt | Wer |
|---|---|---|
| 00–10 Min. | Aufbau prüfen, Grundzustand G0 herstellen, Tester einweisen, Protokoll bereitlegen | Testmanager, Entwickler |
| 10–30 Min. | Modul 1–3: Kernablauf Einfahrt – Bezahlen – Ausfahrt (TC-01 bis TC-07) | Fachtester |
| 30–60 Min. | Modul 4: Grenzwerte und Ausnahmefälle (TC-08 bis TC-12) | Fachtester, Testmanager (Admin-Seite) |
| 60–75 Min. | Modul 5: Robustheit und nicht-funktionale Anforderungen (TC-13 bis TC-15) | Fachtester |
| 75–82 Min. | Retests nach Hotfixes, blockierte Testfälle nachholen; Restzeit: explorativer Test | Fachtester, Entwickler |
| 82–90 Min. | Auswertung, Mängelliste, Freigabeempfehlung und Unterschriften (Kap. 8) | Testmanager, alle |

Die reine Ausführungszeit der 15 Testfälle beträgt rund 58 Minuten. Die Differenz ist Reserve für Fehlersuche, Hotfixes und Retests. Reicht die Zeit nicht, werden zuerst alle Testfälle mit Priorität «Hoch» ausgeführt; die übrigen werden im Protokoll als «nicht ausgeführt» vermerkt und in einer Folgesession nachgeholt.

### 5.3 Eingangs-, Abbruch- und Endekriterien

| Kriterium | Bedingung |
|---|---|
| Start der Session | TEST-Build auf beiden Picos geladen, Komponenten- und Integrationstests der Entwickler fehlerfrei, Grundzustand G0 hergestellt, Rollen besetzt und Protokoll gedruckt. |
| Abbruch | Ein kritischer Mangel (Kap. 6) blockiert den Kernablauf und lässt sich nicht innert 10 Minuten durch einen Hotfix beheben, oder die Hardware fällt aus. Fortsetzung erst nach erfolgreichem Retest von TC-01 bis TC-06. |
| Ende / Freigabe | Alle Testfälle mit Priorität «Hoch» sind ausgeführt und bestanden, mindestens 80 % aller Testfälle sind bestanden (12 von 15), kein kritischer oder hoher Mangel ist offen und das Protokoll (Kap. 8) ist unterschrieben. |

---

## 6 Mängelmanagement und Fehlerklassen

Sollten während der Testausführung Abweichungen vom erwarteten Verhalten auftreten, werden diese vom Testmanager nach folgendem Schema klassifiziert:

| Klasse | Beschreibung | Massnahme |
|---|---|---|
| **Kritisch (Showstopper)** | Kernfunktionalität ist defekt (z. B. Picos stürzen ab, Schranke öffnet grundlos, Preisberechnung fehlerhaft). | Testabbruch, sofortiger Fix durch DEV. |
| **Hoch** | Wichtige Funktion eingeschränkt, aber Workaround vorhanden (z. B. UI lädt langsam, M2M-Request benötigt mehrere Versuche). | Fix vor der Freigabe, Retest in der Folgesession. |
| **Mittel** | Kleinere Fehler ohne Auswirkung auf die Geschäftslogik (z. B. Tippfehler im Web-UI, leicht ungenaue Schranken-Animation). | Fix nach der Session. |
| **Tief (Kosmetisch)** | Schönheitsfehler im CSS der Weboberfläche. | Sammeln, Behebung bei Gelegenheit. |

Jeder Mangel wird auf dem Protokollblatt (Kap. 8) mit einer laufenden Nummer, dem betroffenen Testfall, dem beobachteten Verhalten und der Klasse festgehalten; die Nummer wird zusätzlich in der Status-Spalte des Testfalls notiert. Ein «Go» für die fiktive Produktivsetzung wird nur erteilt, wenn keine kritischen oder hohen Fehler mehr offen sind.

---

## 7 Testfallbeschreibungen (Test Cases)

Die folgenden manuellen Tests wurden aus den definierten User Stories und Akzeptanzkriterien (Einfahrt, Preisberechnung, M2M-Validierung, Ausfahrt) abgeleitet; die Zuordnung zeigt Kapitel 1.3. Die Testfälle sind in der angegebenen Reihenfolge auszuführen, da einige aufeinander aufbauen.

**Status-Spalte:** Kästchen ankreuzen, wenn alle erwarteten Ergebnisse eingetreten sind; sonst die Nummer des Mangels eintragen. «Prio» bezeichnet die Priorität, «≈» die geschätzte Dauer.

### 7.1 Modul 1: Einfahrt und Registrierung

#### TC-01 – Einfahrt · Prio Hoch · ≈ 3 min

- **Pre-Condition:** Grundzustand G0 (Kap. 2.3). Tester B befindet sich auf der Kamera-Sim-UI (Pico 2).
- **Aktion:** Eingabe des Kennzeichens «ZH-123» in das Feld «Einfahrt» und Klick auf «Bestätigen»; Zeit bis zum Öffnen der Schranke stoppen. Danach die Admin-Seite (Pico 1) prüfen.
- **Erwartetes Ergebnis:**
  1. Die UI bestätigt die Erfassung: «Einfahrt registriert: ZH-123» mit Datum und Uhrzeit. **[v1.2]** Format: «Einfahrt registriert: ZH-123 (TT.MM.JJJJ, hh:mm Uhr)».
  2. Die Einfahrtsschranke (LED/Servo an Pico 2) öffnet sich innert 2 Sekunden für 5 Sekunden und schliesst wieder.
  3. Pico 2 hat die Einfahrt per HTTP an Pico 1 gemeldet: Die Admin-Seite zeigt ZH-123 mit Einfahrtszeit und Status «Offen»; freie Plätze: 2.
- **Status:** ☐

#### TC-02 – Doppelte Einfahrt · Prio Mittel · ≈ 2 min

- **Pre-Condition:** TC-01 erfolgreich.
- **Aktion:** Sofortige erneute Eingabe von «ZH-123» als Einfahrt (Fahrzeug ist bereits im System).
- **Erwartetes Ergebnis:** Das System erkennt das Duplikat. Fehlermeldung: «Fahrzeug bereits im Parkhaus». Schranke bleibt ZU. Die Admin-Seite zeigt weiterhin genau einen Eintrag ZH-123.
- **Status:** ☐

### 7.2 Modul 2: Kasse und Preisberechnung

#### TC-03 – Preis abfragen · Prio Hoch · ≈ 2 min

- **Pre-Condition:** «ZH-123» ist im System (seit ca. 2 Minuten).
- **Aktion:** Tester C öffnet die Kassen-UI (Pico 1) und gibt «ZH-123» ein, um den Preis abzufragen.
- **Erwartetes Ergebnis:** Das System zeigt die Einfahrtszeit, die exakte Aufenthaltsdauer (z. B. 0:02) und den berechneten Preis CHF 2.00 (Mindestgebühr) gut lesbar an. Status: «Offen».
- **Status:** ☐

#### TC-04 – Bezahlen (Karte) · Prio Hoch · ≈ 2 min

- **Pre-Condition:** Preis wird angezeigt (TC-03).
- **Aktion:** Tester C wählt die Zahlungsart «Karte» und klickt in der Kassen-UI auf den Button «Gebühr bezahlen».
- **Erwartetes Ergebnis:** UI zeigt Erfolgsmeldung: «Bezahlung erfolgreich – bitte innert 15 Minuten ausfahren». Der Status des Kennzeichens «ZH-123» ändert sich auf «Bezahlt»; die Admin-Seite zeigt Zahlungszeit, «Karte» und CHF 2.00.
- **Status:** ☐

### 7.3 Modul 3: Ausfahrt und M2M-Kommunikation

#### TC-05 – Ausfahrt ohne Zahlung · Prio Hoch · ≈ 3 min

- **Pre-Condition:** Fahrzeug «BE-999» ist eingefahren (wie TC-01), hat aber an der Kasse nicht bezahlt.
- **Aktion:** Tester B gibt in der Kamera-Sim-UI (Pico 2) das Kennzeichen «BE-999» für die Ausfahrt ein.
- **Erwartetes Ergebnis:** Pico 2 fragt Pico 1 an. Antwort ist «Nicht bezahlt». Fehlermeldung auf UI: «Bitte an Kasse bezahlen». Ausfahrtsschranke bleibt geschlossen.
- **Status:** ☐

#### TC-06 – Ausfahrt nach Zahlung · Prio Hoch · ≈ 3 min

- **Pre-Condition:** Fahrzeug «ZH-123» hat bezahlt (TC-04); die Zahlung liegt weniger als 15 Minuten zurück.
- **Aktion:** Tester B gibt «ZH-123» in der Kamera-Sim-UI für die Ausfahrt ein.
- **Erwartetes Ergebnis:** Pico 2 fragt Pico 1 an (M2M). Antwort ist positiv. Ausfahrtsschranke öffnet sich innert 2 Sekunden für 5 Sekunden. Kennzeichen wird aus dem System gelöscht (Admin-Seite: ZH-123 nicht mehr im Abschnitt «Im Parkhaus» aufgeführt, freie Plätze: 2). **[v1.2]** Im Abschnitt «Abgeschlossene Parkvorgänge» erscheint ZH-123 mit Ausfahrtszeit (Kap. 2.3 verlangt die Anzeige der Ausfahrtszeit).
- **Status:** ☐

#### TC-07 – Unbekanntes Kennzeichen · Prio Hoch · ≈ 2 min

- **Pre-Condition:** System im Leerlauf (nach TC-06).
- **Aktion:** Eingabe eines Fantasie-Kennzeichens («XX-000») bei der Ausfahrt, welches nie eingefahren ist (Edge Case). Danach dasselbe mit «ZH-123» (bereits ausgefahren).
- **Erwartetes Ergebnis:** System fängt den Fehler ab. Meldung beide Male: «Kennzeichen nicht gefunden». Schranke bleibt ZU. System stürzt nicht ab. **[v1.2]** «XX-000» ist formal ungültig (kein Kanton, führende Null); bei der *Ausfahrt* gilt trotzdem «Kennzeichen nicht gefunden» und nicht «Ungültiges Kennzeichen» – die Formatmeldung gilt nur bei der Einfahrt (TC-08).
- **Status:** ☐

### 7.4 Modul 4: Grenzwerte und Ausnahmefälle

#### TC-08 – Kennzeichen-Validierung · Prio Mittel · ≈ 6 min

- **Pre-Condition:** G0.

| Schritt | Aktion | Erwartetes Ergebnis |
|---|---|---|
| 1 | Ungültige Einfahrten eingeben: «ZH-», «ZH-1234567», «ZH-0123», «XX-123», «ZH123» und leeres Feld. | Jedes Mal Meldung «Ungültiges Kennzeichen»; Schranke bleibt ZU; kein Eintrag auf der Admin-Seite. |
| 2 | Sonderfälle eingeben: 60 × «A» sowie «`<b>ZH-1</b>`». | Abgewiesen wie in Schritt 1; der Text erscheint nicht fett (kein HTML); Pico 2 stürzt nicht ab. |
| 3 | Gültige Grenzfälle eingeben: «JU-1», «VD-999999», «ag-9999». | Alle drei werden registriert, die Schranke öffnet jeweils; gespeichert als JU-1, VD-999999 und AG-9999. |

- **Status:** ☐

#### TC-09 – Parkhaus voll · Prio Mittel · ≈ 5 min

- **Pre-Condition:** G0 (Kapazität 3). Kamera-Sim-UI in zwei Browser-Tabs geöffnet.

| Schritt | Aktion | Erwartetes Ergebnis |
|---|---|---|
| 1 | Einfahrten «FR-101», «FR-102» und «FR-103». | Die Schranke öffnet jeweils; Anzeige freie Plätze: 0. |
| 2 | Tab 1 neu laden. | Button «Bestätigen» der Einfahrt ist deaktiviert; Anzeige «Parkhaus voll». |
| 3 | In Tab 2 (nicht neu geladen) Einfahrt «FR-104» bestätigen. | Abgewiesen mit «Parkhaus voll»; Schranke bleibt ZU. |
| 4 | FR-101 an der Kasse bezahlen und ausfahren; Tab 1 neu laden; Einfahrt «FR-104». | Ausfahrt öffnet; «Bestätigen» ist wieder aktiv; FR-104 wird registriert, die Schranke öffnet. |

- **Status:** ☐

#### TC-10 – Tarifgrenzen · Prio Hoch · ≈ 8 min

- **Pre-Condition:** G0; Einfahrt «TG-500» registriert.
- **Aktion:** Für jede Spalte der Tabelle: auf der Admin-Seite die Einfahrt von TG-500 auf «vor n Minuten» setzen und innert 30 Sekunden in der Kassen-UI den Preis abfragen.
- **Erwartetes Ergebnis:** Parkdauer und Preis gemäss Tabelle. Die Grenzwerte liegen 1 Minute neben der Grenze, weil die Uhr während des Tests weiterläuft.

| n (Minuten) | 0 | 59 | 61 | 659 | 661 | 1439 | 1441 |
|---|---|---|---|---|---|---|---|
| Parkdauer | 0:00 | 0:59 | 1:01 | 10:59 | 11:01 | 23:59 | 24:01 |
| Preis (CHF) | 2.00 | 2.00 | 4.00 | 22.00 | 24.00 | 24.00 | 26.00 |

- **Status:** ☐

#### TC-11 – Kulanzzeit · Prio Hoch · ≈ 5 min

- **Pre-Condition:** G0; «SZ-710» und «SZ-711» eingefahren und an der Kasse bezahlt (je CHF 2.00).

| Schritt | Aktion | Erwartetes Ergebnis |
|---|---|---|
| 1 | Admin-Seite: Zahlung von SZ-710 auf «vor 14 Minuten» setzen; Ausfahrt SZ-710. | Schranke öffnet (Kulanzzeit eingehalten). |
| 2 | Zahlung von SZ-711 auf «vor 16 Minuten» setzen; Ausfahrt SZ-711. | Schranke bleibt ZU; Meldung «Kulanzzeit überschritten – Nachzahlung CHF 2.00». |
| 3 | SZ-711 an der Kasse abfragen und die Nachgebühr mit «Bargeld» bezahlen; erneut Ausfahrt SZ-711. | Kasse zeigt Nachgebühr CHF 2.00; nach der Zahlung öffnet die Ausfahrtsschranke. |

- **Status:** ☐

#### TC-12 – Ticket verloren · Prio Mittel · ≈ 4 min

- **Pre-Condition:** G0. «GL-4040» wurde nie registriert (Fahrzeug ohne gültiges «Ticket»).

| Schritt | Aktion | Erwartetes Ergebnis |
|---|---|---|
| 1 | In der Kassen-UI «GL-4040» abfragen. | Meldung «Kennzeichen nicht gefunden»; die Option «Ticket verloren» wird angeboten. |
| 2 | Option «Ticket verloren» wählen und mit «Bargeld» bezahlen. | Pauschale CHF 24.00; nach der Zahlung «Bezahlt – Ausfahrt bis hh:mm» (Zahlungszeit + 15 Minuten). |
| 3 | Innert 15 Minuten Ausfahrt «GL-4040». | Schranke öffnet. |

- **Status:** ☐

### 7.5 Modul 5: Robustheit und nicht-funktionale Anforderungen

#### TC-13 – Kasse offline · Prio Hoch · ≈ 5 min

- **Pre-Condition:** G0; «OW-1313» eingefahren und bezahlt.

| Schritt | Aktion | Erwartetes Ergebnis |
|---|---|---|
| 1 | Pico 1 von der Powerbank trennen. | Kassen-UI ist nicht mehr erreichbar. |
| 2 | Ausfahrt «OW-1313»; Zeit bis zur Meldung stoppen. | Nach höchstens 5 Sekunden Meldung «Kasse nicht erreichbar – bitte Personal rufen»; Schranke bleibt ZU. |
| 3 | Einfahrt «NE-2020». | Gleiche Meldung; keine Registrierung, Schranke bleibt ZU. |
| 4 | Pico 1 wieder anschliessen, ca. 15 s warten (WLAN), Admin-Seite öffnen und prüfen, dass die Uhrzeit stimmt (sonst «Uhrzeit übernehmen») **[v1.2]**, Einfahrt «NE-2020» wiederholen – ohne Pico 2 neu zu starten. | NE-2020 wird registriert und die Schranke öffnet; Pico 2 arbeitet ohne Neustart weiter. |

- **Status:** ☐

#### TC-14 – Neustart Pico 2 · Prio Mittel · ≈ 3 min

- **Pre-Condition:** G0.

| Schritt | Aktion | Erwartetes Ergebnis |
|---|---|---|
| 1 | Einfahrt «AI-900»; solange die Schranke offen ist, Pico 2 von der Powerbank trennen und nach 10 Sekunden wieder anschliessen. | Nach dem Aufstarten sind beide Schranken geschlossen. |
| 2 | **[v1.2]** ca. 20 s warten, bis Tablet und Pico 1 wieder im WLAN von Pico 2 sind; Kamera-Sim-UI neu laden; Ausfahrt «AI-900» (nicht bezahlt). | UI wieder erreichbar; Meldung «Bitte an Kasse bezahlen», Schranke bleibt ZU (Parkvorgang auf Pico 1 unverändert). |

- **Status:** ☐

#### TC-15 – Zeiten und UI · Prio Mittel · ≈ 5 min

- **Pre-Condition:** G0; Tablet und Smartphone im Test-WLAN.

| Schritt | Aktion | Erwartetes Ergebnis |
|---|---|---|
| 1 | Einfahrten «SG-321», «SG-322» und «SG-323»; jeweils die Zeit bis zum Öffnen stoppen. | Jedes Mal höchstens 2 Sekunden. |
| 2 | Kamera-Sim-UI, Kassen-UI und Admin-Seite je dreimal neu laden (Zeit stoppen). | Jede Seite ist nach höchstens 3 Sekunden bedienbar. |
| 3 | Kassen-UI auf dem Smartphone öffnen und «SG-321» abfragen. | Betrag ohne Zoomen gut lesbar; keine horizontale Scrollleiste; Bedienung per Touch möglich. |

- **Status:** ☐


---

## 8 Protokoll und Abnahme

Dieses Formular wird am Ende der 90-minütigen Testphase vom Testmanager ausgefüllt und dient als formelle Abnahme des Projekts durch die Testgruppe.

| | |
|---|---|
| Datum, Klasse | ________ |
| Testmanager | ________ |

**Zusammenfassung**

- ___ durchgeführte Testfälle von 15 · ___ erfolgreich (Passed) · ___ fehlgeschlagen (Failed) · ___ nicht ausgeführt
- Priorität «Hoch»: ___ bestanden von 9
- Offene Mängel: ___ kritisch · ___ hoch · ___ mittel · ___ tief

**Festgestellte Mängel (Nr., Testfall, Beobachtung, Klasse):**

| Nr. | Testfall | Beobachtung | Klasse |
|---|---|---|---|
| | | | |

**Freigabeempfehlung**

- ☐ **Freigegeben (Go):** Das System erfüllt alle Akzeptanzkriterien. Keine kritischen Fehler.
- ☐ **Abgelehnt (No-Go):** Behebung der Fehler und Retesting erforderlich.

| | |
|---|---|
| Ort, Datum | ________ |
| Unterschrift Testmanager | ________ |
| Unterschrift Tester 1 | ________ |
| Unterschrift Tester 2 | ________ |