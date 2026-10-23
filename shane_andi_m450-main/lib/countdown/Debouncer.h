#pragma once

// Entprellung fuer einen Taster. Hardware-unabhaengig: Der rohe Zustand
// ("gedrueckt ja/nein") wird von aussen uebergeben, z.B. aus digitalRead().

#include <stdint.h>

class Debouncer {
 public:
  explicit Debouncer(uint32_t delayMs);

  // Einmal in setup() aufrufen. Ein beim Einschalten bereits gedrueckter
  // Taster loest dadurch kein Ereignis aus.
  void begin(bool pressed, uint32_t nowMs);

  // Liefert genau einmal true, wenn der Taster stabil gedrueckt wurde
  // (Druckflanke). Gedrueckt halten loest nicht mehrfach aus.
  bool update(bool pressed, uint32_t nowMs);

  bool isPressed() const { return stablePressed_; }

 private:
  uint32_t delayMs_;
  bool stablePressed_;
  bool lastReading_;
  uint32_t changedAtMs_;
};
