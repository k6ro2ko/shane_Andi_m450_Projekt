# Pico 1 – Kasse: Kassen-UI (/), Admin-Seite (/admin, nur TEST-Build) und M2M-API (/api/...).
import json
import time

import tarif
import webutil as w
import zeitformat as zf
from kennzeichen import ist_gueltig, normalisiere
from parkhaus import ZAHLUNGSARTEN, Parkhaus

M_UNGUELTIG = "Ungültiges Kennzeichen"
M_NICHT_GEFUNDEN = "Kennzeichen nicht gefunden"
M_BEZAHLT = "Bezahlung erfolgreich – bitte innert 15 Minuten ausfahren"
MAX_MINUTEN = 525600


class Uhr:
    """Ortszeit in Sekunden seit 1970. Der Pico hat keine gepufferte Uhr:
    nach jedem Start muss die Zeit auf der Admin-Seite uebernommen werden."""

    def __init__(self, quelle=time.time):
        self._quelle = quelle
        self.offset = 0
        self.gesetzt = False

    def jetzt(self):
        return int(self._quelle()) + self.offset

    def setzen(self, epoch):
        self.offset = int(epoch) - int(self._quelle())
        self.gesetzt = True


def _json(d):
    return "200 OK", json.dumps(d), "application/json"


def _html(body):
    return "200 OK", body


def _404():
    return "404 Not Found", "Nicht gefunden", "text/plain; charset=utf-8"


def _minuten(text):
    try:
        n = int(text)
    except Exception:
        return None
    return n if 0 <= n <= MAX_MINUTEN else None


