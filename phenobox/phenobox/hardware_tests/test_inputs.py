#!/usr/bin/env python

import logging
from logging.handlers import RotatingFileHandler
import time
import RPi.GPIO as GPIO
import sys
sys.path.append("..")
from config import config
from gpio_controllers import InputController, LedController, DoorState, ButtonPress


def cb_door(state):
  global cnt
  print('DOOR: %s' % state)
  if (state == DoorState.CLOSED):
    cnt = 2
  else:
    cnt = 5

def cb_start(state):
  print('START: %s' % state)

def main():

  config.load_config('{}/{}'.format('../config', 'test_config.ini'))

  formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
  file_handler = RotatingFileHandler(getattr(config, 'cfg').get('box', 'log_file'),
                                     maxBytes=5242880, backupCount=4)
  file_handler.setLevel(logging.DEBUG)
  file_handler.setFormatter(formatter)
  root_logger = logging.getLogger()
  root_logger.addHandler(file_handler)


  global cnt
  cnt = 6

  # set by the gpio_controllers module:
  #GPIO.setmode(GPIO.BCM)
  leds = LedController()
  leds.initialize()

  inputs = InputController()
  inputs.initialize(cb_door, cb_start)
  #inputs.register_start_button_cb(cb_start)

  try:
    while True:
      while (cnt  > 0):
        cnt = cnt - 1
        leds.switch_red(True)
        time.sleep(0.05)
        leds.switch_red(False)
        leds.switch_orange(True)
        time.sleep(0.05)
        leds.switch_orange(False)
        leds.switch_green(True)
        time.sleep(0.05)
        leds.switch_green(False)
        leds.switch_blue(True)
        time.sleep(0.05)
        leds.clear_all()
        time.sleep(0.05)
      time.sleep(0.01)

  except KeyboardInterrupt:
    leds.clear_all()
    print
    print('Stopped by Ctrl-C')
  except:
    print('caught error')
  finally:
    GPIO.cleanup()

if __name__ == '__main__':
  main()

