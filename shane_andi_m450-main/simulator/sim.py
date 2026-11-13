# Simulator: zwei Pico W auf dem PC. Jeder Pico laeuft als eigener Prozess mit seinem
# unveraenderten main.py (siehe pico_w/start.py), dieses Skript ist das Steuerpult daneben.
#
#   python simulator/sim.py          nur auf diesem PC
#   python simulator/sim.py --neu    gespeicherte Parkvorgaenge loeschen
#   python simulator/sim.py --lan    auch fuer Tablets/Handys im gleichen Netz
#
# Steuerpult: http://localhost:8000  Kasse: http://localhost:8001  Kamera-Sim: http://localhost:8002
import argparse
import asyncio
import json
import os
import runpy
import subprocess
import sys
import time

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HIER, "..", "parking", "common"))
import webutil as w

PORT_PULT, PORT_KASSE, PORT_SCHRANKE = 8000, 8001, 8002
FLASH = os.path.join(HIER, "flash")
AP_DATEI = os.path.join(FLASH, "ap.json")
NEUSTART_S = 10

cfg = runpy.run_path(os.path.join(HIER, "..", "parking", "pico2_schranke", "config.py"))
ereignisse = []


def uhr():
    t = time.time()
    return time.strftime("%H:%M:%S", time.localtime(t)) + ".%03d" % int((t % 1) * 1000)


def melden(text):
    ereignisse.insert(0, uhr() + "  " + text)
    del ereignisse[30:]
    print(uhr(), text)


class Schranke:
    """Liest den Zustand der Schranke an den GPIOs von Pico 2 ab (gruene LED oder Servo)."""

    def __init__(self, name, servo, gruen):
        self.name = name
        self.servo = servo
        self.gruen = gruen
        self.offen = False
        self.bestaetigt_um = None

    def pruefen(self, pins):
        if self.gruen is not None:
            offen = pins.get(self.gruen) == 1
        else:
            offen = pins.get(self.servo) == cfg["SERVO_OFFEN_US"] * 1000
        if offen == self.offen:
            return
        self.offen = offen
        if offen:
            text = "Schranke %s OFFEN" % self.name
            if self.bestaetigt_um:
                text += " (%.2f s nach Bestätigen)" % (time.monotonic() - self.bestaetigt_um)
            melden(text)
        else:
            melden("Schranke %s ZU" % self.name)


class Pico:
    def __init__(self, nr, rolle, port, host):
        self.nr = nr
        self.rolle = rolle
        self.port = port
        self.host = host
        self.proc = None
        self.bereit = False
        self.pins = {}
        self.bei_pin = None
        self.bei_bestaetigt = None

    async def einschalten(self):
        env = dict(os.environ, SIM_PORT=str(self.port), SIM_HOST=self.host, SIM_AP_DATEI=AP_DATEI,
                   SIM_ADRESSEN="192.168.4.1=%d,192.168.4.2=%d" % (PORT_KASSE, PORT_SCHRANKE),
                   PYTHONIOENCODING="utf-8", PYTHONUNBUFFERED="1", PYTHONDONTWRITEBYTECODE="1")
        self.pins = {}
        self.proc = await asyncio.create_subprocess_exec(
            sys.executable, os.path.join(HIER, "pico_w", "start.py"), self.rolle,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env)
        asyncio.create_task(self._mitlesen(self.proc))

    async def ausschalten(self):
        self.bereit = False
        proc, self.proc = self.proc, None
        if proc is not None and proc.returncode is None:
            proc.kill()
            await proc.wait()
        self.pins = {}
        if self.bei_pin:
            self.bei_pin()

    async def _mitlesen(self, proc):
        while True:
            zeile = await proc.stdout.readline()
            if not zeile:
                break
            zeile = zeile.decode("utf-8", "replace").rstrip()
            if zeile.startswith("@sim "):
                self._sim_meldung(zeile.split()[1:])
            elif zeile:
                print("  [Pico %d] %s" % (self.nr, zeile))
        if proc is self.proc:
            self.bereit = False
            melden("Pico %d abgestürzt (Code %s), siehe Konsole" % (self.nr, proc.returncode))

    def _sim_meldung(self, teile):
        art = teile[0]
        if art in ("pin", "pwm"):
            nr = teile[1] if teile[1] == "LED" else int(teile[1])
            self.pins[nr] = int(teile[2])
            if self.bei_pin:
                self.bei_pin()
        elif art == "bereit":
            self.bereit = True
            melden("Pico %d (%s) bereit" % (self.nr, "Kasse" if self.rolle == "kasse" else "Schranken"))
        elif art == "bestaetigt" and self.bei_bestaetigt:
            self.bei_bestaetigt(teile[1])


