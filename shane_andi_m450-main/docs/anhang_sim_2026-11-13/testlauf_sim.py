# Fuehrt TC-01 bis TC-15 gegen den laufenden Simulator aus (localhost:8000/8001/8002).
import html
import json
import re
import sys
import time
import urllib.parse
import urllib.request

PULT, KASSE, CAM = "http://127.0.0.1:8000", "http://127.0.0.1:8001", "http://127.0.0.1:8002"
R = {}
sys.stdout.reconfigure(encoding="utf-8")


def uhr():
    return time.strftime("%H:%M:%S")


def req(url, daten=None, timeout=15):
    body = urllib.parse.urlencode(daten).encode() if daten is not None else None
    t0 = time.perf_counter()
    with urllib.request.urlopen(urllib.request.Request(url, data=body), timeout=timeout) as r:
        txt = r.read().decode("utf-8")
    return txt, time.perf_counter() - t0


def text(h):
    h = re.sub(r"<script.*?</script>", "", h, flags=re.S)
    return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", h))).strip()


def meldung(h):
    m = re.search(r"id='meldung'>(.*?)</p>", h)
    return html.unescape(m.group(1)) if m else None


def frei(h):
    m = re.search(r"id='frei'>(.*?)</", h)
    return html.unescape(m.group(1)) if m else None


def zustand():
    return json.loads(req(PULT + "/zustand")[0])


def log_ts(zeile):
    hms, ms = zeile[:12].split(".")
    h, m, s = map(int, hms.split(":"))
    return h * 3600 + m * 60 + s + int(ms) / 1000


def schranke_messen(name, warten=True):
    """Liest aus dem Ereignislog Oeffnungszeit und Offen-Dauer der letzten Oeffnung."""
    if warten:
        t_end = time.time() + 9
        while time.time() < t_end:
            z = zustand()
            if not z["ein" if name == "Einfahrt" else "aus"]:
                break
            time.sleep(0.05)
    log = zustand()["log"]
    auf = next((l for l in log if ("Schranke %s OFFEN" % name) in l), None)
    zu = next((l for l in log if ("Schranke %s ZU" % name) in l), None)
    if not auf:
        return None, None
    m = re.search(r"\(([\d.]+) s nach", auf)
    t_auf = float(m.group(1)) if m else None
    dauer = round(log_ts(zu) - log_ts(auf), 2) if zu and log.index(zu) < log.index(auf) else None
    return t_auf, dauer


def anzahl_oeffnungen(name):
    # Letzte Oeffnung (Zeile mit ms-Zeitstempel) statt Anzahl: das Log haelt nur 15 Eintraege.
    return next((l for l in zustand()["log"] if ("Schranke %s OFFEN" % name) in l), "")


def ein(kz):
    return req(CAM + "/einfahrt", {"kz": kz})


def aus(kz):
    return req(CAM + "/ausfahrt", {"kz": kz})


def admin():
    return req(KASSE + "/admin")[0]


def g0():
    epoch = int(time.time() - time.timezone + (3600 if time.localtime().tm_isdst > 0 else 0))
    req(KASSE + "/admin/zeit", {"epoch": epoch})
    h = req(KASSE + "/admin/reset", {})[0]
    assert "Kein Fahrzeug im System" in h and "3</span> von 3" in h, text(h)
    z = zustand()
    while z["ein"] or z["aus"]:
        time.sleep(0.1)
        z = zustand()
    return meldung(h)


def admin_zeile(h, kz):
    m = re.search(r"<tr><td>%s</td>(.*?)</tr>" % re.escape(kz), h)
    return text(m.group(0)) if m else None


def sektionen(h):
    im = h.split("Abgeschlossene")[0]
    ab = h.split("Abgeschlossene")[1] if "Abgeschlossene" in h else ""
    return im, ab


def kasse(kz, verloren=False):
    url = KASSE + "/?kz=" + urllib.parse.quote(kz) + ("&verloren=1" if verloren else "")
    return req(url)[0]


