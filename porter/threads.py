import os
import copy
import logging
import threading
import time
import subprocess
import signal

logger = logging.getLogger(__name__)

try:
    from sour_core import sony
    logger.info("Sony Camera module imported successfully")
except ModuleNotFoundError:
    logger.info("Sony Camera module not found")
except Exception as e:
    logger.error(f"Error importing Sony Camera module: {e}")
    pass

try:
    import pyalvium
    logger.info("Alvium Camera module imported successfully")
except ModuleNotFoundError:
    logger.info("Alvium Camera module not found")
except Exception as e:
    logger.error(f"Error importing Alvium Camera module: {e}")
    pass

class Sensors(threading.Thread):

    def __init__(
        self,
        handler,
        flag,
        date,
        path,
        sensor_name=None,
        *args,
        **kwargs,
    ):
        """Class to create a thread for each sensor

        Parameters:
            conn (Object): object with the connection to a specific sensor
            flag (threading.Event): flag to communicate to the thread a
                                    particular event happened
            date (str): string with the date and time at the program start
            path (str): path for file storage
        """

        super().__init__(*args, **kwargs)

        self.sensor_name = sensor_name

        self.datafile_name = path + self.sensor_name + "_" + date + ".bin"
        self.shutdown_flag = flag
        self.handler = handler

        # Initialize the sensor and start the sensor handler thread
        logger.info(f"Configuring {self.sensor_name}")
        self.handler._connection()
        self.handler._configuration()

    def run(self):
        # Block forever, getting data from the handler thread through the queue, until shutdown
        logger.info(f"Sensor {self.sensor_name} started")
        self.handler.obj.read_continous_binary(self.shutdown_flag, self.datafile_name)

        # Can only get here if shutdown flag is set
        logger.info(f"Sensor {self.sensor_name} closed")

class AlviumCameraStarspec(threading.Thread):

    def __init__(
        self,
        camera_config,
        path,
        flag,
        *args,
        **kwargs,
    ):
        '''
        Class to create a thread for the camera

        Parameters:
            camera (Object): camera object
            flag (threading.Event): flag to communicate to the thread a particular event happened
            camera_mode (str): camera mode
            fps (float): number of fps in case of photo mode
        '''
        super().__init__(*args, **kwargs)

        self.camera_config = camera_config
        self.path = path

        self.camera_name = self.camera_config["name"]
        self.shutdown_flag = flag
        self.process = None

    def run(self):
        self.frame_rate = self.camera_config.get("frame_rate", 5)
        self.mode = self.camera_config.get("mode", 'trigger')
        self.core = self.camera_config.get("core", None)
        self.verbosity = self.camera_config.get("verbosity", False)
        self.roi = self.camera_config.get("roi", None)
        self.processing = self.camera_config.get("processing", False)
        self.exposure = self.camera_config.get("exposure", None)
        self.output = self.path

        cmd = f"alvium --framerate {self.frame_rate} --mode {self.mode}"
        if self.verbosity == True:
            cmd += f" --debug"
        if self.processing == True:
            cmd += f" --processing"
        if self.exposure is not None:
            cmd += f" --exposure {self.exposure}"
        if self.roi is not None:
            cmd += f" --roi {str(self.roi)}"
        if self.output is not None:
            cmd += f" --output {self.output}"
        if self.core is not None:
            cmd += f" --core {int(self.core)}"
        self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True, preexec_fn=os.setsid)

        while not self.shutdown_flag.is_set():
            self.shutdown_flag.wait(1)

        self.close()

    def close(self):
        if self.process is not None:
            try:
                os.killpg(os.getpgid(self.process.pid), signal.SIGINT)
                try:
                    self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    logger.warning(f"Process did not terminate in time, sending SIGTERM.")
                    os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
                    try:
                        self.process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        logger.error(f"Process did not terminate after SIGTERM, sending SIGKILL.")
                        os.killpg(os.getpgid(self.process.pid), signal.SIGKILL)
                        self.process.wait()
            except ProcessLookupError:
                pass
            finally:
                self.process = None

        logger.info(f"Closed sensor {self.name}")

