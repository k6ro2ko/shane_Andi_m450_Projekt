# Pico 2 fragt Pico 1 per HTTP. Wenn die Kasse nicht innert timeout_ms antwortet,
# kommt None zurueck (Kasse aus). Darum eigene Sockets statt asyncio.open_connection.
import json
import select
import socket

try:
    import asyncio
except ImportError:
    import uasyncio as asyncio

try:
    from time import ticks_diff, ticks_ms
except ImportError:
    import time as _t

    def ticks_ms():
        return int(_t.monotonic() * 1000)

    def ticks_diff(a, b):
        return a - b

import webutil

MAX_ANTWORT = 4096
# EAGAIN/EWOULDBLOCK auf Pico, Linux, Mac und Windows
_WOULDBLOCK = (11, 35, 115, 10035)


async def _schlafen(ms):
    if hasattr(asyncio, "sleep_ms"):
        await asyncio.sleep_ms(ms)
    else:
        await asyncio.sleep(ms / 1000)


def _bereit(sock, schreiben):
    if hasattr(select, "poll"):
        p = select.poll()
        p.register(sock, select.POLLOUT if schreiben else select.POLLIN)
        return bool(p.poll(0))
    r, wl, x = select.select([] if schreiben else [sock], [sock] if schreiben else [], [sock], 0)
    if x:
        raise OSError("Verbindung fehlgeschlagen")
    return bool(r or wl)


# POST wenn daten mitgegeben werden, sonst GET. Gibt das JSON als dict zurueck.
async def anfrage(host, pfad, daten=None, timeout_ms=4000, port=80):
    start = ticks_ms()

    def abgelaufen():
        return ticks_diff(ticks_ms(), start) >= timeout_ms

    s = None
    try:
        s = socket.socket()
        s.setblocking(False)
        try:
            s.connect(socket.getaddrinfo(host, port)[0][-1])
        except OSError:
            pass
        while not _bereit(s, True):
            if abgelaufen():
                return None
            await _schlafen(10)

        if daten is None:
            anfrage_text = "GET %s HTTP/1.0\r\nHost: %s\r\n\r\n" % (pfad, host)
        else:
            body = "&".join("%s=%s" % (webutil.url_encode(k), webutil.url_encode(v)) for k, v in daten.items())
            anfrage_text = ("POST %s HTTP/1.0\r\nHost: %s\r\nContent-Type: application/x-www-form-urlencoded\r\n"
                            "Content-Length: %d\r\n\r\n%s" % (pfad, host, len(body.encode()), body))
        rest = anfrage_text.encode()
        while rest:
            try:
                n = s.send(rest)
                rest = rest[n:]
            except OSError as e:
                if not _ist_wouldblock(e):
                    return None
            if rest:
                if abgelaufen():
                    return None
                await _schlafen(10)

        puffer = b""
        while len(puffer) < MAX_ANTWORT:
            if _bereit(s, False):
                try:
                    teil = s.recv(512)
                except OSError as e:
                    if _ist_wouldblock(e):
                        teil = None
                    else:
                        return None
                if teil == b"":
                    break
                if teil:
                    puffer += teil
                    continue
            if abgelaufen():
                return None
            await _schlafen(10)

        kopf, _, body = puffer.partition(b"\r\n\r\n")
        if b" 200 " not in kopf.split(b"\r\n")[0] + b" ":
            return None
        antwort = json.loads(body.decode())
        return antwort if isinstance(antwort, dict) else None
    except Exception:
        return None
    finally:
        if s is not None:
            try:
                s.close()
            except Exception:
                pass


def _ist_wouldblock(e):
    return bool(e.args) and e.args[0] in _WOULDBLOCK
