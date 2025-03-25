import os
from pathlib import Path

def safe_name(name):
    """Convert a name to be jsDelivr-safe."""
    # Replace special character patterns first
    replacements = {
        "Ink & Paint": "Ink-and-Paint",
        "Paper & Canvas": "Paper-and-Canvas",
        "Film Grain": "Film-Grain",
        "Lens Effects": "Lens-Effects",
        "test category": "test-category",
        "Ink:Paint": "Ink-Paint",
        "Paper:Canvas": "Paper-Canvas",
    }
    
    for old, new in replacements.items():
        name = name.replace(old, new)
    
    # Replace any remaining spaces with hyphens
    name = name.replace(" ", "-")
    return name

def rename_files_and_dirs():
    """Rename all files and directories to be jsDelivr-safe."""
    base_dir = Path("textures")
    
    # First, collect all renames to check for conflicts
    renames = []
    
    # Walk bottom-up so we handle files before directories
    for root, dirs, files in os.walk(base_dir, topdown=False):
        root_path = Path(root)
        
        # Handle files
        for name in files:
            if name.startswith('.'):
                continue
            old_path = root_path / name
            new_name = safe_name(name)
            if new_name != name:
                new_path = root_path / new_name
                renames.append((old_path, new_path))
        
        # Handle directories
        for name in dirs:
            old_path = root_path / name
            new_name = safe_name(name)
            if new_name != name:
                new_path = root_path / new_name
                renames.append((old_path, new_path))
    
    # Check for conflicts
    new_paths = [new for _, new in renames]
    if len(set(new_paths)) != len(new_paths):
        print("Error: Rename would create duplicate paths!")
        return
    
    # Perform renames
    for old_path, new_path in renames:
        print(f"Renaming: {old_path} -> {new_path}")
        old_path.rename(new_path)

if __name__ == "__main__":
    print("Starting rename operation...")
    rename_files_and_dirs()
    print("Rename operation complete.")
