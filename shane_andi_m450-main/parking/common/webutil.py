# Kleiner HTTP-Server fuer beide Picos. Laeuft auch mit normalem Python (Tests, Simulator).
try:
    import asyncio
except ImportError:
    import uasyncio as asyncio

MAX_BODY = 2048
MAX_HEADER_ZEILEN = 64
ANFRAGE_TIMEOUT_S = 5
ZU_GROSS = "ZU_GROSS"
_HEX = "0123456789abcdefABCDEF"


def esc(text):
    if text is None:
        return ""
    return (str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;").replace("'", "&#39;"))


def kuerze(text, n=64):
    return text if len(text) <= n else text[:n] + "…"


def url_decode(s):
    s = s.replace("+", " ")
    if "%" not in s:
        return s
    b = s.encode()
    out = bytearray()
    i = 0
    n = len(b)
    while i < n:
        c = b[i]
        if c == 37 and i + 2 < n and chr(b[i + 1]) in _HEX and chr(b[i + 2]) in _HEX:
            out.append(int(chr(b[i + 1]) + chr(b[i + 2]), 16))
            i += 3
            continue
        out.append(c)
        i += 1
    try:
        return bytes(out).decode("utf-8")
    except Exception:
        return ""


def url_encode(s):
    sicher = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_.~"
    out = []
    for byte in str(s).encode():
        ch = chr(byte)
        out.append(ch if ch in sicher else "%%%02X" % byte)
    return "".join(out)


def parse_qs(s, max_felder=20):
    felder = {}
    if not s:
        return felder
    for teil in s.split("&")[:max_felder]:
        if not teil:
            continue
        k, _, v = teil.partition("=")
        felder[url_decode(k)] = url_decode(v)
    return felder


# gibt (methode, pfad, query, form) zurueck, ZU_GROSS oder None
async def lese_anfrage(reader):
    zeile = await reader.readline()
    if not zeile:
        return None
    try:
        teile = zeile.decode().split()
    except Exception:
        return None
    if len(teile) < 2:
        return None
    methode, ziel = teile[0], teile[1]
    laenge = 0
    for _ in range(MAX_HEADER_ZEILEN):
        h = await reader.readline()
        if not h or h in (b"\r\n", b"\n"):
            break
        try:
            name, _, wert = h.decode().partition(":")
            if name.strip().lower() == "content-length":
                laenge = int(wert.strip())
        except Exception:
            pass
    if laenge > MAX_BODY or laenge < 0:
        return ZU_GROSS
    body = b""
    if laenge:
        body = await reader.readexactly(laenge)
    pfad, _, qs = ziel.partition("?")
    try:
        form = parse_qs(body.decode())
    except Exception:
        form = {}
    return methode, pfad, parse_qs(qs), form


async def sende(writer, status, body, ctype="text/html; charset=utf-8", extra=""):
    if isinstance(body, str):
        body = body.encode()
    kopf = ("HTTP/1.0 %s\r\nContent-Type: %s\r\nContent-Length: %d\r\n"
            "Cache-Control: no-store\r\nConnection: close\r\n%s\r\n") % (status, ctype, len(body), extra)
    writer.write(kopf.encode())
    writer.write(body)
    await writer.drain()


def _fehler_ausgeben(e):
    try:
        import sys
        sys.print_exception(e)
    except Exception:
        print("Fehler:", repr(e))


# Eine Verbindung abarbeiten. route(methode, pfad, q, f) gibt (status, body) zurueck,
# optional noch Content-Type und weitere Header.
async def bediene(reader, writer, route):
    try:
        anfrage = await asyncio.wait_for(lese_anfrage(reader), ANFRAGE_TIMEOUT_S)
        if anfrage is None:
            return
        if anfrage == ZU_GROSS:
            await sende(writer, "413 Payload Too Large", "Anfrage zu gross", "text/plain; charset=utf-8")
            return
        antwort = await route(*anfrage)
        await sende(writer, *antwort)
    except Exception as e:
        _fehler_ausgeben(e)
        try:
            await sende(writer, "500 Internal Server Error", "Interner Fehler", "text/plain; charset=utf-8")
        except Exception:
            pass
    finally:
        try:
            writer.close()
            await writer.wait_closed()
        except Exception:
            pass


CSS = (
    "*{box-sizing:border-box}body{margin:0;font-family:system-ui,sans-serif;font-size:18px;"
    "background:#f4f5f7;color:#1c1e21}main{max-width:720px;margin:0 auto;padding:16px}"
    "h1{font-size:1.5em;margin:.2em 0 .6em}h2{font-size:1.15em;margin:1em 0 .4em}"
    "section{background:#fff;border-radius:10px;padding:14px;margin:0 0 14px;"
    "box-shadow:0 1px 3px rgba(0,0,0,.12)}"
    "input[type=text],input[type=number]{font-size:1em;padding:10px;width:100%;"
    "border:1px solid #999;border-radius:6px}"
    "button{font-size:1em;padding:12px 16px;margin-top:8px;border:0;border-radius:6px;"
    "background:#0b5cad;color:#fff;cursor:pointer;min-height:44px}"
    "button:disabled{background:#aab;cursor:not-allowed}button.rot{background:#b3261e}"
    ".m{padding:12px;border-radius:6px;font-weight:600;word-break:break-all}"
    ".ok{background:#dff3e3;color:#14532d}.err{background:#fde2e1;color:#7f1d1d}"
    ".info{background:#e7eefb;color:#1e3a8a}"
    ".betrag{font-size:2em;font-weight:700;margin:.2em 0}"
    "table{border-collapse:collapse;width:100%;font-size:.85em}"
    "td,th{border-bottom:1px solid #ddd;padding:6px;text-align:left;vertical-align:top}"
    ".scroll{overflow-x:auto}label{display:block;margin:.4em 0}"
    "dl{display:grid;grid-template-columns:auto 1fr;gap:4px 12px;margin:0}dt{color:#555}"
    "dd{margin:0;font-weight:600}.klein{font-size:.8em;color:#555}"
)


def seite(titel, inhalt, url=None, script=""):
    rs = ""
    if url:
        rs = "<script>history.replaceState(null,'','%s')</script>" % url
    return ("<!DOCTYPE html><html lang='de'><head><meta charset='utf-8'>"
            "<meta name='viewport' content='width=device-width,initial-scale=1'>"
            "<title>%s</title><style>%s</style></head><body><main>%s</main>%s%s</body></html>"
            % (esc(titel), CSS, inhalt, rs, script))


def meldung(text, art="ok"):
    return "<p class='m %s' id='meldung'>%s</p>" % (art, esc(text))
