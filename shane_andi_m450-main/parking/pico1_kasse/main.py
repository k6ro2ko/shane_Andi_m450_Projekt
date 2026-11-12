# Pico 1 – Kasse (192.168.4.1). Startet automatisch beim Einschalten.
try:
    import asyncio
except ImportError:
    import uasyncio as asyncio
import gc

import config
import netz
import webutil
from kasse_app import KasseApp
from parkhaus import Parkhaus


async def start():
    wlan = netz.verbinden(config.WLAN_SSID, config.WLAN_PASSWORT, config.IP,
                          config.MASKE, config.GATEWAY, config.DNS)
    app = KasseApp(Parkhaus(config.KAPAZITAET), datei=config.DATENDATEI, admin=config.ADMIN_AKTIV)

    async def verbindung(reader, writer):
        await webutil.bediene(reader, writer, app.route)
        gc.collect()

    await asyncio.start_server(verbindung, "0.0.0.0", 80, backlog=5)
    print("Kasse bereit: http://%s/  Admin: http://%s/admin" % (config.IP, config.IP))
    await netz.ueberwachen(wlan, config.WLAN_SSID, config.WLAN_PASSWORT, config.IP,
                           config.MASKE, config.GATEWAY, config.DNS)


asyncio.run(start())
