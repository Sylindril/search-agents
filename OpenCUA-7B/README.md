---
base_model:
- Qwen/Qwen2.5-VL-7B-Instruct
datasets:
- xlangai/AgentNet
- xlangai/aguvis-stage1
- smolagents/aguvis-stage-2
- osunlp/UGround-V1-Data
language:
- en
license: mit
metrics:
- accuracy
- code_eval
pipeline_tag: image-text-to-text
library_name: transformers
tags:
- VLM
- Computer-Use-Agent
- OS-Agent
- GUI
- Grounding
---

<h1 style="
  font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif;
  font-size:48px;
  font-weight:700;
  line-height:1.25;
  text-align:center;
  margin:0 0 24px;">
  OpenCUA: Open Foundations for Computer-Use Agents
</h1>

<div style="
  display:flex;
  justify-content:center;
  gap:12px;
  flex-wrap:wrap;
  margin-bottom:28px;">
  
  <a href="https://opencua.xlang.ai/" style="
     display:inline-block;
     padding:8px 24px;
     background:#2b2b2b;
     color:#ffffff;
     border-radius:36px;
     text-decoration:none;
     font-weight:600;
     font-size:16px;">
    🌐 Website
  </a>

  <a href="https://arxiv.org/abs/2508.09123" style="
     display:inline-block;
     padding:8px 24px;
     background:#2b2b2b;
     color:#ffffff;
     border-radius:36px;
     text-decoration:none;
     font-weight:600;
     font-size:16px;">
    📝 Paper
  </a>

  <a href="https://github.com/xlang-ai/OpenCUA" style="
     display:inline-block;
     padding:8px 24px;
     background:#2b2b2b;
     color:#ffffff;
     border-radius:36px;
     text-decoration:none;
     font-weight:600;
     font-size:16px;">
    💻 Code
  </a>
</div>

<div style="max-width:900px;margin:0 auto;">

#  Introduction
<div style="
  max-width: 880px;              /* 可按需调节整体宽度 */
  margin: 0 auto;               /* 居中容器 */
  text-align: justify;          /* 关键：两端对齐 */
  text-justify: inter-word;     /* 优化英文对齐效果 */
  line-height: 1.6;">
  
