import os

import uvicorn  # skipcq: PY-W2000, PY-R1000, PY-A6006
from fastapi import FastAPI

from .routes import router


if os.getenv("DEBUG_MODE", "false").lower() == "true":
    import pydevd_pycharm

    print("DEBUG_MODE is true in main.py, attempting to connect to PyCharm debugger...")
    pydevd_pycharm.settrace(
        "host.docker.internal", #"'localhost',
        port=5678,  # 5678,
        stdoutToServer=True,
        stderrToServer=True,
        suspend=False
    )

app = FastAPI(title="Mock Order API")

app.include_router(router)