class KasseApp:
    def __init__(self, parkhaus=None, uhr=None, datei=None, admin=True):
        self.ph = parkhaus or Parkhaus()
        self.uhr = uhr or Uhr()
        self.datei = datei
        self.admin = admin
        self._laden()

    def _laden(self):
        if not self.datei:
            return
        try:
            with open(self.datei) as d:
                self.ph.aus_dict(json.load(d))
        except Exception:
            pass

    def _speichern(self):
        if not self.datei:
            return
        try:
            with open(self.datei, "w") as d:
                json.dump(self.ph.als_dict(), d)
        except Exception as e:
            print("Speichern fehlgeschlagen:", e)

    async def route(self, methode, pfad, q, f):
        return self.route_sync(methode, pfad, q, f)

    def route_sync(self, methode, pfad, q, f):
        jetzt = self.uhr.jetzt()
        if pfad == "/" and methode == "GET":
            return _html(self.kasse_seite(q.get("kz", ""), q.get("verloren") == "1", jetzt))
        if pfad == "/bezahlen" and methode == "POST":
            return _html(self.bezahlen(f, jetzt))
        if pfad == "/verloren" and methode == "POST":
            return _html(self.verloren(f, jetzt))
        if pfad == "/api/einfahrt" and methode == "POST":
            return _json(self.api_einfahrt(f, jetzt))
        if pfad == "/api/ausfahrt" and methode == "POST":
            return _json(self.api_ausfahrt(f, jetzt))
        if pfad == "/api/status":
            return _json({"frei": self.ph.frei(), "kapazitaet": self.ph.kapazitaet})
        if pfad.startswith("/admin") and self.admin:
            if methode == "GET" and pfad == "/admin":
                return _html(self.admin_seite(jetzt))
            if methode == "POST":
                return _html(self.admin_aktion(pfad, f, jetzt))
        return _404()

    def api_einfahrt(self, f, jetzt):
        kz = normalisiere(f.get("kz", ""))[:20]
        r = self.ph.einfahrt(kz, jetzt)
        if r == "ok":
            self._speichern()
        return {"r": r, "kz": kz, "zeit": zf.datum_zeit(jetzt) + " Uhr", "frei": self.ph.frei()}

    def api_ausfahrt(self, f, jetzt):
        kz = normalisiere(f.get("kz", ""))[:20]
        r, betrag = self.ph.ausfahrt(kz, jetzt)
        if r == "ok":
            self._speichern()
        return {"r": r, "kz": kz, "betrag": tarif.chf(betrag), "frei": self.ph.frei()}

    def _formular(self, kz=""):
        return ("<section><form method='get' action='/'>"
                "<label for='kz'>Kennzeichen</label>"
                "<input type='text' id='kz' name='kz' value='%s' autocomplete='off' "
                "autocapitalize='characters' placeholder='z. B. ZH-123'>"
                "<button type='submit'>Preis abfragen</button></form></section>" % w.esc(kz))

    def _zahlungsart(self):
        teile = []
        for art in ZAHLUNGSARTEN:
            teile.append("<label><input type='radio' name='art' value='%s' required> %s</label>" % (art, art))
        return "<fieldset style='border:0;padding:0'><legend>Zahlungsart</legend>%s</fieldset>" % "".join(teile)

    def _uhr_warnung(self):
        if self.uhr.gesetzt:
            return ""
        return w.meldung("Uhrzeit nicht gesetzt – bitte Personal informieren (Admin-Seite).", "err")

    def kasse_seite(self, kz_roh, verloren, jetzt, meldung="", art="ok", url=None):
        teile = ["<h1>Kasse</h1>", self._uhr_warnung()]
        if meldung:
            teile.append(w.meldung(meldung, art))
        kz = normalisiere(kz_roh)
        teile.append(self._formular(kz_roh if not ist_gueltig(kz) else kz))
        if kz_roh and not meldung:
            if not ist_gueltig(kz):
                teile.append("<section>%s<p class='klein'>Eingabe: %s</p></section>"
                             % (w.meldung(M_UNGUELTIG, "err"), w.esc(w.kuerze(kz_roh))))
            else:
                teile.append(self._auskunft_html(kz, verloren, jetzt))
        elif ist_gueltig(kz):
            teile.append(self._auskunft_html(kz, False, jetzt))
        return w.seite("Kasse – Smart Parking", "".join(teile), url)

    def _auskunft_html(self, kz, verloren, jetzt):
        a = self.ph.auskunft(kz, jetzt)
        if a is None:
            if not verloren:
                return ("<section>%s<form method='get' action='/'>"
                        "<input type='hidden' name='kz' value='%s'><input type='hidden' name='verloren' value='1'>"
                        "<button type='submit' class='rot'>Ticket verloren</button></form></section>"
                        % (w.meldung(M_NICHT_GEFUNDEN, "err"), w.esc(kz)))
            return ("<section><h2>Ticket verloren: %s</h2><p>Pauschale</p>"
                    "<p class='betrag'>CHF %s</p><form method='post' action='/verloren'>"
                    "<input type='hidden' name='kz' value='%s'>%s"
                    "<button type='submit'>Gebühr bezahlen</button></form></section>"
                    % (w.esc(kz), tarif.chf(tarif.PAUSCHALE_VERLOREN), w.esc(kz), self._zahlungsart()))
        zeilen = ["<dt>Kennzeichen</dt><dd>%s</dd>" % w.esc(kz)]
        if a["ein"] is None:
            zeilen.append("<dt>Einfahrt</dt><dd>– (Ticket verloren)</dd>")
        else:
            zeilen.append("<dt>Einfahrt</dt><dd>%s Uhr</dd>" % zf.datum_zeit(a["ein"]))
            zeilen.append("<dt>Parkdauer</dt><dd>%s h</dd>" % tarif.dauer_text(a["dauer"]))
        zeilen.append("<dt>Status</dt><dd id='status'>%s</dd>" % a["status"])
        if a["bez"] is not None:
            zeilen.append("<dt>Zahlung</dt><dd>%s Uhr, %s</dd>" % (zf.datum_zeit(a["bez"]), w.esc(a["art"])))
        teile = ["<section><dl>%s</dl>" % "".join(zeilen)]
        if a["status"] == "Bezahlt":
            teile.append("<p class='betrag'>CHF %s</p>" % tarif.chf(a["betrag"]))
            teile.append(w.meldung("Bezahlt – Ausfahrt bis %s" % zf.uhrzeit(a["ausfahrt_bis"]), "ok"))
        else:
            titel = "Zu bezahlen" if a["status"] == "Offen" else "Nachgebühr"
            teile.append("<p>%s</p><p class='betrag' id='betrag'>CHF %s</p>" % (titel, tarif.chf(a["offen"])))
            teile.append("<form method='post' action='/bezahlen'><input type='hidden' name='kz' value='%s'>%s"
                         "<button type='submit'>Gebühr bezahlen</button></form>" % (w.esc(kz), self._zahlungsart()))
        teile.append("</section>")
        return "".join(teile)

    def bezahlen(self, f, jetzt):
        kz = normalisiere(f.get("kz", ""))
        url = "/?kz=" + w.url_encode(kz) if ist_gueltig(kz) else "/"
        if not ist_gueltig(kz):
            return self.kasse_seite("", False, jetzt, M_UNGUELTIG, "err", "/")
        r, betrag = self.ph.bezahlen(kz, f.get("art", ""), jetzt)
        if r == "ok":
            self._speichern()
            return self.kasse_seite(kz, False, jetzt, M_BEZAHLT + " (CHF %s, %s)" % (tarif.chf(betrag), f["art"]), "ok", url)
        texte = {"art": "Bitte Zahlungsart «Karte» oder «Bargeld» wählen",
                 "nicht_gefunden": M_NICHT_GEFUNDEN, "nichts_offen": "Keine offene Gebühr"}
        return self.kasse_seite(kz, False, jetzt, texte.get(r, "Fehler"), "err", url)

    def verloren(self, f, jetzt):
        kz = normalisiere(f.get("kz", ""))
        if not ist_gueltig(kz):
            return self.kasse_seite("", False, jetzt, M_UNGUELTIG, "err", "/")
        url = "/?kz=" + w.url_encode(kz)
        r, _ = self.ph.ticket_verloren(kz, f.get("art", ""), jetzt)
        if r == "ok":
            self._speichern()
            bis = zf.uhrzeit(jetzt + tarif.KULANZ_S)
            return self.kasse_seite(kz, False, jetzt, "Bezahlt – Ausfahrt bis %s" % bis, "ok", url)
        texte = {"art": "Bitte Zahlungsart «Karte» oder «Bargeld» wählen",
                 "vorhanden": "Kennzeichen ist im Parkhaus registriert – normal bezahlen"}
        return self.kasse_seite(kz, False, jetzt, texte.get(r, "Fehler"), "err", url)

    _ZEIT_JS = ("Math.round(Date.now()/1000-new Date().getTimezoneOffset()*60)")

    def admin_seite(self, jetzt, meldung="", art="ok"):
        t = ["<h1>Admin (TEST-Build)</h1>"]
        if meldung:
            t.append(w.meldung(meldung, art))
        uhr = ("Uhrzeit Pico 1: %s Uhr" % zf.datum_zeit(jetzt)) if self.uhr.gesetzt else "Uhrzeit NICHT gesetzt"
        t.append("<section><p>%s</p><form method='post' action='/admin/zeit' "
                 "onsubmit=\"this.epoch.value=%s\"><input type='hidden' name='epoch'>"
                 "<button type='submit'>Uhrzeit übernehmen</button></form>" % (uhr, self._ZEIT_JS))
        t.append("<form method='post' action='/admin/reset' "
                 "onsubmit=\"return confirm('Wirklich alle Daten löschen?')\">"
                 "<button type='submit' class='rot'>Alle Daten zurücksetzen</button></form></section>")
        t.append("<section><h2>Im Parkhaus – freie Plätze: <span id='frei'>%d</span> von %d</h2>"
                 % (self.ph.frei(), self.ph.kapazitaet))
        if not self.ph.fahrzeuge:
            t.append("<p>Kein Fahrzeug im System.</p>")
        else:
            t.append("<div class='scroll'><table><tr><th>Kennzeichen</th><th>Einfahrt</th><th>Status</th>"
                     "<th>Zahlung</th><th>Art</th><th>Betrag</th><th>Zeitstempel setzen</th></tr>")
            for kz in sorted(self.ph.fahrzeuge):
                a = self.ph.auskunft(kz, jetzt)
                ein = "– (Ticket verloren)" if a["ein"] is None else "%s<br><span class='klein'>Dauer %s</span>" % (
                    zf.datum_zeit(a["ein"]), tarif.dauer_text(a["dauer"]))
                bez = "–" if a["bez"] is None else zf.datum_zeit(a["bez"])
                t.append("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>CHF %s</td><td>%s%s</td></tr>"
                         % (w.esc(kz), ein, a["status"], bez, w.esc(a["art"] or "–"), tarif.chf(a["betrag"]),
                            self._zeit_form(kz, "einfahrt", "Einfahrt vor n Minuten"),
                            self._zeit_form(kz, "zahlung", "Zahlung vor n Minuten") if a["bez"] is not None else ""))
            t.append("</table></div>")
        t.append("</section>")
        t.append("<section><h2>Abgeschlossene Parkvorgänge (letzte %d)</h2>" % self.ph.max_verlauf)
        if not self.ph.verlauf:
            t.append("<p>Keine.</p>")
        else:
            t.append("<div class='scroll'><table><tr><th>Kennzeichen</th><th>Einfahrt</th><th>Zahlung</th>"
                     "<th>Ausfahrt</th><th>Art</th><th>Betrag</th></tr>")
            for v in self.ph.verlauf:
                t.append("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>CHF %s</td></tr>" % (
                    w.esc(v.get("kz")), "–" if v.get("ein") is None else zf.datum_zeit(v["ein"]),
                    "–" if v.get("bez") is None else zf.datum_zeit(v["bez"]), zf.datum_zeit(v["aus"]),
                    w.esc(v.get("art") or "–"), tarif.chf(v.get("betrag", 0))))
            t.append("</table></div>")
        t.append("</section>")
        script = ""
        if not self.uhr.gesetzt:
            script = ("<script>fetch('/admin/zeit',{method:'POST',headers:{'Content-Type':"
                      "'application/x-www-form-urlencoded'},body:'epoch='+%s}).then(function(){location.reload()})"
                      "</script>" % self._ZEIT_JS)
        return w.seite("Admin – Smart Parking", "".join(t), "/admin", script)

    def _zeit_form(self, kz, was, text):
        return ("<form method='post' action='/admin/%s'><input type='hidden' name='kz' value='%s'>"
                "<input type='number' name='n' min='0' value='0' inputmode='numeric' aria-label='n Minuten'>"
                "<button type='submit'>%s</button></form>" % (was, w.esc(kz), text))

    def admin_aktion(self, pfad, f, jetzt):
        if pfad == "/admin/reset":
            self.ph.reset()
            self._speichern()
            return self.admin_seite(jetzt, "Alle Daten zurückgesetzt – %d freie Plätze" % self.ph.frei())
        if pfad == "/admin/zeit":
            try:
                self.uhr.setzen(int(f.get("epoch", "")))
            except Exception:
                return self.admin_seite(jetzt, "Uhrzeit ungültig", "err")
            return self.admin_seite(self.uhr.jetzt(), "Uhrzeit übernommen")
        if pfad in ("/admin/einfahrt", "/admin/zahlung"):
            kz = normalisiere(f.get("kz", ""))
            n = _minuten(f.get("n", ""))
            if n is None:
                return self.admin_seite(jetzt, "Ungültige Minutenzahl (0 bis %d)" % MAX_MINUTEN, "err")
            if pfad == "/admin/einfahrt":
                r = self.ph.setze_einfahrt(kz, n, jetzt)
                text = "Einfahrt von %s auf vor %d Minuten gesetzt" % (kz, n)
            else:
                r = self.ph.setze_zahlung(kz, n, jetzt)
                text = "Zahlung von %s auf vor %d Minuten gesetzt" % (kz, n)
            if r == "ok":
                self._speichern()
                return self.admin_seite(jetzt, text)
            fehler = {"nicht_gefunden": M_NICHT_GEFUNDEN, "nicht_bezahlt": "Noch nicht bezahlt"}
            return self.admin_seite(jetzt, fehler.get(r, "Fehler"), "err")
        return self.admin_seite(jetzt, "Unbekannte Aktion", "err")
