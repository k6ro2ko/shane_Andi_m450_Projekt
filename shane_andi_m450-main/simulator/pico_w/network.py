# Ersatz fuer das MicroPython-Modul network (WLAN des Pico W).
# Der Access Point von Pico 2 ist eine Datei mit SSID und Passwort. Pico 1 gilt als verbunden,
# solange diese Datei existiert und die Zugangsdaten stimmen. Ist der AP weg oder startet neu,
# muss netz.ueberwachen() wieder connect() aufrufen, wie auf der echten Hardware.
import json
import os
import time

STA_IF = 0
AP_IF = 1
STAT_IDLE = 0
STAT_CONNECTING = 1
STAT_GOT_IP = 3

AP_DATEI = os.environ.get("SIM_AP_DATEI", "ap.json")
VERBINDEN_DAUERT_S = 1.0


def _ap_lesen():
    try:
        with open(AP_DATEI) as d:
            ap = json.load(d)
        return ap, os.path.getmtime(AP_DATEI)
    except (OSError, ValueError):
        return None, None


class WLAN:
    def __init__(self, art=STA_IF):
        self.art = art
        self._aktiv = False
        self._daten = {"ssid": "", "password": ""}
        self._ip = ("0.0.0.0", "0.0.0.0", "0.0.0.0", "0.0.0.0")
        self._verbunden_seit = None
        self._ap_zeit = None

    def active(self, an=None):
        if an is None:
            return self._aktiv
        self._aktiv = bool(an)
        if self.art == AP_IF:
            if self._aktiv:
                with open(AP_DATEI, "w") as d:
                    json.dump(self._daten, d)
            elif os.path.exists(AP_DATEI):
                os.remove(AP_DATEI)

    def config(self, *frage, **werte):
        if frage:
            name = {"essid": "ssid"}.get(frage[0], frage[0])
            return self._daten.get(name)
        for name, wert in werte.items():
            if name in ("ssid", "essid"):
                self._daten["ssid"] = wert
            elif name in ("password", "key"):
                self._daten["password"] = wert

    def connect(self, ssid, passwort=None):
        self._aktiv = True
        self._daten = {"ssid": ssid, "password": passwort or ""}
        self._verbunden_seit = time.time()
        self._ap_zeit = None

    def disconnect(self):
        self._verbunden_seit = None
        self._ap_zeit = None

    def isconnected(self):
        if self.art == AP_IF:
            return self._aktiv
        if not self._aktiv or self._verbunden_seit is None:
            return False
        ap, gestartet = _ap_lesen()
        if self._ap_zeit is not None and (ap != self._daten or gestartet != self._ap_zeit):
            # AP weg oder neu gestartet: Verbindung verloren, connect() ist wieder noetig
            self._verbunden_seit = None
            self._ap_zeit = None
            return False
        if ap != self._daten:
            return False
        if self._ap_zeit is None:
            if time.time() - max(self._verbunden_seit, gestartet) < VERBINDEN_DAUERT_S:
                return False
            self._ap_zeit = gestartet
        return True

    def status(self, *frage):
        if self.isconnected():
            return STAT_GOT_IP
        return STAT_CONNECTING if self._verbunden_seit else STAT_IDLE

    def ifconfig(self, werte=None):
        if werte is None:
            return self._ip
        self._ip = tuple(werte)