class Simulator:
    def __init__(self, host):
        self.host = host
        self.pico1 = Pico(1, "kasse", PORT_KASSE, host)
        self.pico2 = Pico(2, "schranke", PORT_SCHRANKE, host)
        self.ein = Schranke("Einfahrt", cfg["EINFAHRT_SERVO"], cfg["EINFAHRT_LED_GRUEN"])
        self.aus = Schranke("Ausfahrt", cfg["AUSFAHRT_SERVO"], cfg["AUSFAHRT_LED_GRUEN"])
        self.pico2.bei_pin = self._schranken_pruefen
        self.pico2.bei_bestaetigt = self._bestaetigt
        self.stumm = None
        self.stumme_verbindungen = []

    def _schranken_pruefen(self):
        self.ein.pruefen(self.pico2.pins)
        self.aus.pruefen(self.pico2.pins)

    def _bestaetigt(self, wo):
        schranke = self.ein if wo == "einfahrt" else self.aus
        schranke.bestaetigt_um = time.monotonic()

    async def pico1_ein(self):
        if self.pico1.proc is not None:
            return
        if self.stumm is not None:
            self.stumm.close()
            for writer in self.stumme_verbindungen:
                writer.close()
            self.stumm = None
            self.stumme_verbindungen = []
        melden("Pico 1 (Kasse) eingeschaltet, danach Uhrzeit auf der Admin-Seite übernehmen")
        await self.pico1.einschalten()

    async def pico1_aus(self):
        await self.pico1.ausschalten()

        # Ein ausgesteckter Pico lehnt nichts ab, er antwortet einfach nicht (Timeout statt Fehler)
        async def nie_antworten(reader, writer):
            self.stumme_verbindungen.append(writer)

        if self.stumm is None:
            self.stumm = await asyncio.start_server(nie_antworten, self.host, PORT_KASSE)
        melden("Pico 1 (Kasse) AUS")

    async def pico2_neustart(self):
        await self.pico2.ausschalten()
        if os.path.exists(AP_DATEI):
            os.remove(AP_DATEI)
        melden("Pico 2 (Schranken) AUS, Neustart in %d s" % NEUSTART_S)
        await asyncio.sleep(NEUSTART_S)
        await self.pico2.einschalten()
        melden("Pico 2 (Schranken) eingeschaltet")

    async def pult(self, methode, pfad, q, f):
        if pfad == "/zustand":
            return "200 OK", json.dumps({
                "ein": self.ein.offen, "aus": self.aus.offen,
                "pico1": self.pico1.bereit, "pico2": self.pico2.bereit,
                "gpio1": gpio_text(self.pico1), "gpio2": gpio_text(self.pico2),
                "log": ereignisse}), "application/json"
        if methode == "POST" and pfad == "/pico1":
            if f.get("an") == "1":
                await self.pico1_ein()
            else:
                await self.pico1_aus()
            return "303 See Other", "", "text/plain", "Location: /\r\n"
        if methode == "POST" and pfad == "/pico2":
            asyncio.create_task(self.pico2_neustart())
            return "303 See Other", "", "text/plain", "Location: /\r\n"
        if pfad == "/":
            return "200 OK", PULT_HTML
        return "404 Not Found", "Nicht gefunden", "text/plain"


def gpio_text(pico):
    if pico.proc is None:
        return "aus (kein Strom)"
    teile = ["LED %s" % ("an" if pico.pins.get("LED") else "aus")]
    for nr in sorted(n for n in pico.pins if n != "LED"):
        wert = pico.pins[nr]
        if wert > 1:
            # Servo SG90: 500 us = 0 Grad, 2500 us = 180 Grad
            teile.append("GP%d servo %d°" % (nr, round((wert / 1000 - 500) * 180 / 2000)))
        else:
            teile.append("GP%d=%d" % (nr, wert))
    return ", ".join(teile)


