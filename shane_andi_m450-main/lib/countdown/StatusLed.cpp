#include "StatusLed.h"

StatusLed::StatusLed() : on_(false), lastToggleMs_(0) {}

uint32_t StatusLed::blinkIntervalMs(CountdownState state) {
  switch (state) {
    case CountdownState::Counting:
      return 500;
    case CountdownState::Paused:
      return 200;
    case CountdownState::Urgent:
      return 100;
    case CountdownState::Alarm:
      return 0;  // kein Blinken, dauerhaft an
    case CountdownState::Standby:
      break;
  }
  return 1000;
}

bool StatusLed::update(CountdownState state, uint32_t nowMs) {
  if (state == CountdownState::Alarm) {
    on_ = true;
    lastToggleMs_ = nowMs;
    return on_;
  }

  if (nowMs - lastToggleMs_ >= blinkIntervalMs(state)) {
    lastToggleMs_ = nowMs;
    on_ = !on_;
  }
  return on_;
}
