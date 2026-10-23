# Countdown-Firmware (M450)

Countdown mit Tastern, Status-LEDs und serieller Steuerung – in C++ für Raspberry Pi Pico / Pico W und Arduino Uno / Nano / Mega, steuerbar per Python vom PC aus.

- **[ANLEITUNG.md](ANLEITUNG.md)** – Aufbau, Verdrahtung, Bauen, Hochladen, Testen, Python-Steuerung, Erweitern (Motoren)
- **[AENDERUNGEN.md](AENDERUNGEN.md)** – Code-Review: was geändert wurde und warum

## Schnellstart

```bash
pio test -e native
```

Tests auf dem PC, ohne Board.

```bash
pio run -e uno -t upload
```

Firmware bauen und hochladen (`uno`, `nano`, `mega` oder `pico`).

```bash
pip install -r tools/requirements.txt
```

```bash
python tools/countdown_control.py status
```

Board per Python abfragen.

## Struktur

| Ordner | Inhalt |
|---|---|
| `lib/countdown/` | Logik ohne Hardware-Abhängigkeit (getestet) |
| `src/main.cpp` | Hardware-Schicht (Pins, Serial) |
| `include/config.h` | Pins und Zeiten pro Board |
| `test/` | Unit-Tests (Unity) |
| `tools/` | Python-Steuerung |
| `webapp/` | separate ASP.NET-Anwendung |
