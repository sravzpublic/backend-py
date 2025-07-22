from src.util import logger

class engine(object):

    def __init__(self):
        self.logger = logger.RotatingLogger(__name__).getLogger()

    def create_indexes(self):

