"""Retry hosted RPC transport failures, never semantic contract failures."""
import time
import requests
from genlayer_py.exceptions import GenLayerError
from genlayer_py.provider.provider import GenLayerProvider

ATTEMPTS = 8
_original = GenLayerProvider.make_request

def _is_transport(problem: GenLayerError) -> bool:
    text = str(problem)
    return (
        isinstance(problem.__cause__, requests.exceptions.RequestException)
        or "returned invalid JSON" in text
        or "code=-32429" in text
        or "code=-32029" in text
        or "code=429" in text
    )

def _with_retry(self, method, params):
    delay = 5
    for attempt in range(ATTEMPTS):
        try:
            return _original(self, method, params)
        except GenLayerError as problem:
            if not _is_transport(problem) or attempt == ATTEMPTS - 1:
                raise
            print(f"transport failure on {method} ({attempt + 1}/{ATTEMPTS}); retrying in {delay}s", flush=True)
            time.sleep(delay)
            delay = min(delay * 2, 60)

GenLayerProvider.make_request = _with_retry
