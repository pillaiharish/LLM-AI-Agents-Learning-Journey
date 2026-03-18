#!/usr/bin/env python3
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

import uvicorn

from api.app import create_app

app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "run:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