PULT_HTML = w.seite("Simulator", """
<h1>Simulator Smart Parking</h1>
<section><p><a href='http://localhost:8002/' target='_blank'>Kamera-Sim-UI (Pico 2)</a> ·
<a href='http://localhost:8001/' target='_blank'>Kassen-UI (Pico 1)</a> ·
<a href='http://localhost:8001/admin' target='_blank'>Admin-Seite</a></p></section>
<section><h2>Schranken</h2>
<p class='m' id='ein'>Einfahrt: –</p><p class='m' id='aus'>Ausfahrt: –</p></section>
<section><h2>Picos</h2>
<dl><dt>Pico 1 (Kasse)</dt><dd id='p1'>–</dd><dt>GPIO</dt><dd class='klein' id='g1'></dd>
<dt>Pico 2 (Schranken)</dt><dd id='p2'>–</dd><dt>GPIO</dt><dd class='klein' id='g2'></dd></dl>
<form method='post' action='/pico1' style='display:inline'><input type='hidden' name='an' value='0'>
<button class='rot'>Pico 1 aus (Strom weg)</button></form>
<form method='post' action='/pico1' style='display:inline'><input type='hidden' name='an' value='1'>
<button>Pico 1 wieder ein</button></form>
<form method='post' action='/pico2' style='display:inline'><button class='rot'>Pico 2 neu starten (10 s aus)</button></form>
</section>
<section><h2>Ereignisse</h2><pre id='log' style='white-space:pre-wrap;font-size:.8em'></pre></section>
""", script="""<script>
function $(id){return document.getElementById(id)}
function setze(id, name, offen){$(id).textContent=name+': '+(offen?'OFFEN':'ZU');$(id).className='m '+(offen?'ok':'err')}
function holen(){fetch('/zustand').then(function(r){return r.json()}).then(function(z){
setze('ein','Schranke Einfahrt',z.ein);setze('aus','Schranke Ausfahrt',z.aus);
$('p1').textContent=z.pico1?'läuft':'AUS';$('p2').textContent=z.pico2?'läuft':'AUS';
$('g1').textContent=z.gpio1;$('g2').textContent=z.gpio2;
$('log').textContent=z.log.join('\\n')}).catch(function(){})}
setInterval(holen,200);holen();</script>""")


async def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    a = argparse.ArgumentParser()
    a.add_argument("--lan", action="store_true", help="auch von anderen Geraeten erreichbar")
    a.add_argument("--neu", action="store_true", help="gespeicherte Parkvorgaenge loeschen")
    a.add_argument("--kein-browser", action="store_true", help="Browser nicht automatisch oeffnen")
    args = a.parse_args()

    os.makedirs(FLASH, exist_ok=True)
    if os.path.exists(AP_DATEI):
        os.remove(AP_DATEI)
    daten = os.path.join(FLASH, "kasse", "daten.json")
    if args.neu and os.path.exists(daten):
        os.remove(daten)

    sim = Simulator("0.0.0.0" if args.lan else "127.0.0.1")
    await asyncio.start_server(lambda r, wr: w.bediene(r, wr, sim.pult), sim.host, PORT_PULT)
    # Pico 2 zuerst, er spannt das WLAN auf
    await sim.pico2.einschalten()
    await sim.pico1.einschalten()
    try:
        for _ in range(100):
            if sim.pico1.bereit and sim.pico2.bereit:
                break
            await asyncio.sleep(0.1)
        print("\nSteuerpult:  http://localhost:%d" % PORT_PULT)
        print("Kasse:       http://localhost:%d   Admin: http://localhost:%d/admin" % (PORT_KASSE, PORT_KASSE))
        print("Kamera-Sim:  http://localhost:%d" % PORT_SCHRANKE)
        print("Beenden: dieses Fenster schliessen oder Ctrl+C\n")
        if not args.kein_browser:
            import webbrowser
            for port, pfad in ((PORT_PULT, "/"), (PORT_SCHRANKE, "/"), (PORT_KASSE, "/"), (PORT_KASSE, "/admin")):
                webbrowser.open("http://localhost:%d%s" % (port, pfad))
        await asyncio.Event().wait()
    finally:
        for pico in (sim.pico1, sim.pico2):
            if pico.proc is not None and pico.proc.returncode is None:
                pico.proc.kill()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
