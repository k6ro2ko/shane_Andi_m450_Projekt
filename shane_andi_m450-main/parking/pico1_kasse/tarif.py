# Tarif, alle Betraege in Rappen.
# CHF 2.- pro angefangene Stunde, mind. CHF 2.-, max. CHF 24.- pro Tag
STUNDE_S = 3600
TAG_S = 86400
PREIS_STUNDE = 200
MINDESTGEBUEHR = 200
TAGESPAUSCHALE = 2400
PAUSCHALE_VERLOREN = 2400
KULANZ_S = 15 * 60


def gebuehr(dauer_s):
    if dauer_s < 0:
        dauer_s = 0
    tage = dauer_s // TAG_S
    rest = dauer_s - tage * TAG_S
    angefangene_stunden = (rest + STUNDE_S - 1) // STUNDE_S
    betrag = tage * TAGESPAUSCHALE + min(angefangene_stunden * PREIS_STUNDE, TAGESPAUSCHALE)
    return max(betrag, MINDESTGEBUEHR)


def in_kulanz(bezahlt_um, jetzt):
    return jetzt - bezahlt_um <= KULANZ_S


def chf(rappen):
    return "%d.%02d" % (rappen // 100, rappen % 100)


# Parkdauer als h:mm, ueber 24 h wird weitergezaehlt (24:01)
def dauer_text(dauer_s):
    minuten = max(0, dauer_s) // 60
    return "%d:%02d" % (minuten // 60, minuten % 60)
