# Pico 2 – Schranken + Kamera-Sim-UI (192.168.4.2). Startet automatisch beim Einschalten.
import config
from schranke import Schranke

einfahrt = Schranke("Einfahrt", config.EINFAHRT_SERVO, config.EINFAHRT_LED_ROT, config.EINFAHRT_LED_GRUEN,
                    config.SERVO_ZU_US, config.SERVO_OFFEN_US)
ausfahrt = Schranke("Ausfahrt", config.AUSFAHRT_SERVO, config.AUSFAHRT_LED_ROT, config.AUSFAHRT_LED_GRUEN,
                    config.SERVO_ZU_US, config.SERVO_OFFEN_US)

try:
    import asyncio
except ImportError:
    import uasyncio as asyncio
import gc

import m2m
import netz
import webutil
from schranken_app import SchrankenApp


async def schranken_takt():
    while True:
        einfahrt.tick()
        ausfahrt.tick()
        await asyncio.sleep_ms(50)


async def start():
    asyncio.create_task(schranken_takt())
    if config.WLAN_MODUS == "ap":
        wlan = netz.access_point(config.WLAN_SSID, config.WLAN_PASSWORT, config.IP, config.MASKE)
    else:
        wlan = netz.verbinden(config.WLAN_SSID, config.WLAN_PASSWORT, config.IP,
                              config.MASKE, config.GATEWAY, config.DNS)
    app = SchrankenApp(einfahrt, ausfahrt, m2m.anfrage, config.KASSE_HOST,
                       config.M2M_TIMEOUT_MS, config.STATUS_TIMEOUT_MS, config.SCHRANKE_OFFEN_S)

    async def verbindung(reader, writer):
        await webutil.bediene(reader, writer, app.route)
        gc.collect()

    await asyncio.start_server(verbindung, "0.0.0.0", 80, backlog=5)
    print("Schranken bereit: http://%s/" % config.IP)
    if config.WLAN_MODUS == "ap":
        while True:
            await asyncio.sleep(60)
    await netz.ueberwachen(wlan, config.WLAN_SSID, config.WLAN_PASSWORT, config.IP,
                           config.MASKE, config.GATEWAY, config.DNS)


try:
    asyncio.run(start())
finally:
    einfahrt.schliessen()
    ausfahrt.schliessen()
