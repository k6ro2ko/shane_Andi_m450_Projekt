# Änderungsprotokoll und Code-Review

Review und Überarbeitung des Projekts `shane_andi_m450-main` (Countdown-Firmware für Raspberry Pi Pico W, Arduino-Framework, PlatformIO).

---

## 1. Zusammenfassung

### Ausgangslage

| Bereich | Zustand vorher |
|---|---|
| Firmware Pico W | kompilierte |
| Firmware Arduino Uno/Nano/Mega | **kompilierte nicht** (Compilerfehler) |
| Tests | **prüften nichts** – nur Konstanten, die im Test selbst definiert waren |
| Tests ohne Board | **unmöglich** – nur auf Hardware lauffähig, dort scheiterte der Upload |
| Struktur | Logik, Hardware und Ausgabe vermischt in einer Datei; .NET-Projekt mit Build-Artefakten im Firmware-Ordner |
| Python-Anbindung | keine; Zustand liess sich nicht abfragen |
| Reproduzierbarkeit | Plattform ohne Version → jeder Rechner baut mit einer anderen Version |

### Ergebnis

| Prüfung | Ergebnis |
|---|---|
| `pio test -e native` (PC, ohne Board) | **30 / 30 Tests bestanden** |
| `pio run -e pico` | baut (RAM 26,4 %, Flash 14,1 %) |
| `pio run -e uno` / `nano` | baut (RAM 305 B von 2048 B, Flash 4,5 KB) |
| `pio run -e mega` | baut |
| Tests für Uno kompiliert (`pio test -e uno --without-uploading`) | baut |
| Logik mit `g++ -std=c++11 -Wall -Wextra -pedantic -Werror` | keine Warnungen |
| Gegenprobe: Original-Bugs absichtlich wieder eingebaut | Tests schlagen an (rot) → Tests sind wirksam |
| End-to-End: echte `main.cpp` auf dem PC simuliert + Python-Skript | kompletter Ablauf Start → Pause → Fortsetzen → Urgent → Alarm → Auto-Reset funktioniert |

