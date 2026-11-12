# Datum/Uhrzeit aus Sekunden seit 1970 (Ortszeit) formatieren.
def zerlege(epoch):
    tage, sek = divmod(int(epoch), 86400)
    z = tage + 719468
    era = z // 146097
    doe = z - era * 146097
    yoe = (doe - doe // 1460 + doe // 36524 - doe // 146096) // 365
    jahr = yoe + era * 400
    doy = doe - (365 * yoe + yoe // 4 - yoe // 100)
    mp = (5 * doy + 2) // 153
    tag = doy - (153 * mp + 2) // 5 + 1
    monat = mp + 3 if mp < 10 else mp - 9
    if monat <= 2:
        jahr += 1
    return jahr, monat, tag, sek // 3600, (sek // 60) % 60, sek % 60


def datum_zeit(epoch):
    j, mo, t, h, mi, _ = zerlege(epoch)
    return "%02d.%02d.%04d, %02d:%02d" % (t, mo, j, h, mi)


def uhrzeit(epoch):
    _, _, _, h, mi, _ = zerlege(epoch)
    return "%02d:%02d" % (h, mi)
