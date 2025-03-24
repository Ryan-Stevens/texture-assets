#!/usr/bin/env python3
import os
from PIL import Image
import sys

def get_file_size_mb(file_path):
    """Get file size in megabytes"""
    return os.path.getsize(file_path) / (1024 * 1024)

def optimize_image(file_path, max_size_mb=19):
    """Optimize image if it's larger than max_size_mb"""
    current_size = get_file_size_mb(file_path)
    
    if current_size <= max_size_mb:
        print(f"Skipping {file_path} ({current_size:.2f}MB) - already under {max_size_mb}MB")
        return

    print(f"Processing {file_path} (Current size: {current_size:.2f}MB)")
    
    # Open the image
    img = Image.open(file_path)
    
    # Start with quality 95 and reduce until we get under max_size_mb
    quality = 95
    while quality > 5:  # Don't go below quality 5
        # Create a temporary filename
        temp_path = f"{file_path}.temp"
        
        # Save with current quality
        img.save(temp_path, format=img.format, quality=quality, optimize=True)
        
        # Check new size
        new_size = get_file_size_mb(temp_path)
        
        if new_size <= max_size_mb:
            # Success! Replace original with optimized version
            os.replace(temp_path, file_path)
            print(f"  Optimized to {new_size:.2f}MB (quality={quality})")
            return
        
        # Remove temp file
        os.remove(temp_path)
        
        # Reduce quality for next iteration
        quality -= 5
    
    print(f"  WARNING: Could not optimize {file_path} to under {max_size_mb}MB while maintaining acceptable quality")

def process_directory(directory):
    """Process all images in directory and subdirectories"""
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                file_path = os.path.join(root, file)
                try:
                    optimize_image(file_path)
                except Exception as e:
                    print(f"Error processing {file_path}: {str(e)}")

if __name__ == "__main__":
    # Ensure Pillow is installed
    try:
        import PIL
    except ImportError:
        print("Pillow is not installed. Installing...")
        os.system("pip3 install Pillow")
    
    textures_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "textures")
    
    if not os.path.exists(textures_dir):
        print(f"Error: Textures directory not found at {textures_dir}")
        sys.exit(1)
    
    print(f"Processing images in {textures_dir}")
    process_directory(textures_dir)
    print("Done!")
