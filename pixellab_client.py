"""
Pixel Lab API Client for Gallery Generation

Simplified client for generating pixel art images.
Based on the original client from the API testing framework.

Usage:
    from pixellab_client import PixelLabClient

    client = PixelLabClient()
    response = client.generate_image(
        description="cute wizard",
        width=64,
        height=64
    )
"""

import os
import json
import time
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv

from config import api_config

# Load .env file
load_dotenv()

BASE_URL = "https://api.pixellab.ai/v2"


class PixelLabClient:
    """
    Pixel Lab API client for generating pixel art images.
    """

    COMPONENT_NAME = "pixellab"

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = BASE_URL
    ):
        self.api_key = api_key or os.getenv("PIXELLAB_API_KEY")
        self.base_url = base_url

    @property
    def is_live(self) -> bool:
        """Check if this client should use live API."""
        return api_config.is_live(self.COMPONENT_NAME)

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> dict:
        """Make an HTTP request to the Pixel Lab API."""
        try:
            import requests
        except ImportError:
            raise ImportError(
                "requests package not installed. "
                "Run: pip install requests"
            )

        if not self.api_key:
            raise ValueError(
                "PIXELLAB_API_KEY not found. Set it in .env or pass to constructor."
            )

        url = f"{self.base_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        if method == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        response.raise_for_status()
        return response.json()

    def _poll_background_job(self, job_id: str, max_wait: int = 300) -> dict:
        """Poll a background job until completion."""
        start_time = time.time()
        while time.time() - start_time < max_wait:
            response = self._make_request("GET", f"/background-jobs/{job_id}")

            status = response.get("data", {}).get("status")
            if status == "completed":
                return response.get("data", {})
            elif status == "failed":
                raise RuntimeError(f"Job {job_id} failed: {response.get('error')}")

            time.sleep(2)  # Poll every 2 seconds

        raise TimeoutError(f"Job {job_id} did not complete within {max_wait} seconds")

    def generate_image(
        self,
        description: str,
        width: int = 64,
        height: int = 64,
        seed: Optional[int] = None,
        no_background: bool = False,
        reference_images: Optional[list] = None,
        style_image: Optional[dict] = None,
        style_options: Optional[dict] = None
    ) -> dict:
        """
        Generate pixel art image from text description.

        Args:
            description: Text description of the image to generate
            width: Image width in pixels (32, 64, 128, or 256)
            height: Image height in pixels (32, 64, 128, or 256)
            seed: Seed for reproducible generation
            no_background: Remove background from generated images
            reference_images: Optional reference images for subject guidance (up to 4)
            style_image: Optional style image for pixel size and style reference
            style_options: Options for what to copy from the style image

        Returns:
            dict with 'images' key containing list of base64-encoded images
        """
        print(f"[LIVE] Calling Pixel Lab API for: {description[:50]}...")

        payload = {
            "description": description,
            "image_size": {
                "width": width,
                "height": height
            }
        }

        if seed is not None:
            payload["seed"] = seed
        if no_background:
            payload["no_background"] = True
        if reference_images:
            payload["reference_images"] = reference_images
        if style_image:
            payload["style_image"] = style_image
        if style_options:
            payload["style_options"] = style_options

        response = self._make_request("POST", "/generate-image-v2", data=payload)

        # Extract response data
        result = {
            "images": response.get("data", {}).get("images", []),
            "usage": response.get("usage", {}),
            "success": response.get("success", False)
        }

        return result

    def create_character_4_directions(
        self,
        description: str,
        width: int = 64,
        height: int = 64,
        **kwargs
    ) -> dict:
        """
        Create character with 4 directional views (south, west, east, north).

        Args:
            description: Description of the character or object to generate
            width: Canvas width in pixels (32-400)
            height: Canvas height in pixels (32-400)
            **kwargs: Additional parameters (text_guidance_scale, outline, shading, etc.)

        Returns:
            dict with character_id and background_job_id
        """
        print(f"[LIVE] Creating 4-direction character: {description[:50]}...")

        payload = {
            "description": description,
            "image_size": {"width": width, "height": height},
            **kwargs
        }

        response = self._make_request(
            "POST",
            "/create-character-with-4-directions",
            data=payload
        )

        result = {
            "character_id": response.get("data", {}).get("character_id"),
            "background_job_id": response.get("data", {}).get("background_job_id"),
            "usage": response.get("usage", {}),
            "success": response.get("success", False)
        }

        return result

    def get_balance(self) -> dict:
        """Get account balance and usage information."""
        response = self._make_request("GET", "/balance")
        return response.get("data", {})


# =============================================================================
# MODULE-LEVEL CONVENIENCE
# =============================================================================

_default_client: Optional[PixelLabClient] = None


def get_client() -> PixelLabClient:
    """Get or create the default client instance."""
    global _default_client
    if _default_client is None:
        _default_client = PixelLabClient()
    return _default_client


def generate_image(description: str, width: int = 64, height: int = 64, **kwargs) -> dict:
    """Generate image using the default client."""
    return get_client().generate_image(description, width, height, **kwargs)
