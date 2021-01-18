#!/usr/bin/env python
#
# (C) 2020, University of Basel, Lukas Zimmermann
#
# This software is released under the terms of the
# GNU GENERAL PUBLIC LICENSE Version 2, June 1991
# See the LICENSE file in the root of this repository.

import pigpio

class Illumination():

  def __init__(self, gpio_pin):
    self._illu_pin = gpio_pin
    self._illumination_pwm = pigpio.pi()
    self._illumination_percent = 1
    self._illumination_pwm.set_PWM_frequency(self._illu_pin, 200)
    self._illumination_pwm.set_PWM_dutycycle(self._illu_pin, self._illumination_percent * 255 / 100)

  def set_illumination(self, percent):
    self._illumination_percent = percent
    self._illumination_pwm.set_PWM_dutycycle(self._illu_pin, self._illumination_percent * 255 / 100)

