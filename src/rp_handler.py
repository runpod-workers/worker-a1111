import time

import runpod
import requests
from requests.adapters import HTTPAdapter, Retry

automatic_session = requests.Session()
retries = Retry(total=10, backoff_factor=0.1, status_forcelist=[502, 503, 504])
automatic_session.mount('http://', HTTPAdapter(max_retries=retries))


# ---------------------------------------------------------------------------- #
#                              Automatic Functions                             #
# ---------------------------------------------------------------------------- #
def is_service_ready(url):
    '''
    Check if the service is ready to receive requests.
    '''
    try:
        response = requests.get(url, timeout=3)
        return response.status_code == 405
    except ConnectionError:
        return False


def run_inference(inference_request):
    '''
    Run inference on a request.
    '''
    response = automatic_session.post(url='http://127.0.0.1:3000/sdapi/v1/txt2img',
                                      json=inference_request, timeout=600)
    return response.json()


# ---------------------------------------------------------------------------- #
#                                RunPod Handler                                #
# ---------------------------------------------------------------------------- #
def handler(event):
    '''
    This is the handler function that will be called by the serverless.
    '''

    json = run_inference(event["input"])

    # return the output that you want to be returned like pre-signed URLs to output artifacts
    return json


if __name__ == "__main__":
    while is_service_ready(url='http://127.0.0.1:3000/sdapi/v1/txt2img'):
        print("Service not ready yet. Retrying...")
        time.sleep(0.2)

    print("WebUI API Service is ready. Starting RunPod...")

    runpod.serverless.start({"handler": handler})
