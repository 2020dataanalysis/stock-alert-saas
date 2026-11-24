import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from fastapi import HTTPException


BACKEND_URL = "http://127.0.0.1:8004"


def backend_request(method, path, params=None):
    url = f"{BACKEND_URL}{path}"

    if params:
        query = urlencode({
            key: value
            for key, value in params.items()
            if value is not None
        })

        if query:
            url = f"{url}?{query}"

    try:
        with urlopen(Request(url, method=method), timeout=60) as response:
            return json.load(response)

    except HTTPError as error:
        try:
            detail = json.load(error).get(
                "detail",
                "Backend request failed",
            )
        except (ValueError, OSError):
            detail = "Backend request failed"

        raise HTTPException(
            status_code=error.code,
            detail=detail,
        ) from None

    except (URLError, TimeoutError):
        raise HTTPException(
            status_code=503,
            detail="Backend service unavailable",
        ) from None


def backend_get(path, params=None):
    return backend_request("GET", path, params)


def backend_post(path, params=None):
    return backend_request("POST", path, params)
