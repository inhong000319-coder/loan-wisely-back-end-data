from requests import Response, RequestException


def unwrap_api_response(resp: Response):
    try:
        payload = resp.json()
    except ValueError as exc:
        raise RequestException("Invalid JSON response") from exc

    if isinstance(payload, dict) and "data" in payload and "success" in payload:
        if not payload.get("success", True):
            raise RequestException(payload.get("message") or "Upstream error")
        return payload.get("data")

    return payload
