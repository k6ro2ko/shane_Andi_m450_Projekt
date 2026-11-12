# Kennzeichen-Validierung (Testkonzept AK A1, TC-08).
KANTONE = (
    "AG", "AI", "AR", "BE", "BL", "BS", "FR", "GE", "GL", "GR", "JU", "LU", "NE",
    "NW", "OW", "SG", "SH", "SO", "SZ", "TG", "TI", "UR", "VD", "VS", "ZG", "ZH",
)
MAX_ZIFFERN = 6
_ZIFFERN = "0123456789"


def normalisiere(text):
    if not text:
        return ""
    return text.strip().upper()


def ist_gueltig(kz):
    """kz muss bereits normalisiert sein."""
    teile = kz.split("-")
    if len(teile) != 2:
        return False
    kanton, nummer = teile
    if kanton not in KANTONE:
        return False
    if not 1 <= len(nummer) <= MAX_ZIFFERN:
        return False
    if nummer[0] == "0":
        return False
    for c in nummer:
        if c not in _ZIFFERN:
            return False
    return True


def pruefe(text):
    """Liefert das normalisierte Kennzeichen oder None, wenn ungueltig."""
    kz = normalisiere(text)
    return kz if ist_gueltig(kz) else None
