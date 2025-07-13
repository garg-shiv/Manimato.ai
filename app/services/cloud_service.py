import logging
import mimetypes
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict

import cloudinary
import cloudinary.api
import cloudinary.uploader
from core.config import config

logger = logging.getLogger(__name__)


class CloudStorageError(Exception):
    """Custom exception for cloud storage operations"""

    pass


class CloudStorageInterface(ABC):
    """Abstract base class for cloud storage providers"""

    @abstractmethod
    async def upload_file(self, file_path: str) -> str:
        """Upload file and return public_id"""
        pass

    @abstractmethod
    async def get_secure_url(self, public_id: str, **kwargs) -> str:
        """Convert public_id to secure URL"""
        pass

    @abstractmethod
    async def delete_file(self, public_id: str, **kwargs) -> bool:
        """Delete file from cloud storage"""
        pass

    @abstractmethod
    async def get_file_info(self, public_id: str, **kwargs) -> Dict[str, Any]:
        """Get file information"""
        pass


class CloudinaryStorage(CloudStorageInterface):
    """Cloudinary cloud storage implementation"""

    def __init__(self):
        cloudinary.config(
            cloud_name=config.CLOUDINARY_CLOUD_NAME,
            api_key=config.CLOUDINARY_API_KEY,
            api_secret=config.CLOUDINARY_SECRET,
            secure=True,
        )
        self.provider = "cloudinary"

    async def upload_file(self, file_path: str) -> str:
        """Upload file to Cloudinary and return public_id"""
        try:
            if not os.path.exists(file_path):
                raise CloudStorageError(f"File not found: {file_path}")

            # Determine resource type based on file extension
            mime_type, _ = mimetypes.guess_type(file_path)
            resource_type = "raw"  # Cloudinary auto-detects

            format = Path(file_path).suffix[1:]
            if mime_type:
                if mime_type.startswith("video/"):
                    resource_type = "video"
                elif mime_type.startswith("image/"):
                    resource_type = "image"
                elif mime_type.startswith("audio/"):
                    resource_type = "video"  # Cloudinary treats audio as video

            folder = (
                config.CLOUDINARY_FOLDER_NAME
                + "/"
                + ("code" if resource_type == "raw" else resource_type)
            )
            # Upload file
            result = cloudinary.uploader.upload(
                file_path,
                resource_type=resource_type,
                unique_filename=True,
                format=format,
                folder=folder,
            )

            return result.get("public_id")

        except Exception as e:
            raise CloudStorageError(f"Upload failed: {str(e)}")

    async def get_secure_url(self, public_id: str, **kwargs) -> str:
        """Generate secure URL for the file"""
        try:
            # Default transformation options
            transformation = kwargs.get("transformation", {})
            resource_type = kwargs.get("resource_type", "auto")
            format = kwargs.get("format", "py")
            # Generate URL
            url = cloudinary.utils.cloudinary_url(
                public_id,
                resource_type=resource_type,
                secure=True,
                transformation=transformation,
                format=format,
            )[0]

            return url

        except Exception as e:
            raise CloudStorageError(f"URL generation failed: {str(e)}")

    async def delete_file(self, public_id: str, **kwargs) -> bool:
        """Delete file from Cloudinary"""
        try:
            # Try different resource types
            resource_type = kwargs.get("resource_type", "raw")

            result = cloudinary.uploader.destroy(public_id, resource_type=resource_type)
            if result.get("result") == "ok":
                return True
            return False
        except Exception as e:
            raise CloudStorageError(f"Delete failed: {str(e)}")

    async def get_file_info(self, public_id: str, **kwargs) -> Dict[str, Any]:
        """Get file information from Cloudinary"""
        try:
            # Try different resource types
            resource_type = kwargs.get("resource_type", "raw")
            result = cloudinary.api.resource(public_id, resource_type=resource_type)
            return result

            raise CloudStorageError(f"File not found: {public_id}")
        except Exception as e:
            raise CloudStorageError(f"Get info failed: {str(e)}")


class CloudStorage:
    """Main cloud storage service class"""

    def __init__(self, provider: str, **config):
        """
        Initialize cloud storage service

        Args:
            provider: 'cloudinary', 'aws', or 'gcp'
            **config: Provider-specific configuration
        """
        self.provider = provider.lower()

        if self.provider == "cloudinary":
            self.storage = CloudinaryStorage()
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    async def upload_file(self, file_path: str) -> str:
        """Upload file and return public_id"""
        return await self.storage.upload_file(file_path)

    async def get_secure_url(self, public_id: str, **kwargs) -> str:
        """Convert public_id to secure URL"""
        return await self.storage.get_secure_url(public_id, **kwargs)

    async def delete_file(self, public_id: str, **kwargs) -> bool:
        """Delete file from cloud storage"""
        return await self.storage.delete_file(public_id, **kwargs)

    async def get_file_info(self, public_id: str, **kwargs) -> Dict[str, Any]:
        """Get file information"""
        return await self.storage.get_file_info(public_id, **kwargs)

    async def is_video_file(self, file_path: str) -> bool:
        """Check if file is a video file"""
        mime_type, _ = mimetypes.guess_type(file_path)
        return mime_type is not None and mime_type.startswith("video/")

    def is_image_file(self, file_path: str) -> bool:
        """Check if file is an image file"""
        mime_type, _ = mimetypes.guess_type(file_path)
        return mime_type is not None and mime_type.startswith("image/")

    def is_py_file(self, file_path: str) -> bool:
        mime_type, _ = mimetypes.guess_type(file_path)

        file_ext = Path(file_path).suffix[1:]
        return mime_type is not None and file_ext == "py"
