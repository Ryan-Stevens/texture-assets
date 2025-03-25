import os
import json
from pathlib import Path
from urllib.parse import quote

def extract_metadata_from_filename(filepath, base_dir):
    """Extract metadata from filename if it contains special format, otherwise use defaults."""
    filename = Path(filepath).stem
    parts = filename.split('__')
    
    if len(parts) >= 4:  # Special format: Name__Display Name__Blend Mode__Sequence
        base_name = parts[1]
        title = parts[2]
        blend_mode = parts[3]
        sequence = int(parts[4]) if len(parts) > 4 else 1
    else:
        # Default format: just use the filename
        base_name = filename
        title = filename
        blend_mode = "overlay"  # default blend mode
        # Try to extract sequence number from the end of filename
        try:
            sequence = int(''.join(filter(str.isdigit, filename)))
        except ValueError:
            sequence = 1

    # Generate CDN URLs for both the texture and thumbnail
    cdn_base = "https://cdn.jsdelivr.net/gh/Ryan-Stevens/texture-assets@main"
    
    # Get the category and filename for thumbnail path
    path_obj = Path(filepath)
    category_dir = path_obj.parent.name
    file_stem = path_obj.stem
    
    # Process path components: replace spaces with hyphens in directory names, URL encode the rest
    relative_path = str(Path(filepath).relative_to(base_dir))
    texture_path_parts = relative_path.split('/')
    
    # Replace spaces with hyphens in directory names, but use URL encoding for filenames
    encoded_texture_path = '/'.join(
        part.replace(' ', '-') if i < len(texture_path_parts) - 1 else quote(part)
        for i, part in enumerate(texture_path_parts)
    )
    texture_cdn_path = f"{cdn_base}/{encoded_texture_path}"
    
    # Generate thumbnail path
    thumbnail_path_parts = ["thumbnails", "textures", category_dir, f"{file_stem}.jpg"]
    # Replace spaces with hyphens in directory names, but use URL encoding for filenames
    encoded_thumbnail_path = '/'.join(
        part.replace(' ', '-') if i < len(thumbnail_path_parts) - 1 else quote(part)
        for i, part in enumerate(thumbnail_path_parts)
    )
    thumbnail_cdn_path = f"{cdn_base}/{encoded_thumbnail_path}"

    return {
        "filename": base_name,
        "title": title,
        "default_blend_mode": blend_mode,
        "sequence_number": sequence,
        "file_path": texture_cdn_path,
        "thumbnail_path": thumbnail_cdn_path
    }

def get_texture_metadata(category, filename):
    """Get metadata for each texture."""
    # Default metadata generator
    def generate_default_metadata(name):
        # Remove numbers and clean up the name
        clean_name = ' '.join(word for word in name.split() if not word.isdigit())
        return {
            "title": name,  # Keep original name as title
            "description": f"Apply {clean_name.lower()} effects to your design"
        }
    
    # Special metadata for specific textures
    special_metadata = {
        "Grunge": {
            "Grunge 1": {
                "title": "Grimey as bru",
                "description": "Add a gritty, weathered look to your design"
            }
        },
        "Ink:Paint": {},
        "Lens Effects": {},
        "Grain": {}
    }
    
    # Get special metadata if it exists, otherwise generate default
    category_dict = special_metadata.get(category, {})
    return category_dict.get(filename, generate_default_metadata(filename))

def load_existing_metadata():
    """Load existing metadata from the JSON file if it exists."""
    metadata_path = Path.cwd() / "texture_metadata.json"
    if metadata_path.exists() and metadata_path.stat().st_size > 0:
        try:
            with open(metadata_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("Warning: Invalid JSON in metadata file, starting fresh")
    return {"textures": {}}

def update_texture_metadata():
    base_dir = Path.cwd()
    textures_dir = base_dir / "textures"
    
    # Load existing metadata
    metadata = load_existing_metadata()
    
    # Walk through the textures directory
    for category_dir in textures_dir.iterdir():
        if not category_dir.is_dir():
            continue
            
        category_name = category_dir.name
        category_key = category_name.replace(":", "_")
        
        # Initialize category in metadata if it doesn't exist
        if category_key not in metadata["textures"]:
            metadata["textures"][category_key] = {
                "category": category_name,
                "textures": []
            }
        
        # Create a set of existing filenames for this category
        existing_textures = {
            texture["filename"] 
            for texture in metadata["textures"][category_key]["textures"]
        }
        
        # Process all images in the category
        for image_path in category_dir.glob("*.jpg"):
            if image_path.stem.startswith('.'):
                continue
                
            # Skip if this texture already exists in metadata
            if image_path.stem in existing_textures:
                continue
                
            # Extract basic metadata
            texture_metadata = extract_metadata_from_filename(image_path, base_dir)
            
            # Get additional metadata
            additional_metadata = get_texture_metadata(category_name, image_path.stem)
            texture_metadata.update(additional_metadata)
            
            # Add to the category's textures list
            metadata["textures"][category_key]["textures"].append(texture_metadata)
        
        # Sort textures by sequence number
        metadata["textures"][category_key]["textures"].sort(
            key=lambda x: x["sequence_number"]
        )
    
    # Write updated metadata to file
    metadata_path = base_dir / "texture_metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print("Metadata updated successfully!")

if __name__ == "__main__":
    update_texture_metadata()
