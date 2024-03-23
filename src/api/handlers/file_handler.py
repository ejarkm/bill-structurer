import fitz  # PyMuPDF
from PIL import Image
import io

def convert_pdf_to_images(pdf_file):
    doc = fitz.open("pdf", pdf_file.read())
    imgs = []
    for page in doc:  # Iterate through each page
        pix = page.get_pixmap()  # Render page to an image
        img_data = pix.tobytes("png")  # Save as PNG in memory
        img = Image.open(io.BytesIO(img_data))
        imgs.append(img)
    return imgs

def concatenate_images_vertically(images):
    total_height = sum(image.height for image in images)
    max_width = max(image.width for image in images)
    combined_image = Image.new('RGB', (max_width, total_height))
    y_offset = 0
    for image in images:
        combined_image.paste(image, (0, y_offset))
        y_offset += image.height
    return combined_image