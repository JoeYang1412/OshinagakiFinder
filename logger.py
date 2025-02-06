import logging
from pathlib import Path

class LoggerManager:
    """
    Responsible for creating a logger, allowing each module to log independently.
    """
    # set the log directory
    LOG_DIR = Path("./logs") 

    def __init__(self, log_name: str):
        """
        Initialize the logger
        - log_name: The name of the log file for this logger
        - Logs will be saved to logs/{log_name}.log
        """
        # Create the log directory if it does not exist
        self.LOG_DIR.mkdir(parents=True, exist_ok=True)  
        self.log_file = self.LOG_DIR / f"{log_name}.log"

        # Create a logger object
        self.logger = logging.getLogger(log_name)
        self.logger.setLevel(logging.INFO)

        # If the logger does not have any handlers, add a FileHandler
        if not self.logger.handlers:
            file_handler = logging.FileHandler(self.log_file, mode="a", encoding="utf-8")
            file_handler.setLevel(logging.INFO)

            # Set the log format
            formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
            file_handler.setFormatter(formatter)

            # Add the handler to the logger
            self.logger.addHandler(file_handler)

    def get_logger(self):
        """
        Return the logger object for module use
        """
        return self.logger
