#!/usr/bin/env python3
"""
OpenCUA-7B OpenAI-Compatible API Server

This server provides an OpenAI-compatible /v1/chat/completions endpoint
for the OpenCUA-7B GUI grounding model.

Usage:
    python scripts/serve_opencua.py [--port 8000] [--model-path ./OpenCUA-7B]
"""

import argparse
import base64
import io
import os
import time
import uuid
from typing import List, Optional, Union

import torch
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from pydantic import BaseModel, Field
from transformers import AutoImageProcessor, AutoModel, AutoTokenizer

# ============================================================================
# Pydantic Models for OpenAI-compatible API
# ============================================================================

class ImageUrl(BaseModel):
    url: str
    detail: Optional[str] = "auto"


class ContentPart(BaseModel):
    type: str  # "text" or "image_url"
    text: Optional[str] = None
    image_url: Optional[ImageUrl] = None
    image: Optional[str] = None  # For direct base64 data:image format


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


# ============================================================================
# Global Model Variables
# ============================================================================

app = FastAPI(title="OpenCUA-7B API Server")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model instances (loaded at startup)
model = None
tokenizer = None
image_processor = None
device = None
MODEL_NAME = "OpenCUA-7B"


# ============================================================================
# Helper Functions
# ============================================================================

def download_model(model_path: str) -> str:
    """Download OpenCUA-7B model if not already present."""
    if os.path.exists(model_path) and os.path.isdir(model_path):
        # Check if model files exist
        required_files = ["config.json", "tokenizer.json"]
        if all(os.path.exists(os.path.join(model_path, f)) for f in required_files):
            print(f"Model already exists at {model_path}")
            return model_path
    
    print(f"Downloading OpenCUA-7B to {model_path}...")
    from huggingface_hub import snapshot_download
    
    snapshot_download(
        repo_id="xlangai/OpenCUA-7B",
        local_dir=model_path,
        local_dir_use_symlinks=False
    )
    print(f"Model downloaded to {model_path}")
    return model_path


def load_model(model_path: str):
    """Load OpenCUA model, tokenizer, and image processor."""
    global model, tokenizer, image_processor, device
    
    print(f"Loading model from {model_path}...")
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
    print("Tokenizer loaded.")
    
    model = AutoModel.from_pretrained(
        model_path,
        torch_dtype="auto",
        device_map="auto",
        trust_remote_code=True
    )
    print("Model loaded.")
    
    image_processor = AutoImageProcessor.from_pretrained(model_path, trust_remote_code=True)
    print("Image processor loaded.")
    
    print("OpenCUA-7B ready for inference!")


def decode_base64_image(data_url: str) -> Image.Image:
    """Decode a base64 data URL to PIL Image."""
    # Handle data:image/png;base64,... format
    if data_url.startswith("data:"):
        # Extract the base64 part after the comma
        header, base64_data = data_url.split(",", 1)
    else:
        # Assume raw base64
        base64_data = data_url
    
    image_bytes = base64.b64decode(base64_data)
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    return image


def extract_images_and_text(messages: List[Message]) -> tuple:
    """
    Extract images and build text messages from OpenAI-format messages.
    
    Returns:
        - messages_for_chat_template: List of dicts for tokenizer.apply_chat_template
        - images: List of PIL Images
    """
    messages_for_chat = []
    images = []
    
    for msg in messages:
        role = msg.role
        content = msg.content
        
        if isinstance(content, str):
            # Simple text message
            messages_for_chat.append({"role": role, "content": content})
        else:
            # Multimodal message with content parts
            combined_content = []
            for part in content:
                if part.type == "text" and part.text:
                    combined_content.append({"type": "text", "text": part.text})
                elif part.type == "image_url" and part.image_url:
                    # Decode the image
                    try:
                        img = decode_base64_image(part.image_url.url)
                        images.append(img)
                        # Add image placeholder to content
                        combined_content.append({
                            "type": "image",
                            "image": part.image_url.url
                        })
                    except Exception as e:
                        print(f"Warning: Failed to decode image: {e}")
                elif part.type == "image" and part.image:
                    # Direct image format
                    try:
                        img = decode_base64_image(part.image)
                        images.append(img)
                        combined_content.append({
                            "type": "image",
                            "image": part.image
                        })
                    except Exception as e:
                        print(f"Warning: Failed to decode image: {e}")
            
            messages_for_chat.append({"role": role, "content": combined_content})
    
    return messages_for_chat, images


