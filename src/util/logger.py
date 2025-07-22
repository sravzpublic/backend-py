'''
Created on Mar 6, 2017

@author: admin
'''
from src.util import settings
import logging, sys

class RotatingLogger(object):

    def __init__(self, name, level = None, path = None):
        self.name = name
        self.level = level or (logging.DEBUG if settings.constants.development else  logging.WARN)
        self.path = path or self.getLogFile()
        self.maxBytes=1024000000
        self.backupCount=5

    def getLogger(self):
        """
        Creates a rotating logger
        """
        logger = logging.getLogger(self.name)
        logger.setLevel(self.level)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        if not logger.hasHandlers():
            # Log to stream for debugging
            streamHandler = logging.StreamHandler(sys.stdout)
            streamHandler.setFormatter(formatter)
            logger.addHandler(streamHandler)

        return logger

    def getLogFile(self):
        return settings.constants.linux_log_file