class AlviumCamera(threading.Thread):

    def __init__(
        self,
        camera_config,
        path,
        flag,
        *args,
        **kwargs,
    ):
        '''
        Class to create a thread for the camera

        Parameters:
            camera (Object): camera object
            flag (threading.Event): flag to communicate to the thread a particular event happened
            camera_mode (str): camera mode
            fps (float): number of fps in case of photo mode
        '''
        super().__init__(*args, **kwargs)

        self.camera_config = camera_config
        self.path = path

        self.camera_name = self.camera_config["name"]
        self.shutdown_flag = flag

        self.core = self.camera_config.get("core", None)
        self.exposure = self.camera_config.get("exposure", None)
        self.gain = self.camera_config.get("gain", None)
        self.format = self.camera_config.get("format", None)
        self.max_framerate = self.camera_config.get("max_framerate", None)
        self.writing_threads = self.camera_config.get("writing_threads", None)
        self.verbosity = self.camera_config.get("verbosity", None)
        self.output = self.path

        self.settings = {
            "exposure": self.exposure,
            "gain": self.gain,
            "format": self.format,
            "max_framerate": self.max_framerate,
        }

    def run(self):
        with pyalvium.Camera(output_path=self.output, writing_threads=self.writing_threads, settings=self.settings, verbose=self.verbosity) as camera:
            camera.log_all_features()
            camera.start_acquisition()

            while not self.shutdown_flag.is_set():
                self.shutdown_flag.wait(1)

            camera.stop_acquisition()
            logger.info(f"Closed sensor {self.name}")
            self.stats = camera.get_streaming_stats()

class SonyCamera(threading.Thread):

    def __init__(
        self,
        camera_config,
        flag,
        *args,
        **kwargs,
    ):
        """Class to create a thread for each sensor

        Parameters:
            camera (Object): camera object
            flag (threading.Event): flag to communicate to the thread a
                                    particular  event happened
            camera_mode (str): camera mode
            fps (float): number of fps in case of photo mode
            frames (int): number of photo in case of photo mode
            duration (float): duration of the video in case of video mode
        """

        super().__init__(*args, **kwargs)

        self.camera_config = camera_config
        self.camera_name = self.camera_config["name"]
        self.shutdown_flag = flag

    def run(self):
        try:
            camera = sony.SONYconn(self.camera_name, log=logger)
        except IndexError:
            self.shutdown_flag.set()
            logger.info("Camera not Found, stopping the code")
        
        if not self.shutdown_flag.is_set():
            camera.initialize_camera()

            time.sleep(0.2)
            camera.messageHandler(["datetime", 0.04, 1e-3])
            time.sleep(0.1)
            camera.messageHandler(["programmode", self.camera_config["program"]])
            time.sleep(0.1)

            if "ISO" in self.camera_config.keys():
                camera.messageHandler(["iso", self.camera_config["ISO"]])
                time.sleep(0.1)

            if "shutter_speed" in self.camera_config.keys():
                camera.messageHandler(["shutterspeed", self.camera_config["shutter_speed"]])
                time.sleep(0.1)

            if "focus_distance" in self.camera_config.keys():
                camera.messageHandler(
                    ["focusdistance", self.camera_config["focus_distance"]]
                )
                time.sleep(0.1)

            logger.info(f"Camera {self.camera_name} Configured")

        if self.camera_config["mode"] == "video":
            if "duration" in self.camera_config.keys():
                duration = self.camera_config["duration"]
            else:
                duration = 20 * 60

            recording = True
            video_chunks = 30 * 60
            secs_remaining = copy.copy(duration)
            while not self.shutdown_flag.is_set():
                self.shutdown_flag.wait(1)
                camera.messageHandler(["videocontrol"])
                if recording:
                    if secs_remaining < video_chunks:
                        logger.info(
                            f"Camera {self.camera_name} starts recording, remaining {secs_remaining} s"
                        )
                        self.shutdown_flag.wait(secs_remaining)
                        camera.messageHandler(["videocontrol"])
                        self.shutdown_flag.set()
                        recording = not recording
                        logger.info(f"Camera {self.camera_name} stops recording")
                        break
                    else:
                        self.shutdown_flag.wait(video_chunks)
                        camera.messageHandler(["videocontrol"])
                        time.sleep(2)
                        secs_remaining -= video_chunks
                else:
                    recording = not recording

        elif self.camera_config["mode"] == "photo":
            if "fps" in self.camera_config.keys():
                fps = self.camera_config["fps"]
            else:
                fps = 1

            if "frames" in self.camera_config.keys():
                frames = self.camera_config["frames"]
            else:
                frames = 1e9

            timing = 1 / fps

            photo_count = 0
            while not self.shutdown_flag.is_set():
                t = time.time()
                camera.messageHandler(["capture"])

                while (time.time() - t) < timing:
                    self.shutdown_flag.wait(0.1)

                photo_count += 1
                if photo_count > frames:
                    break

        logger.info(f"Camera {self.camera_name} stopped")
        try:
            camera.close_usb_connection()
        except UnboundLocalError:
            pass
