#pragma once

// Countdown-Zustandsmaschine (FSM).
//
// Diese Datei ist bewusst OHNE <Arduino.h> geschrieben: Die Logik kennt weder
// Pins noch Serial noch millis(). Die aktuelle Zeit wird von aussen uebergeben.
// Dadurch laeuft derselbe Code auf jedem Board (Pico, Uno, Nano, ...) und kann
// auf dem PC ohne Hardware getestet werden (`pio test -e native`).
//
// Nur C++11 verwenden: Der AVR-Compiler (Uno/Nano) kann nicht mehr.

#include <stdint.h>

enum class CountdownState : uint8_t {
  Standby,   // wartet auf Start, Restzeit = Startwert
  Counting,  // zaehlt herunter
  Paused,    // angehalten, Restzeit bleibt erhalten
  Urgent,    // zaehlt herunter, letzte 10 % der Zeit
  Alarm      // 0 erreicht, nach ALARM-Dauer automatisch zurueck zu Standby
};

// Was bei einem Aufruf passiert ist. main.cpp entscheidet, was es damit macht
// (z.B. eine Zeile auf Serial ausgeben).
enum class CountdownEvent : uint8_t {
  None,          // nichts passiert
  Started,       // Standby -> Counting
  Paused,        // Counting/Urgent -> Paused
  Resumed,       // Paused -> Counting/Urgent
  Reset,         // beliebig -> Standby (manuell)
  Tick,          // eine Sekunde ist abgelaufen
  AlarmStarted,  // Restzeit hat 0 erreicht
  AlarmEnded,    // Alarm-Dauer vorbei, automatisch zurueck zu Standby
  Ignored        // Befehl im aktuellen Zustand nicht erlaubt (Start waehrend Alarm)
};

class Countdown {
 public:
  Countdown(uint32_t startSeconds, uint32_t alarmDurationMs);

  // Start / Pause / Fortsetzen (ein Taster bzw. Befehl 'S'). Im Alarm ignoriert.
  CountdownEvent toggle(uint32_t nowMs);

  // Zurueck auf Startwert und Standby (Taster Reset bzw. Befehl 'R').
  CountdownEvent reset(uint32_t nowMs);

  // Muss in jedem loop()-Durchlauf aufgerufen werden.
  CountdownEvent update(uint32_t nowMs);

  CountdownState state() const { return state_; }
  uint32_t remainingSeconds() const { return remainingSeconds_; }
  uint32_t startSeconds() const { return startSeconds_; }
  bool isRunning() const {
    return state_ == CountdownState::Counting || state_ == CountdownState::Urgent;
  }

  static const uint32_t TICK_MS = 1000;

 private:
  CountdownState runningState() const;
  void restart(uint32_t nowMs);

  uint32_t startSeconds_;
  uint32_t alarmDurationMs_;
  uint32_t urgentThresholdSeconds_;

  CountdownState state_;
  uint32_t remainingSeconds_;
  uint32_t lastTickMs_;
  uint32_t pausedElapsedMs_;
  uint32_t alarmStartMs_;
};
