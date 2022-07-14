import logging


_log_format = f"%(asctime)s - [%(name)s] - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"


class Logger:
    def __init__(self):
        file_handler = logging.FileHandler("logfile.log")
        file_handler.setFormatter(logging.Formatter(_log_format))
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(file_handler)

    def log(self, msg):
        self.logger.setLevel(logging.INFO)
        self.logger.info(msg)

    def error(self, msg):
        self.logger.setLevel(logging.ERROR)
        self.logger.error(msg)
