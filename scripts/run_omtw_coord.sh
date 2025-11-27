#!/bin/bash
# Run OMTW tasks with raw images and coordinate-based actions

export DATASET=omtw

# Load API key from environment or .env file
if [ -f .env ]; then
    source .env
fi

model="gpt-4o"
agent="search"  # change to "prompt" for baseline without search
result_dir="omtw_gpt4o_coord"
# Use the coordinate-based prompt (no SoM, raw images)
instruction_path="agent/prompts/jsons/p_coord_image_cot.json"

# Search parameters
max_depth=2
max_steps=10
branching_factor=3
vf_budget=10

echo "=== Starting OMTW Evaluation (Coordinate Mode) ==="
echo "Model: $model | Agent: $agent | Task: 0"
echo "Observation: raw image | Actions: coordinate-based"
echo "Debug mode enabled - screenshots will be saved"
echo "=============================================="

python run_omtw.py \
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
    --action_set_tag coord \
    --observation_type image \
    --viewport_height 2048 \
    --viewport_width 1280 \
    --max_obs_length 3840 \
    --top_p 0.95 \
    --temperature 1.0 \
    --max_steps $max_steps \
    --debug

echo "=== Evaluation Complete ==="
echo "Check $result_dir/debug/ for screenshots and debug output"

