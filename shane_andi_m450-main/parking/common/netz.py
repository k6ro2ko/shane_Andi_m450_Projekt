# WLAN mit fester IP. Onboard-LED: blinkt = sucht, an = verbunden.
import time

import network
from machine import Pin

_led = Pin("LED", Pin.OUT)


def verbinden(ssid, passwort, ip, maske, gateway, dns, versuche_s=30):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    try:
        wlan.config(pm=0xA11140)
    except Exception:
        pass
    if not wlan.isconnected():
        wlan.connect(ssid, passwort)
        start = time.time()
        while not wlan.isconnected() and time.time() - start < versuche_s:
            _led.toggle()
            time.sleep(0.25)
    if wlan.isconnected():
        wlan.ifconfig((ip, maske, gateway, dns))
        _led.on()
        print("WLAN verbunden:", wlan.ifconfig())
    else:
        _led.off()
        print("WLAN NICHT verbunden, SSID/Passwort in config.py pruefen")
    return wlan


def access_point(ssid, passwort, ip, maske):
    ap = network.WLAN(network.AP_IF)
    ap.config(ssid=ssid, password=passwort)
    ap.active(True)
    while not ap.active():
        time.sleep(0.1)
    ap.ifconfig((ip, maske, ip, ip))
    _led.on()
    print("Access Point aktiv:", ssid, ap.ifconfig())
    return ap


# alle 3 s schauen ob das WLAN noch da ist, sonst neu verbinden
async def ueberwachen(wlan, ssid, passwort, ip, maske, gateway, dns):
    try:
        import asyncio
    except ImportError:
        import uasyncio as asyncio
    while True:
        await asyncio.sleep(3)
        if not wlan.isconnected():
            _led.off()
            print("WLAN getrennt, verbinde neu")
            try:
                wlan.connect(ssid, passwort)
                for _ in range(40):
                    if wlan.isconnected():
                        wlan.ifconfig((ip, maske, gateway, dns))
                        _led.on()
                        break
                    await asyncio.sleep(0.25)
            except Exception as e:
                print("WLAN-Fehler:", e)
