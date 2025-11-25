import logging
import os
from datetime import datetime
from pathlib import Path

# Create logs directory
log_dir = Path(__file__).parent / "logs"
log_dir.mkdir(exist_ok=True)

# Create log filename with timestamp
log_file = log_dir / f"agent_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

# Configure logger
logger = logging.getLogger("ProductInfoAgent")
logger.setLevel(logging.DEBUG)

# File handler - detailed logs
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter(
    '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
file_handler.setFormatter(file_formatter)

# Console handler - only errors
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.ERROR)
console_formatter = logging.Formatter('%(levelname)s: %(message)s')
console_handler.setFormatter(console_formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Create latest.log symlink
latest_log = log_dir / "latest.log"
if latest_log.exists():
    latest_log.unlink()
try:
    latest_log.write_text(str(log_file))
except:
    pass

logger.info(f"Logging initialized: {log_file}")
