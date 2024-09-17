import logging
from typing import Any, Dict

import bcrypt

logging.basicConfig(filename="api_requests.log", level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger()


def check_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password, hashed)


def log_request(data: Dict[str, Any]) -> None:
    logger.info(data)
