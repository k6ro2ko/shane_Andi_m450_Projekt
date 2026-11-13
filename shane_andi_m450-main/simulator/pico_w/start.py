# Startet einen simulierten Pico W: unser main.py laeuft unveraendert, nur das was es auf dem PC
# nicht gibt (machine, network, time.ticks_ms, ...) wird hier nachgebaut.
#
#   python simulator/pico_w/start.py kasse
#   python simulator/pico_w/start.py schranke
#
# Normalerweise startet sim.py diese Prozesse, man muss das nicht von Hand machen.
import asyncio
import os
import runpy
import socket
import sys
import time
import traceback

from machine import melden

HIER = os.path.dirname(os.path.abspath(__file__))
PARKING = os.path.join(HIER, "..", "..", "parking")
ORDNER = {"kasse": "pico1_kasse", "schranke": "pico2_schranke"}

rolle = sys.argv[1]
port = int(os.environ.get("SIM_PORT", "8001" if rolle == "kasse" else "8002"))
host = os.environ.get("SIM_HOST", "127.0.0.1")
# Pico-IP -> Port auf diesem PC, z.B. "192.168.4.1=8001,192.168.4.2=8002"
adressen = {}
for eintrag in os.environ.get("SIM_ADRESSEN", "192.168.4.1=8001,192.168.4.2=8002").split(","):
    ip, _, p = eintrag.partition("=")
    adressen[ip] = int(p)

# Dateisystem des Picos: daten.json usw. landen in simulator/flash/<rolle>/
flash = os.path.join(HIER, "..", "flash", rolle)
os.makedirs(flash, exist_ok=True)
os.chdir(flash)

# Wie auf dem Pico liegen alle Dateien "flach" nebeneinander
sys.path[1:1] = [os.path.join(PARKING, ORDNER[rolle]), os.path.join(PARKING, "common")]

# --- MicroPython-Funktionen, die CPython nicht hat ---
_PERIODE = 1 << 30


def ticks_ms():
    return int(time.monotonic() * 1000) % _PERIODE


def ticks_add(t, delta):
    return (t + delta) % _PERIODE


def ticks_diff(a, b):
    return (a - b + _PERIODE // 2) % _PERIODE - _PERIODE // 2


time.ticks_ms = ticks_ms
time.ticks_add = ticks_add
time.ticks_diff = ticks_diff
time.sleep_ms = lambda ms: time.sleep(ms / 1000)
asyncio.sleep_ms = lambda ms: asyncio.sleep(ms / 1000)
sys.print_exception = lambda e, datei=None: traceback.print_exception(e, file=datei or sys.stdout)

# --- Netzwerk: Port 80 des Picos auf einen Port des PCs umlenken ---
_start_server = asyncio.start_server
_getaddrinfo = socket.getaddrinfo


async def start_server(callback, h, p, **optionen):
    if p == 80:
        h, p = host, port
    server = await _start_server(callback, h, p, **optionen)
    melden("bereit", p)
    return server


def getaddrinfo(h, p, *rest, **optionen):
    if p == 80 and h in adressen:
        h, p = "127.0.0.1", adressen[h]
    return _getaddrinfo(h, p, *rest, **optionen)


asyncio.start_server = start_server
socket.getaddrinfo = getaddrinfo

# Fuer die Zeitmessung im Steuerpult: melden, wann "Bestaetigen" gedrueckt wurde
if rolle == "schranke":
    from schranken_app import SchrankenApp

    def mit_meldung(name):
        original = getattr(SchrankenApp, name)

        def neu(self, eingabe):
            melden("bestaetigt", name)
            return original(self, eingabe)

        setattr(SchrankenApp, name, neu)

    mit_meldung("einfahrt")
    mit_meldung("ausfahrt")

print("MicroPython (simuliert) auf Pico W, %s, Port %d" % (rolle, port))
runpy.run_path(os.path.join(PARKING, ORDNER[rolle], "main.py"), run_name="__main__")
