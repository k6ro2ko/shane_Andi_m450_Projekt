# Prompt für neuen Chat: Schranken-Pico erreicht die Kasse nicht

> **Vor dem Start:** Den Quellcode **beider** Picos (Arduino/C++-Firmware, vermutlich bei Andreas) in den Projektordner legen, beide Picos per USB bereithalten und den Test-Router einschalten. Dann alles ab der Linie unten in den neuen Chat kopieren.

---

Kontext:
Wir sind Shane und Andreas (Informatiker 3. Lehrjahr). Projekt: Smart-Parking-System mit zwei Raspberry Pi Pico W. Pico 1 = Kasse (Webserver, Preisberechnung, Admin-Seite, feste IP 192.168.4.1), Pico 2 = Schranken + Kamera-Sim-UI (feste IP 192.168.4.2). Kommunikation M2M per HTTP über einen eigenen WLAN-Router ohne Internet. Das Testkonzept steht in `shane_andi_m450-main/docs/Testkonzept_und_Auftrag.md` (v1.2), das Testprotokoll-Gerüst in `docs/testprotokoll.md`.

Problem:
Auf den Picos läuft unsere eigene **Arduino/C++-Firmware** (arduino-pico-Core, USB-Kennung `2e8a:f00a`), nicht MicroPython. Der Quellcode liegt jetzt im Projektordner: [PFAD EINTRAGEN]. Der Schranken-Pico (Pico 2) gibt am seriellen Monitor (115200 Baud) in einer Endlosschleife Folgendes aus:

```
[Schranken] WLAN getrennt bzw. Kasse stumm – neuer Verbindungsversuch
[Schranken] WLAN wieder verbunden
[Schranken] /api/status: Versuch 1 fehlgeschlagen (Code -1)
[Schranken] WLAN-Link verloren
```

Pico 2 kommt also ins WLAN, erreicht aber `http://192.168.4.1/api/status` nicht (HTTPClient-Code -1 = keine Verbindung). Danach trennt er das WLAN und verbindet neu. Die Testsession braucht ein funktionierendes System.

Bisherige Vermutungen (noch nicht geprüft):
1. Pico 1 (Kasse) läuft nicht, stürzt ab oder hat nicht die IP 192.168.4.1.
2. Der Router belegt selbst 192.168.4.1 (IP-Konflikt) oder vergibt .1/.2 per DHCP.
3. Die Firmware von Pico 2 behandelt «Kasse antwortet nicht» als WLAN-Abbruch und baut das WLAN jedes Mal neu auf. Das ist falsch, denn laut Testkonzept (TC-13, NF2) soll Pico 2 in diesem Fall nur «Kasse nicht erreichbar – bitte Personal rufen» melden, die Schranke zu lassen und ohne Neustart weiterarbeiten, sobald die Kasse wieder da ist.
4. SSID, Passwort, IP, Gateway oder Subnetz sind auf den beiden Picos unterschiedlich konfiguriert.

Aufgabe:
1. Lies den Quellcode beider Picos vollständig, besonders WLAN-Setup, feste IP, Webserver von Pico 1, HTTP-Client von Pico 2 und die Reconnect-Logik.
2. Diagnose mit echten Daten, nicht raten:
   - Serielle Ausgabe von Pico 1 und Pico 2 mitlesen (z. B. mit Python/pyserial; `python -m mpremote connect list` zeigt die COM-Ports).
   - Prüfen, ob Pico 1 die IP 192.168.4.1 hat und sein Webserver läuft (Log, `ping 192.168.4.1`, Browser vom Laptop im Test-WLAN).
   - Router-IP und DHCP-Bereich mit mir prüfen (ich lese sie dir vom Router ab).
3. Erkläre mir die Ursache kurz und verständlich, bevor du änderst.
4. Fixe die Ursache im C++-Code. Mindestens:
   - Eine stumme Kasse darf **nicht** zum WLAN-Neuaufbau führen. Neu verbinden nur, wenn `WiFi.status() != WL_CONNECTED`.
   - HTTP-Timeout so, dass die Meldung «Kasse nicht erreichbar – bitte Personal rufen» nach höchstens 5 s erscheint und die Schranke zu bleibt (fail-safe).
   - Feste IPs, SSID und Passwort an **einer** Stelle pro Pico (Config) und auf beiden Picos gleich.
5. Bauen und flashen (PlatformIO oder Arduino IDE, je nachdem, was im Projekt verwendet wird), dann zusammen mit mir prüfen: Einfahrt ZH-123 funktioniert, und wenn Pico 1 ausgesteckt ist, kommt die Meldung und Pico 2 läuft nach dem Wiedereinstecken ohne Neustart weiter (TC-13).
6. Halte jede Änderung in `docs/aenderungen.md` fest (Abschnitt B, ab Ä-10): was falsch war, was geändert wurde, welche Dateien und welche Testfälle als Retest bzw. Regressionstest betroffen sind.

Regeln:
- Erfinde keine Testergebnisse. Die Testfälle führen wir selbst auf der Hardware durch. Fehlende Resultate bleiben [OFFEN].
- Überschreibe die Firmware nicht mit einer anderen Sprache oder Version, ohne mich vorher zu fragen.
- Code einfach halten, wenige Kommentare, so wie Lernende im 3. Lehrjahr ihn schreiben würden.
- Sprache Deutsch, Schweizer Schreibweise («ss» statt «ß»).

Hinweis: Im Ordner `shane_andi_m450-main/parking/` liegt eine getestete MicroPython-Ersatzversion des ganzen Systems (inkl. Admin-Seite). Nutze sie nur als Notlösung, falls sich die C++-Firmware nicht rechtzeitig reparieren lässt, und nur nach meiner Zustimmung.
