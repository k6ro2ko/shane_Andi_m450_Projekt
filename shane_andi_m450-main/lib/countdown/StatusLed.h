#pragma once

// Berechnet, ob die Status-LEDs gerade leuchten sollen. Schaltet selbst keine
// Pins, damit es ohne Hardware testbar ist.
//
//   Standby  -> blinkt langsam (1000 ms)
//   Counting -> blinkt (500 ms)
//   Paused   -> blinkt schnell (200 ms)
//   Urgent   -> blinkt sehr schnell (100 ms)
//   Alarm    -> leuchtet dauerhaft

#include <stdint.h>

#include "Countdown.h"

class StatusLed {
 public:
  StatusLed();

  // Liefert den gewuenschten LED-Zustand (true = an).
  bool update(CountdownState state, uint32_t nowMs);

  static uint32_t blinkIntervalMs(CountdownState state);

 private:
  bool on_;
  uint32_t lastToggleMs_;
};
