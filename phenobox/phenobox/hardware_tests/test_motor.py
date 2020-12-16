#!/usr/bin/env python

import time
import RPi.GPIO as GPIO
import sys
sys.path.append("..")
from gpio_controllers import MotorController


def main():

  #GPIO.setmode(GPIO.BCM)

  # Pin declarations
  _SVON   = 17
  _IN0    = 22
  _IN1    = 23
  _IN2    = 24
  _ENABLE = 26
  _SETUP  = 27
  _DRIVE  = 18
  _RESET  = 25

  _ALARM  = 21
  _INP    = 20
  _SVRE   = 16

  try:
    motor = MotorController()
    motor.initialize()
    print('Motor initialization done.')

    pos = 0
    while True:
      if pos > 5:
        pos = 0
      print('Move to position %d' % pos)
      motor.move_to_position(pos)
      pos = pos + 1
      time.sleep(1)


  except KeyboardInterrupt:
    print
    print('Stopped by Ctrl-C')
  except:
    print('caught error')
  finally:
    GPIO.cleanup()

if __name__ == '__main__':
  main()

