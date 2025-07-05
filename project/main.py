import multiprocessing
import time
import uvicorn
import frontend

def run_backend():
    uvicorn.run("backend:app", host="127.0.0.1", port=8000)

def run_frontend():
    frontend.main
    
if __name__ == "__main__":
    p = multiprocessing.Process(target=run_backend)
    p.start()
    time.sleep(1)
    import flet
    flet.app(target=frontend.main)
    p.join()