def kasse_info(h):
    dl = re.search(r"<dl>(.*?)</dl>", h)
    betrag = re.findall(r"class='betrag'[^>]*>(.*?)</p>", h)
    return {"dl": text(dl.group(1)) if dl else None, "betrag": betrag, "meldung": meldung(h),
            "text": text(h)[:300]}


def log(tc, **kw):
    kw["uhrzeit"] = kw.get("uhrzeit", uhr())
    R.setdefault(tc, []).append(kw)
    print(tc, json.dumps(kw, ensure_ascii=False))


# ---------------------------------------------------------------------------
print("Start", uhr())
R["start"] = uhr()
log("G0", reset=g0(), admin=frei(admin()))

# TC-01
u = uhr()
h, rt = ein("ZH-123")
t_auf, dauer = schranke_messen("Einfahrt")
a = admin()
log("TC-01", uhrzeit=u, meldung=meldung(h), http_s=round(rt, 3), zeit_bis_oeffnen=t_auf, offen_dauer=dauer,
    admin_zeile=admin_zeile(a, "ZH-123"), admin_frei=re.search(r"freie Plätze: <span id='frei'>(\d+)", a).group(1))
t_zh123 = time.time()

# TC-02
u = uhr()
n0 = anzahl_oeffnungen("Einfahrt")
h, _ = ein("ZH-123")
time.sleep(0.3)
a = admin()
log("TC-02", uhrzeit=u, meldung=meldung(h), schranke_ein_offen=zustand()["ein"],
    neue_oeffnung=anzahl_oeffnungen("Einfahrt") != n0, eintraege_zh123=a.count("<tr><td>ZH-123</td>"))

# TC-03: ZH-123 soll ca. 2 Minuten im System sein -> echt warten
rest = 125 - (time.time() - t_zh123)
print("warte %.0f s fuer TC-03" % rest)
time.sleep(max(0, rest))
u = uhr()
h = kasse("ZH-123")
log("TC-03", uhrzeit=u, **kasse_info(h))

# TC-04
u = uhr()
h, _ = req(KASSE + "/bezahlen", {"kz": "ZH-123", "art": "Karte"})
a = admin()
log("TC-04", uhrzeit=u, meldung=meldung(h), status=re.search(r"id='status'>(.*?)<", h).group(1),
    admin_zeile=admin_zeile(a, "ZH-123"))

# TC-05
h, _ = ein("BE-999")
schranke_messen("Einfahrt")
u = uhr()
n0 = anzahl_oeffnungen("Ausfahrt")
h, _ = aus("BE-999")
time.sleep(0.3)
log("TC-05", uhrzeit=u, vorbedingung="BE-999 eingefahren", meldung=meldung(h), schranke_aus_offen=zustand()["aus"],
    neue_oeffnung=anzahl_oeffnungen("Ausfahrt") != n0)

# TC-06
u = uhr()
h, rt = aus("ZH-123")
t_auf, dauer = schranke_messen("Ausfahrt")
a = admin()
im, ab = sektionen(a)
log("TC-06", uhrzeit=u, meldung=meldung(h), http_s=round(rt, 3), zeit_bis_oeffnen=t_auf, offen_dauer=dauer,
    zh123_im_parkhaus="ZH-123" in im, zh123_abgeschlossen=text(re.search(r"<tr><td>ZH-123</td>.*?</tr>", ab).group(0)) if "ZH-123" in ab else None,
    admin_frei=re.search(r"freie Plätze: <span id='frei'>(\d+)", a).group(1))

# TC-07
u = uhr()
n0 = anzahl_oeffnungen("Ausfahrt")
h1, _ = aus("XX-000")
h2, _ = aus("ZH-123")
time.sleep(0.3)
h3, _ = req(CAM + "/")
log("TC-07", uhrzeit=u, xx000=meldung(h1), zh123=meldung(h2), neue_oeffnung=anzahl_oeffnungen("Ausfahrt") != n0,
    seite_danach_ok="Kamera-Simulation" in h3)

