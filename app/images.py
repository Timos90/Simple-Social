"""
ImageKit.io Configuration and Client Initialization.

This module is responsible for setting up the connection to the ImageKit.io
service, which is used for all media uploads and transformations.

The ImageKit client is initialized using credentials (public key, private key,
and URL endpoint) loaded securely from environment variables.
"""

from imagekitio import ImageKit
import os

# The ImageKit client is initialized once when the application starts. It can then
# be imported and used throughout the application for any media operations.
# Uvicorn automatically loads environment variables from the `.env` file.
imagekit = ImageKit(
    public_key=os.getenv("IMAGEKIT_PUBLIC_KEY"),
    private_key=os.getenv("IMAGEKIT_PRIVATE_KEY"),
    url_endpoint=os.getenv("IMAGEKIT_URL"),
)