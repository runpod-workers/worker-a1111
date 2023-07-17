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
    print("txt2img")
    response = automatic_session.post(url='http://127.0.0.1:3000/sdapi/v1/txt2img',
                                      json=inference_request, timeout=600)
    return response.json()

def img2img_inference(inference_request):
    '''
    Run inference using the img2img API.
    '''
    print("img2img")
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
    print("Handler started:", event)

    try:
        print("try loop started")

        input_data = event["input"]
        prompt = input_data["prompt"]

        # Check if 2step is true in the JSON payload
        if input_data.get("2step") is True:
            print("2step = true")

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

            print("txt2img_assembled_prompt:", txt2img_assembled_prompt)

            # Update the input data with the assembled prompt
            input_data["prompt"] = txt2img_assembled_prompt

            print("requesting image")

            # Make a txt2img request
            txt2img_response = txt2img_inference(input_data)
            print("image received")

            # Extract the generated image from the txt2img response
            generated_image = txt2img_response["images"][0]

            # Update the input data for the img2img request
            input_data["init_images"] = [generated_image]

            # Add a new entry in input_data for alwayson_scripts
            input_data["alwayson_scripts"] = {
                "controlnet": {
                    "args": [
                        {
                            "input_image": generated_image,
                            "module": "openpose",
                            "model": "control_sd15_openpose [fef5e48e]",
                        }
                    ]
                }
            }

            # Update the input data with the original prompt
            input_data["prompt"] = prompt

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

            print("img2img_assembled_prompt:", img2img_assembled_prompt)

            # Update the input data with the assembled prompt
            input_data["prompt"] = img2img_assembled_prompt

            print("requesting image")

            # Make an img2img request using the updated input data
            img2img_response = img2img_inference(input_data)

            print("image received")

            # Return the final generated image
            print("return")

            return img2img_response
        else:
            print("2step <> true")
            # Get the assembly instructions from the "pos" field
            txt2img_assembly_instructions = input_data.get("pos", "")

            # Replace the placeholders in the assembly instructions with corresponding values
            txt2img_assembled_prompt = txt2img_assembly_instructions.replace(
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

            print("img2img_assembled_prompt:", txt2img_assembled_prompt)

            # Update the input data with the assembled prompt
            input_data["prompt"] = txt2img_assembled_prompt

            print("requesting image")
            # Make a regular txt2img request
            json_response = txt2img_inference(input_data)
            print("image received")

            print("return")

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
        print("error:", error_message)
        return error_response

if __name__ == "__main__":
    wait_for_service(url='http://127.0.0.1:3000/sdapi/v1/txt2img')

    print("WebUI API Service is ready. Starting RunPod...")