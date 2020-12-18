#!/usr/bin/env python
#
# (C) 2020, University of Basel, Lukas Zimmermann
#
# This software is released under the terms of the
# GNU GENERAL PUBLIC LICENSE Version 2, June 1991
# See the LICENSE file in the root of this repository.

import time
import RPi.GPIO as GPIO
import pigpio
from argparse import ArgumentParser, Action, ArgumentError

def main():
  global ILLUMINATION
  ILLUMINATION = 13

  parser = ArgumentParser(description='Delivers a PWM signal to GPIO13 to control '
                            'Phenobox's illumination intensity. Requires the pigio '
                            'daemon running.')

  # positional parameters
  parser.add_argument('illumination', type=int,
                      help='Set illumination intensity in percent.')
  args = parser.parse_args()


  illu = pigpio.pi()
  illu.set_PWM_frequency(ILLUMINATION, 200)
  illu.set_PWM_dutycycle(ILLUMINATION, args.illumination * 255 / 100)

if __name__ == '__main__':
  main()

