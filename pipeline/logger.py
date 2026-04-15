import logging
from pathlib import Path


def get_logger(name:str)->logging.Logger:

    logger = logging.Logger(name)
    
    if logger.handlers:
        return logger
    logger.setLevel(logging.DEBUG)
    
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    
    log_dir = Path(__file__).parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    file_handler = logging.FileHandler(log_dir / "app.log")
    file_handler.setLevel(logging.DEBUG)
    
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    console.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    logger.addHandler(console)   
    logger.addHandler(file_handler)
    return logger
