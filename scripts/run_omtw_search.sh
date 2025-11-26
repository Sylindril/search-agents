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

echo "=== Starting OMTW Evaluation ==="
echo "Model: $model | Agent: $agent | Tasks: 0-1"
echo "================================"

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
    --max_steps $max_steps

echo "=== Evaluation Complete ==="

