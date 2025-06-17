import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# gino off logs
logging.getLogger("gino.engine._SAEngine").setLevel(logging.ERROR)
logger = logging.getLogger(__name__)

# Set up the handler and formatter
handler = logging.StreamHandler()
# Add handler to the logger
logger.addHandler(handler)
