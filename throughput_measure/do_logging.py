import logging

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
def log(*message):
    logging.info(*message)
