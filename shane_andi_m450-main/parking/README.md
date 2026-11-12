# Smart-Parking-System – Firmware (MicroPython, Raspberry Pi Pico W)

| Pico | Adresse | Inhalt |
|---|---|---|
| Pico 1 – Kasse | http://192.168.4.1/ (Admin: `/admin`) | `common/*` + `pico1_kasse/*` |
| Pico 2 – Schranken + Kamera-Sim-UI | http://192.168.4.2/ | `common/*` + `pico2_schranke/*` |

## Schnellweg: ein Befehl pro Pico

Pico per USB-**Datenkabel** einstecken, dann im Ordner `parking/`:

```
pip install mpremote
python flash_pico.py kasse    --ssid "WLAN-NAME" --passwort "PASSWORT"
python flash_pico.py schranke --ssid "WLAN-NAME" --passwort "PASSWORT"
python flash_pico.py log      (nur Ausgabe mitlesen)
```

Das Skript erkennt den Pico und versetzt ihn bei einer anderen Firmware (z. B. Arduino) automatisch in den Flash-Modus. Es spielt MicroPython aus `firmware/` auf (die bisherige Firmware wird **überschrieben**), lädt die passenden Dateien samt WLAN-Daten hoch und zeigt danach 40 s lang die Ausgabe. Findet es kein Laufwerk: Pico ausstecken, BOOTSEL halten, einstecken, nochmals starten.

## Flashen von Hand

1. MicroPython-Firmware **für den Pico W** (nicht für den Pico ohne W!) installieren: BOOTSEL gedrückt halten, einstecken, `.uf2` auf das Laufwerk kopieren. Empfohlen: v1.22 oder neuer.
2. In `pico1_kasse/config.py` **und** `pico2_schranke/config.py` WLAN-Name und Passwort frei wählen (Passwort 8–63 Zeichen) und in beiden Configs gleich eintragen. Pico 2 spannt dieses WLAN auf.
3. Dateien **flach** ins Wurzelverzeichnis des jeweiligen Picos kopieren (ohne Unterordner):
   - Thonny: Datei öffnen → «Speichern unter» → «Raspberry Pi Pico» → gleicher Dateiname.
   - oder mit mpremote (`pip install mpremote`), Port anpassen:
     ```
     cd parking
     mpremote connect COM5 cp common/*.py pico1_kasse/*.py :
     mpremote connect COM6 cp common/*.py pico2_schranke/*.py :
     ```
4. Beide Picos neu starten (ausstecken/einstecken). `main.py` startet automatisch. Onboard-LED dauernd an = WLAN verbunden, blinkt = sucht WLAN.
5. Admin-Seite einmal öffnen: Die Uhrzeit wird automatisch vom Browser übernommen.

## Netzwerk (ohne Router)

- **Pico 2 spannt das Test-WLAN selbst auf** (Access Point, WPA2, ohne Internet), Pico 1 verbindet sich damit. Tablets und Smartphones der Tester verbinden sich ebenfalls mit diesem WLAN.
- Darum Pico 2 und nicht Pico 1: Bei TC-13 wird Pico 1 ausgesteckt. Wäre Pico 1 der Access Point, wäre auch die Schranken-UI weg.
- Pico 2 zuerst einschalten. Pico 1 verbindet sich innert ca. 3–10 s, auch nach einem Neustart von Pico 2 automatisch wieder.
- Auf den Test-Geräten **mobile Daten ausschalten**: Das WLAN hat kein Internet, und manche Handys schicken Anfragen sonst über das Mobilnetz.
- Mit Router statt Access Point: in `pico2_schranke/config.py` `WLAN_MODUS = "sta"` setzen und in beiden Configs Gateway/DNS auf die Router-IP. Der Router darf dann nicht .1 oder .2 belegen.

## Pins Pico 2 (anpassbar in `pico2_schranke/config.py`)

| Schranke | Servo SG90 (Signal) | LED rot (zu) | LED grün (offen) |
|---|---|---|---|
| Einfahrt | GP15 | GP16 | GP17 |
| Ausfahrt | GP14 | GP18 | GP19 |

Servo: rot an VBUS (5 V), braun an GND, orange an GPIO. LEDs je mit Vorwiderstand (220–330 Ω) gegen GND. Nicht vorhandene Teile in der Config auf `None` setzen.

## Tests auf dem PC

```
pip install pytest
python -m pytest tests
```
