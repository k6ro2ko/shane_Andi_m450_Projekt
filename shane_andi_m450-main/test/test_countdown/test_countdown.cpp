// Tests fuer die Countdown-Zustandsmaschine.
// Laufen auf dem PC (`pio test -e native`) und auf dem Board (`pio test -e pico`).

#include <unity.h>

#include "Countdown.h"

namespace {
const uint32_t START = 60;
const uint32_t ALARM_MS = 5000;

// Laesst den Countdown `seconds` Sekunden lang laufen (update() alle 10 ms,
// wie es loop() auf dem Board auch tun wuerde). Gibt die neue Zeit zurueck.
uint32_t runFor(Countdown& countdown, uint32_t nowMs, uint32_t durationMs) {
  const uint32_t end = nowMs + durationMs;
  while (nowMs != end) {
    nowMs += 10;
    countdown.update(nowMs);
  }
  return nowMs;
}
}  // namespace

void setUp() {}
void tearDown() {}

void test_starts_in_standby_with_start_value() {
  Countdown countdown(START, ALARM_MS);
  TEST_ASSERT_EQUAL(CountdownState::Standby, countdown.state());
  TEST_ASSERT_EQUAL_UINT32(START, countdown.remainingSeconds());
}

void test_does_not_count_in_standby() {
  Countdown countdown(START, ALARM_MS);
  runFor(countdown, 0, 5000);
  TEST_ASSERT_EQUAL_UINT32(START, countdown.remainingSeconds());
}

void test_toggle_starts_counting() {
  Countdown countdown(START, ALARM_MS);
  TEST_ASSERT_EQUAL(CountdownEvent::Started, countdown.toggle(0));
  TEST_ASSERT_EQUAL(CountdownState::Counting, countdown.state());
}

void test_counts_one_second_per_tick() {
  Countdown countdown(START, ALARM_MS);
  countdown.toggle(0);
  TEST_ASSERT_EQUAL(CountdownEvent::None, countdown.update(999));
  TEST_ASSERT_EQUAL(CountdownEvent::Tick, countdown.update(1000));
  TEST_ASSERT_EQUAL_UINT32(START - 1, countdown.remainingSeconds());
}

void test_late_update_does_not_drift() {
  Countdown countdown(START, ALARM_MS);
  countdown.toggle(0);
  // loop() kam 300 ms zu spaet, naechster Tick trotzdem bei 2000 ms.
  TEST_ASSERT_EQUAL(CountdownEvent::Tick, countdown.update(1300));
  TEST_ASSERT_EQUAL(CountdownEvent::None, countdown.update(1999));
  TEST_ASSERT_EQUAL(CountdownEvent::Tick, countdown.update(2000));
}

void test_pause_stops_counting() {
  Countdown countdown(START, ALARM_MS);
  countdown.toggle(0);
  uint32_t now = runFor(countdown, 0, 3000);
  TEST_ASSERT_EQUAL(CountdownEvent::Paused, countdown.toggle(now));
  runFor(countdown, now, 10000);
  TEST_ASSERT_EQUAL(CountdownState::Paused, countdown.state());
  TEST_ASSERT_EQUAL_UINT32(START - 3, countdown.remainingSeconds());
}

void test_pause_keeps_started_second() {
  Countdown countdown(START, ALARM_MS);
  countdown.toggle(0);
  countdown.toggle(700);                // Pause nach 700 ms
  countdown.toggle(5000);               // Fortsetzen
  TEST_ASSERT_EQUAL(CountdownEvent::None, countdown.update(5299));
  TEST_ASSERT_EQUAL(CountdownEvent::Tick, countdown.update(5300));  // 700 + 300 = 1 s
}

void test_resume_in_urgent_phase_stays_urgent() {
  Countdown countdown(START, ALARM_MS);
  countdown.toggle(0);
  uint32_t now = runFor(countdown, 0, (START - 5) * 1000);
  TEST_ASSERT_EQUAL(CountdownState::Urgent, countdown.state());
  countdown.toggle(now);
  TEST_ASSERT_EQUAL(CountdownEvent::Resumed, countdown.toggle(now + 100));
  TEST_ASSERT_EQUAL(CountdownState::Urgent, countdown.state());
}

void test_urgent_in_last_ten_percent() {
  Countdown countdown(START, ALARM_MS);
  countdown.toggle(0);
  uint32_t now = runFor(countdown, 0, (START - 7) * 1000);
  TEST_ASSERT_EQUAL(CountdownState::Counting, countdown.state());
  runFor(countdown, now, 1000);
  TEST_ASSERT_EQUAL_UINT32(6, countdown.remainingSeconds());
  TEST_ASSERT_EQUAL(CountdownState::Urgent, countdown.state());
}

