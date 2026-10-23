#include "Protocol.h"

Command parseCommand(char c) {
  switch (c) {
    case 'S':
    case 's':
      return Command::Toggle;
    case 'R':
    case 'r':
      return Command::Reset;
    case '?':
      return Command::Status;
    case 'H':
    case 'h':
      return Command::Help;
    case '\r':
    case '\n':
    case ' ':
    case '\t':
      return Command::None;
    default:
      return Command::Unknown;
  }
}

const char* stateName(CountdownState state) {
  switch (state) {
    case CountdownState::Standby:
      return "STANDBY";
    case CountdownState::Counting:
      return "COUNTING";
    case CountdownState::Paused:
      return "PAUSED";
    case CountdownState::Urgent:
      return "URGENT";
    case CountdownState::Alarm:
      return "ALARM";
  }
  return "UNKNOWN";
}
