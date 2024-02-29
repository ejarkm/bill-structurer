import json
import base64
import requests


# Function to encode the image to base64
def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


# def bill_parser(*, api_key, model, system_prompt, image_url, max_tokens=2000):
#     client = OpenAI(api_key=api_key)
#     response = client.chat.completions.create(
#         model=model,
#         messages=[
#             {
#                 "role": "user",
#                 "content": [
#                     {"type": "text", "text": system_prompt},
#                     {"type": "image_url", "image_url": image_url},
#                 ],
#             }
#         ],
#         max_tokens=max_tokens,
#     )
#     parsed_response = response.choices[0].message.content
#     parsed_response = parsed_response.split("```json")[1].split("```")[0].strip()
#     parsed_response = json.loads(parsed_response)

#     return parsed_response


def bill_parser(*, api_key, model, system_prompt, image_path, max_tokens=2000):
    # Encode the provided image to base64
    base64_image = encode_image_to_base64(image_path)

    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}

    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": system_prompt},
                    {"type": "image_url", "image_url": f"data:image/jpeg;base64,{base64_image}"},
                ],
            }
        ],
        "max_tokens": max_tokens,
    }

    response = requests.post(
        "https://api.openai.com/v1/chat/completions", headers=headers, json=payload
    )

    # Assuming response structure is similar to the original snippet,
    # and that we're meant to parse a JSON response embedded in the reply.
    # The actual path to the content may need adjustment based on actual API response.
    try:
        parsed_response_text = response.json()["choices"][0]["message"]["content"]
        parsed_response = json.loads(
            parsed_response_text.split("```json")[1].split("```")[0].strip()
        )
    except KeyError:
        # Fall back if parsing fails
        parsed_response = {
            "error": "Failed to parse API response",
            "full_response": response.json(),
        }

    return parsed_response