OpenCUA models (OpenCUA-7B and OpenCUA-32B) are end-to-end computer-use foundation models than can produce executable actions in the computer environments.  They are based on the weights of Qwen2.5-VL-7B-Instruction and Qwen2.5-VL-32B-Instruction. 
They demonstrate superior performance across CUA benchmarks. In particular, <b>OpenCUA-32B</b> achieves an average success rate of **34.8%** on [OSWorld-Verified](https://os-world.github.io/), 
establishing a new state-of-the-art (SOTA) among open-source models and surpassing OpenAI CUA (GPT-4o). Both models also have strong grounding performance, OpenCUA-32B achieves 59.6% on [OSWorld-G](https://osworld-grounding.github.io/) and 55.3% on [Screenspot-Pro](https://arxiv.org/abs/2504.07981).
</div>

## 📢 Updates
- 2025-10-12:  <span style="font-weight:bold">[OpenCUA-7B-exl2](https://huggingface.co/sujitvasanth/OpenCUA-7B-exl2) is now live!</span> ⚡️  
  Thanks to [Sujit Vasanth](https://huggingface.co/sujitvasanth) for producing a quantized **exllamav2** version of OpenCUA-7B — enabling much faster inference with lower VRAM usage.
  
### Key Features

- **Superior Computer-Use Capablity**: Able to execute multi-step computer-use actions with effective planning and reasoning
- **Multi-OS Support**: Trained on demonstrations across Ubuntu, Windows, and macOS
- **Visual Grounding**: Strong GUI element recognition and spatial reasoning capabilities
- **Multi-Image Context**: Processes up to 3 screenshot history for better context understanding
- **Reflective Reasoning**: Enhanced with reflective long Chain-of-Thought that identifies errors and provides corrective reasoning


# Performance

### Online Agent Evaluation
OpenCUA models achieves strong performance on **[OSWorld-Verified](https://os-world.github.io/)**. 
OPENCUA-32B achieves the best performance among all open-source models with an average success rate of 34.8%, outperforming prior baselines by large margins. 
It also closes the gap to proprietary Claude models.
<div align="center">

| **Model**                        | **15 Steps** | **50 Steps** | **100 Steps** |
|-------------------------------|:--------:|:--------:|:---------:|
| **Proprietary**               |          |          |           |
| OpenAI CUA                    | 26.0     | 31.3     | 31.4      |
| Seed 1.5-VL                   | 27.9     | —        | 34.1      |
| Claude 3.7 Sonnet             | 27.1     | 35.8     | 35.9      |
| Claude 4 Sonnet               | 31.2     | 43.9     | 41.5      |
| **Open-Source**               |          |          |           |
| Qwen 2.5-VL-32B-Instruct       | 3.0      | —        | 3.9       |
| Qwen 2.5-VL-72B-Instruct       | 4.4      | —        | 5.0       |
| Kimi-VL-A3B                   | 9.7      | —        | 10.3      |
| UI-TARS-72B-DPO               | 24.0     | 25.8     | 27.1      |
| UI-TARS-1.5-7B                | 24.5     | 27.3     | 27.4      |
| OpenCUA-7B *(Ours)*           | 24.3     | 27.9     | 26.6      |
| **OpenCUA-32B *(Ours)***      | **29.7** | **34.1** | **34.8**  |
</div>

*OpenCUA scores are the mean of 3 independent runs.*

### GUI Grounding Performance
<div align="center">

| **Model** | **OSWorld-G** | **ScreenSpot-V2** | **ScreenSpot-Pro** |
|-------|-----------|---------------|----------------|
| Qwen2.5-VL-7B | 31.4 | 88.8 | 27.6 |  
| Qwen2.5-VL-32B | 46.5 | 87.0 | 39.4 |
| UI-TARS-72B | 57.1 | 90.3 | 38.1 |
| **OpenCUA-A3B** | 48.6 | 91.4 | 28.5 |
| **OpenCUA-Qwen2-7B** | 45.7 | 88.5 | 23.7 |
| **OpenCUA-7B** | 55.3 | 92.3 | 50.0 |
| **OpenCUA-32B** | **59.6** | **93.4** | **55.3** |
</div>


### AgentNetBench (Offline Evaluation)
<div align="center">

| **Model** | **Coordinate Actions** | **Content Actions** | **Function Actions** | **Average** |
|-------|-------------------|-----------------|------------------|---------|
| Qwen2.5-VL-7B | 50.7 | 40.8 | 3.1 | 48.0 |
| Qwen2.5-VL-32B | 66.6 | 47.2 | 41.5 | 64.8 |
| Qwen2.5-VL-72B | 67.2 | 52.6 | 50.5 | 67.0 |
| OpenAI CUA          | 71.7 | 57.3 | **80.0** | 73.1 |
| **OpenCUA-7B**  | 79.0 | 62.0 | 44.3 | 75.2 |
| **OpenCUA-32B** | **81.9** | 66.1 | 55.7 | **79.1** |
</div>

#  🚀 Quick Start
<div style="border-left: 6px solid #f28c28; background: #fff8e6; padding: 12px 16px; margin: 16px 0;">
  <strong>⚠️ Important for Qwen-based Models (OpenCUA-7B, OpenCUA-32B):</strong>
  
  To align with our training infrastructure, we have modified the model in two places:
  <ul style="margin-top: 8px;">
    <li>1. Multimodal Rotary Position Embedding (M-RoPE) has been replaced with 1D RoPE</strong>.</li>
    <li>2. Using the same Tokenizer and ChatTemplate as Kimi-VL.</li>
    <li>Do not use the default transformers and vllm classes to load the model. Tokenizer and Chat Template should be aligned if training the models.</li>
  </ul>
</div>


## Installation & Download

First, install the required transformers dependencies:

```bash
conda create -n opencua python=3.10
conda activate opencua
pip install -r requirement.txt
```

Download the model weight from huggingface:
```bash
from huggingface_hub import snapshot_download
snapshot_download(
    repo_id="xlangai/OpenCUA-7B",
    local_dir="OpenCUA-7B",                
    local_dir_use_symlinks=False  
)
```

## 🎯 GUI Grounding 

The following code demonstrates how to use OpenCUA models for GUI grounding tasks:

```python
import base64
import torch
from transformers import AutoTokenizer, AutoModel, AutoImageProcessor
from PIL import Image
import json

def encode_image(image_path: str) -> str:
    """Encode image to base64 string for model input."""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def load_opencua_model(model_path: str):
    """Load OpenCUA model, tokenizer, and image processor."""
    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
    model = AutoModel.from_pretrained(
        model_path, 
        torch_dtype="auto", 
        device_map="auto", 
        trust_remote_code=True
    )
    image_processor = AutoImageProcessor.from_pretrained(model_path, trust_remote_code=True)
    
    return model, tokenizer, image_processor

def create_grounding_messages(image_path: str, instruction: str):
    """Create chat messages for GUI grounding task."""
    system_prompt = (
        "You are a GUI agent. You are given a task and a screenshot of the screen. "
        "You need to perform a series of pyautogui actions to complete the task."
    )
    
    messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": [
                {"type": "image", "image": f"data:image/png;base64,{encode_image(image_path)}"},
                {"type": "text", "text": instruction},
            ],
        },
    ]
    return messages

def run_inference(model, tokenizer, image_processor, messages, image_path):
    """Run inference on the model."""
    # Prepare text input
    input_ids = tokenizer.apply_chat_template(
        messages, tokenize=True, add_generation_prompt=True
    )
    input_ids = torch.tensor([input_ids]).to(model.device)
    
    # Prepare image input  
    image = Image.open(image_path).convert('RGB')
    image_info = image_processor.preprocess(images=[image])
    pixel_values = torch.tensor(image_info['pixel_values']).to(
        dtype=torch.bfloat16, device=model.device
    )
    grid_thws = torch.tensor(image_info['image_grid_thw'])
    
    # Generate response
    with torch.no_grad():
        generated_ids = model.generate(
            input_ids,
            pixel_values=pixel_values,
            grid_thws=grid_thws,
            max_new_tokens=512,
            temperature=0
        )
    
    # Decode output
    prompt_len = input_ids.shape[1]
    generated_ids = generated_ids[:, prompt_len:]
    output_text = tokenizer.batch_decode(
        generated_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False
    )[0]
    
    return output_text

# Example usage
model_path = "xlangai/OpenCUA-7B"  # or other model variants
image_path = "screenshot.png"
instruction = "Click on the submit button"

# Load model
model, tokenizer, image_processor = load_opencua_model(model_path)

# Create messages and run inference
messages = create_grounding_messages(image_path, instruction)
result = run_inference(model, tokenizer, image_processor, messages, image_path)

print("Model output:", result)
```

<div style="border-left: 6px solid #9ca3af; background: #f5f5f5; padding: 12px 16px; margin: 16px 0;">
  <em>Expected result:</em> ```python
pyautogui.click(x=1443, y=343)
```
</div>

You can also run the five grounding examples in [OpenCUA/model/inference/huggingface_inference.py](https://github.com/xlang-ai/OpenCUA/blob/main/model/inference/huggingface_inference.py):
``` 
cd ./model/inference/
python huggingface_inference.py
```

## 🖥️ Computer Use Agent
**[OpenCUAAgent](https://github.com/xlang-ai/OSWorld/blob/main/mm_agents/opencua_agent.py)** is developed in the [OSWorld](https://github.com/xlang-ai/OSWorld) environment based on OpenCUA models. It iteratively perceives the environment via screenshots, produces reflective long CoT as inner monologue, and predicts the next action to be executed. OpenCUAAgent uses 3 images in total and L2 CoT format in default.

Command for running OpenCUA-7B and OpenCUA-32B in OSWorld:
```
    python run_multienv_opencua.py \
        --headless \
        --observation_type screenshot \
        --model OpenCUA-32B \
        --result_dir ./results --test_all_meta_path evaluation_examples/test_all_no_gdrive.json \
        --max_steps 100 \
        --num_envs 30  \
        --coordinate_type qwen25
```
<div style="border-left: 6px solid #9ca3af; background: #f5f5f5; padding: 12px 16px; margin: 16px 0;">
  <em>Currently we only supports huggingface inference. We are implementing the vLLM supports of OpenCUA models. Please stay tuned.</em>
</div>

---

# AgentNet Dataset - Large-Scale Computer-Use Dataset

<div align="center">
  <img src="https://cdn-uploads.huggingface.co/production/uploads/67b327cdd4665a0448eef7d5/dw5k183ucDSB2SZuS5f2V.png" width="400" alt="AgentNet Dataset Domain Distribution">
</div>

AgentNet is the first large-scale desktop computer-use agent trajectory dataset, containing 22.6K human-annotated computer-use tasks across Windows, macOS, and Ubuntu systems. 

👉 **[AgentNet Huggingface Dataset](https://huggingface.co/datasets/xlangai/AgentNet)**

Download the dataset here：
```
pip install -U huggingface_hub
huggingface-cli download xlangai/AgentNet --repo-type dataset --local-dir ./AgentNet
```

Collecting computer-use agent training data requires 3 steps:
- Demonstrate human computer-use task via [AgentNetTool](https://agentnet-tool.xlang.ai/);
- Preprocess the demonstration using [Action Reduction & State-Action Matching](./data/data-processor);
- For each step, [synthesize reflective long CoT](./data/cot-generator)


## 1 AgentNetTool – Annotation & Verification Tool
<div align="center">
  <img src="https://cdn-uploads.huggingface.co/production/uploads/67b327cdd4665a0448eef7d5/ETjCOoIRR7f1YZCJ2kfiW.png" width="700" alt="AgentNet Tool">
</div>


Our **AgentNetTool** is a cross-platform GUI recorder that runs unobtrusively on annotators’ machines. It captures synchronized **screen video**, **mouse/keyboard events**, and **accessibility trees**, then provides an in-browser UI for reviewing, trimming, and submitting demonstrations. AgentNet Tool is available on Windows, macOS and Ubuntu. 

👉 **[AgentNetTool Document](https://agentnet-tool.xlang.ai/)**



## 2 DataProcessor – Action Reduction & State–Action Matching
Raw demonstrations can contain thousands of low-level events that are too dense for model training.  
The **DataProcessor** module (`./data/data-process/`) performs two key steps:

1.  **Action Reduction** — merges granular signals into concise, semantically meaningful PyAutoGUI actions (e.g., collapsing mouse moves → click, coalescing scrolls, grouping key-press sequences into text or hotkeys).  
2.  **State–Action Matching** — aligns every reduced action with the *last visually distinct frame* **before** the action begins, avoiding future-information leakage and yielding compact state–action pairs.

These processed trajectories underlie all downstream training and evaluation.

---

## 3 CoTGenerator – Synthesizing Reflective Long Chain-of-Thought Inner Monologue
To boost robustness and interpretability, we augment each trajectory with **reflective long Chain-of-Thought (CoT) reasoning**.  
The **CoTGenerator** pipeline (`./data/cot-generator/`) synthesizes step-level reflections that:

*   reflect on the previous action,
*   explain *why* an action is chosen given the current observation and history,  
*   note potential alternative actions, and  
*   forecast the expected next state.

Empirically, models trained with these rich CoTs scale better with data and generalize across unseen applications.


# Evaluation

<div align="center">
  <img src="https://cdn-uploads.huggingface.co/production/uploads/67b327cdd4665a0448eef7d5/emy1QCJwQj9KqHkVmtNH2.png" width="800" alt="AgentNetBench">
</div>


**AgentNetBench** (`./AgentNetBench/`) provides a realistic offline evaluator for OS agent trajectories. It compares model-predicted low-level actions (click, moveTo, write, press, scroll, terminate, etc.) against ground-truth human actions and reports detailed metrics.

👉 See **[AgentNetBench/README.md](./evaluation/agentnetbench/README.md)** for usage instructions.

# TODO
## vLLM Support
We are actively working with the vLLM team to add support for OpenCUA models.

**Workaround:** For now, please use the standard transformers library as shown in the examples above. We will update this section once vLLM support becomes available.

## Training Code
OpenCUA models are developed based on the training infrastructure of Kimi Team. We are developting the training pipeline based on the open-source infrastructure as well.

# Acknowledge
<p>
We thank Su Yu, Caiming Xiong, Binyuan Hui, and the anonymous reviewers for their insightful discussions and valuable feedback. 
We are grateful to Moonshot AI for providing training infrastructure and annotated data. 
We also sincerely appreciate Calvin, Ziwei Chen, Jin Zhang, Ze Li, Zhengtao Wang, Yanxu Chen, and Qizheng Gu from the Kimi Team for their strong infrastructure support and helpful guidance. 
The development of our tool is based on the open-source projects-<a href="https://github.com/TheDuckAI/DuckTrack" target="_blank">DuckTrack</a> and <a href="https://github.com/OpenAdaptAI/OpenAdapt" target="_blank">OpenAdapt</a>. 
We are very grateful to their commitment to the open source community. Finally, we extend our deepest thanks to all annotators for their tremendous effort and contributions to this project.
</p>

# License

This project is licensed under the MIT License - see the LICENSE file in the root folder for details.

## Research Use and Disclaimer

OpenCUA models are intended for **research and educational purposes only**. 

### Prohibited Uses
- The model may **not** be used for any purpose or activity that violates applicable laws or regulations in any jurisdiction
- Use for illegal, unethical, or harmful activities is strictly prohibited

### Disclaimer
- The authors, contributors, and copyright holders are **not responsible** for any illegal, unethical, or harmful use of the Software, nor for any direct or indirect damages resulting from such use
- Use of the "OpenCUA" name, logo, or trademarks does **not** imply any endorsement or affiliation unless separate written permission is obtained
- Users are solely responsible for ensuring their use complies with applicable laws and regulations

## Important Notes on Coordinate Systems
<div style="border-left: 6px solid #9ca3af; background: #f5f5f5; padding: 12px 16px; margin: 16px 0;">
  <ul style="margin: 0;">
    <li><strong><code>OpenCUA/OpenCUA-A3B</code></strong> – Relative coordinates <em>(not supported in this code)</em></li>
    <li><strong><code>OpenCUA/OpenCUA-Qwen2-7B</code></strong> – Relative coordinates</li>
    <li><strong><code>OpenCUA/OpenCUA-7B</code></strong> – Absolute coordinates</li>
    <li><strong><code>OpenCUA/OpenCUA-32B</code></strong> – Absolute coordinates</li>
  </ul>
</div>

**OpenCUA models use different coordinate systems depending on the base model:**

- **OpenCUA-Qwen2-7B**: Outputs **relative coordinates** (0.0 to 1.0 range)
  ```python
  # Example output: pyautogui.click(x=0.5, y=0.3)
  # x=0.5 means 50% from left edge, y=0.3 means 30% from top edge
  
  # Convert to absolute coordinates:
  def qwen2_relative_to_absolute(rel_x, rel_y, original_width, original_height):
      abs_x = int(rel_x * original_width)
      abs_y = int(rel_y * original_height)
      return abs_x, abs_y
  ```

- **OpenCUA-7B and OpenCUA-32B** (Qwen2.5-based): Output **absolute coordinates** after smart resize
  ```python
  # Example output: pyautogui.click(x=960, y=324)  
  # These are coordinates on the smart-resized image, not the original image
  
  # Convert to original image coordinates:
  # Please refer to the smart_resize function in: https://github.com/huggingface/transformers/blob/67ddc82fbc7e52c6f42a395b4a6d278c55b77a39/src/transformers/models/qwen2_vl/image_processing_qwen2_vl.py#L55
  def qwen25_smart_resize_to_absolute(model_x, model_y, original_width, original_height):
      # First, calculate the smart-resized dimensions
      resized_height, resized_width = smart_resize(original_height, original_width, factor = 28, min_pixels = 3136, max_pixels = 12845056)
      
      # Convert model output to relative coordinates on original image
      rel_x = model_x / resized_width
      rel_y = model_y / resized_height
      
      # Then convert to absolute coordinates on original image
      abs_x = int(rel_x * original_width)
      abs_y = int(rel_y * original_height)
      return abs_x, abs_y
  ```

<div style="border-left: 6px solid #9ca3af; background: #f5f5f5; padding: 12px 16px; margin: 16px 0;">
  <strong>Understanding Smart Resize for Qwen2.5-based Models:</strong>
  <p style="margin: 8px 0 0;">
    The Qwen2.5-VL models use a “smart resize” preprocessing that maintains aspect ratio while fitting within pixel constraints.
    For coordinate conversion, you need the smart resize function from the
    <a href="https://github.com/QwenLM/Qwen2.5-VL/blob/d2240f11656bfe404b9ba56db4e51cd09f522ff1/qwen-vl-utils/src/qwen_vl_utils/vision_process.py#L60">
      official Qwen2.5-VL implementation</a>.
  </p>
</div>

## Citation

If you use OpenCUA models in your research, please cite our work:

```bibtex
@misc{wang2025opencuaopenfoundationscomputeruse,
      title={OpenCUA: Open Foundations for Computer-Use Agents}, 
      author={Xinyuan Wang and Bowen Wang and Dunjie Lu and Junlin Yang and Tianbao Xie and Junli Wang and Jiaqi Deng and Xiaole Guo and Yiheng Xu and Chen Henry Wu and Zhennan Shen and Zhuokai Li and Ryan Li and Xiaochuan Li and Junda Chen and Boyuan Zheng and Peihang Li and Fangyu Lei and Ruisheng Cao and Yeqiao Fu and Dongchan Shin and Martin Shin and Jiarui Hu and Yuyan Wang and Jixuan Chen and Yuxiao Ye and Danyang Zhang and Dikang Du and Hao Hu and Huarong Chen and Zaida Zhou and Haotian Yao and Ziwei Chen and Qizheng Gu and Yipu Wang and Heng Wang and Diyi Yang and Victor Zhong and Flood Sung and Y. Charles and Zhilin Yang and Tao Yu},
      year={2025},
      eprint={2508.09123},
      archivePrefix={arXiv},
      primaryClass={cs.AI},
      url={https://arxiv.org/abs/2508.09123}, 
}
```

</div>