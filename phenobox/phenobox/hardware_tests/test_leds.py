#!/usr/bin/env python

import time
import RPi.GPIO as GPIO
import sys
sys.path.append("..")
from gpio_controllers import InputController, LedController, MotorController, DoorState, ButtonPress


def main():
  global ILLUMINATION

  #GPIO.setmode(GPIO.BCM)
  leds = LedController()
  leds.initialize()

  ILLUMINATION = 13
  GPIO.setup(ILLUMINATION, GPIO.OUT, initial=GPIO.HIGH)
  #illum_pwm = GPIO.PWM(ILLUMINATION, 200)
  #illum_pwm.start(10)

  try:
    while (True):
      GPIO.output(ILLUMINATION, GPIO.HIGH)
      leds.switch_blue(True)
      print('blue')
      time.sleep(0.05)
      leds.switch_blue(False)
      leds.switch_green(True)
      print('green')
      time.sleep(0.05)
      leds.switch_green(False)
      leds.switch_orange(True)
      print('orange')
      time.sleep(0.05)
      leds.switch_orange(False)
      leds.switch_red(True)
      print('red')
      time.sleep(0.05)
      leds.clear_all()
      print('all off')
      GPIO.output(ILLUMINATION, GPIO.LOW)
      time.sleep(0.05)

  except KeyboardInterrupt:
    print
    print('Stopped by Ctrl-C')
    GPIO.output(ILLUMINATION, GPIO.LOW)
    leds.clear_all()
    time.sleep(1)
  except:
    print('caught error')
  finally:
    GPIO.cleanup()

if __name__ == '__main__':
  main()

