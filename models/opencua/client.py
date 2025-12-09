#!/usr/bin/env python3
"""
Test client for OpenCUA API server.
"""

import base64
import sys
from openai import OpenAI


def encode_image(image_path: str) -> str:
    """Encode image to base64."""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def test_text_only(client: OpenAI):
    """Test text-only completion."""
    print("\n" + "="*60)
    print("Test 1: Text-only completion")
    print("="*60)

    response = client.chat.completions.create(
        model="OpenCUA-7B",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is 2+2?"}
        ],
        temperature=0,
        max_tokens=100
    )

    print(f"Response: {response.choices[0].message.content}")
    print(f"Usage: {response.usage}")


def test_multimodal(client: OpenAI, image_path: str):
    """Test multimodal completion."""
    print("\n" + "="*60)
    print("Test 2: Multimodal completion")
    print("="*60)

    image_base64 = encode_image(image_path)
    data_url = f"data:image/png;base64,{image_base64}"

    response = client.chat.completions.create(
        model="OpenCUA-7B",
        messages=[
            {
                "role": "system",
                "content": "You are a GUI agent. Given a screenshot and instruction, output the pyautogui command."
            },
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": data_url}},
                    {"type": "text", "text": "Click on the submit button"}
                ]
            }
        ],
        temperature=0,
        max_tokens=100
    )

    print(f"Response: {response.choices[0].message.content}")
    print(f"Usage: {response.usage}")


def test_streaming(client: OpenAI):
    """Test streaming completion."""
    print("\n" + "="*60)
    print("Test 3: Streaming completion")
    print("="*60)

    stream = client.chat.completions.create(
        model="OpenCUA-7B",
        messages=[
            {"role": "user", "content": "Count from 1 to 5"}
        ],
        temperature=0,
        max_tokens=100,
        stream=True
    )

    print("Streaming response: ", end="", flush=True)
    for chunk in stream:
        if chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="", flush=True)
    print()


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Test OpenCUA API")
    parser.add_argument("--base-url", default="http://localhost:8000/v1")
    parser.add_argument("--image", help="Path to test image for multimodal test")
    args = parser.parse_args()

    client = OpenAI(
        base_url=args.base_url,
        api_key="EMPTY"
    )

    # Test health
    import requests
    health_url = args.base_url.replace("/v1", "/health")
    try:
        resp = requests.get(health_url)
        print(f"Health check: {resp.json()}")
    except Exception as e:
        print(f"Health check failed: {e}")
        sys.exit(1)

    # Run tests
    test_text_only(client)

    if args.image:
        test_multimodal(client, args.image)

    test_streaming(client)

    print("\n" + "="*60)
    print("All tests completed!")
    print("="*60)


if __name__ == "__main__":
    main()
