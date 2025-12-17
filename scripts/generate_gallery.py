#!/usr/bin/env python3
"""
Gallery Image Generator

Generates pixel art images using the PixelLab API and saves them
as PNG files for display in the portfolio gallery.

Usage:
    cd /Users/ctavolazzi/Code/ctavolazzi.github.io
    pip install -r scripts/requirements.txt
    cp .env.example .env
    # Edit .env and add PIXELLAB_API_KEY
    python scripts/generate_gallery.py
"""

import os
import sys
import json
import base64
from pathlib import Path
from datetime import datetime
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import after path setup
from pixellab_client import PixelLabClient

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
GALLERY_DIR = PROJECT_ROOT / "assets" / "gallery"
IMAGES_DIR = GALLERY_DIR / "images"
METADATA_FILE = GALLERY_DIR / "metadata.json"


# Gallery configuration - customize these prompts
GALLERY_IMAGES = [
    {
        "id": "wizard",
        "description": "a mysterious pixel art wizard with a glowing staff and purple robes, fantasy RPG style",
        "width": 128,
        "height": 128,
        "seed": 42,
    },
    {
        "id": "knight",
        "description": "a brave pixel art knight in shining armor with a sword and shield, retro game style",
        "width": 128,
        "height": 128,
        "seed": 123,
    },
    {
        "id": "dragon",
        "description": "a fierce pixel art dragon breathing fire, classic 16-bit RPG style",
        "width": 128,
        "height": 128,
        "seed": 456,
    },
    {
        "id": "spaceship",
        "description": "a sleek pixel art spaceship with glowing engines, retro sci-fi arcade style",
        "width": 128,
        "height": 128,
        "seed": 789,
    },
    {
        "id": "robot",
        "description": "a friendly pixel art robot with antenna and digital eyes, cute retro style",
        "width": 128,
        "height": 128,
        "seed": 101,
    },
    {
        "id": "treasure",
        "description": "an open pixel art treasure chest overflowing with gold coins and gems, classic RPG style",
        "width": 128,
        "height": 128,
        "seed": 202,
    },
]


def save_base64_image(base64_data: str, output_path: Path) -> bool:
    """
    Convert base64 image data to PNG file.
    
    Args:
        base64_data: Base64-encoded image string
        output_path: Path to save the PNG file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Remove data URL prefix if present
        if "," in base64_data:
            base64_data = base64_data.split(",")[1]
        
        # Decode base64
        image_bytes = base64.b64decode(base64_data)
        
        # Save as PNG
        with open(output_path, "wb") as f:
            f.write(image_bytes)
        
        return True
    except Exception as e:
        print(f"Error saving image: {e}")
        return False


def generate_gallery():
    """Generate all gallery images and save metadata."""
    
    # Check for API key
    api_key = os.getenv("PIXELLAB_API_KEY")
    if not api_key:
        print("Error: PIXELLAB_API_KEY not found in environment")
        print("Please set it in .env file:")
        print("  PIXELLAB_API_KEY=your-api-key-here")
        sys.exit(1)
    
    # Ensure directories exist
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    
    # Initialize client
    client = PixelLabClient(api_key=api_key)
    
    # Check balance first
    print("Checking API balance...")
    try:
        balance = client.get_balance()
        print(f"Balance: {balance}")
    except Exception as e:
        print(f"Warning: Could not check balance: {e}")
    
    # Generate images
    metadata = {
        "generated_at": datetime.now().isoformat(),
        "images": []
    }
    
    successful = 0
    failed = 0
    
    for config in GALLERY_IMAGES:
        image_id = config["id"]
        description = config["description"]
        width = config.get("width", 128)
        height = config.get("height", 128)
        seed = config.get("seed")
        
        print(f"\nGenerating: {image_id}")
        print(f"  Description: {description[:60]}...")
        
        try:
            # Generate image
            response = client.generate_image(
                description=description,
                width=width,
                height=height,
                seed=seed
            )
            
            if not response.get("images"):
                print(f"  Error: No images returned for {image_id}")
                failed += 1
                continue
            
            # Save the first image
            base64_image = response["images"][0]
            output_path = IMAGES_DIR / f"{image_id}_{width}x{height}.png"
            
            if save_base64_image(base64_image, output_path):
                print(f"  Saved: {output_path.name}")
                
                # Add to metadata
                metadata["images"].append({
                    "id": image_id,
                    "filename": output_path.name,
                    "description": description,
                    "width": width,
                    "height": height,
                    "seed": seed,
                    "generated_at": datetime.now().isoformat()
                })
                successful += 1
            else:
                print(f"  Error: Failed to save {image_id}")
                failed += 1
                
        except Exception as e:
            print(f"  Error generating {image_id}: {e}")
            failed += 1
    
    # Save metadata
    with open(METADATA_FILE, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"\nMetadata saved to: {METADATA_FILE}")
    
    # Summary
    print(f"\n{'='*50}")
    print(f"Gallery Generation Complete")
    print(f"{'='*50}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Total: {len(GALLERY_IMAGES)}")
    
    if successful > 0:
        print(f"\nImages saved to: {IMAGES_DIR}")
        print("\nNext steps:")
        print("  1. Review generated images")
        print("  2. Commit and push to deploy:")
        print("     git add assets/gallery/")
        print("     git commit -m 'Add pixel art gallery'")
        print("     git push")


def list_existing_images():
    """List existing gallery images."""
    if not IMAGES_DIR.exists():
        print("No gallery images found.")
        return
    
    images = list(IMAGES_DIR.glob("*.png"))
    if not images:
        print("No gallery images found.")
        return
    
    print(f"Found {len(images)} images:")
    for img in sorted(images):
        size = img.stat().st_size / 1024
        print(f"  - {img.name} ({size:.1f} KB)")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate pixel art gallery images")
    parser.add_argument("--list", action="store_true", help="List existing images")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be generated")
    
    args = parser.parse_args()
    
    if args.list:
        list_existing_images()
    elif args.dry_run:
        print("Would generate the following images:")
        for config in GALLERY_IMAGES:
            print(f"  - {config['id']}: {config['description'][:50]}...")
    else:
        generate_gallery()
