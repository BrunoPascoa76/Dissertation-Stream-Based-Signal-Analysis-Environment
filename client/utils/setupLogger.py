import logging
from logging import Logger
import sys

def setup_logger(name:str,log_file:str=None,level=logging.INFO)->Logger:
    """
    Setup and return a logger
    
    :param name: Logger name
    :type name: str
    :param log_file: File path (if none, log to console)
    :type log_file: str
    :param level: Default logging level
    :return: The configured logger
    :rtype: Logger
    """
    
    logger=logging.getLogger(name)
    logger.setLevel(level)
    formatter=logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    
    if log_file:
        fh = logging.FileHandler(log_file)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    else:
        ch = logging.StreamHandler(sys.stdout)
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        
    return logger