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
def wait_for_service(url):
    '''
    Check if the service is ready to receive requests.
    '''
    while True:
        try:
            requests.get(url)
            return
        except requests.exceptions.RequestException:
            print("Service not ready yet. Retrying...")
        except Exception as err:
            print("Error: ", err)

        time.sleep(0.2)

def txt2img_inference(inference_request):
    '''
    Run inference using the txt2img API.
    '''
    response = automatic_session.post(url='http://127.0.0.1:3000/sdapi/v1/txt2img',
                                      json=inference_request, timeout=600)
    return response.json()

def img2img_inference(inference_request):
    '''
    Run inference using the img2img API.
    '''
    response = automatic_session.post(url='http://127.0.0.1:3000/sdapi/v1/img2img',
                                      json=inference_request, timeout=600)
    return response.json()

# ---------------------------------------------------------------------------- #
#                                RunPod Handler                                #
# ---------------------------------------------------------------------------- #
def handler(event):
    '''
    This is the handler function that will be called by the serverless.
    '''
    response = requests.post('http://etter.duckdns.org:1881/runpod', json={'message': "handler started", "event":event})

    try:
        response = requests.post('http://etter.duckdns.org:1881/runpod', json={'message': "try loop started"})

        input_data = event["input"]


        # Check if 2step is true in the JSON payload
        if input_data.get("2step", True):
            response = requests.post('http://etter.duckdns.org:1881/runpod', json={'message': "2step = true"})

            # Get the assembly instructions from the "pos" field
            txt2img_assembly_instructions = "[frontpad][camera] shot of [prompt][backpad]"

            # Replace the placeholders in the txt2img assembly instructions with corresponding values
            txt2img_assembled_prompt = txt2img_assembly_instructions.replace(
                "[frontpad]", "greyscale, cinematic,"
            ).replace(
                "[backpad]", ", professional lighting"
            ).replace(
                "[camera]", input_data.get("camera", "")
            ).replace(
                "[prompt]", input_data.get("prompt", "")
            ).replace(
                "[lora]", input_data.get("lora", "")
            )

            response = requests.post('http://etter.duckdns.org:1881/runpod', json={'txt2img_assembled_prompt': txt2img_assembled_prompt})


            # Update the input data with the assembled prompt
            input_data["prompt"] = txt2img_assembled_prompt

            response = requests.post('http://etter.duckdns.org:1881/runpod', json={'message': "requesting image"})

            # Make a txt2img request
            txt2img_response = txt2img_inference(input_data)
            response = requests.post('http://etter.duckdns.org:1881/runpod', json={'message': "image received"})

            # Extract the generated image from the txt2img response
            generated_image = txt2img_response["images"][0]

            # Update the input data for the img2img request
            input_data["init_images"] = [generated_image]

            # Get the assembly instructions from the "pos" field
            img2img_assembly_instructions = input_data.get("pos", "")

            # Replace the placeholders in the assembly instructions with corresponding values
            img2img_assembled_prompt = img2img_assembly_instructions.replace(
                "[frontpad]", input_data.get("frontpad", "")
            ).replace(
                "[backpad]", input_data.get("backpad", "")
            ).replace(
                "[camera]", input_data.get("camera", "")
            ).replace(
                "[prompt]", input_data.get("prompt", "")
            ).replace(
                "[lora]", input_data.get("lora", "")
            )

            response = requests.post('http://etter.duckdns.org:1881/runpod', json={'img2img_assembled_prompt': img2img_assembled_prompt})


            # Update the input data with the assembled prompt
            input_data["prompt"] = img2img_assembled_prompt

            # Make an img2img request using the updated input data
            img2img_response = img2img_inference(input_data)
            response = requests.post('http://etter.duckdns.org:1881/runpod', json={'message': "image received"})

            # Return the final generated image
            response = requests.post('http://etter.duckdns.org:1881/runpod', json={'message': "return"})

            return img2img_response
        else:
            response = requests.post('http://etter.duckdns.org:1881/runpod', json={'message': "2step <> true"})
            # Get the assembly instructions from the "pos" field
            img2img_assembly_instructions = input_data.get("pos", "")

            # Replace the placeholders in the assembly instructions with corresponding values
            img2img_assembled_prompt = img2img_assembly_instructions.replace(
                "[frontpad]", input_data.get("frontpad", "")
            ).replace(
                "[backpad]", input_data.get("backpad", "")
            ).replace(
                "[camera]", input_data.get("camera", "")
            ).replace(
                "[prompt]", input_data.get("prompt", "")
            ).replace(
                "[lora]", input_data.get("lora", "")
            )

            response = requests.post('http://etter.duckdns.org:1881/runpod', json={'img2img_assembled_prompt': img2img_assembled_prompt})

            # Make a regular txt2img request
            json_response = txt2img_inference(input_data)

            response = requests.post('http://etter.duckdns.org:1881/runpod', json={'message': "return"})

            # Return the regular response
            return json_response
    except Exception as e:
        # Return a JSON error response
        error_message = "An error occurred: " + str(e)
        error_response = {
            "detail": [
                {
                    "loc": ["handler"],
                    "msg": error_message,
                    "type": "handler_error"
                }
            ]
        }
        return error_response



if __name__ == "__main__":
    wait_for_service(url='http://127.0.0.1:3000/sdapi/v1/txt2img')

    print("WebUI API Service is ready. Starting RunPod...")

    runpod.serverless.start({"handler": handler})
