import logging
import time

from colorama import Fore
from transitions import Machine
from transitions import State
import uuid
import re

from camera import CaptureError, ConnectionError
from plant import Plant


class PhenoboxStateMachine(Machine):
    camera_controller = None
    code_scanner = None
    motor_controller = None
    led_controller = None
    image_handler = None
    illumination = None
    code_information = None
    plant = None
    pic_count = 0
    error_code = 0

    error_messages = {
        1: "Unable to read QR-Code",
        2: "Unable to upload pictures",
        3: "Door was opened unexpectedly",
        4: "Unable to capture picture",
        5: "Unable to connect to camera",
        6: "Unable to retrieve data",
        7: "Unable to authenticate",
        8: "Unable to get picture from camera",
        9: "Unable to create snapshot on server",
        10: "This plant has already been processed for the current timestamp",
        11: "Unable to connect to server",
        12: "QR-Code has unknown meaning"
    }

    def __init__(self, camera_controller, code_scanner, motor_controller,
                 led_controller, image_handler, illumination, photo_count=6):

        self.camera_controller = camera_controller
        self.code_scanner = code_scanner
        self.motor_controller = motor_controller
        self.led_controller = led_controller
        self.image_handler = image_handler
        self.illumination = illumination
        self.photo_count = photo_count
        # this is used to split QR code data into several fields:
        self.qrcode_pattern = re.compile('^([^ ]+) ([^ ]+) ([^ ]+) ([^ ]+).*$')

        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.INFO)

        states = ['STARTUP',
                  State(name='IDLE', on_enter='on_enter_idle'),
                  State(name='AUTH', on_enter='on_enter_auth'),
                  State(name='TAKE_FIRST_PICTURE', on_enter='on_enter_take_first_picture'),
                  State(name='ANALYZE_PICTURE', on_enter='on_enter_analyze_picture'),
                  State(name='SETUP', on_enter='on_enter_setup'),
                  State(name='DRIVE', on_enter='on_enter_drive'),
                  State(name='TAKE_PICTURE', on_enter='on_enter_take_picture'),
                  State(name='RETURN', on_enter='on_enter_return'),
                  State(name='UPLOAD', on_enter='on_enter_upload'),
                  State(name='ERROR', on_enter='on_enter_error', on_exit='on_exit_error', ignore_invalid_triggers=True)
                  ]

        Machine.__init__(self, states=states, send_event=True, initial="STARTUP")
        self.add_transition('initialize', 'STARTUP', 'RETURN', after=[self.after_return])

        # ----FROM IDLE----#
        self.add_transition('start', 'IDLE', 'SETUP', after=[self.after_start], conditions=[self.valid_authentication])
        self.add_transition('start', 'IDLE', 'AUTH', unless=[self.valid_authentication])
        # ----FROM AUTH----#
        self.add_transition('start', 'AUTH', 'SETUP', after=[self.after_start])
        self.add_transition('error', 'AUTH', 'ERROR')
        # ----FROM TAKE_FIRST_PICTURE----#
        self.add_transition('analyze', 'TAKE_FIRST_PICTURE', 'ANALYZE_PICTURE', after=[self.after_analyze])
        self.add_transition('error', 'TAKE_FIRST_PICTURE', 'ERROR')
        # ----FROM ANALYZE_PICTURE----#
        self.add_transition('rotate', 'ANALYZE_PICTURE', 'DRIVE', after=[self.after_rotate])
        self.add_transition('error', 'ANALYZE_PICTURE', 'ERROR')
        # ----FROM SETUP----#
        self.add_transition('take_first', 'SETUP', 'TAKE_FIRST_PICTURE', after=[self.after_take_first])
        # ----FROM DRIVE----#
        self.add_transition('picture', 'DRIVE', 'TAKE_PICTURE', after=[self.after_picture])
        # ----FROM TAKE_PICTURE----#
        self.add_transition('error', "TAKE_PICTURE", 'ERROR')
        self.add_transition('next_picture', 'TAKE_PICTURE', 'DRIVE', after=[self.after_rotate],
                            unless=[self.enough_pictures])
        self.add_transition('next_picture', 'TAKE_PICTURE', 'UPLOAD', after=[self.after_upload],
                            conditions=[self.enough_pictures])
        # ----FROM RETURN----#
        self.add_transition('idle', 'RETURN', 'IDLE')
        # ----FROM UPLOAD----#
        self.add_transition('upload_finished', 'UPLOAD', 'RETURN', after=[self.after_return])
        # ----FROM ERROR----#
        self.add_transition('restart', 'ERROR', 'SETUP', after=[self.after_start],
                            conditions=[self.valid_authentication])
        self.add_transition('restart', 'ERROR', 'AUTH',
                            unless=[self.valid_authentication])
        # ----DOOR----#
        self.add_transition('door_opened', ['TAKE_FIRST_PICTURE', 'ANALYZE_PICTURE', 'SETUP',
                                            'DRIVE', 'TAKE_PICTURE', 'UPLOAD', 'RETURN', 'AUTH'], 'ERROR')


    def valid_authentication(self, event):
        return True

    def on_enter_return(self, event):
        print(Fore.BLUE + 'Returning to Origin')
        # time.sleep(1)
        self.motor_controller.return_to_origin()

    def after_return(self, event):
        self.idle()

    def on_enter_idle(self, event):
        print(Fore.GREEN + 'Idle. Waiting for user Input')
        self.led_controller.clear_all()
        self.led_controller.switch_green(True)
        self.code_information = None
        self.plant = None

    def on_enter_auth(self, event):
        print(Fore.BLUE + 'Skipping Authentication')
        self.led_controller.switch_green(False)
        self.led_controller.switch_blue(True)
        self.start()

    def on_enter_setup(self, event):
        print(Fore.BLUE + 'Setting up')
        self.led_controller.switch_green(False)
        self.led_controller.switch_blue(True)
        self.motor_controller.return_to_origin()
        self.plant = Plant()

    def after_start(self, event):
        self.take_first()

    def on_enter_take_first_picture(self, event):
        pict_name = str(uuid.uuid4())
        print(Fore.BLUE + 'Taking first picture: {}'.format(pict_name))
        try:
            self.illumination.set_illumination(100)
            time.sleep(1)
            picture_path = self.camera_controller.capture_and_download(pict_name)
            print('Picture path: "{}"'.format(picture_path))
            if picture_path is None:
                self.error(error_code=8)
            else:
                self.plant.add_picture(picture_path, self.motor_controller.current_angle)
                self.analyze()

        except ConnectionError as err:
            self._logger.error(err.message)
            self.error(error_code=5)
        except CaptureError as err:
            self._logger.error(err.message)
            self.error(error_code=4)
        finally:
            self.illumination.set_illumination(1)

    def after_take_first(self, event):
        pass
        # self.analyze()

    def on_enter_analyze_picture(self, event):
        print(Fore.BLUE + 'Analyzing')
        path, _ = self.plant.get_first_picture()
        self.code_information = self.code_scanner.scan_image(path)
        self.plant.name = self.code_information.decode('utf8')

    def after_analyze(self, event):
      if self.code_information is not None:
        qrcode = self.code_information.decode('utf8')
        print(Fore.CYAN + 'Decoded symbol "{}"'.format(qrcode))
        self._logger.info( 'decoded symbol "{}"'.format(qrcode))
        m = self.qrcode_pattern.match(qrcode)
        if not m:
          self.error(error_code=12)
          return
        
        plant_id = m.group(1)

        # the following in the original phenobox comes from a query to the server,
        # here we create the property values from the scanned QR code instead. 
        self.plant.experiment_name = m.group(1)    # experiment (project)
        self.plant.timestamp_id = m.group(2)       # time point
        self.plant.snapshot_id = m.group(3)        # treatment
        self.plant.sample_group_name = m.group(4)  # replicate
      else:
        self.error(error_code=1)
        return
      self.rotate()

    def on_enter_drive(self, event):
        print(Fore.BLUE + 'Driving')
        # time.sleep(1)
        self.motor_controller.move_to_position(self.plant.get_picture_count())

    def after_rotate(self, event):
        time.sleep(1)
        self.picture()

    def on_enter_take_picture(self, event):
        print(Fore.BLUE + 'Taking picture at angle ' + str(self.motor_controller.current_angle))
        try:
            picture_path = self.camera_controller.capture_and_download(str(uuid.uuid4()))
            if picture_path is None:
                self.error(error_code=6)
            else:
                self.plant.add_picture(picture_path, self.motor_controller.current_angle)
                #copy(picture_path, '/home/pi/Phenobox/smbmnt')
                self.next_picture()
        except CaptureError:
            self.error(error_code=4)

    def enough_pictures(self, event):
        return self.plant.get_picture_count() >= self.photo_count

    def after_picture(self, event):
        pass

    def on_enter_upload(self, event):
        print(Fore.BLUE + 'Dispatching picture tasks')
        self.led_controller.blink_orange()
        self.image_handler.add_plant(self.plant)

    # TODO rename to after_upload_dispatched
    def after_upload(self, event):
        self.led_controller.switch_orange(False)
        self.upload_finished()

    def on_enter_error(self, event):
        print(Fore.RED + 'Something wrong happened')
        error_code = event.kwargs.get('error_code', -1)
        # Reset state variables
        self.pic_count = 0
        self.code_information = None
        if self.plant is not None:
            self.plant.delete_all_pictures()
        self.plant = None

        msg = self.error_messages.get(error_code, "Unknown error")
        self._logger.info('Machine transitioned to error state with code {}. ({})'.format(error_code, msg))
        print(Fore.RED + msg)
        self.led_controller.clear_all()
        if error_code == 1:
            self.led_controller.switch_orange(True)
        elif error_code == 2 or error_code == 6 or error_code == 7 or error_code == 9 or error_code == 11:
            self.led_controller.switch_red(True)
        elif error_code == 3:
            self.led_controller.blink_orange()
            self.led_controller.blink_blue()
        elif error_code == 4 or error_code == 5 or error_code == 8:
            self.led_controller.blink_orange()
        elif error_code == 10:
            self.led_controller.blink_blue()

    def on_exit_error(self, event):
        self.led_controller.clear_all()