void test_alarm_at_zero() {
  Countdown countdown(START, ALARM_MS);
  countdown.toggle(0);
  runFor(countdown, 0, START * 1000);
  TEST_ASSERT_EQUAL(CountdownState::Alarm, countdown.state());
  TEST_ASSERT_EQUAL_UINT32(0, countdown.remainingSeconds());
}

void test_alarm_ends_after_duration() {
  Countdown countdown(3, ALARM_MS);
  countdown.toggle(0);
  countdown.update(1000);
  countdown.update(2000);
  TEST_ASSERT_EQUAL(CountdownEvent::AlarmStarted, countdown.update(3000));
  TEST_ASSERT_EQUAL(CountdownEvent::None, countdown.update(3000 + ALARM_MS - 1));
  TEST_ASSERT_EQUAL(CountdownEvent::AlarmEnded, countdown.update(3000 + ALARM_MS));
  TEST_ASSERT_EQUAL(CountdownState::Standby, countdown.state());
  TEST_ASSERT_EQUAL_UINT32(3, countdown.remainingSeconds());
}

void test_toggle_ignored_during_alarm() {
  Countdown countdown(1, ALARM_MS);
  countdown.toggle(0);
  countdown.update(1000);
  TEST_ASSERT_EQUAL(CountdownEvent::Ignored, countdown.toggle(1500));
  TEST_ASSERT_EQUAL(CountdownState::Alarm, countdown.state());
}

void test_reset_restores_start_value() {
  Countdown countdown(START, ALARM_MS);
  countdown.toggle(0);
  uint32_t now = runFor(countdown, 0, 10000);
  TEST_ASSERT_EQUAL(CountdownEvent::Reset, countdown.reset(now));
  TEST_ASSERT_EQUAL(CountdownState::Standby, countdown.state());
  TEST_ASSERT_EQUAL_UINT32(START, countdown.remainingSeconds());
}

void test_reset_during_alarm() {
  Countdown countdown(1, ALARM_MS);
  countdown.toggle(0);
  countdown.update(1000);
  countdown.reset(1200);
  TEST_ASSERT_EQUAL(CountdownState::Standby, countdown.state());
  TEST_ASSERT_EQUAL_UINT32(1, countdown.remainingSeconds());
}

void test_millis_overflow() {
  // millis() springt nach ~49 Tagen von 0xFFFFFFFF auf 0.
  Countdown countdown(START, ALARM_MS);
  const uint32_t nearOverflow = 0xFFFFFFFFUL - 500;
  countdown.toggle(nearOverflow);
  TEST_ASSERT_EQUAL(CountdownEvent::None, countdown.update(nearOverflow + 999));
  TEST_ASSERT_EQUAL(CountdownEvent::Tick, countdown.update(nearOverflow + 1000));
  TEST_ASSERT_EQUAL_UINT32(START - 1, countdown.remainingSeconds());
}

void test_zero_start_value_is_clamped() {
  Countdown countdown(0, ALARM_MS);
  TEST_ASSERT_EQUAL_UINT32(1, countdown.remainingSeconds());
}

int runTests() {
  UNITY_BEGIN();
  RUN_TEST(test_starts_in_standby_with_start_value);
  RUN_TEST(test_does_not_count_in_standby);
  RUN_TEST(test_toggle_starts_counting);
  RUN_TEST(test_counts_one_second_per_tick);
  RUN_TEST(test_late_update_does_not_drift);
  RUN_TEST(test_pause_stops_counting);
  RUN_TEST(test_pause_keeps_started_second);
  RUN_TEST(test_resume_in_urgent_phase_stays_urgent);
  RUN_TEST(test_urgent_in_last_ten_percent);
  RUN_TEST(test_alarm_at_zero);
  RUN_TEST(test_alarm_ends_after_duration);
  RUN_TEST(test_toggle_ignored_during_alarm);
  RUN_TEST(test_reset_restores_start_value);
  RUN_TEST(test_reset_during_alarm);
  RUN_TEST(test_millis_overflow);
  RUN_TEST(test_zero_start_value_is_clamped);
  return UNITY_END();
}

#ifdef ARDUINO
#include <Arduino.h>
void setup() {
  delay(2000);  // Zeit fuer den seriellen Monitor
  runTests();
}
void loop() {}
#else
int main() { return runTests(); }
#endif
