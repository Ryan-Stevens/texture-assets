import json
import os
import requests
from openai import OpenAI
from pathlib import Path
import base64
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def download_image(url, save_path):
    """Download image from URL and save to local path."""
    response = requests.get(url)
    response.raise_for_status()
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    with open(save_path, 'wb') as f:
        f.write(response.content)
    return save_path

def encode_image_to_base64(image_path):
    """Encode image to base64 string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def analyze_image(client, image_path):
    """Use OpenAI's Vision API to analyze the image."""
    base64_image = encode_image_to_base64(image_path)
    
    response = client.chat.completions.create(
        model="gpt-4o-2024-08-06",
        max_tokens=300,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Please analyze this texture image and provide a short but descriptive title (max 2 words) and a brief description (max 3-4 words) that captures its visual characteristics. Format your response as JSON with 'title' and 'description' fields."},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                            "detail": "low"
                        }
                    }
                ]
            }
        ],
    )
    
    try:
        # Extract JSON from the response
        response_text = response.choices[0].message.content
        # Find JSON-like content between curly braces
        start = response_text.find('{')
        end = response_text.rfind('}') + 1
        json_str = response_text[start:end]
        return json.loads(json_str)
    except Exception as e:
        print(f"Error parsing response: {e}")
        print(f"Raw response: {response_text}")
        return {"title": "", "description": ""}

def main():
    # Check for OpenAI API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("Please set OPENAI_API_KEY environment variable")
    
    client = OpenAI()
    
    # Load the texture metadata
    with open('texture_metadata.json', 'r') as f:
        metadata = json.load(f)
    
    # Create a temporary directory for downloaded images
    temp_dir = Path('temp_images')
    temp_dir.mkdir(exist_ok=True)
    
    # Process each texture
    for category in metadata['textures'].values():
        for texture in category['textures']:
            try:
                print(f"Processing {texture['filename']}...")
                
                # Download the image
                image_path = temp_dir / f"{texture['filename']}.jpg"
                download_image(texture['file_path'], image_path)
                
                # Analyze the image
                result = analyze_image(client, image_path)
                
                # Update metadata
                if result.get('title'):
                    texture['title'] = result['title']
                if result.get('description'):
                    texture['description'] = result['description']
                
                # Clean up the temporary image
                image_path.unlink()
                
            except Exception as e:
                print(f"Error processing {texture['filename']}: {e}")
            
            # Save after every image
            with open('texture_metadata_updated.json', 'w') as f:
                json.dump(metadata, f, indent=2)
    
    # Clean up temp directory
    for f in temp_dir.glob('*'):
        f.unlink()
    temp_dir.rmdir()
    print("\nProcessing complete. Check texture_metadata_updated.json for results.")

if __name__ == '__main__':
    main()
