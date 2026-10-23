// Tests fuer die Taster-Entprellung.

#include <unity.h>

#include "Debouncer.h"

namespace {
const uint32_t DELAY_MS = 30;
}

void setUp() {}
void tearDown() {}

void test_stable_press_triggers_once() {
  Debouncer button(DELAY_MS);
  button.begin(false, 0);
  TEST_ASSERT_FALSE(button.update(true, 100));
  TEST_ASSERT_FALSE(button.update(true, 129));
  TEST_ASSERT_TRUE(button.update(true, 130));
  TEST_ASSERT_TRUE(button.isPressed());
}

void test_holding_does_not_retrigger() {
  Debouncer button(DELAY_MS);
  button.begin(false, 0);
  button.update(true, 100);
  TEST_ASSERT_TRUE(button.update(true, 130));
  for (uint32_t t = 140; t < 5000; t += 10) {
    TEST_ASSERT_FALSE(button.update(true, t));
  }
}

void test_bouncing_is_ignored() {
  Debouncer button(DELAY_MS);
  button.begin(false, 0);
  // Prellen: wechselt schneller als 30 ms
  TEST_ASSERT_FALSE(button.update(true, 100));
  TEST_ASSERT_FALSE(button.update(false, 105));
  TEST_ASSERT_FALSE(button.update(true, 110));
  TEST_ASSERT_FALSE(button.update(false, 120));
  TEST_ASSERT_FALSE(button.update(true, 125));
  TEST_ASSERT_FALSE(button.update(true, 154));
  TEST_ASSERT_TRUE(button.update(true, 155));
}

void test_release_does_not_trigger() {
  Debouncer button(DELAY_MS);
  button.begin(false, 0);
  button.update(true, 100);
  button.update(true, 130);
  button.update(false, 200);
  TEST_ASSERT_FALSE(button.update(false, 230));
  TEST_ASSERT_FALSE(button.isPressed());
}

void test_second_press_triggers_again() {
  Debouncer button(DELAY_MS);
  button.begin(false, 0);
  button.update(true, 100);
  TEST_ASSERT_TRUE(button.update(true, 130));
  button.update(false, 200);
  button.update(false, 230);
  button.update(true, 300);
  TEST_ASSERT_TRUE(button.update(true, 330));
}

void test_pressed_at_boot_does_not_trigger() {
  Debouncer button(DELAY_MS);
  button.begin(true, 0);
  for (uint32_t t = 10; t < 1000; t += 10) {
    TEST_ASSERT_FALSE(button.update(true, t));
  }
}

int runTests() {
  UNITY_BEGIN();
  RUN_TEST(test_stable_press_triggers_once);
  RUN_TEST(test_holding_does_not_retrigger);
  RUN_TEST(test_bouncing_is_ignored);
  RUN_TEST(test_release_does_not_trigger);
  RUN_TEST(test_second_press_triggers_again);
  RUN_TEST(test_pressed_at_boot_does_not_trigger);
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
