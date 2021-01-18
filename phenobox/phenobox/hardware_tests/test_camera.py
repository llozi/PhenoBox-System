#!/usr/bin/env python
  
import logging
from logging.handlers import RotatingFileHandler
import time
import os
import sys
sys.path.append(os.path.expanduser('~/github/PhenoBox-System/phenobox'))
from phenobox.config import config
from phenobox.camera import CameraController
from phenobox.camera.errors import ConnectionError, CaptureError
from phenobox.image_processing.code_scanner import CodeScanner

def main():

  config.load_config('{}/{}'.format('../config', 'test_config.ini'))

  formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
  file_handler = RotatingFileHandler(getattr(config, 'cfg').get('box', 'log_file'),
                                     maxBytes=5242880, backupCount=4)
  file_handler.setLevel(logging.DEBUG)
  file_handler.setFormatter(formatter)
  root_logger = logging.getLogger()
  root_logger.addHandler(file_handler)
  root_logger.setLevel(logging.DEBUG)

  try:
    camera = CameraController()
    camera.initialize()

    camera.capture_and_download('test1')
    code_scanner = CodeScanner()
    code_information = code_scanner.scan_image('/home/pi/pictures/test1.jpg')
    if code_information is not None:
      print('Decoded from QRCode: "%s"' % code_information)
    else:
      print('No decodable QRCode found')
    camera.close()
  except ConnectionError as e:
    print('Connection Error "%s"' % e)
  except CaptureError as e:
    print('Capture Error "%s"' % e)
    

if __name__ == '__main__':
  main()

