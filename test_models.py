import sys
from google import genai

client = genai.Client(api_key="AIzaSyC-NvnO5AO04k2ieA-myfIMY__wuhBnORI")

models_to_test = [
    'gemini-2.5-flash',
    'gemini-2.0-flash',
    'gemini-1.5-flash',
    'gemini-1.5-flash-8b'
]

for m in models_to_test:
    print(f"Testing {m}...")
    try:
        response = client.models.generate_content(
            model=m,
            contents='hello'
        )
        print(f"SUCCESS: {m}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"FAILED: {m}")
        print(f"Error: {e}")
    print("-" * 40)
