import logging

# Configure the logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],  # Outputs logs to the console
)

# Create a logger instance
logger = logging.getLogger("MinMod")
