#include "pulse.h"
#include <wiringPi.h>
#include <stdio.h>
#include <stdlib.h>

const int posPin = 29 //Note wiringPi is diff than BCM
const int negPin = 26

int turnHigh() {
    wiringPiSetup();
    pinMode(posPin, OUTPUT);
    pinMode(negPin, INPUT);
    digitalWrite(posPin, HIGH);
    delay(10000);
    digitalWrite(posPin, LOW);
    delay(10000);
    return 0;
}

int return90() {
    int five = 90;
    return five;
}