# TC-08
g0()
u = uhr()
schritte = [("1a", "ZH-"), ("1b", "ZH-1234567"), ("1c", "ZH-0123"), ("1d", "XX-123"), ("1e", "ZH123"),
            ("1f", ""), ("2a", "A" * 60), ("2b", "<b>ZH-1</b>"), ("3a", "JU-1"), ("3b", "VD-999999"), ("3c", "ag-9999")]
erg = []
for nr, eingabe in schritte:
    n0 = anzahl_oeffnungen("Einfahrt")
    h, _ = ein(eingabe)
    if nr.startswith("3"):
        schranke_messen("Einfahrt")
    else:
        time.sleep(0.2)
    e = {"nr": nr, "eingabe": eingabe, "meldung": meldung(h), "geoeffnet": anzahl_oeffnungen("Einfahrt") != n0}
    if nr == "2b":
        e["roh_b_tag_im_html"] = "<b>ZH-1</b>" in h
        e["escaped"] = "&lt;b&gt;ZH-1&lt;/b&gt;" in h
    if nr == "2a":
        e["seite_ok"] = "Kamera-Simulation" in h
    erg.append(e)
a = admin()
im, _ = sektionen(a)
log("TC-08", uhrzeit=u, schritte=erg, admin_kz=re.findall(r"<tr><td>([^<]+)</td>", im))

# TC-09
g0()
u = uhr()
s1 = []
for kz in ("FR-101", "FR-102", "FR-103"):
    h, _ = ein(kz)
    t_auf, _d = schranke_messen("Einfahrt", warten=False)
    s1.append({"kz": kz, "meldung": meldung(h), "frei": frei(h)})
    time.sleep(0.1)
tab2_alt = None  # Tab 2 wurde vor Schritt 1 geladen (Formular aktiv) -> POST ohne neu laden
t1, _ = req(CAM + "/")
s2 = {"frei": frei(t1), "button_disabled": "disabled" in t1.split("Einfahrt</h2>")[1].split("</form>")[0]}
n0 = anzahl_oeffnungen("Einfahrt")
h, _ = ein("FR-104")
time.sleep(0.3)
s3 = {"meldung": meldung(h), "geoeffnet": anzahl_oeffnungen("Einfahrt") != n0}
# Warten bis Einfahrtsschranke zu
schranke_messen("Einfahrt")
hb, _ = req(KASSE + "/bezahlen", {"kz": "FR-101", "art": "Karte"})
ha, _ = aus("FR-101")
t_aus, d_aus = schranke_messen("Ausfahrt", warten=False)
t1, _ = req(CAM + "/")
btn = "disabled" not in t1.split("Einfahrt</h2>")[1].split("</form>")[0]
h, _ = ein("FR-104")
t_ein, _ = schranke_messen("Einfahrt", warten=False)
s4 = {"bezahlt": meldung(hb), "ausfahrt": meldung(ha), "aus_oeffnet_s": t_aus, "frei_nach_reload": frei(t1),
      "button_aktiv": btn, "fr104": meldung(h), "ein_oeffnet_s": t_ein}
schranke_messen("Einfahrt")
log("TC-09", uhrzeit=u, schritt1=s1, schritt2=s2, schritt3=s3, schritt4=s4)

# TC-10
g0()
ein("TG-500")
schranke_messen("Einfahrt")
u = uhr()
zeilen = []
for n in (0, 59, 61, 659, 661, 1439, 1441):
    ha, _ = req(KASSE + "/admin/einfahrt", {"kz": "TG-500", "n": n})
    t0 = time.time()
    h = kasse("TG-500")
    info = kasse_info(h)
    dauer = re.search(r"Parkdauer (\S+) h", info["dl"]).group(1)
    zeilen.append({"n": n, "admin": meldung(ha), "dauer": dauer, "chf": info["betrag"][0],
                   "abfrage_nach_s": round(time.time() - t0, 2)})
