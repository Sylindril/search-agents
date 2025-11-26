# OMTW Setup Guide for search-agents

This guide documents all steps needed to run search-agents on real websites (OMTW - Online Mind2Web tasks) with GPT-4o.

## Prerequisites
- Conda installed
- CUDA-capable GPU with ~12GB VRAM (for BLIP2 captioning model)
- OpenAI API key

---

## Step 1: Create Fresh Conda Environment

```bash
conda create -n search-agents python=3.10 -y
conda activate search-agents
```

---

## Step 2: Clone and Install Base Requirements

```bash
cd /path/to/search-agents
pip install -r requirements.txt
playwright install
pip install -e .
```

---

## Step 3: Fix Package Versions (Critical!)

The base requirements.txt has some version conflicts. Run these to fix:

```bash
# Fix httpx/openai compatibility
pip install httpx==0.25.0 openai==1.3.5

# Upgrade PyTorch (required for transformers 4.57+)
pip install torch --upgrade

# Upgrade transformers (fixes BLIP2 tokenizer issues)
pip install transformers --upgrade

# These may show warnings but should work
pip install tokenizers huggingface-hub
```

---

## Step 4: Set Up Environment Variables

Create a `.env` file in the search-agents directory:

```bash
# .env
OPENAI_API_KEY=sk-your-key-here
```

Or export directly:
```bash
export OPENAI_API_KEY="sk-your-key-here"
```

---

## Step 5: Code Modifications (Already Done)

The following files were modified to support OMTW:

### 5.1 `browser_env/env_config.py`
Added OMTW dataset support (bypasses VWA URL requirements):

```python
# After line 4, add:
# OMTW - real websites (no VWA setup needed)
if DATASET == "omtw":
    REDDIT = SHOPPING = WIKIPEDIA = HOMEPAGE = CLASSIFIEDS = CLASSIFIEDS_RESET_TOKEN = ""
    URL_MAPPINGS = {}

# WebArena
elif DATASET == "webarena":
    # ... rest of file
```

### 5.2 `browser_env/auto_login.py`
Added OMTW support (no auto-login needed for real websites):

```python
# After the visualwebarena elif block, add:
elif DATASET == "omtw":
    # OMTW uses real websites - no auto-login needed
    SITES = []
    URLS = []
    EXACT_MATCH = []
    KEYWORDS = []
```

### 5.3 `config_files/omtw/` directory
Copy task configs from ExACT:
```bash
mkdir -p config_files/omtw
cp /path/to/ExACT/configs/omtw/test_omtw/*.json config_files/omtw/
```

### 5.4 `scripts/run_omtw_search.sh`
Created run script (see below).

---

## Step 6: Run Script

The run script `scripts/run_omtw_search.sh`:

```bash
#!/bin/bash
export DATASET=omtw

# Load API key from environment or .env file
if [ -f .env ]; then
    source .env
fi

model="gpt-4o"
agent="search"  # change to "prompt" for baseline without search
result_dir="omtw_gpt4o_search"
instruction_path="agent/prompts/jsons/p_som_cot_id_actree_3s.json"

# Search parameters
max_depth=4
max_steps=5
branching_factor=5
vf_budget=20

python run.py \
    --instruction_path $instruction_path \
    --test_start_idx 0 \
    --test_end_idx 1 \
    --model $model \
    --agent_type $agent \
    --max_depth $max_depth \
    --branching_factor $branching_factor \
    --vf_budget $vf_budget \
    --result_dir $result_dir \
    --test_config_base_dir=config_files/omtw \
    --action_set_tag som \
    --observation_type image_som \
    --viewport_height 2048 \
    --max_obs_length 3840 \
    --top_p 0.95 \
    --temperature 1.0 \
    --max_steps $max_steps \
    --render
```

Make executable:
```bash
chmod +x scripts/run_omtw_search.sh
```

---

## Step 7: Run

```bash
cd /path/to/search-agents
conda activate search-agents
./scripts/run_omtw_search.sh
```

**First run will download BLIP2 model (~15GB)**. Subsequent runs will use cached model.

---

## Quick Setup Script (All-in-One)

For a fresh GPU cluster, run this:

```bash
#!/bin/bash
set -e

# Create environment
conda create -n search-agents python=3.10 -y
conda activate search-agents

# Navigate to repo
cd /path/to/search-agents

# Install base requirements
pip install -r requirements.txt
playwright install
pip install -e .

# Fix package versions
pip install httpx==0.25.0 openai==1.3.5
pip install torch --upgrade
pip install transformers --upgrade

# Set API key (replace with your key)
export OPENAI_API_KEY="sk-your-key-here"

# Run
./scripts/run_omtw_search.sh
```

---

## Troubleshooting

### Error: `TypeError: Client.__init__() got an unexpected keyword argument 'proxies'`
```bash
pip install httpx==0.25.0 openai==1.3.5
```

### Error: `tokenizers>=0.14,<0.15 is required`
```bash
pip install transformers --upgrade
```

### Error: `PyTorch >= 2.1 is required`
```bash
pip install torch --upgrade
```

### Error: `BLIP2 tokenizer data did not match`
```bash
rm -rf ~/.cache/huggingface/hub/models--Salesforce--blip2-flan-t5-xl
pip install transformers --upgrade
```

### Error: `Dataset not implemented: omtw`
Make sure you've modified both:
- `browser_env/env_config.py`
- `browser_env/auto_login.py`

---

## OMTW Task Files

The OMTW tasks are in `config_files/omtw/`:
- `0.json` - Trader Joe's store locator
- `1.json` - FlightAware AeroAPI pricing
- `2.json` - Discogs release submission (requires login)

---

## Notes

- Remove `--render` flag if running headless (no display)
- BLIP2 model requires ~12GB GPU VRAM
- First run downloads ~15GB of model weights
- Results saved to `result_dir` (default: `omtw_gpt4o_search/`)

