import uvicorn
import multiprocessing
import os
import sys

# Add the project directory to the Python path
sys.path.append('/project')

def run_fastapi():
    uvicorn.run("data_api:app", host="0.0.0.0", port=8000, log_level='info')

def run_dash():
    os.environ['DASH_URL_BASE_PATHNAME'] = '/projects/nvidia-alm/applications/dash-app/'
    os.system("python /project/code/app.py")

if __name__ == "__main__":
    api_process = multiprocessing.Process(target=run_fastapi)
    dash_process = multiprocessing.Process(target=run_dash)
    
    api_process.start()
    dash_process.start()
    
    api_process.join()
    dash_process.join()