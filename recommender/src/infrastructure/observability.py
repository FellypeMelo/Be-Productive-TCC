import json
import logging
import threading
import time
import uuid
from collections import defaultdict

from fastapi import Request, Response


logger = logging.getLogger("be_productive.recommender")
_lock = threading.Lock()
_requests = defaultdict(int)
_duration = defaultdict(float)


async def observe_request(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", "")[:128] or uuid.uuid4().hex
    started = time.perf_counter()
    status_code = 500
    try:
        response = await call_next(request)
        status_code = response.status_code
        response.headers["X-Request-ID"] = request_id
        return response
    finally:
        elapsed = time.perf_counter() - started
        route = request.scope.get("route")
        path = getattr(route, "path", "unmatched")
        key = (request.method, path, status_code)
        with _lock:
            _requests[key] += 1
            _duration[key] += elapsed
        logger.info(json.dumps({
            "duration_ms": round(elapsed * 1000, 2),
            "method": request.method,
            "path": path,
            "request_id": request_id,
            "status": status_code,
        }, separators=(",", ":")))


def metrics_response() -> Response:
    lines = []
    with _lock:
        for key, count in sorted(_requests.items()):
            method, route, status = key
            labels = f'method="{method}",route="{route}",status="{status}"'
            lines.append(f"be_productive_recommender_requests_total{{{labels}}} {count}")
            lines.append(
                f"be_productive_recommender_request_duration_seconds_sum{{{labels}}} {_duration[key]:.6f}"
            )
    return Response("\n".join(lines) + "\n", media_type="text/plain; version=0.0.4")
