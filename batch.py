"""
Main application file
"""
import logging

# Initialize Logger
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

if __name__ == '__main__':
    LOGGER.info('Running')