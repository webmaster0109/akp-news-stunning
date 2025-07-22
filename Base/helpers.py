from io import BytesIO
from PIL import Image
import os
from django.core.files.base import ContentFile

def optimize_image(image_field, target_kb=100, max_width=1000):
    try:
        img = Image.open(image_field)

        if img.width > max_width:
            new_height = int((max_width / img.width) * img.height)
            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)

        if img.mode == 'RGBA':
            img = img.convert('RGB')
        buffer = BytesIO()
        quality = 85
        img.save(buffer, format='WEBP', quality=quality, optimize=True)
        
        while buffer.tell() / 1024 > target_kb and quality > 10:
            buffer = BytesIO()
            quality -= 5
            img.save(buffer, format='WEBP', quality=quality, optimize=True)
        
        original_filename = os.path.splitext(image_field.name)[0]
        new_filename = f"{original_filename}.webp"

        return ContentFile(buffer.getvalue(), name=new_filename)
    except Exception as e:
        print(f"Error optimizing image: {e}")
        return None