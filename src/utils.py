import logging

# Configure the logging system
logging.basicConfig(
    level=logging.INFO,  # Set the logging level
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # Set the log message format
    handlers=[
        logging.FileHandler("logs/parser.log"),  # Log to a file
        logging.StreamHandler(),  # Log to the console
    ],
)

# Create a logger object
logger = logging.getLogger("fipi-parser")
