# Anleitung – Countdown-Firmware (C++ / PlatformIO)

Diese Anleitung beschreibt, wie das Projekt aufgebaut ist, wie man es baut, testet, auf ein Board lädt, per Python steuert und **wie man es erweitern muss**, damit es sauber und geräteunabhängig bleibt.

---

## 1. Was macht das Projekt?

Ein Countdown (Standard: 60 s) läuft auf einem Mikrocontroller:

- **Start-Taster** (oder Befehl `S`): Start → Pause → Fortsetzen → Pause …
- **Reset-Taster** (oder Befehl `R`): zurück auf den Startwert
- **LEDs** (extern + Onboard) zeigen den Zustand über das Blinkmuster
- In den letzten 10 % der Zeit wird der Zustand `URGENT`, bei 0 kommt `ALARM` (5 s), danach automatisch zurück zu `STANDBY`
- Über USB-Serial kann ein PC (z. B. ein **Python-Skript**) den Countdown steuern und abfragen

Die Firmware ist in **C++** geschrieben und läuft auf **Raspberry Pi Pico / Pico W, Arduino Uno, Nano und Mega**. Die Logik kann auf dem PC **ohne Board** getestet werden.

---

## 2. Projektstruktur

```text
shane_andi_m450-main/
├── platformio.ini          Build-Konfiguration: ein Environment pro Board + "native" für PC-Tests
├── include/
│   └── config.h            Pins pro Board und Zeitwerte (zentral, überschreibbar)
├── lib/
│   └── countdown/          REINE LOGIK – kein Arduino.h, läuft überall
│       ├── Countdown.h/.cpp    Zustandsmaschine (Standby/Counting/Paused/Urgent/Alarm)
│       ├── Debouncer.h/.cpp    Taster-Entprellung
│       ├── StatusLed.h/.cpp    Blinkmuster je Zustand
│       └── Protocol.h/.cpp     serielle Befehle (S, R, ?, H)
├── src/
│   └── main.cpp            HARDWARE-SCHICHT – Pins, Serial, millis(); verbindet alles
├── test/                   Unit-Tests (Unity), laufen auf PC und Board
│   ├── test_countdown/
│   ├── test_debouncer/
│   ├── test_protocol/
│   └── test_status_led/
├── tools/
│   ├── countdown_control.py   Python-Steuerung vom PC aus
│   └── requirements.txt
├── webapp/                 separate ASP.NET-Anwendung (hat mit der Firmware nichts zu tun)
├── ANLEITUNG.md            diese Datei
└── AENDERUNGEN.md          was geändert wurde und warum
```

### Die wichtigste Regel des Projekts

| Ordner | Darf enthalten | Darf **nicht** enthalten |
|---|---|---|
| `lib/…` | Logik, Berechnungen, Zustände, Zeitvergleiche | `#include <Arduino.h>`, `digitalRead`, `Serial`, `millis()`, `delay()` |
| `src/main.cpp` | Pins lesen/schreiben, Serial, `millis()`, Aufruf der Logik | komplizierte Logik (gehört nach `lib/` und wird dort getestet) |
| `include/config.h` | Pin-Nummern, Zeiten, Baudrate | Code |

**Warum?** Nur Code ohne Hardware-Abhängigkeit kann auf jedem Board laufen und auf dem PC getestet werden. Die Zeit (`nowMs`) und Taster-Zustände werden der Logik deshalb **als Parameter übergeben**, statt dass sie selbst `millis()` oder `digitalRead()` aufruft.

---

## 3. Voraussetzungen

