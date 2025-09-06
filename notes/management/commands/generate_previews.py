from django.core.management.base import BaseCommand
from django.conf import settings
import os
import fitz
from PIL import Image

class Command(BaseCommand):
    help = 'Generate preview images for new PDF files in media/notesheets.'

    def handle(self, *args, **options):
        notesheets_dir = os.path.join(settings.BASE_DIR, 'notes', 'media', 'notesheets')
        previews_dir = os.path.join(settings.BASE_DIR, 'notes', 'media', 'previews')
        os.makedirs(previews_dir, exist_ok=True)
        for filename in os.listdir(notesheets_dir):
            if filename.lower().endswith('.pdf'):
                pdf_path = os.path.join(notesheets_dir, filename)
                preview_name = os.path.splitext(filename)[0] + '.png'
                preview_path = os.path.join(previews_dir, preview_name)
                if not os.path.exists(preview_path):
                    try:
                        doc = fitz.open(pdf_path)
                        page = doc.load_page(0)
                        pix = page.get_pixmap()
                        pix.save(preview_path)
                        # Optional: show image (for debugging)
                        # img = Image.open(preview_path)
                        # img.show()
                        self.stdout.write(self.style.SUCCESS(f"Generated preview for {filename}"))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"Error generating preview for {filename}: {e}"))
                else:
                    self.stdout.write(f"Preview already exists for {filename}")
