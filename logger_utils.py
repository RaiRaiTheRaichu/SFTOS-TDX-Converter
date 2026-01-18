import logging
import sys

debug_mode = '--debug' in sys.argv

def set_handlers():
    formatter = logging.Formatter('%(asctime)s [%(levelname)s]: %(message)s')

    # Console logger for all info (normally not seen by user anyway)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    log_handlers = [console_handler]

    # File logger, used when running the program with the '--debug' flag
    if debug_mode:
        file_handler = logging.FileHandler(filename='output.log')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)

        log_handlers.append(file_handler)

    print(f'Log handlers to return: {log_handlers}')
    return log_handlers