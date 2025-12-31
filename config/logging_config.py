import logging
import sys

def setup_logging(debug=False):
    level = logging.DEBUG if debug else logging.INFO

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=level,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('bot.log', encoding='utf-8')
        ]
    )

    # Suppress verbose libraries
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('telegram').setLevel(logging.WARNING)
    logging.getLogger('apscheduler').setLevel(logging.WARNING)

    return logging.getLogger(__name__)
