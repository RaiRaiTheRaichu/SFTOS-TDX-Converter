import logging
import sys
from typing import Tuple

debug_mode = '--debug' in sys.argv
file_mode = not '--nofile' in sys.argv

def instantiate_logger():
    log = logging.getLogger(__name__)
    log.setLevel(logging.DEBUG)
    set_handlers(log)
    return log

def set_handlers(log):
    formatter = logging.Formatter('%(asctime)s [%(levelname)s]: %(message)s')

    # Console logger for all info (normally not seen by user anyway)
    console_handler = logging.StreamHandler()
    if debug_mode:
        console_handler.setLevel(logging.DEBUG)
    else:
        console_handler.setLevel(logging.INFO)

    console_handler.setFormatter(formatter)
    log.addHandler(console_handler)

    # File logger, used when running the program with the '--debug' flag
    if debug_mode and file_mode:
        file_handler = logging.FileHandler(filename='output.log')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        log.addHandler(file_handler)

    return log

def dump_failed_conversions(image_list: dict):
    with open('error_list.csv', "w") as output:
        output.write(f'File path,Error\n')
        for image in image_list.keys():
            output.write(f'{image},{image_list[image]}\n')
    return