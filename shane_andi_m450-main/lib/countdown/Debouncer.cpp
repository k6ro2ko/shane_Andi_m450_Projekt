#include "Debouncer.h"

Debouncer::Debouncer(uint32_t delayMs)
    : delayMs_(delayMs), stablePressed_(false), lastReading_(false), changedAtMs_(0) {}

void Debouncer::begin(bool pressed, uint32_t nowMs) {
  stablePressed_ = pressed;
  lastReading_ = pressed;
  changedAtMs_ = nowMs;
}

bool Debouncer::update(bool pressed, uint32_t nowMs) {
  if (pressed != lastReading_) {
    lastReading_ = pressed;
    changedAtMs_ = nowMs;
  }

  if (nowMs - changedAtMs_ < delayMs_ || pressed == stablePressed_) {
    return false;
  }

  stablePressed_ = pressed;
  return pressed;
}
