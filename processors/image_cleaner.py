import os
import base64
from collections import defaultdict
from PIL import Image
import logging

class ImageCleaner:
    def __init__(self, figure_folder, image_format="JPG"):
        self.figure_folder = figure_folder
        self.image_format = image_format
        self.image_files = os.listdir(figure_folder)
        self.image_base64_dict = defaultdict(list)
        self.images_to_keep = []
        self.logger = self.setup_logger()
        
    def setup_logger(self):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        return logging.getLogger(__name__)

    def encode_image_to_base64(self, image_path):
        with open(image_path, 'rb') as img_file:
            return base64.b64encode(img_file.read()).decode("utf-8")

    def process_image(self, image_path):
        try:
            with Image.open(image_path) as img:
                img = img.convert("RGB")
                img.save(image_path, format=self.image_format)
                self.logger.info(f"Image processed (no resize): {image_path}")
        except Exception as e:
            self.logger.error(f"Failed to process image {image_path}: {e}")

    def process_images(self):
        for image_file in self.image_files:
            image_path = os.path.join(self.figure_folder, image_file)
            encoded = self.encode_image_to_base64(image_path)
            self.image_base64_dict[encoded].append(image_file)

        for base64_str, files in self.image_base64_dict.items():
            if len(files) > 1:
                for f in files:
                    self.logger.info(f"Removing duplicate image: {f}")
                    os.remove(os.path.join(self.figure_folder, f))
            else:
                image_file = files[0]
                self.images_to_keep.append(image_file)
                image_path = os.path.join(self.figure_folder, image_file)
                self.process_image(image_path)