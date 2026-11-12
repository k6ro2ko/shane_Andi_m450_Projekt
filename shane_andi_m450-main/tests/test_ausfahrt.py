from ablauf import ausfahrt_ergebnis
from parkhaus import Parkhaus

START = 1000000


def test_kulanzzeit_14_minuten_ok():
    p = Parkhaus()
    p.einfahrt("SZ-710", START)
    p.bezahlen("SZ-710", "Karte", START)
    assert p.ausfahrt("SZ-710", START + 14 * 60) == ("ok", 0)


def test_kulanzzeit_16_minuten_nachzahlung():
    p = Parkhaus()
    p.einfahrt("SZ-711", START)
    p.bezahlen("SZ-711", "Karte", START)
    assert p.ausfahrt("SZ-711", START + 16 * 60) == ("kulanz", 200)
    p.bezahlen("SZ-711", "Bargeld", START + 16 * 60)
    assert p.ausfahrt("SZ-711", START + 17 * 60) == ("ok", 0)


def test_ticket_verloren():
    p = Parkhaus()
    assert p.ticket_verloren("GL-4040", "Bargeld", START) == ("ok", 2400)
    assert p.ausfahrt("GL-4040", START + 10 * 60) == ("ok", 0)


def test_parkhaus_voll():
    p = Parkhaus(3)
    p.einfahrt("FR-101", START)
    p.einfahrt("FR-102", START)
    p.einfahrt("FR-103", START)
    assert p.einfahrt("FR-104", START) == "voll"


# Entscheidungstabelle Ausfahrt (Testkonzept Kap. 3)
def test_r1_nicht_im_system():
    assert ausfahrt_ergebnis({"r": "nicht_gefunden"}, "XX-000") == (False, "Kennzeichen nicht gefunden")


def test_r2_nicht_bezahlt():
    assert ausfahrt_ergebnis({"r": "unbezahlt"}, "BE-999") == (False, "Bitte an Kasse bezahlen")


def test_r3_bezahlt_in_kulanz():
    oeffnen, meldung = ausfahrt_ergebnis({"r": "ok", "kz": "ZH-123"}, "ZH-123")
    assert oeffnen is True


def test_r4_kulanz_ueberschritten():
    antwort = {"r": "kulanz", "betrag": "2.00"}
    assert ausfahrt_ergebnis(antwort, "SZ-711") == (False, "Kulanzzeit überschritten – Nachzahlung CHF 2.00")


def test_r5_kasse_nicht_erreichbar():
    assert ausfahrt_ergebnis(None, "OW-1313") == (False, "Kasse nicht erreichbar – bitte Personal rufen")
