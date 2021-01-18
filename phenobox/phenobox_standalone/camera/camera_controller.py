import errno
import logging
import os
import gphoto2 as gp

from .errors import ConnectionError, CaptureError
from config import config


class libgphoto2error(Exception):
    def __init__(self, result, message):
        self.result = result
        self.message = message

    def __str__(self):
        return self.message + ' (' + str(self.result) + ')'



class CameraController:
  context = None
  cam = None  #:a reference to the camera which should be used


  def __init__(self, target_dir=None):
    if target_dir is None:
        self.target_dir = getattr(config, 'cfg').get('box', 'local_image_folder')
    else:
        self.target_dir = target_dir
    self._logger = logging.getLogger(__name__)
    self._logger.setLevel(logging.INFO)
    self._logger.info('Target directory set to {}'.format(self.target_dir))

  def connect(self):
    """
    Connects to the attached camera

    :raises ConnectionError: if the connection to the camera failed

    :return: None
    """
    if self.cam is None:
      self.cam = gp.Camera()
      try:
        self.cam.init()
      except gp.GPhoto2Error as ex:
        if ex.code == gp.GP_ERROR_MODEL_NOT_FOUND:
          self.release()
          self._logger.warning('Unable to connect to camera. (Error code: {}, {})'.format(ex.code, ex.string))
          raise ConnectionError('Unable to connect to camera')

        # some other error we can't handle here
        raise

  def release(self):
    """
    Disconnects from the camera

    :return: None
    """
    if self.cam is not None:
      self.cam.exit()
      self.cam = None

  def initialize(self):
    """
    Sets up the context needed by gphoto

    :return: None
    """
    self.context = gp.gp_context_new()

  def capture_and_download(self, name):
    """
    Takes a photo and downloads it from the camera and saves it to the target_dir

    :param name: the file name which should be used when saving the downloaded image

    :return: The return value of :meth:`.download`
    """
    self.connect()
    try:
      file_path = self.cam.capture(gp.GP_CAPTURE_IMAGE)
    except gp.GPhoto2Error as ex:
      self._logger.warning('Error during capture. (Error code: {}, {})'.format(ex.code, ex.string))
      self.release()
      raise CaptureError("Unable to capture")
    else:
      return self.download(os.path.join(self.target_dir), file_path, name)

  def download(self, dest_folder, file_path, name):
    """
    Downloads the image given by file_path and saves it to the path given by dest_folder with the given name

    :param dest_folder: The directory to store the image to
    :param file_path: The path to the image on the camera
    :param name: The file name to be used for the downloaded image

    :return: the full path to the downloaded image or None if the download was not successfull
    """
    dest = os.path.join(dest_folder, name + '.jpg')

    try:
      os.makedirs(dest[:dest.rindex('/') + 1])
    except OSError as exception:
      if exception.errno != errno.EEXIST:
        self._logger.exception('Unable to create folder ({}). (errno: {})'.format(dest, exception.errno))
        return None
        # raise  # TODO handle this
    try:
      self._logger.info('Shot picture on camera at {}/{}'.format(file_path.folder, file_path.name))
      camera_file = self.cam.file_get(file_path.folder, file_path.name, gp.GP_FILE_TYPE_NORMAL)
      self._logger.info('Camera file: "{}"'.format(camera_file.get_name()))
      camera_file.save(dest)


    except libgphoto2error as err:
      self._logger.exception('Unable to download and save image from camera')
      return None
    return dest

  # TODO refactor into property
  def get_target_dir(self):
    return self.target_dir

  def close(self):
    """
    Alias for :meth:`.release`

    :return: None
    """
    self.release()
