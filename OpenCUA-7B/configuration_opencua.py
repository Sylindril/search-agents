from transformers.configuration_utils import PretrainedConfig
from transformers.models.qwen2_5_vl.configuration_qwen2_5_vl import Qwen2_5_VLVisionConfig
from transformers.models.qwen2.configuration_qwen2 import Qwen2Config


class OpenCUAConfig(PretrainedConfig):
    """OpenCUA-2.5-7B model configuration.

    Args:
        vision_config: Configuration for the vision model.Qwen2_5_VLVisionConfig
        text_config: Configuration for the text model. Qwen2Config
        pad_token_id: The token ID to use for padding.
    """

    model_type = "opencua"

    def __init__(
        self,
        vision_config: dict | Qwen2_5_VLVisionConfig | None = None,
        text_config: dict | Qwen2Config | None = None,
        ignore_index: int = -100,
        media_placeholder_token_id: int = 151664,
        pad_token_id: int = 0,
        **kwargs
    ):
        if isinstance(vision_config, dict):
            vision_config = Qwen2_5_VLVisionConfig(**vision_config)
        self.vision_config = vision_config

        if isinstance(text_config, dict):
            text_config = Qwen2Config(**text_config)
        self.text_config = text_config

        self.ignore_index = ignore_index
        self.media_placeholder_token_id = media_placeholder_token_id

        super().__init__(pad_token_id=pad_token_id, **kwargs)
        
