"""
Moirai model loader from HuggingFace.
Handles downloading, caching, and device management.
"""

import torch
from pathlib import Path
from typing import Optional, Literal
from loguru import logger
import os

from ..utils.exceptions import ModelException
from ..utils.helpers import ensure_directory


class MoiraiModelLoader:
    """
    Loads and manages Salesforce Moirai time-series models.
    """

    # Available model sizes
    MODELS = {
        "small": "Salesforce/moirai-1.0-R-small",
        "base": "Salesforce/moirai-1.0-R-base", 
        "large": "Salesforce/moirai-1.0-R-large",
    }

    def __init__(
        self,
        model_size: Literal["small", "base", "large"] = "small",
        device: Optional[str] = None,
        cache_dir: Optional[str] = None,
    ):
        """
        Initialize Moirai model loader.

        Args:
            model_size: Size of model (small, base, or large)
            device: Device to load model on (cpu, cuda, mps, or auto)
            cache_dir: Directory to cache downloaded models
        """
        if model_size not in self.MODELS:
            raise ModelException(
                f"Invalid model size: {model_size}. "
                f"Choose from: {list(self.MODELS.keys())}"
            )

        self.model_size = model_size
        self.model_id = self.MODELS[model_size]
        self.cache_dir = cache_dir or "storage/models"
        
        # Ensure cache directory exists
        ensure_directory(self.cache_dir)
        
        # Determine device
        self.device = self._get_device(device)
        
        self.model = None
        self.pipeline = None
        
        logger.info(
            f"MoiraiModelLoader initialized: size={model_size}, device={self.device}"
        )

    def _get_device(self, device: Optional[str] = None) -> str:
        """
        Determine the best device to use.

        Args:
            device: Requested device (cpu, cuda, mps, auto, or None)

        Returns:
            Device string (cpu, cuda, or mps)
        """
        if device and device != "auto":
            return device

        # Auto-detect best device
        if torch.cuda.is_available():
            logger.info("CUDA GPU detected")
            return "cuda"
        elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            logger.info("Apple Silicon (MPS) detected")
            return "mps"
        else:
            logger.info("Using CPU (no GPU detected)")
            return "cpu"

    def load_model(self) -> None:
        """
        Load the Moirai model from HuggingFace.

        Raises:
            ModelException: If model loading fails
        """
        try:
            logger.info(f"Loading Moirai model: {self.model_id}")
            logger.info(f"Cache directory: {self.cache_dir}")
            
            # Import here to avoid issues if not installed
            from uni2ts.model.moirai import MoiraiForecast, MoiraiModule
            
            # Load the model
            logger.info("Downloading/loading model from HuggingFace...")
            self.pipeline = MoiraiForecast.load_from_checkpoint(
                checkpoint_path=self.model_id,
                prediction_length=30,  # Default forecast horizon
                context_length=512,    # Context window
                patch_size=32,
                num_samples=100,       # Number of forecast samples
                target_dim=1,
                feat_dynamic_real_dim=0,
                past_feat_dynamic_real_dim=0,
            )
            
            # Move to device
            if self.device != "cpu":
                self.pipeline = self.pipeline.to(self.device)
            
            logger.info(f"✓ Model loaded successfully on {self.device}")
            
        except ImportError as e:
            raise ModelException(
                f"Failed to import Moirai dependencies. "
                f"Install with: pip install uni2ts\n"
                f"Error: {e}"
            )
        except Exception as e:
            raise ModelException(f"Failed to load Moirai model: {e}")

    def get_model_info(self) -> dict:
        """
        Get information about the loaded model.

        Returns:
            Dictionary with model information
        """
        return {
            "model_id": self.model_id,
            "model_size": self.model_size,
            "device": self.device,
            "cache_dir": self.cache_dir,
            "loaded": self.pipeline is not None,
        }

    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        return self.pipeline is not None

    def unload_model(self) -> None:
        """Unload model from memory."""
        if self.pipeline is not None:
            del self.pipeline
            self.pipeline = None
            
            # Clear CUDA cache if using GPU
            if self.device == "cuda":
                torch.cuda.empty_cache()
            
            logger.info("Model unloaded from memory")
