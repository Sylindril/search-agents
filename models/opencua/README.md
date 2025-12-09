# OpenCUA-7B API Server

OpenAI-compatible API wrapper for OpenCUA-7B multimodal GUI grounding model.

## Features

- ✅ OpenAI-compatible `/v1/chat/completions` endpoint
- ✅ Multimodal support (text + base64-encoded images)
- ✅ Streaming responses (SSE)
- ✅ KV caching for faster inference
- ✅ Health check and model info endpoints
- ✅ Automatic model download from HuggingFace
- ✅ Configurable cache directory

## Quick Start

### 1. Run Setup Script

```bash
cd /home/adityaku/search-agents
./models/opencua/setup.sh
```

This creates a conda environment `opencua_inference` with all dependencies:
- transformers==4.53.0
- torch==2.8.0
- pillow==11.3.0
- tiktoken==0.11.0
- blobfile==3.0.0
- accelerate==1.10.0
- fastapi, uvicorn, openai, requests

### 2. Start the Server

```bash
./models/opencua/start_server.sh [PORT]
```

Examples:
```bash
# Start on default port 8000
./models/opencua/start_server.sh

# Start on custom port
./models/opencua/start_server.sh 8001

# Start with custom cache directory
./models/opencua/start_server.sh 8001 /path/to/cache
```

**Note**: First startup will download the model from HuggingFace (~16GB). Subsequent starts will use the cached model.

### 3. Test the Server

```bash
conda run -n opencua_inference python models/opencua/client.py
```

### 4. Stop the Server (Cleanup)

```bash
./models/opencua/cleanup.sh
```

This script:
- Kills all server processes
- Frees GPU memory
- Cleans up zombie processes
- Prevents NCCL and GPU memory errors

**Always run cleanup before restarting the server!**

## Usage

### Python (OpenAI Client)

```python
from openai import OpenAI
import base64

# Initialize client
client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="EMPTY"
)

# Text-only request
response = client.chat.completions.create(
    model="OpenCUA-7B",
    messages=[
        {"role": "user", "content": "What is 2+2?"}
    ],
    temperature=0,
    max_tokens=100
)
print(response.choices[0].message.content)

# Multimodal request (with image)
def encode_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

image_base64 = encode_image("screenshot.png")
data_url = f"data:image/png;base64,{image_base64}"

response = client.chat.completions.create(
    model="OpenCUA-7B",
    messages=[
        {
            "role": "system",
            "content": "You are a GUI agent. Output pyautogui commands."
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
print(response.choices[0].message.content)

# Streaming request
stream = client.chat.completions.create(
    model="OpenCUA-7B",
    messages=[{"role": "user", "content": "Count from 1 to 5"}],
    stream=True,
    temperature=0,
    max_tokens=50
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
print()
```

### cURL

```bash
# Health check
curl http://localhost:8000/health

# List models
curl http://localhost:8000/v1/models

# Chat completion
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "OpenCUA-7B",
    "messages": [{"role": "user", "content": "Hello!"}],
    "max_tokens": 100
  }'

# Streaming
curl -N -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "OpenCUA-7B",
    "messages": [{"role": "user", "content": "Count to 3"}],
    "max_tokens": 50,
    "stream": true
  }'
```

## SBATCH Deployment

Create `run_opencua_api.sh`:

```bash
#!/bin/bash
#SBATCH --job-name=opencua-api
#SBATCH --gres=gpu:1
#SBATCH --time=24:00:00
#SBATCH --mem=32G

cd /home/adityaku/search-agents
./models/opencua/start_server.sh 8000
```

Submit job:
```bash
sbatch run_opencua_api.sh
```

Get the node and port:
```bash
squeue -u $USER
# Note the node name (e.g., gpu-node-01)
```

Access from another process:
```bash
# Set environment variables
export OPENAI_API_BASE=http://localhost:8000/v1
export OPENAI_API_KEY=EMPTY

# Use in your code
python your_script.py
```

## Integration with Existing Codebase

This server is designed to work with the OMTW search-agents codebase:

