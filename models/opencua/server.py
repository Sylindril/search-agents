#!/usr/bin/env python3
"""
OpenCUA-7B OpenAI-Compatible API Server

Simple, robust API server for OpenCUA-7B with streaming and batch support.
"""

import argparse
import base64
import io
import os
import time
import uuid
import json
from typing import List, Optional, Union
import asyncio

import torch
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from pydantic import BaseModel, Field
from transformers import AutoImageProcessor, AutoModel, AutoTokenizer


# ============================================================================
# Pydantic Models
# ============================================================================

class ImageUrl(BaseModel):
    url: str
    detail: Optional[str] = "auto"


class ContentPart(BaseModel):
    type: str
    text: Optional[str] = None
    image_url: Optional[ImageUrl] = None
    image: Optional[str] = None


class Message(BaseModel):
    role: str
    content: Union[str, List[ContentPart]]


class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[Message]
    temperature: Optional[float] = 0.0
    top_p: Optional[float] = 1.0
    max_tokens: Optional[int] = 512
    n: Optional[int] = 1
    stream: Optional[bool] = False


class ChatCompletionChoice(BaseModel):
    index: int
    message: Message
    finish_reason: str


class Usage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[ChatCompletionChoice]
    usage: Usage


class DeltaMessage(BaseModel):
    role: Optional[str] = None
    content: Optional[str] = None


class ChatCompletionChunkChoice(BaseModel):
    index: int
    delta: DeltaMessage
    finish_reason: Optional[str] = None


class ChatCompletionChunk(BaseModel):
    id: str
    object: str = "chat.completion.chunk"
    created: int
    model: str
    choices: List[ChatCompletionChunkChoice]


# ============================================================================
# Global State
# ============================================================================

