# Pico 2 – Kamera-Sim-UI und Schrankensteuerung (ohne Hardware-Import -> testbar).
import ablauf
import webutil as w
from kennzeichen import ist_gueltig, normalisiere


class SchrankenApp:
    def __init__(self, einfahrt, ausfahrt, anfrage, kasse_host,
                 timeout_ms=4000, status_timeout_ms=2000, offen_s=5):
        self.ein = einfahrt
        self.aus = ausfahrt
        self.anfrage = anfrage
        self.host = kasse_host
        self.timeout_ms = timeout_ms
        self.status_timeout_ms = status_timeout_ms
        self.offen_s = offen_s

    async def route(self, methode, pfad, q, f):
        if pfad == "/" and methode == "GET":
            return "200 OK", self.seite(await self._frei())
        if pfad == "/einfahrt" and methode == "POST":
            return "200 OK", await self.einfahrt(f.get("kz", ""))
        if pfad == "/ausfahrt" and methode == "POST":
            return "200 OK", await self.ausfahrt(f.get("kz", ""))
        return "404 Not Found", "Nicht gefunden", "text/plain; charset=utf-8"

    async def _frei(self):
        antwort = await self.anfrage(self.host, "/api/status", None, self.status_timeout_ms)
        if isinstance(antwort, dict) and isinstance(antwort.get("frei"), int):
            return antwort["frei"]
        return None

    async def einfahrt(self, eingabe):
        kz = normalisiere(eingabe)
        if not ist_gueltig(kz):
            return self.seite(await self._frei(), ablauf.M_UNGUELTIG, False, eingabe)
        antwort = await self.anfrage(self.host, "/api/einfahrt", {"kz": kz}, self.timeout_ms)
        oeffnen, text = ablauf.einfahrt_ergebnis(antwort, kz)
        if oeffnen:
            self.ein.oeffnen_fuer(self.offen_s)
        frei = antwort.get("frei") if isinstance(antwort, dict) else None
        return self.seite(frei, text, oeffnen, eingabe)

    async def ausfahrt(self, eingabe):
        kz = normalisiere(eingabe)
        if not ist_gueltig(kz):
            return self.seite(await self._frei(), ablauf.M_NICHT_GEFUNDEN, False, eingabe)
        antwort = await self.anfrage(self.host, "/api/ausfahrt", {"kz": kz}, self.timeout_ms)
        oeffnen, text = ablauf.ausfahrt_ergebnis(antwort, kz)
        if oeffnen:
            self.aus.oeffnen_fuer(self.offen_s)
        frei = antwort.get("frei") if isinstance(antwort, dict) else None
        return self.seite(frei, text, oeffnen, eingabe)

    def seite(self, frei, text="", ok=True, eingabe=""):
        t = ["<h1>Kamera-Simulation</h1>"]
        if text:
            t.append(w.meldung(text, "ok" if ok else "err"))
            if not ok and eingabe and text == ablauf.M_UNGUELTIG:
                t.append("<p class='klein'>Eingabe: %s</p>" % w.esc(w.kuerze(eingabe)))
        voll = frei == 0
        if frei is None:
            t.append("<p class='m info' id='frei'>Freie Plätze: unbekannt</p>")
        elif voll:
            t.append("<p class='m err' id='frei'>Parkhaus voll</p>")
        else:
            t.append("<p class='m info' id='frei'>Freie Plätze: %d</p>" % frei)
        t.append("<p class='klein'>Schranke Einfahrt: <b>%s</b> · Schranke Ausfahrt: <b>%s</b></p>" % (
            "OFFEN" if self.ein.offen else "ZU", "OFFEN" if self.aus.offen else "ZU"))
        t.append(self._formular("Einfahrt", "/einfahrt", "kz-ein", voll))
        t.append(self._formular("Ausfahrt", "/ausfahrt", "kz-aus", False))
        return w.seite("Kamera-Sim – Smart Parking", "".join(t), "/")

    def _formular(self, titel, aktion, feld_id, deaktiviert):
        return ("<section><h2>%s</h2><form method='post' action='%s'>"
                "<label for='%s'>Kennzeichen</label>"
                "<input type='text' id='%s' name='kz' autocomplete='off' autocapitalize='characters' "
                "placeholder='z. B. ZH-123'><button type='submit'%s>Bestätigen</button></form></section>"
                % (titel, aktion, feld_id, feld_id, " disabled" if deaktiviert else ""))
