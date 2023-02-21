import hashlib
from io import BytesIO
from typing import Optional

import requests
from PIL import Image
from .logger import log


from functools import lru_cache


@lru_cache
def load_profile_picture(email: str, size: int) -> Optional["Image"]:
    """
    returns profile picture associated with email on gravatar.com, or None if no picture was found.
    """
    if not email:
        return None

    url = (
        "https://www.gravatar.com/avatar/"
        + hashlib.md5(email.lower().encode("utf8")).hexdigest()
    )

    response = requests.get(url, params={"size": size, "d": "404"})
    if response.status_code != 200:
        log.warning(
            "no profile picture found for %s, %s",
            email,
            response.status_code,
        )
        return

    profile_picture = Image.open(BytesIO(response.content))
    return (
        profile_picture
        if profile_picture.mode == "RGB"
        else profile_picture.convert("RGB")
    )