| Was | Wofür | Installation |
|---|---|---|
| **VS Code + PlatformIO IDE** (Extension) | bauen, hochladen, testen | In VS Code: Extensions → „PlatformIO IDE“ |
| oder **PlatformIO Core** (Kommandozeile) | dasselbe ohne VS Code | `pip install platformio` |
| **Git** im `PATH` | lädt die Pico-Plattform | https://git-scm.com |
| **C++-Compiler** (g++) | nur für PC-Tests (`native`) | Linux: `sudo apt install g++` · macOS: `xcode-select --install` · Windows: [MSYS2](https://www.msys2.org) → `pacman -S mingw-w64-ucrt-x86_64-gcc`, dann `C:\msys64\ucrt64\bin` in den `PATH` |
| **Python 3.8+** | Python-Steuerung | https://python.org |

> Es wird **keine** Arduino IDE und keine Arduino-CLI gebraucht. PlatformIO lädt den passenden Compiler für jedes Board beim ersten Build automatisch herunter (beim Pico einige hundert MB, das dauert einmalig ein paar Minuten).

**Linux:** Damit der Benutzer auf den USB-Port darf:

```bash
sudo usermod -aG dialout $USER
```

Danach ab- und wieder anmelden. Für Uploads zusätzlich die [PlatformIO-udev-Regeln](https://docs.platformio.org/en/latest/core/installation/udev-rules.html) installieren.

Alle folgenden Befehle werden im Projektordner ausgeführt (in VS Code: *PlatformIO → New Terminal*). `pio` und `platformio` sind derselbe Befehl.

---

## 4. Board auswählen

Jedes Board ist ein **Environment** in `platformio.ini`. Man wählt es mit `-e <name>`:

| Environment | Board | Hinweis |
|---|---|---|
| `pico` | Raspberry Pi Pico **W** | Standard, wenn man kein `-e` angibt. Für den normalen Pico (ohne W) in `platformio.ini` `board = rpipico` setzen. |
| `uno` | Arduino Uno | |
| `nano` | Arduino Nano | Ältere Klone: `board = nanoatmega328` |
| `mega` | Arduino Mega 2560 | |
| `native` | **PC** | nur für Tests, kein Board nötig |

In VS Code kann das Environment unten in der blauen Statusleiste gewählt werden (*Default (shane_andi_m450-main)* anklicken).

**Wenn ihr hauptsächlich einen Arduino verwendet**, in `platformio.ini` `default_envs = uno` (bzw. `nano`/`mega`) setzen. Dann kann man `-e` weglassen.

---

## 5. Verdrahtung

Taster werden **zwischen Pin und GND** angeschlossen (kein Widerstand nötig, der interne Pull-Up ist aktiv). Die externe LED braucht einen **Vorwiderstand (220–330 Ω)** gegen GND.

| Funktion | Pico / Pico W | Uno / Nano / Mega |
|---|---|---|
| Externe LED (+ Widerstand → GND) | GP14 (Pin 19) | D7 |
| Start-Taster → GND | GP15 (Pin 20) | D2 |
| Reset-Taster → GND | GP16 (Pin 21) | D4 |
| Onboard-LED | eingebaut | eingebaut (D13) |

Beim Arduino bleiben die PWM-Pins **3, 5, 6, 9, 10, 11** absichtlich frei – die braucht ihr später für Motortreiber.

Andere Pins? Siehe [Abschnitt 10](#10-konfiguration-anpassen-ohne-code-zu-ändern).

---

## 6. Bauen und Hochladen

```bash
pio run -e uno
```

baut die Firmware für den Uno (ohne Board möglich – gut, um Compilerfehler zu finden).

```bash
pio run -e uno -t upload
```

baut und lädt hoch. Für den Pico entsprechend `-e pico`.

```bash
pio device monitor
```

öffnet den seriellen Monitor (115200 Baud). Beenden mit `Ctrl+C`.

In VS Code geht alles auch über die Symbole in der Statusleiste: ✓ (Build), → (Upload), 🔌 (Serial Monitor).

### Pico: erstes Hochladen

1. BOOTSEL-Taste gedrückt halten, Pico per USB anschliessen, loslassen.
2. `pio run -e pico -t upload`
3. Danach erscheint der Pico als eigener serieller Port. Weitere Uploads funktionieren meist ohne BOOTSEL.

---

## 7. Tests

### Auf dem PC (empfohlen, kein Board nötig)

```bash
pio test -e native
```

Erwartete Ausgabe am Ende:

```text
================= 30 test cases: 30 succeeded =================
```

Nur eine Testgruppe ausführen:

```bash
pio test -e native -f test_countdown
```

### Auf dem Board

Dieselben Tests laufen auch direkt auf dem Mikrocontroller (PlatformIO lädt dafür ein Testprogramm hoch, danach muss die normale Firmware wieder hochgeladen werden):

```bash
pio test -e uno
```

### Regel

**Jede Änderung an `lib/` braucht einen Test in `test/`.** Vor jedem Commit:

```bash
pio test -e native
pio run -e pico -e uno
```

Beides muss grün sein. Der Uno-Build ist wichtig, weil der AVR-Compiler strenger ist (nur C++11) – was dort baut, baut fast überall.

---

## 8. Bedienung

### Zustände und LED-Muster

| Zustand | Bedeutung | LED |
|---|---|---|
| `STANDBY` | wartet auf Start | blinkt langsam (1 s) |
| `COUNTING` | zählt herunter | blinkt (0,5 s) |
| `PAUSED` | angehalten | blinkt schnell (0,2 s) |
| `URGENT` | letzte 10 % der Zeit | blinkt sehr schnell (0,1 s) |
| `ALARM` | 0 erreicht, dauert 5 s | leuchtet dauerhaft |

### Serielle Befehle

Ein Zeichen genügt, Gross-/Kleinschreibung egal, Zeilenumbrüche werden ignoriert.

| Befehl | Wirkung | Antwort (Beispiel) |
|---|---|---|
| `S` | Start / Pause / Fortsetzen | `[FSM] Gestartet.` |
| `R` | Reset auf Startwert | `[FSM] Reset auf Startwert.` |
| `?` | Status abfragen | `[STATUS] state=COUNTING remaining=42` |
| `H` | Hilfe | `[HELP] S = Start/Pause/Fortsetzen, …` |

Weitere Ausgaben der Firmware: `[COUNTDOWN] Restzeit: 41s`, `[ALARM] …`, `[ERROR] Unbekannter Befehl …`. Jede Zeile beginnt mit einem Präfix in eckigen Klammern, damit Programme sie einfach auswerten können.

---

## 9. Steuerung mit Python

Die Firmware ist C++, gesteuert werden kann sie vom PC aus mit Python.

### Einmalig installieren

```bash
pip install -r tools/requirements.txt
```

(Windows, falls `pip` nicht gefunden wird: `py -m pip install -r tools/requirements.txt`)

### Kommandozeile

```bash
python tools/countdown_control.py ports
```

zeigt angeschlossene Boards. Weitere Befehle:

| Befehl | Wirkung |
|---|---|
| `python tools/countdown_control.py status` | Zustand und Restzeit |
| `python tools/countdown_control.py toggle` | Start / Pause / Fortsetzen |
| `python tools/countdown_control.py reset` | Reset |
| `python tools/countdown_control.py monitor` | Ausgabe live mitlesen |
| `python tools/countdown_control.py shell` | interaktiv Befehle tippen (`q` beendet) |

Der Port wird automatisch gefunden. Bei mehreren Boards: `--port COM5` (Windows) bzw. `--port /dev/ttyACM0` (Linux) bzw. `--port /dev/cu.usbmodem1101` (macOS).

> **Wichtig:** Der serielle Port kann nur von **einem** Programm gleichzeitig geöffnet sein. Vorher den Serial Monitor in VS Code schliessen.
>
> Ein Uno/Nano startet beim Öffnen des Ports neu. Das Skript wartet deshalb 2 s, bevor es Befehle sendet.

### In eigenem Python-Code

```python
import sys
sys.path.insert(0, "tools")
from countdown_control import CountdownDevice

with CountdownDevice() as device:          # oder CountdownDevice("COM5")
    print(device.toggle())                 # "[FSM] Gestartet."
    state, remaining = device.status()     # ("COUNTING", 59)
    print(state, remaining)
```

---

## 10. Konfiguration anpassen (ohne Code zu ändern)

Alle Werte in `include/config.h` können pro Board in `platformio.ini` überschrieben werden:

```ini
[env:uno]
platform = platformio/atmelavr@5.3.0
board = uno
framework = arduino
build_flags =
    -D PIN_LED_EXTERNAL=8
    -D COUNTDOWN_START_SECONDS=30
```

| Makro | Standard | Bedeutung |
|---|---|---|
| `PIN_LED_EXTERNAL` | 14 (Pico) / 7 (AVR) | externe LED |
| `PIN_BUTTON_START` | 15 / 2 | Start-Taster |
| `PIN_BUTTON_RESET` | 16 / 4 | Reset-Taster |
| `PIN_LED_ONBOARD` | `LED_BUILTIN` | Onboard-LED |
| `COUNTDOWN_START_SECONDS` | 60 | Startwert |
| `COUNTDOWN_ALARM_DURATION_MS` | 5000 | Alarmdauer |
| `BUTTON_DEBOUNCE_MS` | 30 | Entprellzeit |
| `SERIAL_BAUD` | 115200 | Baudrate (dann auch `monitor_speed` und `--baud` im Python-Skript anpassen) |

---

## 11. Ein neues Board hinzufügen

1. Board-ID suchen: `pio boards uno` oder https://docs.platformio.org/en/latest/boards/
2. In `platformio.ini` ein Environment anlegen:

   ```ini
   [env:esp32]
   platform = espressif32
   board = esp32dev
   framework = arduino
   build_flags =
       -D PIN_LED_EXTERNAL=2
       -D PIN_BUTTON_START=4
       -D PIN_BUTTON_RESET=5
   ```

3. `pio run -e esp32` – wenn Pins fehlen, sagt `config.h` mit einer klaren Fehlermeldung, welche.
4. Version der Plattform festschreiben (`platform = espressif32@<version>`), sobald es läuft.

`lib/` und `src/` müssen dafür **nicht** geändert werden.

---

## 12. Motoren hinzufügen – so muss es gemacht werden

Die Motorsteuerung ist noch nicht eingebaut. Damit sie sauber und testbar wird, nach demselben Muster wie der Countdown vorgehen:

```text
lib/motor/MotorController.h/.cpp   Logik: Sollwert, Rampe, Richtung, Grenzen  → ohne Arduino.h, mit Tests
src/MotorDriver.h/.cpp             Hardware: analogWrite / digitalWrite auf die Treiber-Pins
include/config.h                   Pins des Motortreibers (PIN_MOTOR_PWM, PIN_MOTOR_DIR, …)
test/test_motor/                   Tests für MotorController
```

**Beispiel für die Aufteilung:**

```cpp
// lib/motor/MotorController.h  – reine Logik
class MotorController {
 public:
  void setTarget(int16_t speed);          // -255 … 255
  int16_t update(uint32_t nowMs);         // liefert aktuelle Geschwindigkeit (mit Rampe)
};

// src/main.cpp  – nur Hardware
const int16_t speed = motor.update(now);
analogWrite(PIN_MOTOR_PWM, abs(speed));
digitalWrite(PIN_MOTOR_DIR, speed >= 0 ? HIGH : LOW);
```

**Hardware-Regeln (wichtig, sonst geht etwas kaputt):**

- Einen Motor **nie direkt** an einen Pin anschliessen – immer über einen **Motortreiber** (z. B. L298N, TB6612FNG, DRV8833) bzw. Servo/Schrittmotor-Treiber.
- Motor bekommt eine **eigene Stromversorgung**. **GND von Board und Motorversorgung verbinden.**
- Der Pico arbeitet mit **3,3 V**, der Uno mit **5 V** – Treiber wählen, der mit der Logikspannung des Boards umgehen kann.
- Für Geschwindigkeit PWM-fähige Pins verwenden (Uno: 3, 5, 6, 9, 10, 11; Pico: alle GPIO).

**Software-Regeln:**

- **Kein `delay()`** in `loop()` – sonst reagieren Taster und Serial nicht mehr. Zeiten immer über `now - start >= dauer` prüfen (wie in `Countdown.cpp`).
- Für Befehle mit Werten (z. B. „Motor auf 120“) reicht das 1-Zeichen-Protokoll nicht mehr. Dann `Protocol` auf zeilenbasierte Befehle erweitern (z. B. `M 120\n`) und die Erweiterung in `test/test_protocol` testen. Das Python-Skript bekommt eine passende Methode (`device.send("M 120")`).

---

## 13. Regeln für sauberen Code in diesem Projekt

1. **Nur C++11** in `lib/` und `src/` (AVR-Compiler). Kein `<vector>`, `<string>`, `<algorithm>`, `<cstdint>` – stattdessen `<stdint.h>`.
2. **`uint32_t` für Zeiten**, nie `int` oder `long`. Zeitvergleich immer als `now - start >= dauer` (funktioniert auch beim `millis()`-Überlauf nach 49 Tagen).
3. **Kein `delay()`** ausser in `setup()`.
4. **Keine Hardware in `lib/`.**
5. **Strings mit `F("…")`** in `Serial.print` – spart RAM auf dem Uno (nur 2 KB).
6. **Eigene Makros mit eindeutigem Namen** (`PIN_…`, `COUNTDOWN_…`), damit sie nicht mit Namen der Board-Pakete kollidieren.
7. Quellcode nur **ASCII** (keine Umlaute in `.cpp`/`.h`) – vermeidet Encoding-Probleme zwischen Windows/Linux/macOS.
8. Vor jedem Commit: `pio test -e native` und `pio run -e pico -e uno`.

---

## 14. Fehlerbehebung

| Problem | Lösung |
|---|---|
| `No accessible RP2040/RP2350 devices in BOOTSEL mode` (Windows) | WinUSB-Treiber fehlt. Pico mit gedrückter BOOTSEL-Taste anschliessen, mit [Zadig](https://zadig.akeo.ie) für das Gerät „RP2 Boot“ den Treiber **WinUSB** installieren. |
| Upload findet den Port nicht | Serial Monitor / Python-Skript schliessen. Port prüfen mit `pio device list`. **COM3/COM4 als „Bluetooth“** sind nicht das Board. |
| `Permission denied: /dev/ttyACM0` (Linux) | Siehe Abschnitt 3 (`dialout`-Gruppe). |
| `pio test -e native` meldet, `g++`/`gcc` nicht gefunden | C++-Compiler installieren (Abschnitt 3), Terminal neu öffnen. |
| Keine Ausgabe im Serial Monitor | Baudrate 115200? Beim Pico nach dem Upload 1–2 s warten, dann `?` senden. |
| Python: `Kein Board gefunden` | Board angeschlossen? `python tools/countdown_control.py ports` – sonst `--port` angeben. |
| Python: `Mehrere Boards gefunden` | `--port` angeben. |
| Python: `Keine Antwort … vom Board` | Richtige Firmware hochgeladen? Anderes Programm hat den Port offen? |
| Erster Pico-Build dauert sehr lange | Normal, die Toolchain wird einmalig heruntergeladen. |
| Taster löst nicht aus | Taster muss zwischen Pin und **GND** liegen (nicht 3,3 V / 5 V). |
