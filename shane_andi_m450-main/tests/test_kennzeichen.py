from kennzeichen import pruefe


def test_gueltige_kennzeichen():
    assert pruefe("ZH-123") == "ZH-123"
    assert pruefe("JU-1") == "JU-1"
    assert pruefe("VD-999999") == "VD-999999"


def test_kleinbuchstaben_werden_gross():
    assert pruefe("ag-9999") == "AG-9999"


def test_ungueltige_kennzeichen():
    for kz in ["ZH-", "ZH-1234567", "ZH-0123", "XX-123", "ZH123", "", "A" * 60, "<b>ZH-1</b>"]:
        assert pruefe(kz) is None