> **Nicht geprüft:** auf echter Hardware (es war kein Board angeschlossen) und das .NET-Projekt (kein .NET-SDK vorhanden, Code wurde nur verschoben, nicht verändert). Checkliste für den Hardwaretest: siehe [Abschnitt 5](#5-offene-punkte-und-empfehlungen).

---

## 2. Befunde und Fixes

Sortiert nach Schweregrad. Jeder Punkt: **Problem → Warum es nicht ging → Fix.**

### 🔴 Kritisch

#### K1 – Firmware kompiliert auf Arduino Uno/Nano/Mega nicht

**Problem:** `src/main.cpp` (alt):

```cpp
struct Button {
  uint8_t pin;
  bool stablePressed = false;   // Standardwert direkt im struct
  ...
};
Button startButton{PIN_BTN_START};
```

**Warum es nicht ging:** Ein `struct` mit Standardwerten an den Membern darf erst ab **C++14** mit `{…}` initialisiert werden. Der AVR-Compiler für Uno/Nano/Mega arbeitet mit **C++11**. Ergebnis:

```text
src/main.cpp:35:33: error: no matching function for call to 'Button::Button(<brace-enclosed initializer list>)'
```

Auf dem Pico fiel das nicht auf, weil dessen Compiler C++17 kann. Das Projekt war also nur auf genau einem Board lauffähig.

**Fix:** Alle Klassen haben jetzt einen Konstruktor (`Debouncer(uint32_t delayMs)`), der gesamte Code ist C++11-kompatibel. Geprüft mit `-std=c++11 -pedantic -Werror` und echten Builds für `uno`, `nano`, `mega`.

---

#### K2 – Die Tests haben nichts getestet

**Problem:** `test/test_countdown/test_main.cpp` (alt):

```cpp
constexpr unsigned long START_SECONDS = 60;        // im Test selbst definiert
...
TEST_ASSERT_EQUAL_UINT32(60, START_SECONDS);       // prüft 60 == 60

unsigned long remainingSeconds = 0;
remainingSeconds = START_SECONDS;
TEST_ASSERT_EQUAL_UINT32(START_SECONDS, remainingSeconds);  // prüft x = y; x == y
```

**Warum es nicht ging:** Die Tests haben eigene Kopien der Konstanten angelegt und dann geprüft, dass diese Kopien ihren eigenen Wert haben. Mit `test_build_src = no` wurde der echte Code nicht einmal mitkompiliert. Ein Test, der **nie fehlschlagen kann**, ist kein Test. Jeder Bug in `main.cpp` wäre durchgekommen.

**Fix:** Die Logik liegt jetzt in `lib/countdown/` (siehe K3) und wird von **30 Tests in 4 Gruppen** direkt geprüft – inklusive Randfällen (Prellen, Pause mitten in einer Sekunde, `millis()`-Überlauf, Taster beim Einschalten gedrückt). Die Wirksamkeit wurde geprüft, indem die alten Bugs testweise wieder eingebaut wurden: Die Tests schlagen dann an.

---

#### K3 – Tests nur mit Board möglich, Logik nicht vom Gerät trennbar

**Problem:** Alles lag in `main.cpp`: Zustandsmaschine, Entprellung, Blinklogik, `digitalRead`, `Serial`, `millis()` – ineinander verschachtelt.

**Warum es nicht ging:**

- Die Logik konnte nur zusammen mit `Arduino.h` kompiliert werden → **Testen nur auf Hardware**.
- Auf der Hardware scheiterte der Test-Upload unter Windows (WinUSB-Treiber, siehe altes README: *„aktuell brechen die Tests vorher beim Upload ab“*). Es gab also **keine einzige ausgeführte Prüfung**.
- Jede Erweiterung (Motoren) hätte die Datei weiter aufgebläht.

**Fix:** Aufteilung in Schichten:

| Schicht | Ort | Abhängigkeiten |
|---|---|---|
| Logik | `lib/countdown/` (`Countdown`, `Debouncer`, `StatusLed`, `Protocol`) | nur `<stdint.h>` |
| Konfiguration | `include/config.h` | Board-Erkennung |
| Hardware | `src/main.cpp` | `Arduino.h` |

Die Logik bekommt Zeit und Taster-Zustand **als Parameter** (`update(bool pressed, uint32_t nowMs)`), statt selbst `millis()`/`digitalRead()` aufzurufen. Dadurch läuft sie auf jedem Board und auf dem PC. Neues Environment `native` in `platformio.ini`: `pio test -e native` braucht kein Board.

---

### 🟠 Hoch

#### H1 – Jede Pause hat die Restzeit verlängert

**Problem:** Beim Fortsetzen wurde `lastTickMillis = now` gesetzt.

**Warum es falsch war:** Pausiert man nach 0,7 s einer Sekunde, beginnt nach dem Fortsetzen wieder eine volle Sekunde. Die angebrochenen 0,7 s gehen verloren. Bei häufigem Pausieren läuft der Countdown pro Pause bis zu 1 s zu lange.

**Fix:** Beim Pausieren wird die bereits vergangene Zeit der laufenden Sekunde gespeichert (`pausedElapsedMs_`) und beim Fortsetzen verrechnet. Test: `test_pause_keeps_started_second`.

---

#### H2 – Fortsetzen in der Urgent-Phase lieferte falschen Zustand

**Problem:** Fortsetzen setzte immer `Counting`, auch wenn nur noch z. B. 5 s übrig waren.

**Warum es falsch war:** Bis zum nächsten Tick (bis zu 1 s) blinkte die LED im falschen Muster, und eine Statusabfrage hätte `COUNTING` statt `URGENT` gemeldet.

**Fix:** `runningState()` bestimmt beim Starten und Fortsetzen anhand der Restzeit, ob `Counting` oder `Urgent` richtig ist. Test: `test_resume_in_urgent_phase_stays_urgent`.

---

#### H3 – Beim Einschalten gedrückter Taster startete den Countdown

**Problem:** Die Entprellung startete immer mit „nicht gedrückt“.

**Warum es falsch war:** Hält man beim Einschalten/Reset den Taster (oder ist er falsch verdrahtet und dauerhaft auf GND), wurde nach 30 ms ein „Druck“ erkannt und der Countdown startete ungewollt.

**Fix:** `Debouncer::begin()` übernimmt in `setup()` den tatsächlichen Anfangszustand. Test: `test_pressed_at_boot_does_not_trigger`.

---

#### H4 – Pins fest im Code, keine Board-Unterscheidung

**Problem:** `PIN_LED_EXT = 14`, `PIN_BTN_START = 15`, `PIN_BTN_RESET = 16` fest in `main.cpp`.

**Warum es nicht ging:** Das sind Pico-GPIO-Nummern. Auf einem Uno sind 14–16 die Analog-Pins A0–A2 – das funktioniert zwar zufällig, ist aber verwirrend und belegt Pins, die man oft für Sensoren braucht. Für ein anderes Board musste man den Code ändern.

**Fix:** `include/config.h` erkennt das Board (`ARDUINO_ARCH_RP2040` / `ARDUINO_ARCH_AVR`) und setzt passende Standard-Pins. Beim Arduino bleiben die PWM-Pins für Motoren frei. Jeder Wert ist per `build_flags` in `platformio.ini` überschreibbar. Bei einem unbekannten Board bricht der Build mit einer klaren Meldung ab, statt still falsche Pins zu verwenden.

---

#### H5 – Build nicht reproduzierbar

**Problem:** `platform = https://github.com/maxgerhardt/platform-raspberrypi.git` ohne Version.

**Warum es ein Problem war:** PlatformIO lädt dann immer den neuesten Stand des Repositories. Rechner A (Schule, vor zwei Monaten installiert) und Rechner B (heute installiert) bauen mit unterschiedlichen Versionen – „bei mir geht’s“ wird zum Dauerproblem, und eine Änderung im fremden Repository kann den Build über Nacht kaputt machen.

**Fix:** Alle Plattformen sind fest versioniert:

```ini
platform = https://github.com/maxgerhardt/platform-raspberrypi.git#5d4561a05e3b212660ac6fdd3fbfb328d1988aa1
platform = platformio/atmelavr@5.3.0
platform = platformio/native@1.2.1
```

---

#### H6 – Befehl während des Alarms wurde kommentarlos verschluckt

**Problem:** `S` während des Alarms wurde ignoriert, ohne Rückmeldung.

**Warum es ein Problem war:** Gefunden im End-to-End-Test mit dem Python-Skript: Das Skript sendet `S` und wartet auf eine Antwort, die nie kommt → Timeout. Für ein steuerndes Programm ist „keine Antwort“ nicht von „Verbindung kaputt“ unterscheidbar.

**Fix:** Neues Ereignis `CountdownEvent::Ignored`, die Firmware antwortet mit `[FSM] Ignoriert: Alarm aktiv, nur Reset moeglich.` Test: `test_toggle_ignored_during_alarm`.

---

### 🟡 Mittel

#### M1 – Onboard-LED wurde im Alarm tausende Male pro Sekunde geschrieben

**Problem:** Im Alarm-Zustand rief `updateSignaling()` in **jedem** `loop()`-Durchlauf `digitalWrite()` auf beide LEDs auf.

**Warum es ein Problem war:** Beim Pico W hängt die Onboard-LED nicht am RP2040, sondern am WLAN-Chip (CYW43). Jeder Schreibzugriff ist eine Übertragung über den Bus zu diesem Chip. Das bremst `loop()` unnötig aus – und damit Taster und Serial.

**Fix:** LEDs werden nur noch geschrieben, wenn sich der Zustand ändert (`updateLeds()` in `main.cpp`).

---

#### M2 – Startmeldung ging beim Pico verloren

**Problem:** `Serial.println(...)` direkt nach `Serial.begin()`.

**Warum es ein Problem war:** Pico (und andere Boards mit nativem USB) brauchen nach dem Start einen Moment, bis der PC den Port verbunden hat. Was vorher gesendet wird, ist weg.

**Fix:** `setup()` wartet bis zu 2 s auf die Verbindung (`SERIAL_WAIT_MS`), danach geht es auch ohne PC weiter. Beim Uno ist `Serial` sofort bereit, dort entsteht keine Wartezeit.

---

#### M3 – `unsigned long` für Zeiten

**Problem:** Zeiten waren `unsigned long`.

**Warum es ein Problem war:** Auf Arduino/Pico ist `unsigned long` 32 Bit, auf einem 64-Bit-PC aber 64 Bit. Dieselbe Logik verhält sich auf dem PC (Tests) dann anders als auf dem Board – insbesondere beim `millis()`-Überlauf nach ~49 Tagen, der auf dem PC nie auftreten würde.

**Fix:** Überall `uint32_t` – gleiche Breite auf jedem System. Test: `test_millis_overflow`.

---

#### M4 – Keine maschinenlesbare Schnittstelle für Python

**Problem:** Es gab nur `S` und `R`. Man konnte den Zustand nicht abfragen, und unbekannte Zeichen wurden stillschweigend ignoriert.

**Warum es ein Problem war:** Die Anforderung „soll auch mit Python funktionieren“ war damit nicht erfüllbar – ein Python-Programm wusste nie, in welchem Zustand das Board ist.

**Fix:**

- Neue Befehle `?` (Status) und `H` (Hilfe), Fehlermeldung bei unbekannten Zeichen.
- Feste, parsbare Statuszeile: `[STATUS] state=COUNTING remaining=42`.
- Neues Werkzeug `tools/countdown_control.py` (Windows/Linux/macOS): findet das Board automatisch, berücksichtigt den Auto-Reset des Uno beim Port-Öffnen, wartet gezielt auf die passende Antwort, als Kommandozeile **und** als importierbares Modul nutzbar.
- Protokoll in `lib/countdown/Protocol.h` dokumentiert und getestet.

---

#### M5 – Falsche Reihenfolge der Meldungen am Alarmende

**Problem:** Am Alarmende rief der Code `resetCountdown()` auf (gibt *„Reset auf Startwert“* aus) und danach *„Alarm beendet“*.

**Warum es ein Problem war:** Im Log sah es so aus, als hätte jemand Reset gedrückt. Zudem war Ausgabe fest in der Logik verdrahtet.

**Fix:** Die Logik gibt nichts mehr aus, sondern liefert ein Ereignis (`CountdownEvent::AlarmEnded`). `main.cpp` entscheidet, was ausgegeben wird.

---

#### M6 – Texte belegten RAM auf dem Uno

**Problem:** `Serial.println("…")` legt jeden Text auf AVR-Boards zusätzlich im RAM ab.

**Warum es ein Problem ist:** Der Uno hat nur 2 KB RAM. Mit jeder weiteren Meldung (Motoren!) wird es enger, und volles RAM führt zu zufälligen Abstürzen ohne Fehlermeldung.

**Fix:** Alle Texte mit `F("…")` – sie bleiben im Flash. Aktuell 305 Byte RAM belegt (15 %).

---

### 🔵 Struktur und Projektpflege

#### S1 – .NET-Projekt mitten im Firmware-Ordner, mit Build-Artefakten

**Problem:** `Program.cs`, `WebApplication1.csproj`, `appsettings*.json`, `launchSettings.json` lagen im Root neben `platformio.ini`; dazu `bin/` und `obj/` mit kompilierten Dateien (`WebApplication1.exe`, `apphost.exe`, `.dll`, `.pdb`).

**Warum es ein Problem war:**

- `obj/project.assets.json` enthielt absolute Pfade eines einzelnen Rechners (`C:\Users\Shane\Desktop\Codeing\shane_andi_m450\…`). Auf jedem anderen Rechner sind diese Dateien falsch.
- Build-Artefakte gehören nicht in ein Repository (werden bei jedem Build neu erzeugt, blähen das Repo auf, erzeugen Merge-Konflikte). Die `.gitignore` schloss sie nicht aus.
- `launchSettings.json` lag im Root. `dotnet run` sucht sie aber **nur** in `Properties/` → die Datei wurde ignoriert, die konfigurierten Ports (5097/7058) galten nicht.
- Zwei völlig verschiedene Projekte im selben Root sind verwirrend.

**Fix:**

- .NET-Projekt nach `webapp/` verschoben, `launchSettings.json` nach `webapp/Properties/`. Inhalt unverändert.
- `bin/`, `obj/` und der PlatformIO-Build-Ordner `.pio/` gelöscht (werden beim Build automatisch neu erzeugt).
- `.gitignore` um .NET- und Python-Artefakte ergänzt.

Starten jetzt mit `cd webapp` und `dotnet run`.

---

#### S2 – README beschrieb einen Zustand, der nicht stimmte

**Problem:** Das alte README sprach von „automatisierten Konfigurations- und Hardwaretests“ – es gab weder das eine noch das andere (siehe K2).

**Fix:** README kurz gehalten und auf `ANLEITUNG.md` (Bedienung) und dieses Dokument verwiesen.

---

#### S3 – Kleinere Punkte

- `platformio.ini`: gemeinsame Einstellungen in `[env]` zusammengefasst, damit jedes neue Board sie automatisch erbt.
- Environments für `uno`, `nano`, `mega` und `native` ergänzt; `pico` bleibt Standard.
- Kommentare im Code auf Deutsch und auf das Nötige beschränkt; Quellcode bleibt ASCII (keine Umlaute in `.cpp`/`.h`), damit es keine Encoding-Probleme zwischen Windows und Linux gibt.
- Bei der Überarbeitung aufgefallen: Der Pico-Core definiert selbst ein Makro `BOARD_NAME`. Eigene Makros heissen deshalb eindeutig (`APP_BOARD_NAME`, `PIN_…`, `COUNTDOWN_…`).

---

## 3. Datei-Übersicht

| Datei | Status |
|---|---|
| `platformio.ini` | überarbeitet (Versionen fix, 5 Environments) |
| `src/main.cpp` | neu geschrieben, nur noch Hardware-Schicht |
| `include/config.h` | **neu** – Pins und Zeiten pro Board |
| `lib/countdown/Countdown.h/.cpp` | **neu** – Zustandsmaschine (aus `main.cpp` herausgelöst, Bugs H1, H2, H6 behoben) |
| `lib/countdown/Debouncer.h/.cpp` | **neu** – Entprellung (aus `main.cpp`, Bug H3 behoben) |
| `lib/countdown/StatusLed.h/.cpp` | **neu** – Blinkmuster (aus `main.cpp`) |
| `lib/countdown/Protocol.h/.cpp` | **neu** – serielle Befehle |
| `test/test_countdown/test_main.cpp` | **gelöscht** (wirkungslos, siehe K2) |
| `test/test_countdown/test_countdown.cpp` | **neu** – 16 Tests |
| `test/test_debouncer/test_debouncer.cpp` | **neu** – 6 Tests |
| `test/test_status_led/test_status_led.cpp` | **neu** – 4 Tests |
| `test/test_protocol/test_protocol.cpp` | **neu** – 4 Tests |
| `tools/countdown_control.py`, `tools/requirements.txt` | **neu** – Python-Steuerung |
| `Program.cs`, `*.csproj`, `appsettings*.json` | nach `webapp/` verschoben |
| `launchSettings.json` | nach `webapp/Properties/` verschoben |
| `bin/`, `obj/`, `.pio/` | gelöscht (Build-Artefakte) |
| `.gitignore` | ergänzt |
| `README.md` | überarbeitet |
| `ANLEITUNG.md`, `AENDERUNGEN.md` | **neu** |

---

## 4. Wie wurde geprüft?

1. **Ausgangslage gemessen:** Original für Pico gebaut (✓) und für Uno gebaut (✗, Fehler K1).
2. **Unit-Tests auf dem PC:** `pio test -e native` → 30/30.
3. **Gegenprobe (Mutationstest):** Die Original-Logik für Fortsetzen und Entprellung testweise wieder eingesetzt → 3 Tests schlagen an. Damit ist belegt, dass die Tests die alten Fehler finden.
4. **C++11-Strenge:** Alle Dateien in `lib/` mit `g++ -std=c++11 -Wall -Wextra -pedantic -Werror` → keine Warnung.
5. **Firmware-Builds:** `pico`, `uno`, `nano`, `mega` → alle erfolgreich, ohne Warnungen aus Projektcode. Tests zusätzlich für `uno` kompiliert.
6. **End-to-End ohne Hardware:** Die echte `src/main.cpp` wurde mit einem minimalen Arduino-Ersatz auf dem PC kompiliert, `Serial` auf einen virtuellen Port umgeleitet und mit `tools/countdown_control.py` gesteuert. Durchgespielt: Status → Start → Pause (Restzeit bleibt stehen) → Fortsetzen → Ticks bis 0 → Alarm → `S` wird mit Meldung abgelehnt → Auto-Reset nach Alarmdauer → Status `STANDBY`. Dabei wurden H6 und ein Ausgabepuffer-Problem im Python-Monitor gefunden und behoben.

---

## 5. Offene Punkte und Empfehlungen

1. **Hardwaretest durchführen** (konnte hier nicht gemacht werden):
   - [ ] `pio run -e <board> -t upload`, Serial Monitor zeigt Startmeldung und `[STATUS] state=STANDBY remaining=60`
   - [ ] LED blinkt langsam
   - [ ] Start-Taster: Countdown läuft, LED blinkt schneller; nochmal drücken → Pause
   - [ ] Taster gedrückt halten → nur **ein** Ereignis
   - [ ] Reset-Taster → zurück auf 60
   - [ ] Bei 6 s: sehr schnelles Blinken; bei 0: LED dauerhaft an, nach 5 s Standby
   - [ ] `python tools/countdown_control.py status` liefert den Zustand
   - [ ] `pio test -e <board>` auf dem Board
2. **Standard-Board festlegen:** `default_envs = pico` wurde beibehalten. Wenn ihr hauptsächlich einen Arduino nutzt, auf `uno`/`nano` umstellen.
3. **.NET-Projekt prüfen:** `cd webapp` und `dotnet build`. Falls die Web-App nicht zum Auftrag gehört, kann `webapp/` ganz entfernt werden.
4. **Motoren:** Vorgehen und Regeln stehen in `ANLEITUNG.md`, Abschnitt 12. Für Befehle mit Werten muss das Protokoll auf zeilenbasierte Befehle erweitert werden.
5. **Versionskontrolle:** Der Ordner ist aktuell kein Git-Repository. Empfehlung: `git init`, alles committen, und die Tests (`pio test -e native`) vor jedem Commit laufen lassen – optional automatisch per GitHub Actions.
