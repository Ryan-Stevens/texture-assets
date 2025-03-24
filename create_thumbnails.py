import os
from PIL import Image

def create_thumbnails(source_dirs):
    # Get the script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create thumbnails directory if it doesn't exist
    thumbnails_dir = os.path.join(script_dir, 'thumbnails')
    if not os.path.exists(thumbnails_dir):
        os.makedirs(thumbnails_dir)
        
    # Process each source directory
    for source_dir_name in source_dirs:
        # Get absolute paths
        source_dir = os.path.join(script_dir, source_dir_name)
        thumb_dir = os.path.join(thumbnails_dir, source_dir_name)
        
        if not os.path.exists(thumb_dir):
            os.makedirs(thumb_dir)
            
        # Process each image in the source directory
        for filename in os.listdir(source_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                # Skip .DS_Store and other hidden files
                if filename.startswith('.'):
                    continue
                    
                input_path = os.path.join(source_dir, filename)
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
    # List of directories containing textures
    source_dirs = ['textures/Grunge', 'textures/Ink:Paint', 'textures/Lens Effects', 'textures/Paper:Canvas', 'textures/Grain']
    create_thumbnails(source_dirs)
    print('Thumbnail creation complete!')
