#!/usr/bin/env python3
"""Steuert die Countdown-Firmware vom PC aus ueber USB-Serial.

Funktioniert unter Windows, Linux und macOS mit Pico, Uno, Nano und Mega.

Beispiele:
    python tools/countdown_control.py ports            # angeschlossene Boards anzeigen
    python tools/countdown_control.py status           # Zustand abfragen
    python tools/countdown_control.py toggle           # Start / Pause / Fortsetzen
    python tools/countdown_control.py reset            # Reset auf Startwert
    python tools/countdown_control.py monitor          # Ausgabe mitlesen (Ctrl+C beendet)
    python tools/countdown_control.py shell            # interaktiv Befehle senden
    python tools/countdown_control.py --port COM5 status

Als Modul in eigenem Python-Code:
    from countdown_control import CountdownDevice
    with CountdownDevice() as device:
        device.toggle()
        print(device.status())
"""

import argparse
import re
import sys
import threading
import time

try:
    import serial
    from serial.tools import list_ports
except ImportError:
    sys.exit("pyserial fehlt. Installieren mit:  pip install -r tools/requirements.txt")

BAUD = 115200
STATUS_PATTERN = re.compile(r"\[STATUS\] state=(\w+) remaining=(\d+)")

# USB-Hersteller-IDs typischer Boards und USB-Serial-Wandler
KNOWN_VENDOR_IDS = {
    0x2E8A: "Raspberry Pi",
    0x2341: "Arduino",
    0x2A03: "Arduino",
    0x1A86: "CH340 (Arduino-Klon)",
    0x0403: "FTDI",
    0x10C4: "CP210x",
}


def find_boards():
    """Liefert alle seriellen Ports, die nach einem bekannten Board aussehen."""
    return [p for p in list_ports.comports() if p.vid in KNOWN_VENDOR_IDS]


def find_port():
    boards = find_boards()
    if not boards:
        raise RuntimeError("Kein Board gefunden. Ist es angeschlossen? Sonst --port angeben.")
    if len(boards) > 1:
        names = ", ".join(p.device for p in boards)
        raise RuntimeError(f"Mehrere Boards gefunden ({names}). Bitte --port angeben.")
    return boards[0].device


class CountdownDevice:
    """Verbindung zur Firmware. Befehle siehe lib/countdown/Protocol.h."""

    def __init__(self, port=None, baud=BAUD, boot_wait=2.0):
        self.port = port or find_port()
        self._serial = serial.Serial(self.port, baud, timeout=0.1)
        # Ein Uno/Nano startet beim Oeffnen des Ports neu. Warten, bis er bereit ist,
        # und die Startmeldungen verwerfen.
        time.sleep(boot_wait)
        self._serial.reset_input_buffer()

    def close(self):
        self._serial.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def send(self, command):
        self._serial.write(f"{command}\n".encode("ascii"))
        self._serial.flush()

    def read_line(self, timeout=1.0):
        """Liest eine Zeile oder liefert None, wenn innerhalb von `timeout` nichts kam."""
        deadline = time.monotonic() + timeout
        buffer = b""
        while time.monotonic() < deadline:
            buffer += self._serial.readline()
            if buffer.endswith(b"\n"):
                return buffer.decode("ascii", errors="replace").strip()
        return buffer.decode("ascii", errors="replace").strip() or None

    def _wait_for(self, prefix, timeout):
        """Liest Zeilen, bis eine mit `prefix` beginnt. Andere Zeilen (z.B. Ticks) werden uebersprungen."""
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            line = self.read_line(timeout=deadline - time.monotonic())
            if line and line.startswith(prefix):
                return line
        raise TimeoutError(f"Keine Antwort '{prefix}...' vom Board erhalten.")

    def status(self, timeout=2.0):
        """Liefert (zustand, restzeit_sekunden), z.B. ("COUNTING", 42)."""
        self.send("?")
        match = STATUS_PATTERN.search(self._wait_for("[STATUS]", timeout))
        return match.group(1), int(match.group(2))

    def toggle(self, timeout=2.0):
        """Start / Pause / Fortsetzen. Liefert die Antwortzeile der Firmware."""
        self.send("S")
        return self._wait_for("[FSM]", timeout)

    def reset(self, timeout=2.0):
        self.send("R")
        return self._wait_for("[FSM]", timeout)


def cmd_ports(_args):
    boards = find_boards()
    if not boards:
        print("Kein bekanntes Board gefunden. Alle seriellen Ports:")
        for p in list_ports.comports():
            print(f"  {p.device:20} {p.description}")
        return
    for p in boards:
        print(f"  {p.device:20} {KNOWN_VENDOR_IDS[p.vid]:22} {p.description}")


def cmd_status(args):
    with CountdownDevice(args.port, args.baud) as device:
        state, remaining = device.status()
        print(f"Zustand: {state}, Restzeit: {remaining}s")


def cmd_toggle(args):
    with CountdownDevice(args.port, args.baud) as device:
        print(device.toggle())


def cmd_reset(args):
    with CountdownDevice(args.port, args.baud) as device:
        print(device.reset())


def cmd_monitor(args):
    with CountdownDevice(args.port, args.baud, boot_wait=0) as device:
        print(f"Verbunden mit {device.port}. Ctrl+C beendet.")
        while True:
            line = device.read_line(timeout=0.5)
            if line:
                print(line, flush=True)


def cmd_shell(args):
    with CountdownDevice(args.port, args.baud, boot_wait=0) as device:
        print(f"Verbunden mit {device.port}. Befehle: S, R, ?, H. 'q' beendet.")
        stop = threading.Event()

        def reader():
            while not stop.is_set():
                line = device.read_line(timeout=0.2)
                if line:
                    print(line, flush=True)

        thread = threading.Thread(target=reader, daemon=True)
        thread.start()
        try:
            for command in sys.stdin:
                command = command.strip()
                if command.lower() == "q":
                    break
                if command:
                    device.send(command)
        finally:
            stop.set()
            thread.join(timeout=1)


def main():
    parser = argparse.ArgumentParser(description="Countdown-Firmware ueber USB steuern.")
    parser.add_argument("--port", help="z.B. COM5 oder /dev/ttyACM0 (Standard: automatisch)")
    parser.add_argument("--baud", type=int, default=BAUD)
    sub = parser.add_subparsers(dest="command", required=True)
    for name, func, help_text in (
        ("ports", cmd_ports, "angeschlossene Boards anzeigen"),
        ("status", cmd_status, "Zustand und Restzeit abfragen"),
        ("toggle", cmd_toggle, "Start / Pause / Fortsetzen"),
        ("reset", cmd_reset, "auf Startwert zuruecksetzen"),
        ("monitor", cmd_monitor, "serielle Ausgabe mitlesen"),
        ("shell", cmd_shell, "interaktiv Befehle senden"),
    ):
        sub.add_parser(name, help=help_text).set_defaults(func=func)

    args = parser.parse_args()
    try:
        args.func(args)
    except KeyboardInterrupt:
        pass
    except (RuntimeError, TimeoutError, serial.SerialException) as error:
        sys.exit(f"Fehler: {error}")


if __name__ == "__main__":
    main()
