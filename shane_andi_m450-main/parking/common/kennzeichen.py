# Kennzeichen pruefen: Kanton, Bindestrich, 1-6 Ziffern ohne fuehrende Null (z.B. ZH-123)
KANTONE = (
    "AG", "AI", "AR", "BE", "BL", "BS", "FR", "GE", "GL", "GR", "JU", "LU", "NE",
    "NW", "OW", "SG", "SH", "SO", "SZ", "TG", "TI", "UR", "VD", "VS", "ZG", "ZH",
)
MAX_ZIFFERN = 6


def normalisiere(text):
    if not text:
        return ""
    return text.strip().upper()


# kz muss schon normalisiert sein (gross, ohne Leerzeichen)
def ist_gueltig(kz):
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
        if c not in "0123456789":
            return False
    return True


# gibt das Kennzeichen in Grossbuchstaben zurueck, oder None wenn ungueltig
def pruefe(text):
    kz = normalisiere(text)
    return kz if ist_gueltig(kz) else None
