// Firmware: Countdown mit zwei Tastern, Status-LEDs und seriellem Befehlsprotokoll.
//
// Diese Datei ist nur die "Hardware-Schicht": Pins lesen/schreiben und Serial.
// Die eigentliche Logik liegt in lib/countdown/ und ist dort getestet.

#include <Arduino.h>

#include "Countdown.h"
#include "Debouncer.h"
#include "Protocol.h"
#include "StatusLed.h"
#include "config.h"

namespace {

Countdown countdown(COUNTDOWN_START_SECONDS, COUNTDOWN_ALARM_DURATION_MS);
Debouncer startButton(BUTTON_DEBOUNCE_MS);
Debouncer resetButton(BUTTON_DEBOUNCE_MS);
StatusLed statusLed;
bool ledsOn = false;

// Taster sind gegen GND geschaltet (interner Pull-Up): gedrueckt = LOW.
bool isPressed(uint8_t pin) { return digitalRead(pin) == LOW; }

void writeLeds(bool on) {
  digitalWrite(PIN_LED_EXTERNAL, on ? HIGH : LOW);
  digitalWrite(PIN_LED_ONBOARD, on ? HIGH : LOW);
  ledsOn = on;
}

void printRemaining() {
  Serial.print(F("[COUNTDOWN] Restzeit: "));
  Serial.print(countdown.remainingSeconds());
  Serial.println(F("s"));
}

void printStatus() {
  Serial.print(F("[STATUS] state="));
  Serial.print(stateName(countdown.state()));
  Serial.print(F(" remaining="));
  Serial.println(countdown.remainingSeconds());
}

void printHelp() {
  Serial.println(F("[HELP] S = Start/Pause/Fortsetzen, R = Reset, ? = Status, H = Hilfe"));
}

void report(CountdownEvent event) {
  switch (event) {
    case CountdownEvent::Started:
      Serial.println(F("[FSM] Gestartet."));
      break;
    case CountdownEvent::Resumed:
      Serial.println(F("[FSM] Fortgesetzt."));
      break;
    case CountdownEvent::Paused:
      Serial.println(F("[FSM] Pausiert."));
      break;
    case CountdownEvent::Reset:
      Serial.println(F("[FSM] Reset auf Startwert."));
      break;
    case CountdownEvent::Tick:
      printRemaining();
      break;
    case CountdownEvent::AlarmStarted:
      printRemaining();
      Serial.println(F("[ALARM] Zielwert T0 = 0 erreicht!"));
      break;
    case CountdownEvent::AlarmEnded:
      Serial.println(F("[ALARM] Alarm beendet. Rueckkehr zu Standby."));
      break;
    case CountdownEvent::Ignored:
      Serial.println(F("[FSM] Ignoriert: Alarm aktiv, nur Reset moeglich."));
      break;
    case CountdownEvent::None:
      break;
  }
}

void handleCommand(Command command, uint32_t now) {
  switch (command) {
    case Command::Toggle:
      report(countdown.toggle(now));
      break;
    case Command::Reset:
      report(countdown.reset(now));
      break;
    case Command::Status:
      printStatus();
      break;
    case Command::Help:
      printHelp();
      break;
    case Command::Unknown:
      Serial.println(F("[ERROR] Unbekannter Befehl. H fuer Hilfe."));
      break;
    case Command::None:
      break;
  }
}

void handleInput(uint32_t now) {
  if (startButton.update(isPressed(PIN_BUTTON_START), now)) {
    handleCommand(Command::Toggle, now);
  }
  if (resetButton.update(isPressed(PIN_BUTTON_RESET), now)) {
    handleCommand(Command::Reset, now);
  }

  while (Serial.available() > 0) {
    handleCommand(parseCommand(static_cast<char>(Serial.read())), now);
  }
}

void updateLeds(uint32_t now) {
  const bool on = statusLed.update(countdown.state(), now);
  // Nur bei Aenderung schreiben: Beim Pico W laeuft die Onboard-LED ueber den
  // WLAN-Chip, jeder Schreibzugriff ist dort vergleichsweise langsam.
  if (on != ledsOn) {
    writeLeds(on);
  }
}

}  // namespace

void setup() {
  Serial.begin(SERIAL_BAUD);
  // USB-Serial (Pico, Leonardo, ...) braucht einen Moment, bis der PC verbunden
  // ist. Ohne Wartezeit gehen die ersten Zeilen verloren. Beim Uno ist Serial
  // sofort bereit, die Schleife endet dann direkt.
  const uint32_t serialWaitStart = millis();
  while (!Serial && millis() - serialWaitStart < SERIAL_WAIT_MS) {
    delay(10);
  }

  pinMode(PIN_LED_ONBOARD, OUTPUT);
  pinMode(PIN_LED_EXTERNAL, OUTPUT);
  pinMode(PIN_BUTTON_START, INPUT_PULLUP);
  pinMode(PIN_BUTTON_RESET, INPUT_PULLUP);
  writeLeds(false);

  const uint32_t now = millis();
  startButton.begin(isPressed(PIN_BUTTON_START), now);
  resetButton.begin(isPressed(PIN_BUTTON_RESET), now);
  countdown.reset(now);

  Serial.print(F(APP_BOARD_NAME));
  Serial.println(F(" - Countdown System"));
  printHelp();
  printStatus();
}

void loop() {
  const uint32_t now = millis();
  handleInput(now);
  report(countdown.update(now));
  updateLeds(now);
}
