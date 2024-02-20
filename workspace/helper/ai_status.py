
import requests
import time

URL = 'http://localhost:8501/v1/models/tool_classifier:predict'

def is_ai_ready():
    try:
        response = requests.get(URL)
        return response.status_code == 400
    except Exception:
        return False
    
def wait_for_ai():
    while not is_ai_ready():
        print(".", end="", flush=True)
        time.sleep(1)
