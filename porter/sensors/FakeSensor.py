import logging
import time
import random

logger = logging.getLogger()
# logger.setLevel(logging.INFO)


class FakeConnection:

    def __init__(self, name):

        self.name = name

        logger.info(f"Created fake sensor for {name}")

    def read(self, chunk_size):

        count = 0
        while count < chunk_size:
            val = bytes(int(random.random()))
            count += 1

        time.sleep(0.01)
        return val

    def close(self):

        logger.info(f"Closed fake sensor {self.name}")
