#!/usr/bin/env python

import time
import RPi.GPIO as GPIO
import sys


def main():
  global ILLUMINATION

  GPIO.setmode(GPIO.BCM)

  ILLUMINATION = 13
  GPIO.setwarnings(False)
  GPIO.setup(ILLUMINATION, GPIO.OUT, initial=GPIO.LOW)
  #GPIO.cleanup()

if __name__ == '__main__':
  main()