```bash
# In terminal 1: Start the API server
./models/opencua/start_server.sh 8000

# In terminal 2: Run your agent
export OPENAI_API_BASE=http://localhost:8000/v1
export OPENAI_API_KEY=EMPTY
python run_omtw.py --model OpenCUA-7B
```

## API Endpoints

### `GET /health`
Health check endpoint.

**Response:**
```json
{"status": "ok", "model": "OpenCUA-7B"}
```

### `GET /v1/models`
List available models (OpenAI-compatible).

**Response:**
```json
{
  "object": "list",
  "data": [
    {
      "id": "OpenCUA-7B",
      "object": "model",
      "created": 1234567890,
      "owned_by": "xlangai"
    }
  ]
}
```

### `POST /v1/chat/completions`
Chat completions endpoint (OpenAI-compatible).

**Request:**
```json
{
  "model": "OpenCUA-7B",
  "messages": [
    {"role": "user", "content": "Hello"}
  ],
  "temperature": 0.0,
  "max_tokens": 512,
  "stream": false
}
```

**Response (non-streaming):**
```json
{
  "id": "chatcmpl-abc123",
  "object": "chat.completion",
  "created": 1234567890,
  "model": "OpenCUA-7B",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Hello! How can I help you?"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 8,
    "total_tokens": 18
  }
}
```

**Response (streaming):**
```
data: {"id":"chatcmpl-abc123","object":"chat.completion.chunk","created":1234567890,"model":"OpenCUA-7B","choices":[{"index":0,"delta":{"content":"H"},"finish_reason":null}]}

data: {"id":"chatcmpl-abc123","object":"chat.completion.chunk","created":1234567890,"model":"OpenCUA-7B","choices":[{"index":0,"delta":{"content":"e"},"finish_reason":null}]}

...

data: [DONE]
```

## Configuration

### Model Cache Location

By default, models are cached in `/data/user_data/adityaku/hf_cache`.

To use a different location:
```bash
./models/opencua/start_server.sh 8000 /your/custom/cache
```

### Server Port

Default port is `8000`. Change it with the first argument:
```bash
./models/opencua/start_server.sh 8001
```

## Troubleshooting

### Port Already in Use
```bash
# Find process using port
lsof -i :8000

# Kill it
kill -9 <PID>

# Or use a different port
./models/opencua/start_server.sh 8001
```

### Model Download Issues
The model will be automatically downloaded from HuggingFace on first startup (~16GB). Ensure you have:
- Sufficient disk space
- Internet connectivity
- Write permissions to cache directory

### GPU Out of Memory
OpenCUA-7B requires ~16GB GPU VRAM. If you get OOM errors:
- Ensure no other processes are using the GPU: `nvidia-smi`
- Reduce batch size (not applicable for single requests)
- Use a larger GPU

### Server Not Responding
Check server logs:
```bash
# If running in foreground, check terminal output
# If running in background, check system logs

# Test health endpoint
curl http://localhost:8000/health

# Check if server is running
ps aux | grep opencua/server.py
```

## Files

- `server.py` - Main FastAPI server implementation
- `client.py` - Test client with examples
- `setup.sh` - Environment setup script
- `start_server.sh` - Server startup script
- `cleanup.sh` - Server cleanup script (kills processes, frees GPU)
- `README.md` - This file
- `DELIVERABLES.md` - Summary of deliverables

## Model Information

- **Model**: OpenCUA-7B
- **Source**: [xlangai/OpenCUA-7B](https://huggingface.co/xlangai/OpenCUA-7B)
- **Type**: Multimodal GUI grounding model
- **Size**: ~16GB
- **Input**: Text + Images
- **Output**: PyAutoGUI commands for GUI interaction

## Performance

- **Cold start**: ~60 seconds (model loading)
- **Warm start**: < 1 second (cached model)
- **Inference**: ~1-2 seconds per request (depends on GPU and prompt length)
- **KV caching**: Enabled for faster multi-turn conversations

## License

This wrapper follows the OpenCUA-7B model license. Check the HuggingFace model page for details.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review server logs for error messages
3. Ensure all dependencies are correctly installed

## Example Integration

See `client.py` for a complete working example of:
- Text-only completion
- Multimodal completion with images
- Streaming responses
- Error handling
