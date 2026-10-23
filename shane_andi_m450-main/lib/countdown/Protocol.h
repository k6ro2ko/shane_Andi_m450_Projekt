#pragma once

// Serielles Protokoll zwischen PC (z.B. Python-Skript) und Board.
// Ein Befehl ist ein einzelnes Zeichen, Gross-/Kleinschreibung egal.
// Zeilenumbrueche und Leerzeichen werden ignoriert, "S\n" funktioniert also auch.
//
//   S  Start / Pause / Fortsetzen
//   R  Reset auf Startwert
//   ?  Status ausgeben:  [STATUS] state=<ZUSTAND> remaining=<SEKUNDEN>
//   H  Hilfe ausgeben

#include "Countdown.h"

enum class Command : uint8_t { None, Toggle, Reset, Status, Help, Unknown };

Command parseCommand(char c);

// Maschinenlesbarer Name, z.B. "COUNTING". Wird vom Python-Skript ausgewertet.
const char* stateName(CountdownState state);
