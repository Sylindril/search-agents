# OMTW Integration Documentation

## Overview

This document describes the integration of **OMTW (Online Mind2Web)** tasks into the `search-agents` codebase. OMTW allows running web navigation tasks on **real websites** instead of the simulated VisualWebArena environment.

The key modification is adding support for **coordinate-based actions** with **raw screenshots** (no Set-of-Mark overlay), allowing a VLM like GPT-4o to directly see the webpage and specify pixel coordinates for interactions.

---

## Files Modified/Created

### 1. Core Run Script: `run_omtw.py`
**Location:** `/mnt/d/Aditya/CMU/Research/Kate_Group/search-agents/run_omtw.py`

A copy of `run.py` with OMTW-specific modifications:

**Key Changes:**
- Added `--debug` flag for verbose output and screenshot saving
- Added `--action_set_tag coord` support for coordinate-based actions
- Modified action compatibility check to allow `coord` with `image` observation
- Added debug logging during search (shows candidate actions, scores, screenshots)
- Screenshots saved to `{result_dir}/debug/{task_id}/`

**Debug Output Includes:**
- Initial screenshot
- Each search step screenshot
- Candidate actions generated
- Value function scores
- Execution logs

### 2. Agent Action Parsing: `agent/agent.py`
**Location:** `/mnt/d/Aditya/CMU/Research/Kate_Group/search-agents/agent/agent.py`

**Added Function:** `create_coord_based_action(response, viewport_width=1280, viewport_height=2048)`

Parses LLM responses in coordinate format:
```
click [x, y]           → MOUSE_CLICK at normalized coords
type [x, y] [text]     → TYPE at coords + keyboard input + Enter
scroll [up|down]       → SCROLL action
press [key]            → KEY_PRESS action
hover [x, y]           → MOUSE_HOVER at normalized coords
stop [answer]          → STOP action
goto [url]             → GOTO_URL action
```

**Critical:** Pixel coordinates are **normalized** to 0-1 range:
- `norm_x = pixel_x / viewport_width` (default 1280)
- `norm_y = pixel_y / viewport_height` (default 2048)

This is required because `execute_mouse_click()` expects normalized coordinates.

**Modified:** `PromptAgent.next_action()` and `SearchAgent.next_action()` to handle `coord` action_set_tag by calling `create_coord_based_action()` directly on the raw LLM response.

### 3. Action Execution: `browser_env/actions.py`
**Location:** `/mnt/d/Aditya/CMU/Research/Kate_Group/search-agents/browser_env/actions.py`

**Added:** Coordinate-based TYPE execution (around line 1228):
```python
case ActionTypes.TYPE:
    if "coords" in action and action["coords"] is not None:
        # Click at coords, wait 300ms, type text, press Enter
        execute_mouse_click(coords[0], coords[1], page)
        time.sleep(0.3)  # Wait for focus
        page.keyboard.type(text)
        page.keyboard.press("Enter")
```

**Added:** Execution logging for MOUSE_CLICK and TYPE actions:
- `>> EXEC CLICK: (pixel_x, pixel_y)`
- `>> EXEC TYPE: click (x, y) then type 'text'`

### 4. Helper Functions: `browser_env/helper_functions.py`
**Location:** `/mnt/d/Aditya/CMU/Research/Kate_Group/search-agents/browser_env/helper_functions.py`

**Added:** `coord` case to:
- `get_render_action()` - For HTML rendering of actions
- `get_action_description()` - For action history text

### 5. Environment Config: `browser_env/env_config.py`
**Location:** `/mnt/d/Aditya/CMU/Research/Kate_Group/search-agents/browser_env/env_config.py`

**Added:** OMTW dataset support (lines 8-11):
```python
if DATASET == "omtw":
    REDDIT = SHOPPING = WIKIPEDIA = HOMEPAGE = CLASSIFIEDS = CLASSIFIEDS_RESET_TOKEN = ""
    URL_MAPPINGS = {}
```

### 6. Auto Login: `browser_env/auto_login.py`
**Location:** `/mnt/d/Aditya/CMU/Research/Kate_Group/search-agents/browser_env/auto_login.py`

**Added:** OMTW case with empty login sites (no auto-login needed).

### 7. Prompt Constructor: `agent/prompts/prompt_constructor.py`
**Location:** `/mnt/d/Aditya/CMU/Research/Kate_Group/search-agents/agent/prompts/prompt_constructor.py`

**Modified:** `MultimodalCoTPromptConstructor`:
- Handle empty examples list (no in-context examples for coord mode)
- Handle missing `{observation}` in template (image-only mode)
- Skip example images if path is empty

### 8. Coordinate Prompt: `agent/prompts/jsons/p_coord_image_cot.json`
**Location:** `/mnt/d/Aditya/CMU/Research/Kate_Group/search-agents/agent/prompts/jsons/p_coord_image_cot.json`

```json
{
  "intro": "You are a web navigation agent. You see a screenshot of a webpage (1280x2048 pixels)...",
  "examples": [],
  "template": "URL: {url}\nTASK: {objective}\nPREVIOUS ACTION: {previous_action}",
  "meta_data": {
    "observation": "image",
    "action_type": "coord",
    "keywords": ["url", "objective", "previous_action"],
    "prompt_constructor": "MultimodalCoTPromptConstructor",
    "answer_phrase": "In summary, the next action I will perform is",
    "action_splitter": "```"
  }
}
```

**Key Points:**
- No in-context examples (empty array)
- No `{observation}` in template (image sent separately)
- Tells LLM viewport is 1280x2048 pixels
- Expected action format: `click [x, y]`, `type [x, y] [text]`, etc.

### 9. Run Script: `scripts/run_omtw_coord.sh`
**Location:** `/mnt/d/Aditya/CMU/Research/Kate_Group/search-agents/scripts/run_omtw_coord.sh`

```bash
#!/bin/bash
export DATASET=omtw

