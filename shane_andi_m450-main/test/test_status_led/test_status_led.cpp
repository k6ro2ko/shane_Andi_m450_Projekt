// Tests fuer das LED-Blinkmuster.

#include <unity.h>

#include "StatusLed.h"

void setUp() {}
void tearDown() {}

void test_intervals_per_state() {
  TEST_ASSERT_EQUAL_UINT32(1000, StatusLed::blinkIntervalMs(CountdownState::Standby));
  TEST_ASSERT_EQUAL_UINT32(500, StatusLed::blinkIntervalMs(CountdownState::Counting));
  TEST_ASSERT_EQUAL_UINT32(200, StatusLed::blinkIntervalMs(CountdownState::Paused));
  TEST_ASSERT_EQUAL_UINT32(100, StatusLed::blinkIntervalMs(CountdownState::Urgent));
}

void test_blinks_with_interval() {
  StatusLed led;
  TEST_ASSERT_FALSE(led.update(CountdownState::Counting, 0));
  TEST_ASSERT_FALSE(led.update(CountdownState::Counting, 499));
  TEST_ASSERT_TRUE(led.update(CountdownState::Counting, 500));
  TEST_ASSERT_TRUE(led.update(CountdownState::Counting, 999));
  TEST_ASSERT_FALSE(led.update(CountdownState::Counting, 1000));
}

void test_alarm_is_steady_on() {
  StatusLed led;
  for (uint32_t t = 0; t < 5000; t += 10) {
    TEST_ASSERT_TRUE(led.update(CountdownState::Alarm, t));
  }
}

void test_blinking_resumes_after_alarm() {
  StatusLed led;
  led.update(CountdownState::Alarm, 1000);
  TEST_ASSERT_TRUE(led.update(CountdownState::Standby, 1999));
  TEST_ASSERT_FALSE(led.update(CountdownState::Standby, 2000));
}

int runTests() {
  UNITY_BEGIN();
  RUN_TEST(test_intervals_per_state);
  RUN_TEST(test_blinks_with_interval);
  RUN_TEST(test_alarm_is_steady_on);
  RUN_TEST(test_blinking_resumes_after_alarm);
  return UNITY_END();
}

#ifdef ARDUINO
#include <Arduino.h>
void setup() {
  delay(2000);
  runTests();
}
void loop() {}
#else
int main() { return runTests(); }
#endif
