import logging
import time
import random

logger =logging.getLogger()


class FakeConnection:

    def __init__(self, name):

        logging.info(f'Created fake sensor for {name}')

    def read(self, chunk_size):

        count = 0
        while count < chunk_size:
            val = str(random.random())
            count += 1

        time.sleep(0.01)
        return val
