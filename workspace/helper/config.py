import configparser

config_parser = configparser.ConfigParser()
config_parser.read("config.ini")

CONFIG = config_parser["DEFAULT"]

HOST            = CONFIG["RobotHost"]
IMAGE_DIRECTORY = CONFIG["ImageDirectory"]
CSV_PATH        = CONFIG["CsvPath"]
PREDICTION_URL  = CONFIG["ClassifierApiUrl"]
CROPPED_IMAGE_WIDTH = CONFIG["CroppedImageWidth"]
CROPPED_IMAGE_HEIGHT = CONFIG["CroppedImageHeight"]
LOG_FILE_PATH   = CONFIG["LogFilePath"]