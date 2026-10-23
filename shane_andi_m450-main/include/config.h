#pragma once

// Zentrale Konfiguration: Pins pro Board und Zeitwerte.
//
// Das Board wird automatisch ueber das gewaehlte PlatformIO-Environment erkannt.
// Jeder Wert kann ohne Code-Aenderung in platformio.ini ueberschrieben werden:
//   build_flags = -D PIN_LED_EXTERNAL=9 -D COUNTDOWN_START_SECONDS=30

#include <Arduino.h>

// ---------------------------------------------------------------------------
// Pins
// ---------------------------------------------------------------------------
#if defined(ARDUINO_ARCH_RP2040)
  // Raspberry Pi Pico / Pico W (GPIO-Nummern)
  #define APP_BOARD_NAME "Raspberry Pi Pico"
  #ifndef PIN_LED_EXTERNAL
    #define PIN_LED_EXTERNAL 14
  #endif
  #ifndef PIN_BUTTON_START
    #define PIN_BUTTON_START 15
  #endif
  #ifndef PIN_BUTTON_RESET
    #define PIN_BUTTON_RESET 16
  #endif

#elif defined(ARDUINO_ARCH_AVR)
  // Arduino Uno / Nano / Mega (Digital-Pins). Die PWM-Pins 3, 5, 6, 9, 10, 11
  // bleiben frei fuer Motortreiber.
  #define APP_BOARD_NAME "Arduino (AVR)"
  #ifndef PIN_LED_EXTERNAL
    #define PIN_LED_EXTERNAL 7
  #endif
  #ifndef PIN_BUTTON_START
    #define PIN_BUTTON_START 2
  #endif
  #ifndef PIN_BUTTON_RESET
    #define PIN_BUTTON_RESET 4
  #endif

#else
  // Anderes Board: Pins muessen in platformio.ini per build_flags gesetzt werden.
  #define APP_BOARD_NAME "Generic Arduino"
  #if !defined(PIN_LED_EXTERNAL) || !defined(PIN_BUTTON_START) || !defined(PIN_BUTTON_RESET)
    #error "Unbekanntes Board: PIN_LED_EXTERNAL, PIN_BUTTON_START und PIN_BUTTON_RESET per build_flags setzen."
  #endif
#endif

// Onboard-LED. Beim Pico W haengt sie am WLAN-Chip, LED_BUILTIN funktioniert trotzdem.
#ifndef PIN_LED_ONBOARD
  #ifdef LED_BUILTIN
    #define PIN_LED_ONBOARD LED_BUILTIN
  #else
    #error "Board hat kein LED_BUILTIN: PIN_LED_ONBOARD per build_flags setzen."
  #endif
#endif

// ---------------------------------------------------------------------------
// Zeiten und serielle Schnittstelle
// ---------------------------------------------------------------------------
#ifndef COUNTDOWN_START_SECONDS
  #define COUNTDOWN_START_SECONDS 60
#endif
#ifndef COUNTDOWN_ALARM_DURATION_MS
  #define COUNTDOWN_ALARM_DURATION_MS 5000
#endif
#ifndef BUTTON_DEBOUNCE_MS
  #define BUTTON_DEBOUNCE_MS 30
#endif
#ifndef SERIAL_BAUD
  #define SERIAL_BAUD 115200
#endif
// Maximale Wartezeit in setup(), bis ein USB-Serial-Monitor verbunden ist.
#ifndef SERIAL_WAIT_MS
  #define SERIAL_WAIT_MS 2000
#endif
