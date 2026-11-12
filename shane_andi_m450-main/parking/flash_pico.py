# Spielt MicroPython und unsere Firmware auf einen Pico W.
#
#   python flash_pico.py kasse    --ssid NAME --passwort PW
#   python flash_pico.py schranke --ssid NAME --passwort PW
#   python flash_pico.py log                     (nur Ausgabe mitlesen)
#
# Optionen: --port COM6, --ohne-firmware (MicroPython nicht neu flashen), --trocken (nichts am Pico aendern)
import argparse
import glob
import os
import re
import shutil
import string
import subprocess
import sys
import tempfile
import time

import serial
from serial.tools import list_ports

HIER = os.path.dirname(os.path.abspath(__file__))
PID_MICROPYTHON = 0x0005
ORDNER = {"kasse": "pico1_kasse", "schranke": "pico2_schranke"}


def picos():
    return [p for p in list_ports.comports() if p.vid == 0x2E8A]


def finde_pico(port=None):
    for p in picos():
        if port is None or p.device.upper() == port.upper():
            return p
    return None


def finde_laufwerk():
    for buchstabe in string.ascii_uppercase[3:]:
        if os.path.exists(buchstabe + ":\\INFO_UF2.TXT"):
            return buchstabe + ":\\"
    for pfad in glob.glob("/media/*/RPI-RP2") + glob.glob("/Volumes/RPI-RP2"):
        return pfad
    return None


def warte(bedingung, sekunden, text):
    print(text, end="", flush=True)
    ende = time.time() + sekunden
    while time.time() < ende:
        ergebnis = bedingung()
        if ergebnis:
            print(" ok")
            return ergebnis
        print(".", end="", flush=True)
        time.sleep(0.5)
    print(" Zeit abgelaufen")
    return None


def micropython_flashen(port):
    uf2 = sorted(glob.glob(os.path.join(HIER, "firmware", "RPI_PICO_W-*.uf2")))[-1]
    laufwerk = finde_laufwerk()
    if laufwerk is None and port is not None:
        print("Pico in den Flash-Modus versetzen (1200-Baud-Reset)")
        try:
            s = serial.Serial(port, 1200)
            s.dtr = False
            s.close()
        except Exception:
            pass
        laufwerk = warte(finde_laufwerk, 20, "Warte auf Laufwerk RPI-RP2")
    if laufwerk is None:
        sys.exit("Kein Flash-Laufwerk. Pico ausstecken, BOOTSEL gedrueckt halten, einstecken, Skript nochmals starten.")
    print("Kopiere", os.path.basename(uf2), "nach", laufwerk)
    shutil.copy(uf2, laufwerk)
    p = warte(lambda: next((x for x in picos() if x.pid == PID_MICROPYTHON), None), 40, "Warte auf MicroPython")
    if p is None:
        sys.exit("MicroPython startet nicht. Pico neu einstecken und mit --ohne-firmware weitermachen.")
    time.sleep(2)
    return p.device


def dateien_vorbereiten(rolle, ssid, passwort):
    ziel = tempfile.mkdtemp(prefix="pico_")
    for pfad in glob.glob(os.path.join(HIER, "common", "*.py")) + glob.glob(os.path.join(HIER, ORDNER[rolle], "*.py")):
        shutil.copy(pfad, ziel)
    config = os.path.join(ziel, "config.py")
    text = open(config, encoding="utf-8").read()
    text = re.sub(r'WLAN_SSID = ".*"', lambda m: "WLAN_SSID = %r" % ssid, text)
    text = re.sub(r'WLAN_PASSWORT = ".*"', lambda m: "WLAN_PASSWORT = %r" % passwort, text)
    open(config, "w", encoding="utf-8").write(text)
    return ziel, sorted(os.listdir(ziel))


def mpremote(port, *befehl):
    r = subprocess.run([sys.executable, "-m", "mpremote", "connect", port] + list(befehl),
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout, r.stderr)
        sys.exit("mpremote-Fehler")
    return r.stdout


def hochladen(port, ordner, dateien):
    print("Lade %d Dateien hoch: %s" % (len(dateien), ", ".join(dateien)))
    mpremote(port, "cp", *[os.path.join(ordner, d) for d in dateien], ":")
    auf_pico = mpremote(port, "exec", "import os; print(os.listdir())")
    fehlt = [d for d in dateien if d not in auf_pico]
    if fehlt:
        sys.exit("Fehlt auf dem Pico: %s" % fehlt)
    print("Alle Dateien auf dem Pico.")
    mpremote(port, "reset")


def log_lesen(port, sekunden=40):
    p = warte(lambda: finde_pico(port), 15, "Warte auf Pico")
    if p is None:
        sys.exit("Kein Pico gefunden.")
    print("--- Ausgabe von %s (%d s) ---" % (p.device, sekunden))
    s = serial.Serial(p.device, 115200, timeout=0.5)
    ende = time.time() + sekunden
    while time.time() < ende:
        zeile = s.readline()
        if zeile:
            print(zeile.decode(errors="replace").rstrip())
    s.close()


def main():
    a = argparse.ArgumentParser()
    a.add_argument("rolle", choices=["kasse", "schranke", "log"])
    a.add_argument("--ssid")
    a.add_argument("--passwort")
    a.add_argument("--port")
    a.add_argument("--ohne-firmware", action="store_true")
    a.add_argument("--trocken", action="store_true")
    args = a.parse_args()

    if args.rolle == "log":
        log_lesen(args.port)
        return
    if not args.ssid or args.passwort is None:
        sys.exit("--ssid und --passwort angeben (fuer beide Picos gleich)")
    if not 8 <= len(args.passwort) <= 63:
        sys.exit("Das WLAN-Passwort muss 8 bis 63 Zeichen lang sein (WPA2).")

    ordner, dateien = dateien_vorbereiten(args.rolle, args.ssid, args.passwort)
    if args.trocken:
        print("Trockenlauf, vorbereitet in", ordner, ":", dateien)
        return

    p = finde_pico(args.port)
    if p is None and finde_laufwerk() is None:
        sys.exit("Kein Pico gefunden. Einstecken (USB-Datenkabel!) und nochmals starten.")
    port = p.device if p else None
    if p is not None and p.pid == PID_MICROPYTHON:
        print("%s: MicroPython laeuft bereits." % port)
    elif args.ohne_firmware:
        sys.exit("Auf dem Pico laeuft kein MicroPython – ohne --ohne-firmware starten.")
    else:
        print("ACHTUNG: Die bisherige Firmware auf dem Pico wird ueberschrieben.")
        port = micropython_flashen(port)

    try:
        hochladen(port, ordner, dateien)
    finally:
        shutil.rmtree(ordner, ignore_errors=True)
    log_lesen(port)


if __name__ == "__main__":
    main()
