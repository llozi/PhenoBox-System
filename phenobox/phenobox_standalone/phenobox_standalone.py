#! /usr/bin/env python
import os
import sys
import signal
import subprocess
import logging
from logging.handlers import RotatingFileHandler
from queue import Queue, Empty

from colorama import init, Fore

import gpio_controllers as gpio
from gpio_controllers.input_controller import InputController, DoorState, ButtonPress
from gpio_controllers.led_controller import LedController
from gpio_controllers.motor_controller import MotorController
from gpio_controllers.blinker import Blinker
from gpio_controllers.illumination import Illumination
from camera import CameraController
from config import config
from event import UserEvent
from image_processing import CodeScanner
from statemachine.statemachine import PhenoboxStateMachine
from network.image_handler import ImageHandler



class Phenobox():

  def __init__(self):

    self.initialize()

    self.eventQueue = Queue()
    self._logger = logging.getLogger(__name__)
    self._logger.setLevel(logging.INFO)
    self.door_state = self.input_controller.get_door_state()


  def door_state_changed(self, state):
    """
    If it is opened while the box is not in the IDLE or ERROR state it will transition to the ERROR state

    :param state: The current/new DoorState

    :return: None
    """
    self.door_state = state
    if state == DoorState.OPEN:
      if not self.phenobox_statemachine.is_IDLE() and not self.phenobox_statemachine.is_ERROR():
        self._logger.info('Door Opened while running')
        self.phenobox_statemachine.door_opened(error_code=3)


  def start_pressed(self, press):
    if press == ButtonPress.SHORT:
      print(Fore.CYAN + "State: " + self.phenobox_statemachine.state)
    if self.phenobox_statemachine.is_IDLE() or self.phenobox_statemachine.is_ERROR():
      if press == ButtonPress.LONG:
        print(Fore.MAGENTA + "Shutdown Requested")
        self._logger.info('Shutdown action placed')
        self.eventQueue.put(UserEvent.SHUTDOWN)
      else:
        if self.door_state == DoorState.CLOSED:
          print(Fore.BLUE + "Start")
          if self.phenobox_statemachine.is_IDLE():
            self._logger.info('Start action placed')
            self.eventQueue.put(UserEvent.START)
          else:
            self._logger.info('Restart action placed')
            self.eventQueue.put(UserEvent.RESTART)
        else:
          print(Fore.RED + "Please close the door before starting!")


  def initialize(self):
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler = RotatingFileHandler(getattr(config, 'cfg').get('box', 'log_file'), maxBytes=5242880,
                                       backupCount=4)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)

    init(autoreset=True)

    photo_count = getattr(config, 'cfg').getint('box', 'photo_count')
    self.illumination = Illumination(13)  # use GPIO pin 13 for illumination PWM control
    self.led_controller = LedController()
    self.led_controller.initialize()
    self.led_controller.blink_green(1)
    self.led_controller.blink_blue(1)
    self.scanner = CodeScanner()
    self.camera_controller = CameraController()
    self.camera_controller.initialize()
    self.motor_controller = MotorController()
    self.motor_controller.initialize()

    self.image_handler = ImageHandler(photo_count=photo_count)
    self.image_handler.setDaemon(True)
    self.image_handler.start()

    self.phenobox_statemachine = PhenoboxStateMachine(
      self.camera_controller, self.scanner, self.motor_controller,
      self.led_controller, self.image_handler, self.illumination,
      photo_count
    )
    self.phenobox_statemachine.initialize()
    self.input_controller = InputController()
    self.input_controller.initialize(self.door_state_changed, self.start_pressed)
    signal.signal(signal.SIGUSR1, sigUSR1_handler)


  def _terminate(self):
    self.led_controller.clear_all()
    self.camera_controller.close()
    self.led_controller.blink_green(interval=1)
    self.led_controller.blink_blue(interval=1)
    self.image_handler.stop()
    self.image_handler.join()
    self.led_controller.clear_all()
    gpio.clean()


  def run(self):
    shutdown = False
    try:
      while True:
        try:
          event = self.eventQueue.get(True, 0.1)
        except Empty:
          continue
        if event == UserEvent.START:
          self.phenobox_statemachine.start()
        if event == UserEvent.RESTART:
          self.phenobox_statemachine.restart()
        if event == UserEvent.SHUTDOWN:
          shutdown = True
          break

    except KeyboardInterrupt:
      print("keyboard interrupt")
    print(Fore.MAGENTA + 'Shutdown initiated')
    self._terminate()
    if shutdown:
      subprocess.call(['sudo shutdown -h now "System halted by GPIO action" &'], shell=True)


def sigUSR1_handler(signum, frame):
  phenobox.start_pressed(ButtonPress.SHORT)


if __name__ == '__main__':
  print('loading config file "{}/{}"'.format('config', sys.argv[1]))
  config.load_config('{}/{}'.format('config', sys.argv[1]))
  phenobox = Phenobox()
  phenobox.run()

