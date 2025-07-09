from django.db import models
from Base.base import HomeBaseModel
from akp_accounts.models import CustomUser
from akp_news.base import BaseModel

import fitz  # PyMuPDF for PDF manipulation
from django.core.files.base import ContentFile
from io import BytesIO
from PIL import Image, ImageOps
# Create your models here.


class Epaper(HomeBaseModel):
    file = models.FileField(upload_to='epapers/')
    is_active = models.BooleanField(default=True)
    timestamp = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "E-Papers"
        ordering = ['-timestamp']
    
    def __str__(self):
        return self.meta_title
    
    def save(self, *args, **kwargs):
        """
        Overrides the save method to extract PDF metadata and a cropped thumbnail image,
        populating the fields inherited from HomeBaseModel.
        """
        # Check if the file is new or has been changed to avoid reprocessing
        process_pdf = True
        if not self._state.adding: # if this is an existing object
            try:
                old_instance = Epaper.objects.get(pk=self.pk)
                if old_instance.file == self.file:
                    process_pdf = False # Don't re-process if the file is the same
            except Epaper.DoesNotExist:
                pass # Should not happen, but good to handle

        if process_pdf and self.file:
            try:
                # Store original file position
                original_position = self.file.tell()
                
                # Read the file content for processing
                self.file.seek(0)
                pdf_file_stream = self.file.read()
                
                # Reset file position immediately after reading
                self.file.seek(original_position)
                
                # Open PDF document from the stream
                pdf_document = fitz.open(stream=pdf_file_stream, filetype="pdf")

                # --- 1. Extract Metadata ---
                metadata = pdf_document.metadata
                # 'subject' is the standard PDF metadata field for a description
                self.meta_description = metadata.get('subject') 
                self.meta_keywords = metadata.get('keywords')

                # If description is still missing, extract text from the first page as a fallback
                if not self.meta_description and pdf_document.page_count > 0:
                    first_page = pdf_document.load_page(0)
                    # Get the first 40 words for a concise description
                    self.meta_description = " ".join(first_page.get_text("text").split()[:40]) + "..."

                # --- 2. Extract and Crop Thumbnail ---
                if pdf_document.page_count > 0:
                    first_page = pdf_document.load_page(0)

                    # Set zoom factor to get high quality image
                    zoom_factor = 4.0
                    matrix = fitz.Matrix(zoom_factor, zoom_factor)
                    pix = first_page.get_pixmap(matrix=matrix)
                    
                    # Convert pixmap to PIL Image for cropping
                    img_data = pix.tobytes("png")
                    img_buffer = BytesIO(img_data)
                    pil_image = Image.open(img_buffer)
                    
                    # Define target dimensions
                    target_width = 800
                    target_height = 450
                    target_ratio = target_width / target_height
                    
                    # Get current image dimensions
                    current_width, current_height = pil_image.size
                    current_ratio = current_width / current_height
                    
                    # Determine how to crop based on aspect ratios
                    if current_ratio > target_ratio:
                        # Image is wider than target - crop horizontally
                        # Calculate new width to match target ratio
                        new_width = int(current_height * target_ratio)
                        left = (current_width - new_width) // 2
                        top = 0
                        right = left + new_width
                        bottom = current_height
                    else:
                        # Image is taller than target - crop vertically (half cut from top)
                        # Calculate new height to match target ratio
                        new_height = int(current_width / target_ratio)
                        left = 0
                        # Crop from the top half of the image
                        top = 0
                        right = current_width
                        bottom = min(new_height, current_height)
                    
                    # Crop the image
                    cropped_image = pil_image.crop((left, top, right, bottom))
                    
                    # Resize to exact target dimensions
                    final_image = cropped_image.resize((target_width, target_height), Image.LANCZOS)
                    
                    # Optional: Apply some image enhancement
                    final_image = ImageOps.exif_transpose(final_image)  # Fix rotation if needed
                    
                    # Save the final image to buffer
                    final_buffer = BytesIO()
                    final_image.save(final_buffer, format='PNG', quality=95, optimize=True)
                    final_buffer.seek(0)
                    
                    # Generate unique image name
                    # base_name = os.path.splitext(self.file.name)[0]
                    image_name = f"meta_{self.id}.png"
                    
                    # Create ContentFile and assign to meta_image
                    self.meta_image = ContentFile(final_buffer.read(), name=image_name)
                    
                    # Clean up buffers
                    img_buffer.close()
                    final_buffer.close()

                pdf_document.close()

            except Exception as e:
                # Handle potential errors with corrupted PDFs or other issues
                print(f"Error processing PDF for metadata: {e}")
                # Ensure there's a default title if extraction fails
                if not self.meta_title:
                    self.meta_title = str(self.file.name).split('/')[-1]

        # Call the original save method from the parent class
        super().save(*args, **kwargs)


class EpaperDownload(BaseModel):
    epaper = models.ForeignKey(Epaper, on_delete=models.CASCADE, related_name='downloads')
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='epapers_downloads')
    ip_addr = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        verbose_name_plural = "E-Paper Downloads"

    def __str__(self):
        return f"{self.customer.get_full_name()} - {self.epaper}"