// Tests fuer das serielle Befehlsprotokoll (wird auch vom Python-Skript genutzt).

#include <string.h>
#include <unity.h>

#include "Protocol.h"

void setUp() {}
void tearDown() {}

void test_commands_case_insensitive() {
  TEST_ASSERT_EQUAL(Command::Toggle, parseCommand('S'));
  TEST_ASSERT_EQUAL(Command::Toggle, parseCommand('s'));
  TEST_ASSERT_EQUAL(Command::Reset, parseCommand('R'));
  TEST_ASSERT_EQUAL(Command::Reset, parseCommand('r'));
  TEST_ASSERT_EQUAL(Command::Help, parseCommand('H'));
  TEST_ASSERT_EQUAL(Command::Help, parseCommand('h'));
  TEST_ASSERT_EQUAL(Command::Status, parseCommand('?'));
}

void test_whitespace_is_ignored() {
  TEST_ASSERT_EQUAL(Command::None, parseCommand('\n'));
  TEST_ASSERT_EQUAL(Command::None, parseCommand('\r'));
  TEST_ASSERT_EQUAL(Command::None, parseCommand(' '));
  TEST_ASSERT_EQUAL(Command::None, parseCommand('\t'));
}

void test_unknown_command() {
  TEST_ASSERT_EQUAL(Command::Unknown, parseCommand('x'));
  TEST_ASSERT_EQUAL(Command::Unknown, parseCommand('1'));
}

void test_state_names() {
  TEST_ASSERT_EQUAL_STRING("STANDBY", stateName(CountdownState::Standby));
  TEST_ASSERT_EQUAL_STRING("COUNTING", stateName(CountdownState::Counting));
  TEST_ASSERT_EQUAL_STRING("PAUSED", stateName(CountdownState::Paused));
  TEST_ASSERT_EQUAL_STRING("URGENT", stateName(CountdownState::Urgent));
  TEST_ASSERT_EQUAL_STRING("ALARM", stateName(CountdownState::Alarm));
}

int runTests() {
  UNITY_BEGIN();
  RUN_TEST(test_commands_case_insensitive);
  RUN_TEST(test_whitespace_is_ignored);
  RUN_TEST(test_unknown_command);
  RUN_TEST(test_state_names);
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
