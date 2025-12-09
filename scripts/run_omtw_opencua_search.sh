#!/bin/bash
# OpenCUA-7B OMTW Search Script
# This script runs OMTW tasks using OpenCUA-7B as the action and value model

export DATASET=omtw

# Point to local OpenCUA server
export OPENAI_API_BASE=http://localhost:7999/v1
# Set a dummy key (not used with local server)
export OPENAI_API_KEY=EMPTY

# Model name (must match what's registered in the server)
model="OpenCUA-7B"
agent="search"  # change to "prompt" for baseline without search
result_dir="omtw_opencua_search"

# Use coordinate-based prompt for raw images (no BLIP2/SoM needed)
instruction_path="agent/prompts/jsons/p_coord_image_cot.json"

# Search parameters
max_depth=4
max_steps=5
branching_factor=5
vf_budget=20

echo "=== Starting OMTW Evaluation with OpenCUA-7B ==="
echo "Model: $model | Agent: $agent | Tasks: 0-1"
echo "API Base: $OPENAI_API_BASE"
echo "================================================"

python run.py \
    --instruction_path $instruction_path \
    --test_start_idx 0 \
    --test_end_idx 1 \
    --model $model \
    --agent_type $agent \
    --max_depth $max_depth \
    --branching_factor $branching_factor \
    --vf_budget $vf_budget \
    --value_function local \
    --result_dir $result_dir \
    --test_config_base_dir=config_files/omtw \
    --action_set_tag coord \
    --observation_type image \
    --viewport_width 1280 \
    --viewport_height 2048 \
    --max_obs_length 3840 \
    --top_p 0.95 \
    --temperature 1.0 \
    --max_steps $max_steps \
    --verbose

echo "=== Evaluation Complete ==="