log("TC-10", uhrzeit=u, werte=zeilen)

# TC-11
g0()
u = uhr()
vor = []
for kz in ("SZ-710", "SZ-711"):
    ein(kz)
    schranke_messen("Einfahrt")
    h, _ = req(KASSE + "/bezahlen", {"kz": kz, "art": "Karte"})
    vor.append({"kz": kz, "meldung": meldung(h)})
ha1, _ = req(KASSE + "/admin/zahlung", {"kz": "SZ-710", "n": 14})
n0 = anzahl_oeffnungen("Ausfahrt")
h1, _ = aus("SZ-710")
t1o, d1 = schranke_messen("Ausfahrt")
s1 = {"admin": meldung(ha1), "meldung": meldung(h1), "geoeffnet": anzahl_oeffnungen("Ausfahrt") != n0, "oeffnet_s": t1o}
ha2, _ = req(KASSE + "/admin/zahlung", {"kz": "SZ-711", "n": 16})
n0 = anzahl_oeffnungen("Ausfahrt")
h2, _ = aus("SZ-711")
time.sleep(0.3)
s2 = {"admin": meldung(ha2), "meldung": meldung(h2), "geoeffnet": anzahl_oeffnungen("Ausfahrt") != n0}
k = kasse_info(kasse("SZ-711"))
hb, _ = req(KASSE + "/bezahlen", {"kz": "SZ-711", "art": "Bargeld"})
n0 = anzahl_oeffnungen("Ausfahrt")
h3, _ = aus("SZ-711")
t3o, _ = schranke_messen("Ausfahrt")
s3 = {"kasse_vorher": k, "bezahlen": meldung(hb), "ausfahrt": meldung(h3),
      "geoeffnet": anzahl_oeffnungen("Ausfahrt") != n0, "oeffnet_s": t3o}
log("TC-11", uhrzeit=u, vorbedingung=vor, schritt1=s1, schritt2=s2, schritt3=s3)

# TC-12
g0()
u = uhr()
h = kasse("GL-4040")
s1 = {"meldung": meldung(h), "button_ticket_verloren": "Ticket verloren</button>" in h}
hv = kasse("GL-4040", verloren=True)
s2a = kasse_info(hv)
t_zahl = time.localtime()
hp, _ = req(KASSE + "/verloren", {"kz": "GL-4040", "art": "Bargeld"})
erw_bis = time.strftime("%H:%M", time.localtime(time.mktime(t_zahl) + 900))
s2 = {"pauschale_angezeigt": s2a["betrag"], "meldung": meldung(hp), "betrag_danach": kasse_info(hp)["betrag"],
      "zahlung_um": time.strftime("%H:%M", t_zahl), "erwartet_bis": erw_bis}
n0 = anzahl_oeffnungen("Ausfahrt")
h3, _ = aus("GL-4040")
t3o, _ = schranke_messen("Ausfahrt")
s3 = {"meldung": meldung(h3), "geoeffnet": anzahl_oeffnungen("Ausfahrt") != n0, "oeffnet_s": t3o}
log("TC-12", uhrzeit=u, schritt1=s1, schritt2=s2, schritt3=s3)

# TC-13
g0()
ein("OW-1313")
schranke_messen("Einfahrt")
req(KASSE + "/bezahlen", {"kz": "OW-1313", "art": "Karte"})
u = uhr()
req(PULT + "/pico1", {"an": "0"})
time.sleep(0.5)
try:
    req(KASSE + "/", timeout=5)
    kasse_erreichbar = True
except Exception as e:
    kasse_erreichbar = "nein (%s)" % type(e).__name__
