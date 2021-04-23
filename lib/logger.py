import logging
import colorlog
log_colors_config = {
    'DEBUG': 'cyan',
    'INFO': 'green',
    'WARNING': 'yellow',
    'ERROR': 'red',
    'CRITICAL': 'red',
}

logger = logging.getLogger('mylogger')
logger.setLevel(logging.DEBUG)

fh = logging.FileHandler('test.log')
fh.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
color_formatter = colorlog.ColoredFormatter('%(log_color)s[%(levelname)s] - %(asctime)s - %(name)s - %(message)s',log_colors=log_colors_config)

fh.setFormatter(file_formatter)
ch.setFormatter(color_formatter)

logger.addHandler(fh)
logger.addHandler(ch)

# logger.info("test info")
# logger.error("error")