def run_inference(messages: List[dict], images: List[Image.Image], 
                  temperature: float = 0.0, max_tokens: int = 512,
                  num_outputs: int = 1) -> List[str]:
    """Run inference on the OpenCUA model."""
    global model, tokenizer, image_processor
    
    # Prepare text input using chat template
    input_ids = tokenizer.apply_chat_template(
        messages, tokenize=True, add_generation_prompt=True
    )
    input_ids = torch.tensor([input_ids]).to(model.device)
    
    # Prepare image input if images are provided
    if images:
        image_info = image_processor.preprocess(images=images)
        pixel_values = torch.tensor(image_info['pixel_values']).to(
            dtype=torch.bfloat16, device=model.device
        )
        grid_thws = torch.tensor(image_info['image_grid_thw'])
    else:
        pixel_values = None
        grid_thws = None
    
    # Generate responses
    outputs = []
    for _ in range(num_outputs):
        with torch.no_grad():
            if pixel_values is not None:
                generated_ids = model.generate(
                    input_ids,
                    pixel_values=pixel_values,
                    grid_thws=grid_thws,
                    max_new_tokens=max_tokens,
                    temperature=temperature if temperature > 0 else None,
                    do_sample=temperature > 0,
                )
            else:
                generated_ids = model.generate(
                    input_ids,
                    max_new_tokens=max_tokens,
                    temperature=temperature if temperature > 0 else None,
                    do_sample=temperature > 0,
                )
        
        # Decode output (skip the prompt tokens)
        prompt_len = input_ids.shape[1]
        generated_ids = generated_ids[:, prompt_len:]
        output_text = tokenizer.batch_decode(
            generated_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False
        )[0]
        outputs.append(output_text)
    
    return outputs


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "model": MODEL_NAME}


@app.get("/v1/models")
async def list_models():
    """List available models (OpenAI-compatible)."""
    return {
        "object": "list",
        "data": [
            {
                "id": MODEL_NAME,
                "object": "model",
                "created": int(time.time()),
                "owned_by": "xlangai"
            }
        ]
    }


@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    """
    OpenAI-compatible chat completions endpoint.
    
    Supports multimodal input with images encoded as base64 data URLs.
    """
    global model, tokenizer, image_processor
    
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Extract images and build messages for the model
        messages_for_chat, images = extract_images_and_text(request.messages)
        
        # Run inference
        outputs = run_inference(
            messages=messages_for_chat,
            images=images,
            temperature=request.temperature or 0.0,
            max_tokens=request.max_tokens or 512,
            num_outputs=request.n or 1
        )
        
        # Build response
        choices = []
        for idx, output in enumerate(outputs):
            choices.append(ChatCompletionChoice(
                index=idx,
                message=Message(role="assistant", content=output),
                finish_reason="stop"
            ))
        
        # Estimate token counts (rough approximation)
        prompt_tokens = sum(len(str(m.content)) // 4 for m in request.messages)
        completion_tokens = sum(len(o) // 4 for o in outputs)
        
        response = ChatCompletionResponse(
            id=f"chatcmpl-{uuid.uuid4().hex[:8]}",
            created=int(time.time()),
            model=request.model,
            choices=choices,
            usage=Usage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens
            )
        )
        
        return response
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="OpenCUA-7B API Server")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the server on")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--model-path", type=str, default="./OpenCUA-7B", 
                        help="Path to model weights (will download if not present)")
    args = parser.parse_args()
    
    # Download and load model
    model_path = download_model(args.model_path)
    load_model(model_path)
    
    # Start server
    print(f"\n{'='*60}")
    print(f"OpenCUA-7B API Server starting on http://{args.host}:{args.port}")
    print(f"OpenAI-compatible endpoint: http://{args.host}:{args.port}/v1/chat/completions")
    print(f"{'='*60}\n")
    
    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()

