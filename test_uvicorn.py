from fastapi import FastAPI, HTTPException
import uvicorn
import requests
import time
import threading
import sys

app = FastAPI()

@app.post("/test")
def test():
    raise HTTPException(status_code=500, detail="Custom detail")

def run_server():
    uvicorn.run(app, host="127.0.0.1", port=8002)

if __name__ == "__main__":
    t = threading.Thread(target=run_server, daemon=True)
    t.start()
    time.sleep(2)
    try:
        res = requests.post("http://127.0.0.1:8002/test")
        print(res.status_code, res.text)
    except Exception as e:
        print(e)
    time.sleep(1)
    sys.exit(0)
