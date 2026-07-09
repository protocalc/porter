from signal import SIGINT, SIGTERM
import logging

LOGGING_FORMAT_FILE = "[%(asctime)s.%(msecs)03d - %(levelname)s] name: %(name)s thread: %(threadName)s: %(message)s"
#LOGGING_FORMAT_STREAM = AnsiColorFormatter('[%(asctime)s.%(msecs)03d - %(levelname)s] name: %(name)s thread: %(threadName)s: %(message)s')
LOGGING_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOGGING_LEVEL = "INFO"

# define signal to catch
signal_to_catch = [SIGINT, SIGTERM]

THREAD_JOIN_TIMEOUT = 10  # seconds

# define paths
data_directory       = "data"
sensors_folder_name  = "sensors_data"
camera_folder_name   = "camera_data"
current_symlink_name = "current"
logfile_name         = "flight.log"