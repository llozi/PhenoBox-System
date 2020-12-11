#!/usr/bin/env python

import time
import RPi.GPIO as GPIO
import sys
sys.path.append("..")
from gpio_controllers import MotorController


def main():

  GPIO.setmode(GPIO.BCM)

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

  GPIO.setup(_ENABLE, GPIO.OUT, initial=GPIO.LOW)
  GPIO.setup(_SVON, GPIO.OUT, initial=GPIO.LOW)
  GPIO.setup(_IN0, GPIO.OUT, initial=GPIO.LOW)
  GPIO.setup(_IN1, GPIO.OUT, initial=GPIO.LOW)
  GPIO.setup(_IN2, GPIO.OUT, initial=GPIO.LOW)
  GPIO.setup(_SETUP, GPIO.OUT, initial=GPIO.LOW)
  GPIO.setup(_DRIVE, GPIO.OUT, initial=GPIO.LOW)
  GPIO.setup(_RESET, GPIO.OUT, initial=GPIO.LOW)

  GPIO.setup(_ALARM, GPIO.IN)
  GPIO.setup(_INP, GPIO.IN)
  GPIO.setup(_SVRE, GPIO.IN)

  print('GPIO pin setup done.')
  time.sleep(1)

  GPIO.output(_ENABLE, GPIO.HIGH)
  GPIO.output(_SVON, GPIO.HIGH)
  GPIO.output(_SETUP, GPIO.HIGH)
  time.sleep(0.1)
  GPIO.output(_SETUP, GPIO.LOW)
  GPIO.output(_IN0, GPIO.HIGH)

  try:
    alarm = GPIO.input(_ALARM)
    if not alarm:
      print('Alarm: ON, resetting...')
      GPIO.output(_RESET, GPIO.HIGH)
      time.sleep(0.1)
      GPIO.output(_RESET, GPIO.LOW)
    else:
      print('Alarm: OFF')

    attarget = GPIO.input(_INP)
    if attarget:
      print('Target reached')
    else:
      print('heading Target')

    svrdy = GPIO.input(_SVRE)
    if svrdy:
      print('Servo ready')
    else:
      print('Servo not ready')


    #motor = MotorController()
    #motor.initialize()
    while True:
      pass


  except KeyboardInterrupt:
    print
    print('Stopped by Ctrl-C')
  except:
    print('caught error')
  finally:
    GPIO.cleanup()

if __name__ == '__main__':
  main()