python run_omtw.py \
    --instruction_path agent/prompts/jsons/p_coord_image_cot.json \
    --test_start_idx 0 \
    --test_end_idx 1 \
    --model gpt-4o \
    --agent_type search \
    --action_set_tag coord \
    --observation_type image \
    --viewport_height 2048 \
    --viewport_width 1280 \
    --debug
```

### 10. Task Configs: `config_files/omtw/`
**Location:** `/mnt/d/Aditya/CMU/Research/Kate_Group/search-agents/config_files/omtw/`

Example task config (`0.json`):
```json
{
  "sites": ["google"],
  "task_id": 0,
  "require_login": false,
  "storage_state": null,
  "start_url": "https://www.google.com/",
  "intent": "Search for 'weather in Pittsburgh' and tell me the current temperature.",
  "image": null,
  "require_reset": false,
  "eval": {
    "eval_types": ["string_match"],
    "reference_answers": {"must_include": ["°"]}
  }
}
```

---

## Architecture Flow

```
1. run_omtw.py loads config from config_files/omtw/{task_id}.json
2. ScriptBrowserEnv opens browser with observation_type="image"
3. Agent receives raw screenshot (no SoM markers)
4. Prompt constructed with URL, TASK, PREVIOUS_ACTION + screenshot
5. GPT-4o outputs: "In summary... ```type [640, 500] [weather]```"
6. create_coord_based_action() parses response:
   - Extracts pixel coords (640, 500)
   - Normalizes to (0.5, 0.244)
   - Creates ACTION dict with coords + text
7. env.step(action) executes:
   - MOUSE_CLICK: page.mouse.click(norm_x * width, norm_y * height)
   - TYPE: click → wait 300ms → keyboard.type(text) → Enter
8. Value function scores trajectory
9. Search continues until score=1.0 or budget exhausted
```

---

## Key Technical Details

### Coordinate Normalization
The browser execution expects **normalized coordinates (0-1)**:
```python
def execute_mouse_click(left: float, top: float, page: Page):
    viewport_size = page.viewport_size
    page.mouse.click(
        left * viewport_size["width"],   # e.g., 0.5 * 1280 = 640
        top * viewport_size["height"]    # e.g., 0.244 * 2048 = 500
    )
```

The LLM outputs **pixel coordinates**, so we normalize in `create_coord_based_action()`:
```python
norm_x = pixel_x / viewport_width  # 640 / 1280 = 0.5
norm_y = pixel_y / viewport_height # 500 / 2048 = 0.244
```

### Viewport Size
Default: **1280 x 2048 pixels** (width x height)
- This is a tall viewport to capture more page content
- Must match what's told to the LLM in the prompt

### Search Algorithm
Uses value-function guided tree search:
1. Generate `branching_factor` candidate actions per step
2. Execute each, get value function score (GPT-4o evaluates progress)
3. Expand best-scoring paths up to `max_depth`
4. Commit best action found within `vf_budget` evaluations

---

## Known Issues & TODOs

### Current Issues
1. **Coordinate accuracy**: LLM sometimes outputs coordinates that miss the target element
2. **Google search bar**: May require specific y-coordinate tuning for the viewport size
3. **No accessibility tree fallback**: Pure image mode has no text backup for element identification

### Potential Improvements
1. Add click verification (check if element was actually focused)
2. Add retry logic if type action doesn't produce expected result
3. Consider hybrid mode: image + accessibility tree text
4. Add coordinate validation (clamp to viewport bounds)
5. Fine-tune prompt with better examples

### Testing
To test the integration:
```bash
cd /mnt/d/Aditya/CMU/Research/Kate_Group/search-agents
conda activate search-agents
rm -rf omtw_gpt4o_coord && ./scripts/run_omtw_coord.sh
```

Check output:
- Screenshots: `omtw_gpt4o_coord/debug/0/`
- HTML render: `omtw_gpt4o_coord/render_0.html`
- Logs: `log_files/log_*.log`

---

## Environment Setup

### Prerequisites
```bash
conda create -n search-agents python=3.10 -y
conda activate search-agents
pip install -r requirements.txt
playwright install
```

### API Keys
Create `.env` file:
```
OPENAI_API_KEY=sk-...
```

### Dependencies Fixed During Integration
```bash
pip install "numpy<2" --force-reinstall
pip install httpx==0.25.0 openai==1.3.5
pip install langchain==0.2.16 langchain-community==0.2.17 langchain-core==0.2.40 langchain-openai
```

---

## File Checklist

| File | Status | Purpose |
|------|--------|---------|
| `run_omtw.py` | ✅ Created | Main entry point for OMTW tasks |
| `agent/agent.py` | ✅ Modified | Coordinate action parsing |
| `browser_env/actions.py` | ✅ Modified | Coordinate action execution |
| `browser_env/helper_functions.py` | ✅ Modified | Action description for coord |
| `browser_env/env_config.py` | ✅ Modified | OMTW dataset support |
| `browser_env/auto_login.py` | ✅ Modified | Skip login for OMTW |
| `agent/prompts/prompt_constructor.py` | ✅ Modified | Handle empty examples |
| `agent/prompts/jsons/p_coord_image_cot.json` | ✅ Created | Coordinate prompt |
| `scripts/run_omtw_coord.sh` | ✅ Created | Run script |
| `config_files/omtw/*.json` | ✅ Created | Task configs |

---

## Contact / Attribution

Integration done as part of adapting ExACT/search-agents for real-website evaluation using OMTW benchmark tasks.

