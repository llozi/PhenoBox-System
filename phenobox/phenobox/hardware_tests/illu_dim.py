#!/usr/bin/env python

import time
import RPi.GPIO as GPIO
import pigpio
from argparse import ArgumentParser, Action, ArgumentError

def main():
  global ILLUMINATION
  ILLUMINATION = 13

  parser = ArgumentParser(description='Calibrates a Buck-3603 with custom firmware asking')

  # positional parameters
  parser.add_argument('illumination', type=int,
                      help='Set illumination intensity in percent.')
  args = parser.parse_args()


  illu = pigpio.pi()
  illu.set_PWM_frequency(ILLUMINATION, 200)
  illu.set_PWM_dutycycle(ILLUMINATION, args.illumination * 255 / 100)

if __name__ == '__main__':
  main()

