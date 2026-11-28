import os
import sys
import uvicorn

if __name__ == "__main__":
    backend_dir = os.path.join(os.path.dirname(__file__), "backend")
    sys.path.insert(0, backend_dir)
    print("Starting FastAPI Electoral Forensics Backend on http://localhost:8000...")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True, app_dir=backend_dir)
