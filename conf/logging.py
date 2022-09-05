

def get_logging_config(filename: str) -> dict:
    logging: dict = {
        "version": 1,
        "handlers": {
            "stdout-handler": {
                "level": "DEBUG",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
                "formatter": "detailed",
            },
            "file-handler": {
                "level": "DEBUG",
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "detailed",
                "filename": filename,
                "mode": "a",
            },
        },
        "formatters": {
            "detailed": {
                "format": "[%(asctime)s] %(levelname).1s %(message)s",
                'datefmt': "%Y.%m.%d %H:%M:%S",
            },
        },
        "loggers": {
            'log-analyzer': {
                'handlers': ["file-handler"],
                'level': 'INFO',
                'propagate': False,
            }
        },
    }
    if not filename:
        logging['loggers']['log-analyzer']['handlers'] = ["stdout-handler"]
        logging['handlers'].pop('file-handler')

    return logging
