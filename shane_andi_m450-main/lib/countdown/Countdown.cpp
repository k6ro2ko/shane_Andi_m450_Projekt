#include "Countdown.h"

// Hinweis zu Zeitberechnungen: Es wird immer `now - frueher` gerechnet und mit
// einer Dauer verglichen. Mit uint32_t ist das auch dann korrekt, wenn millis()
// nach ca. 49 Tagen ueberlaeuft und wieder bei 0 beginnt.

Countdown::Countdown(uint32_t startSeconds, uint32_t alarmDurationMs)
    : startSeconds_(startSeconds > 0 ? startSeconds : 1),
      alarmDurationMs_(alarmDurationMs),
      urgentThresholdSeconds_(startSeconds_ / 10),
      state_(CountdownState::Standby),
      remainingSeconds_(startSeconds_),
      lastTickMs_(0),
      pausedElapsedMs_(0),
      alarmStartMs_(0) {}

CountdownState Countdown::runningState() const {
  return remainingSeconds_ <= urgentThresholdSeconds_ ? CountdownState::Urgent
                                                      : CountdownState::Counting;
}

void Countdown::restart(uint32_t nowMs) {
  state_ = CountdownState::Standby;
  remainingSeconds_ = startSeconds_;
  lastTickMs_ = nowMs;
  pausedElapsedMs_ = 0;
  alarmStartMs_ = 0;
}

CountdownEvent Countdown::toggle(uint32_t nowMs) {
  switch (state_) {
    case CountdownState::Standby:
      state_ = runningState();
      lastTickMs_ = nowMs;
      return CountdownEvent::Started;

    case CountdownState::Paused:
      // Die bereits angebrochene Sekunde wird beim Fortsetzen beruecksichtigt,
      // sonst wuerde jede Pause die Restzeit um bis zu 1 s verlaengern.
      state_ = runningState();
      lastTickMs_ = nowMs - pausedElapsedMs_;
      return CountdownEvent::Resumed;

    case CountdownState::Counting:
    case CountdownState::Urgent:
      pausedElapsedMs_ = nowMs - lastTickMs_;
      state_ = CountdownState::Paused;
      return CountdownEvent::Paused;

    case CountdownState::Alarm:
      break;
  }
  return CountdownEvent::Ignored;
}

CountdownEvent Countdown::reset(uint32_t nowMs) {
  restart(nowMs);
  return CountdownEvent::Reset;
}

CountdownEvent Countdown::update(uint32_t nowMs) {
  if (isRunning()) {
    if (nowMs - lastTickMs_ < TICK_MS) {
      return CountdownEvent::None;
    }

    // += statt = now: so entsteht keine Drift, falls loop() einmal laenger dauert.
    lastTickMs_ += TICK_MS;
    if (remainingSeconds_ > 0) {
      --remainingSeconds_;
    }

    if (remainingSeconds_ == 0) {
      state_ = CountdownState::Alarm;
      alarmStartMs_ = nowMs;
      return CountdownEvent::AlarmStarted;
    }
    state_ = runningState();
    return CountdownEvent::Tick;
  }

  if (state_ == CountdownState::Alarm && nowMs - alarmStartMs_ >= alarmDurationMs_) {
    restart(nowMs);
    return CountdownEvent::AlarmEnded;
  }

  return CountdownEvent::None;
}