app = FastAPI(title="OpenCUA-7B API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = None
tokenizer = None
image_processor = None
MODEL_NAME = "OpenCUA-7B"


# ============================================================================
# Helper Functions
# ============================================================================

def setup_cache(cache_dir: Optional[str] = None):
    """Setup HuggingFace cache directory."""
    if cache_dir:
        if os.access(cache_dir, os.W_OK):
            os.environ['HF_HOME'] = cache_dir
            print(f"Using HuggingFace cache: {cache_dir}")
            return cache_dir
        else:
            print(f"Warning: Cannot write to {cache_dir}, using default cache")

    # Fall back to local cache
    local_cache = os.path.expanduser("~/.cache/huggingface")
    os.makedirs(local_cache, exist_ok=True)
    os.environ['HF_HOME'] = local_cache
    print(f"Using HuggingFace cache: {local_cache}")
    return local_cache


def load_model(model_path_or_id: str):
    """Load model from HuggingFace or local path."""
    global model, tokenizer, image_processor

    print(f"Loading model from {model_path_or_id}...")

    # Auto download from HuggingFace if needed
    if not os.path.exists(model_path_or_id):
        print(f"Model not found locally, will download from HuggingFace: {model_path_or_id}")

    tokenizer = AutoTokenizer.from_pretrained(model_path_or_id, trust_remote_code=True)
    print("✓ Tokenizer loaded")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    model = AutoModel.from_pretrained(
        model_path_or_id,
        torch_dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32,
        trust_remote_code=True,
        attn_implementation="eager"
    ).to(device)
    print(f"✓ Model loaded on {device}")

    image_processor = AutoImageProcessor.from_pretrained(model_path_or_id, trust_remote_code=True)
    print("✓ Image processor loaded")

    print(f"\n{'='*60}")
    print(f"OpenCUA-7B ready for inference!")
    print(f"{'='*60}\n")


def decode_base64_image(data_url: str) -> Image.Image:
    """Decode base64 image."""
    if data_url.startswith("data:"):
        _, base64_data = data_url.split(",", 1)
    else:
        base64_data = data_url

    image_bytes = base64.b64decode(base64_data)
    return Image.open(io.BytesIO(image_bytes)).convert("RGB")


def extract_images_and_text(messages: List[Message]):
    """Extract images and text from messages."""
    messages_for_chat = []
    images = []

    for msg in messages:
        role = msg.role
        content = msg.content

        if isinstance(content, str):
            messages_for_chat.append({"role": role, "content": content})
        else:
            combined_content = []
            for part in content:
                if part.type == "text" and part.text:
                    combined_content.append({"type": "text", "text": part.text})
                elif part.type == "image_url" and part.image_url:
                    img = decode_base64_image(part.image_url.url)
                    images.append(img)
                    combined_content.append({"type": "image", "image": part.image_url.url})
                elif part.type == "image" and part.image:
                    img = decode_base64_image(part.image)
                    images.append(img)
                    combined_content.append({"type": "image", "image": part.image})

            messages_for_chat.append({"role": role, "content": combined_content})

    return messages_for_chat, images


def run_inference(messages: List[dict], images: List[Image.Image],
                  temperature: float = 0.0, max_tokens: int = 512) -> str:
    """Run inference."""
    input_ids = tokenizer.apply_chat_template(
        messages, tokenize=True, add_generation_prompt=True
    )
    input_ids = torch.tensor([input_ids]).to(model.device)

    # Prepare images
    if images:
        image_info = image_processor.preprocess(images=images)
        pixel_values = torch.tensor(image_info['pixel_values']).to(
            dtype=torch.bfloat16, device=model.device
        )
        grid_thws = torch.tensor(image_info['image_grid_thw'])
    else:
        pixel_values = None
        grid_thws = None

    # Generate
    with torch.no_grad():
        gen_kwargs = {
            "max_new_tokens": max_tokens,
            "temperature": temperature if temperature > 0 else None,
            "do_sample": temperature > 0,
        }

        if pixel_values is not None:
            gen_kwargs["pixel_values"] = pixel_values
            gen_kwargs["grid_thws"] = grid_thws

        generated_ids = model.generate(input_ids, **gen_kwargs)

    # Decode
    prompt_len = input_ids.shape[1]
    output_text = tokenizer.batch_decode(
        generated_ids[:, prompt_len:],
        skip_special_tokens=True,
        clean_up_tokenization_spaces=False
    )[0]

    return output_text


async def stream_inference(messages: List[dict], images: List[Image.Image],
                           temperature: float = 0.0, max_tokens: int = 512,
                           request_id: str = None, model_name: str = MODEL_NAME):
    """Stream inference token by token."""
    # For simplicity, we'll do single shot and chunk the output
    # Real streaming would require model.generate with streamer
    output = run_inference(messages, images, temperature, max_tokens)

    # Stream character by character
    for i, char in enumerate(output):
        chunk = ChatCompletionChunk(
            id=request_id,
            created=int(time.time()),
            model=model_name,
            choices=[ChatCompletionChunkChoice(
                index=0,
                delta=DeltaMessage(content=char),
                finish_reason=None
            )]
        )
        yield f"data: {chunk.model_dump_json()}\n\n"
        await asyncio.sleep(0.01)  # Small delay for streaming effect

    # Final chunk
    final_chunk = ChatCompletionChunk(
        id=request_id,
        created=int(time.time()),
        model=model_name,
        choices=[ChatCompletionChunkChoice(
            index=0,
            delta=DeltaMessage(content=""),
            finish_reason="stop"
        )]
    )
    yield f"data: {final_chunk.model_dump_json()}\n\n"
    yield "data: [DONE]\n\n"


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/health")
async def health():
    return {"status": "ok", "model": MODEL_NAME}


@app.get("/v1/models")
async def list_models():
    return {
        "object": "list",
        "data": [{
            "id": MODEL_NAME,
            "object": "model",
            "created": int(time.time()),
            "owned_by": "xlangai"
        }]
    }


@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    """OpenAI-compatible chat completions with streaming support."""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        messages_for_chat, images = extract_images_and_text(request.messages)
        request_id = f"chatcmpl-{uuid.uuid4().hex[:8]}"

        # Handle streaming
        if request.stream:
            return StreamingResponse(
                stream_inference(
                    messages_for_chat,
                    images,
                    request.temperature or 0.0,
                    request.max_tokens or 512,
                    request_id,
                    request.model
                ),
                media_type="text/event-stream"
            )

        # Non-streaming
        output = run_inference(
            messages=messages_for_chat,
            images=images,
            temperature=request.temperature or 0.0,
            max_tokens=request.max_tokens or 512
        )

        # Build response
        response = ChatCompletionResponse(
            id=request_id,
            created=int(time.time()),
            model=request.model,
            choices=[ChatCompletionChoice(
                index=0,
                message=Message(role="assistant", content=output),
                finish_reason="stop"
            )],
            usage=Usage(
                prompt_tokens=len(str(request.messages)) // 4,
                completion_tokens=len(output) // 4,
                total_tokens=(len(str(request.messages)) + len(output)) // 4
            )
        )

        return response

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Main
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="OpenCUA-7B API Server")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--model", type=str, default="xlangai/OpenCUA-7B",
                        help="Model ID or path")
    parser.add_argument("--cache-dir", type=str, default=None,
                        help="HuggingFace cache directory")
    args = parser.parse_args()

    # Setup cache
    setup_cache(args.cache_dir)

    # Load model
    load_model(args.model)

    # Start server
    print(f"\n{'='*60}")
    print(f"OpenCUA-7B API Server")
    print(f"Endpoint: http://{args.host}:{args.port}/v1/chat/completions")
    print(f"Health: http://{args.host}:{args.port}/health")
    print(f"{'='*60}\n")

    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
