# Eine Schranke an Pico 2: Servo SG90 und/oder zwei LEDs (rot = zu, gruen = offen)
from machine import PWM, Pin
from time import ticks_add, ticks_diff, ticks_ms


class Schranke:
    def __init__(self, name, servo_pin=None, led_rot=None, led_gruen=None,
                 servo_zu_us=500, servo_offen_us=1500):
        self.name = name
        self._zu_us = servo_zu_us
        self._offen_us = servo_offen_us
        self._rot = Pin(led_rot, Pin.OUT) if led_rot is not None else None
        self._gruen = Pin(led_gruen, Pin.OUT) if led_gruen is not None else None
        self._servo = None
        if servo_pin is not None:
            self._servo = PWM(Pin(servo_pin))
            self._servo.freq(50)
        self._schliessen_um = None
        self.offen = False
        self.schliessen()

    def _stellen(self, offen):
        self.offen = offen
        if self._rot is not None:
            self._rot.value(0 if offen else 1)
        if self._gruen is not None:
            self._gruen.value(1 if offen else 0)
        if self._servo is not None:
            self._servo.duty_ns((self._offen_us if offen else self._zu_us) * 1000)

    def schliessen(self):
        self._schliessen_um = None
        self._stellen(False)

    def oeffnen_fuer(self, sekunden):
        self._stellen(True)
        self._schliessen_um = ticks_add(ticks_ms(), int(sekunden * 1000))

    # wird alle 50 ms aufgerufen und macht die Schranke nach Ablauf der Zeit wieder zu
    def tick(self):
        if self._schliessen_um is not None and ticks_diff(ticks_ms(), self._schliessen_um) >= 0:
            self.schliessen()
