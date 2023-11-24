# import logging
# import os.path
# from app.core.settings import Settings

# app_logger = logging.getLogger(__name__)
# app_logger.setLevel(Settings.LOG_LEVEL)

# fh = logging.handlers.RotatingFileHandler(filename=os.path.join(Settings.APP_LOG_PATH, ""), mode="a", maxBytes=30*1024, backupCount=2)
# fh.setLevel(Settings.LOG_LEVEL)
# app_logger.addHandler(fh)