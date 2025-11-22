"""
This file is going to handle all the image upload and management.Imagekit will save
all the images and will return the url of the image.Imagekit has also performance 
optimization.
"""

from dotenv import load_dotenv
from imagekitio import ImageKit
import os

load_dotenv()

imagekit = ImageKit(
    public_key=os.getenv("IMAGEKIT_PUBLIC_KEY"),
    private_key=os.getenv("IMAGEKIT_PRIVATE_KEY"),
    url_endpoint=os.getenv("IMAGEKIT_URL"),
)