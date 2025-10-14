from typing import Annotated, Literal, Union

from pydantic import Field, model_validator

from invoke_training.config.base_pipeline_config import BasePipelineConfig
from invoke_training.config.data.data_loader_config import DreamboothSDDataLoaderConfig, ImageCaptionSDDataLoaderConfig
from invoke_training.config.optimizer.optimizer_config import AdamOptimizerConfig, ProdigyOptimizerConfig


class SdxlFinetuneConfig(BasePipelineConfig):
    type: Literal["SDXL_FINETUNE"] = "SDXL_FINETUNE"

    model: str = "stabilityai/stable-diffusion-xl-base-1.0"
    """Name or path of the base model to train. Can be in diffusers format, or a single stable diffusion checkpoint
    file. (E.g. 'stabilityai/stable-diffusion-xl-base-1.0', '/path/to/JuggernautXL.safetensors', etc. )
    """

    hf_variant: str | None = "fp16"
    """The Hugging Face Hub model variant to use. Only applies if `model` is a Hugging Face Hub model name.
    """

    save_checkpoint_format: Literal["full_diffusers", "trained_only_diffusers"] = "trained_only_diffusers"
    """The save format for the checkpoints.

    Options:

    - `full_diffusers`: Save the full model in diffusers format (including models that weren't finetuned). If you want a
    single output artifact that can be used for generation, then this is the recommended option.
    - `trained_only_diffusers`: Save only the models that were finetuned in diffusers format. For example, if only the
    UNet model was trained, then only the UNet model will be saved. This option will significantly reduce the disk space
    consumed by the saved checkpoints. If you plan to extract a LoRA from the fine-tuned model, then this is the
    recommended option.
    """

    save_dtype: Literal["float32", "float16", "bfloat16"] = "float16"
    """The dtype to use when saving the model.
    """

    optimizer: AdamOptimizerConfig | ProdigyOptimizerConfig = AdamOptimizerConfig()

    lr_scheduler: Literal[
        "linear", "cosine", "cosine_with_restarts", "polynomial", "constant", "constant_with_warmup"
    ] = "constant"

    lr_warmup_steps: int = 0
    """The number of warmup steps in the learning rate scheduler. Only applied to schedulers that support warmup.
    See lr_scheduler.
    """

    min_snr_gamma: float | None = 5.0
    """Min-SNR weighting for diffusion training was introduced in https://arxiv.org/abs/2303.09556. This strategy
    improves the speed of training convergence by adjusting the weight of each sample.

    `min_snr_gamma` acts like an an upper bound on the weight of samples with low noise levels.

    If `None`, then Min-SNR weighting will not be applied. If enabled, the recommended value is `min_snr_gamma = 5.0`.
    """

    cache_text_encoder_outputs: bool = False
    """If True, the text encoder(s) will be applied to all of the captions in the dataset before starting training and
    the results will be cached to disk. This reduces the VRAM requirements during training (don't have to keep the
    text encoders in VRAM), and speeds up training  (don't have to run the text encoders for each training example).
    This option can only be enabled if `train_text_encoder == False` and there are no caption augmentations being
    applied.
    """

    cache_vae_outputs: bool = False
    """If True, the VAE will be applied to all of the images in the dataset before starting training and the results
    will be cached to disk. This reduces the VRAM requirements during training (don't have to keep the VAE in VRAM), and
    speeds up training (don't have to run the VAE encoding step). This option can only be enabled if all
    non-deterministic image augmentations are disabled (i.e. center_crop=True, random_flip=False).
    """

    enable_cpu_offload_during_validation: bool = False
    """If True, models will be kept in CPU memory and loaded into GPU memory one-by-one while generating validation
    images. This reduces VRAM requirements at the cost of slower generation of validation images.
    """

    gradient_accumulation_steps: int = 1
    """The number of gradient steps to accumulate before each weight update. This value is passed to Hugging Face
    Accelerate. This is an alternative to increasing the batch size when training with limited VRAM.
    """

    weight_dtype: Literal["float32", "float16", "bfloat16"] = "bfloat16"
    """All weights (trainable and fixed) will be cast to this precision. Lower precision dtypes require less VRAM, and
    result in faster training, but are more prone to issues with numerical stability.

    Recommendations:

    - `"float32"`: Use this mode if you have plenty of VRAM available.
    - `"bfloat16"`: Use this mode if you have limited VRAM and a GPU that supports bfloat16.
    - `"float16"`: Use this mode if you have limited VRAM and a GPU that does not support bfloat16.

    See also [`mixed_precision`][invoke_training.pipelines.stable_diffusion_xl.lora.config.SdxlLoraConfig.mixed_precision].
    """  # noqa: E501

    mixed_precision: Literal["no", "fp16", "bf16", "fp8"] = "no"
    """The mixed precision mode to use.

    If mixed precision is enabled, then all non-trainable parameters will be cast to the specified `weight_dtype`, and
    trainable parameters are kept in float32 precision to avoid issues with numerical stability.

    This value is passed to Hugging Face Accelerate. See
    [`accelerate.Accelerator.mixed_precision`](https://huggingface.co/docs/accelerate/package_reference/accelerator#accelerate.Accelerator.mixed_precision)
    for more details.
    """  # noqa: E501

    xformers: bool = False
    """If true, use xformers for more efficient attention blocks.
    """

    gradient_checkpointing: bool = False
    """Whether or not to use gradient checkpointing to save memory at the expense of a slower backward pass. Enabling
    gradient checkpointing slows down training by ~20%.
    """

    max_checkpoints: int | None = None
    """The maximum number of checkpoints to keep. New checkpoints will replace earlier checkpoints to stay under this
    limit. Note that this limit is applied to 'step' and 'epoch' checkpoints separately.
    """

    prediction_type: Literal["epsilon", "v_prediction"] | None = None
    """The prediction_type that will be used for training. Choose between 'epsilon' or 'v_prediction' or leave 'None'.
    If 'None', the prediction type of the scheduler: `noise_scheduler.config.prediction_type` is used.
    """

    max_grad_norm: float | None = None
    """Max gradient norm for clipping. Set to null or 0 for no clipping.
    """

    validation_prompts: list[str] = []
    """A list of prompts that will be used to generate images throughout training for the purpose of tracking progress.
    See also 'validate_every_n_epochs'.
    """

    negative_validation_prompts: list[str] | None = None
    """A list of negative prompts that will be applied when generating validation images. If set, this list should have
    the same length as 'validation_prompts'.
    """

    num_validation_images_per_prompt: int = 4
    """The number of validation images to generate for each prompt in 'validation_prompts'. Careful, validation can
    become quite slow if this number is too large.
    """

    train_batch_size: int = 4
    """The training batch size.
    """

    use_masks: bool = False
    """If True, image masks will be applied to weight the loss during training. The dataset must contain masks for this
    feature to be used.
    """

    data_loader: Annotated[
        Union[ImageCaptionSDDataLoaderConfig, DreamboothSDDataLoaderConfig], Field(discriminator="type")
    ]

    vae_model: str | None = None
    """The name of the Hugging Face Hub VAE model to train against. This will override the VAE bundled with the base
    model (specified by the `model` parameter). This config option is provided for SDXL models, because SDXL shipped
    with a VAE that produces NaNs in fp16 mode, so it is common to replace this VAE with a fixed version.
    """

    @model_validator(mode="after")
    def check_validation_prompts(self):
        if self.negative_validation_prompts is not None and len(self.negative_validation_prompts) != len(
            self.validation_prompts
        ):
            raise ValueError(
                f"The number of validation_prompts ({len(self.validation_prompts)}) must match the number of "
                f"negative_validation_prompts ({len(self.negative_validation_prompts)})."
            )
        return self
