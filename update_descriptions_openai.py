import json
import os
import time
import shutil
import argparse
from datetime import datetime
from openai import OpenAI
from pathlib import Path

# Set your OpenAI API key
# Note: It's better to use environment variables for API keys
# For this script, you'll need to set your API key here or via environment variable
api_key = os.environ.get("OPENAI_API_KEY", "")  # Add your API key here or set it as an environment variable
client = OpenAI(api_key=api_key)

def shorten_description(description):
    """
    Send description to OpenAI API to shorten it to 20 characters or less
    while maintaining accuracy.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o",  # or another appropriate model
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that shortens texture descriptions to 20 characters or less while maintaining accuracy."
                },
                {
                    "role": "user",
                    "content": f"Shorten this texture description to 20 characters or less while keeping it accurate: '{description}'"
                }
            ],
            max_tokens=50
        )
        
        # Extract the shortened description from the response
        shortened = response.choices[0].message.content.strip()
        
        # Remove quotes if present
        if shortened.startswith('"') and shortened.endswith('"'):
            shortened = shortened[1:-1]
        if shortened.startswith("'") and shortened.endswith("'"):
            shortened = shortened[1:-1]
            
        # Ensure it's 20 characters or less
        if len(shortened) > 20:
            print(f"Warning: API returned description longer than 20 chars: '{shortened}'")
            shortened = shortened[:20]
            
        return shortened
    except Exception as e:
        print(f"Error with OpenAI API: {e}")
        # Return a shortened version of the original as fallback
        return description[:20]

def update_texture_descriptions(dry_run=False, backup=True, max_length=20):
    # Path to the metadata file
    metadata_path = Path.cwd() / "texture_metadata.json"
    
    # Create backup if requested
    if backup and not dry_run:
        backup_path = Path.cwd() / f"texture_metadata_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        shutil.copy2(metadata_path, backup_path)
        print(f"Created backup at: {backup_path}")
    
    # Load the existing metadata
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
    
    # Counter for API rate limiting and statistics
    request_count = 0
    updated_count = 0
    already_short_count = 0
    total_descriptions = 0
    
    # Iterate through each category
    for category_key, category_data in metadata["textures"].items():
        print(f"Processing category: {category_key}")
        
        # Iterate through each texture in the category
        for i, texture in enumerate(category_data["textures"]):
            total_descriptions += 1
            original_description = texture.get("description", "")
            
            # Skip if no description
            if not original_description:
                print(f"  Warning: No description for {texture.get('filename', 'unknown')}")
                continue
                
            # Skip if already short enough
            if len(original_description) <= max_length:
                print(f"  Already short enough: {original_description}")
                already_short_count += 1
                continue
                
            print(f"  Processing: {texture['filename']}")
            print(f"  Original description: {original_description}")
            
            # Send to OpenAI for shortening
            print(f"  Original ({len(original_description)} chars): {original_description}")
            
            if not dry_run:
                shortened_description = shorten_description(original_description)
                
                # Update the texture with the shortened description
                texture["description"] = shortened_description
                updated_count += 1
                
                print(f"  Shortened ({len(shortened_description)} chars): {shortened_description}")
                
                # Increment request counter and handle rate limiting
                request_count += 1
                if request_count % 3 == 0:  # Adjust based on your API rate limits
                    print("Pausing for API rate limiting...")
                    time.sleep(1)  # Add delay to avoid hitting rate limits
            else:
                print("  [DRY RUN] Would shorten this description")
            
            # Show progress
            if (i + 1) % 10 == 0:
                print(f"Progress: Processed {i + 1}/{len(category_data['textures'])} in {category_key}")
    
    # Save the updated metadata back to the file if not a dry run
    if not dry_run:
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"Updated {updated_count} descriptions successfully!")
    
    # Print summary
    print("\nSummary:")
    print(f"Total descriptions: {total_descriptions}")
    print(f"Already short enough: {already_short_count}")
    print(f"Updated: {updated_count if not dry_run else 0}")
    print(f"Would update: {total_descriptions - already_short_count if dry_run else 'N/A'}")
    
    return updated_count

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Update texture descriptions to be 20 characters or less using OpenAI.")
    parser.add_argument("--dry-run", action="store_true", help="Run without making changes")
    parser.add_argument("--no-backup", action="store_true", help="Skip creating a backup")
    parser.add_argument("--max-length", type=int, default=20, help="Maximum character length for descriptions")
    parser.add_argument("--api-key", type=str, help="OpenAI API key (overrides environment variable)")
    args = parser.parse_args()
    
    # Override API key if provided
    if args.api_key:
        api_key = args.api_key
        client = OpenAI(api_key=api_key)
    
    # Check if API key is set
    if not api_key:
        print("Error: OpenAI API key is not set. Please set it in the script, as an environment variable, or use --api-key.")
    else:
        update_texture_descriptions(
            dry_run=args.dry_run,
            backup=not args.no_backup,
            max_length=args.max_length
        )
