#include <Arduino.h>

void setup() {
  Serial.begin(9600);
  pinMode(2, INPUT_PULLUP); // Pin 2 și GND
}

void loop() {
  // Dacă butonul e apăsat, trimitem BLOCK, altfel FREE
  if (digitalRead(2) == LOW) {
    Serial.println("BLOCK");
  } else {
    Serial.println("FREE");
  }
  delay(50); // Viteză mare de reacție
}