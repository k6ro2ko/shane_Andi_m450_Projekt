# Parkhaus-Logik von Pico 1 (ohne Netzwerk, damit man sie mit pytest testen kann)
import tarif
from kennzeichen import ist_gueltig

ZAHLUNGSARTEN = ("Karte", "Bargeld")
OFFEN = "Offen"
BEZAHLT = "Bezahlt"
KULANZ_UEBERSCHRITTEN = "Kulanzzeit überschritten"


class Parkhaus:
    def __init__(self, kapazitaet=3, max_verlauf=10):
        self.kapazitaet = kapazitaet
        self.max_verlauf = max_verlauf
        self.reset()

    def reset(self):
        self.fahrzeuge = {}
        self.verlauf = []

    def frei(self):
        return max(0, self.kapazitaet - len(self.fahrzeuge))

    def einfahrt(self, kz, jetzt):
        if not ist_gueltig(kz):
            return "ungueltig"
        if kz in self.fahrzeuge:
            return "doppelt"
        if self.frei() <= 0:
            return "voll"
        self.fahrzeuge[kz] = {"ein": jetzt, "bez": None, "art": None, "betrag": 0, "verloren": False}
        return "ok"

    # gibt (status, offener Betrag in Rappen) zurueck
    def _zustand(self, f, jetzt):
        if f["bez"] is None:
            return OFFEN, tarif.gebuehr(jetzt - f["ein"])
        if tarif.in_kulanz(f["bez"], jetzt):
            return BEZAHLT, 0
        return KULANZ_UEBERSCHRITTEN, tarif.gebuehr(jetzt - f["bez"])

    def auskunft(self, kz, jetzt):
        f = self.fahrzeuge.get(kz)
        if f is None:
            return None
        status, offen = self._zustand(f, jetzt)
        return {
            "kz": kz,
            "ein": f["ein"],
            "dauer": None if f["ein"] is None else max(0, jetzt - f["ein"]),
            "status": status,
            "offen": offen,
            "bez": f["bez"],
            "art": f["art"],
            "betrag": f["betrag"],
            "verloren": f["verloren"],
            "ausfahrt_bis": None if f["bez"] is None else f["bez"] + tarif.KULANZ_S,
        }

    # Ergebnis: ok, art, nicht_gefunden oder nichts_offen
    def bezahlen(self, kz, art, jetzt):
        if art not in ZAHLUNGSARTEN:
            return "art", 0
        f = self.fahrzeuge.get(kz)
        if f is None:
            return "nicht_gefunden", 0
        _, offen = self._zustand(f, jetzt)
        if offen <= 0:
            return "nichts_offen", 0
        f["bez"] = jetzt
        f["art"] = art
        f["betrag"] += offen
        return "ok", offen

    # Pauschale, wenn das Kennzeichen nicht im System ist
    # Ergebnis: ok, ungueltig, art oder vorhanden
    def ticket_verloren(self, kz, art, jetzt):
        if not ist_gueltig(kz):
            return "ungueltig", 0
        if art not in ZAHLUNGSARTEN:
            return "art", 0
        if kz in self.fahrzeuge:
            return "vorhanden", 0
        self.fahrzeuge[kz] = {"ein": None, "bez": jetzt, "art": art,
                              "betrag": tarif.PAUSCHALE_VERLOREN, "verloren": True}
        return "ok", tarif.PAUSCHALE_VERLOREN

    # Ergebnis: ok, nicht_gefunden, unbezahlt oder kulanz
    def ausfahrt(self, kz, jetzt):
        f = self.fahrzeuge.get(kz)
        if f is None:
            return "nicht_gefunden", 0
        status, offen = self._zustand(f, jetzt)
        if status == OFFEN:
            return "unbezahlt", offen
        if status == KULANZ_UEBERSCHRITTEN:
            return "kulanz", offen
        del self.fahrzeuge[kz]
        eintrag = dict(f)
        eintrag["kz"] = kz
        eintrag["aus"] = jetzt
        self.verlauf.insert(0, eintrag)
        if len(self.verlauf) > self.max_verlauf:
            self.verlauf = self.verlauf[: self.max_verlauf]
        return "ok", 0

    def setze_einfahrt(self, kz, minuten, jetzt):
        f = self.fahrzeuge.get(kz)
        if f is None:
            return "nicht_gefunden"
        f["ein"] = jetzt - minuten * 60
        return "ok"

    def setze_zahlung(self, kz, minuten, jetzt):
        f = self.fahrzeuge.get(kz)
        if f is None:
            return "nicht_gefunden"
        if f["bez"] is None:
            return "nicht_bezahlt"
        f["bez"] = jetzt - minuten * 60
        return "ok"

    def als_dict(self):
        return {"fahrzeuge": self.fahrzeuge, "verlauf": self.verlauf}

    def aus_dict(self, d):
        self.fahrzeuge = dict(d.get("fahrzeuge", {}))
        self.verlauf = list(d.get("verlauf", []))[: self.max_verlauf]
