# Was Pico 2 mit der Antwort der Kasse macht: Schranke auf oder nicht, und welche Meldung.
M_UNGUELTIG = "Ungültiges Kennzeichen"
M_DOPPELT = "Fahrzeug bereits im Parkhaus"
M_VOLL = "Parkhaus voll"
M_NICHT_GEFUNDEN = "Kennzeichen nicht gefunden"
M_UNBEZAHLT = "Bitte an Kasse bezahlen"
M_KASSE_OFFLINE = "Kasse nicht erreichbar – bitte Personal rufen"


def m_kulanz(betrag_chf):
    return "Kulanzzeit überschritten – Nachzahlung CHF " + betrag_chf


def m_einfahrt_ok(kz, zeit):
    return "Einfahrt registriert: %s (%s)" % (kz, zeit)


def m_ausfahrt_ok(kz):
    return "Ausfahrt frei: %s – gute Fahrt" % kz


# antwort ist das JSON von Pico 1, oder None wenn die Kasse nicht geantwortet hat
def einfahrt_ergebnis(antwort, kz):
    if not isinstance(antwort, dict):
        return False, M_KASSE_OFFLINE
    r = antwort.get("r")
    if r == "ok":
        return True, m_einfahrt_ok(antwort.get("kz", kz), antwort.get("zeit", ""))
    if r == "doppelt":
        return False, M_DOPPELT
    if r == "voll":
        return False, M_VOLL
    if r == "ungueltig":
        return False, M_UNGUELTIG
    return False, M_KASSE_OFFLINE


def ausfahrt_ergebnis(antwort, kz):
    if not isinstance(antwort, dict):
        return False, M_KASSE_OFFLINE
    r = antwort.get("r")
    if r == "ok":
        return True, m_ausfahrt_ok(antwort.get("kz", kz))
    if r == "nicht_gefunden":
        return False, M_NICHT_GEFUNDEN
    if r == "unbezahlt":
        return False, M_UNBEZAHLT
    if r == "kulanz":
        return False, m_kulanz(antwort.get("betrag", "?"))
    return False, M_KASSE_OFFLINE
