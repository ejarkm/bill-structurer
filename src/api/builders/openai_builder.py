from openai import OpenAI
import json


# Complete it
def bill_parser(*, api_key, model, system_prompt, image_url, max_tokens=2000):
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": system_prompt},
                    {"type": "image_url", "image_url": image_url},
                ],
            }
        ],
        max_tokens=max_tokens,
    )
    parsed_response = response.choices[0].message.content
    parsed_response = parsed_response.split("```json")[1].split("```")[0].strip()
    parsed_response = json.loads(parsed_response)

    return parsed_response
