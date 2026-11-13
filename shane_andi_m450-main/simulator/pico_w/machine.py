# Ersatz fuer das MicroPython-Modul machine auf dem PC.
# Jede Aenderung an einem Pin wird als "@sim ..." ausgegeben, sim.py zeigt das im Steuerpult an.


def melden(*teile):
    print("@sim", *teile, flush=True)


class Pin:
    IN = 0
    OUT = 1
    PULL_UP = 1
    PULL_DOWN = 2

    def __init__(self, nr, modus=-1, pull=-1, value=None):
        self.nr = nr
        self._wert = 0
        if value is not None:
            self.value(value)

    def value(self, v=None):
        if v is None:
            return self._wert
        v = 1 if v else 0
        if v != self._wert:
            self._wert = v
            melden("pin", self.nr, v)

    __call__ = value

    def on(self):
        self.value(1)

    def off(self):
        self.value(0)

    def toggle(self):
        self.value(not self._wert)


class PWM:
    def __init__(self, pin, freq=50, duty_ns=0):
        self.pin = pin
        self._freq = freq
        self._ns = 0
        if duty_ns:
            self.duty_ns(duty_ns)

    def freq(self, f=None):
        if f is None:
            return self._freq
        self._freq = f

    def duty_ns(self, ns=None):
        if ns is None:
            return self._ns
        if ns != self._ns:
            self._ns = ns
            melden("pwm", self.pin.nr, ns)

    def duty_u16(self, d=None):
        periode_ns = 1000000000 // self._freq
        if d is None:
            return self._ns * 65535 // periode_ns
        self.duty_ns(d * periode_ns // 65535)

    def deinit(self):
        self.duty_ns(0)


def reset():
    raise SystemExit("machine.reset()")