n0a = anzahl_oeffnungen("Ausfahrt")
h2, rt2 = aus("OW-1313")
s2 = {"meldung": meldung(h2), "zeit_s": round(rt2, 2), "aus_offen": zustand()["aus"]}
n0e = anzahl_oeffnungen("Einfahrt")
h3, rt3 = ein("NE-2020")
s3 = {"meldung": meldung(h3), "zeit_s": round(rt3, 2), "ein_offen": zustand()["ein"],
      "geoeffnet": anzahl_oeffnungen("Einfahrt") != n0e}
req(PULT + "/pico1", {"an": "1"})
time.sleep(15)
a_vor = admin()
uhr_vor = re.search(r"<p>(Uhrzeit[^<]*)</p>", a_vor).group(1)
kasse_warnung = "Uhrzeit nicht gesetzt" in req(KASSE + "/")[0]
g_epoch = int(time.time() - time.timezone + (3600 if time.localtime().tm_isdst > 0 else 0))
a_nach = req(KASSE + "/admin/zeit", {"epoch": g_epoch})[0]
uhr_nach = re.search(r"<p>(Uhrzeit[^<]*)</p>", a_nach).group(1)
ow_noch_da = "<tr><td>OW-1313</td>" in a_nach
h4, rt4 = ein("NE-2020")
t4o, _ = schranke_messen("Einfahrt")
s4 = {"admin_uhr_vorher": uhr_vor, "kasse_warnung_uhr": kasse_warnung, "admin_uhr_nachher": uhr_nach,
      "ow1313_nach_neustart_noch_gespeichert": ow_noch_da, "meldung": meldung(h4), "oeffnet_s": t4o}
log("TC-13", uhrzeit=u, schritt1_kasse_erreichbar=kasse_erreichbar, schritt2=s2, schritt3=s3, schritt4=s4)

# TC-14
g0()
u = uhr()
h, _ = ein("AI-900")
offen_vor = zustand()["ein"]
req(PULT + "/pico2", {})
time.sleep(1)
try:
    req(CAM + "/", timeout=3)
    cam_waehrend = "erreichbar"
except Exception as e:
    cam_waehrend = "nicht erreichbar (%s)" % type(e).__name__
z = zustand()
while not z["pico2"]:
    time.sleep(0.2)
    z = zustand()
s1 = {"meldung_einfahrt": meldung(h), "ein_offen_vor_neustart": offen_vor, "cam_waehrend_aus": cam_waehrend,
      "nach_start_ein": z["ein"], "nach_start_aus": z["aus"], "pico2_wieder_an": uhr()}
time.sleep(20)
hc, rt = req(CAM + "/")
n0 = anzahl_oeffnungen("Ausfahrt")
h2, _ = aus("AI-900")
time.sleep(0.3)
s2 = {"ui_erreichbar": "Kamera-Simulation" in hc, "ladezeit_s": round(rt, 3), "meldung": meldung(h2),
      "geoeffnet": anzahl_oeffnungen("Ausfahrt") != n0, "aus_offen": zustand()["aus"]}
log("TC-14", uhrzeit=u, schritt1=s1, schritt2=s2)

# TC-15
g0()
u = uhr()
s1 = []
for kz in ("SG-321", "SG-322", "SG-323"):
    h, rt = ein(kz)
    t_auf, d = schranke_messen("Einfahrt")
    s1.append({"kz": kz, "oeffnet_s": t_auf, "offen_s": d, "http_s": round(rt, 3)})
lade = {}
for name, url in (("kamera", CAM + "/"), ("kasse", KASSE + "/"), ("admin", KASSE + "/admin")):
    lade[name] = [round(req(url)[1], 3) for _ in range(3)]
log("TC-15", uhrzeit=u, schritt1=s1, schritt2=lade)

R["ende"] = uhr()
print("Ende", R["ende"])
with open(sys.argv[1], "w", encoding="utf-8") as f:
    json.dump(R, f, ensure_ascii=False, indent=1)
