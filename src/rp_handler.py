import runpod
import requests
from requests.adapters import HTTPAdapter, Retry

automatic_session = requests.Session()
retries = Retry(total=100, backoff_factor=0.01, status_forcelist=[502, 503, 504])
automatic_session.mount('http://', HTTPAdapter(max_retries=retries))


# ---------------------------------------------------------------------------- #
#                              Automatic Functions                             #
# ---------------------------------------------------------------------------- #
def is_service_ready(url):
    '''
    Check if the service is ready to receive requests.
    '''
    try:
        response = automatic_session.get(url, timeout=600)
        return response.status_code == 200
    except ConnectionError:
        return False


def run_inference(inference_request):
    '''
    Run inference on a request.
    '''
    response = automatic_session.post(url='http://127.0.0.1:3000/sdapi/v1/txt2img',
                                      json=inference_request, timeout=600)
    return response.json()


def handler(event):
    '''
    This is the handler function that will be called by the serverless.
    '''

    json = run_inference(event["input"])

    # return the output that you want to be returned like pre-signed URLs to output artifacts
    return json


if __name__ == "__main__":
    if is_service_ready(url='http://127.0.0.1:3000/sdapi/v1/txt2img'):
        runpod.serverless.start({"handler": handler})
