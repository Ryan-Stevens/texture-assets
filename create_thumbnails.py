import os
import shutil
from PIL import Image

def create_thumbnails():
    # Get the script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Get the textures directory
    textures_dir = os.path.join(script_dir, 'textures')
    
    # Remove existing thumbnails directory if it exists
    thumbnails_dir = os.path.join(script_dir, 'thumbnails')
    if os.path.exists(thumbnails_dir):
        shutil.rmtree(thumbnails_dir)
    
    # Create fresh thumbnails and thumbnails/textures directories
    thumbnails_textures_dir = os.path.join(thumbnails_dir, 'textures')
    os.makedirs(thumbnails_textures_dir)
    
    # Process each category directory in textures
    for category in os.listdir(textures_dir):
        # Skip hidden files and non-directories
        category_path = os.path.join(textures_dir, category)
        if not os.path.isdir(category_path) or category.startswith('.'):
            continue
        
        # Create corresponding thumbnail directory
        thumb_dir = os.path.join(thumbnails_textures_dir, category)
        os.makedirs(thumb_dir)
        
        # Process each image in the category directory
        for filename in os.listdir(category_path):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                # Skip hidden files
                if filename.startswith('.'):
                    continue
                
                input_path = os.path.join(category_path, filename)
                output_path = os.path.join(thumb_dir, filename)
                
                try:
                    with Image.open(input_path) as img:
                        # Convert to RGB if necessary
                        if img.mode in ('RGBA', 'P'):
                            img = img.convert('RGB')
                        
                        # Calculate new size while maintaining aspect ratio
                        # Target width of 800px for thumbnails
                        basewidth = 800
                        wpercent = (basewidth / float(img.size[0]))
                        hsize = int((float(img.size[1]) * float(wpercent)))
                        
                        # Resize and save with reduced quality
                        img_resized = img.resize((basewidth, hsize), Image.Resampling.LANCZOS)
                        img_resized.save(output_path, 'JPEG', quality=60, optimize=True)
                        
                        print(f'Created thumbnail for {filename}')
                except Exception as e:
                    print(f'Error processing {filename}: {str(e)}')

if __name__ == '__main__':
    create_thumbnails()
    print('Thumbnail creation complete!')
