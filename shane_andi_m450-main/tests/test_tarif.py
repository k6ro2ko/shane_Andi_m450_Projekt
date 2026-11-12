from tarif import chf, dauer_text, gebuehr


def preis(minuten):
    return chf(gebuehr(minuten * 60))


def test_mindestgebuehr():
    assert preis(0) == "2.00"
    assert preis(59) == "2.00"


def test_angefangene_stunde():
    assert preis(61) == "4.00"
    assert preis(659) == "22.00"


def test_tagespauschale():
    assert preis(661) == "24.00"
    assert preis(1439) == "24.00"
    assert preis(1441) == "26.00"


def test_parkdauer_anzeige():
    assert dauer_text(2 * 60) == "0:02"
    assert dauer_text(1441 * 60) == "24:01"
