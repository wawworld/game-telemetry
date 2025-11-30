"""Frame writer for saving screen captures with timestamps in filenames."""

from pathlib import Path
from typing import Optional
from PIL import Image
from services.data_writer import DataWriter
from utils.logging import get_logger

logger = get_logger(__name__)


class FrameWriter(DataWriter):
    """Saves screen capture frames as JPEG/PNG with timestamp in filename."""
    
    def __init__(
        self,
        output_directory: str,
        session_id: str,
        image_format: str = "jpeg",
        image_quality: int = 85,
    ):
        """Initialize frame writer.
        
        Args:
            output_directory: Directory for output files
            session_id: Session identifier
            image_format: Image format ("jpeg" or "png")
            image_quality: Quality for JPEG (0-100)
        """
        super().__init__(output_directory)
        self.session_id = session_id
        self.image_format = image_format.lower()
        self.image_quality = image_quality
        self._frames_written = 0
        
        # Validate format
        if self.image_format not in ["jpeg", "png"]:
            raise ValueError(f"Unsupported image format: {image_format}")
    
    async def write(self, image: Image.Image, timestamp_ms: int) -> str:
        """Write a frame to disk with timestamp in filename.
        
        Args:
            image: PIL Image object to save
            timestamp_ms: Unix timestamp in milliseconds
            
        Returns:
            Relative path to saved image file
        """
        # Generate filename: frame_<unix_timestamp_ms>.jpg
        extension = "jpg" if self.image_format == "jpeg" else "png"
        filename = f"frame_{timestamp_ms}.{extension}"
        filepath = self.output_directory / filename
        
        try:
            # Convert RGBA to RGB for JPEG format
            if self.image_format == "jpeg" and image.mode == 'RGBA':
                # Create RGB image with white background
                rgb_image = Image.new('RGB', image.size, (255, 255, 255))
                rgb_image.paste(image, mask=image.split()[3])  # Use alpha channel as mask
                image = rgb_image
            
            if self.image_format == "jpeg":
                image.save(filepath, "JPEG", quality=self.image_quality, optimize=True)
            else:  # png
                image.save(filepath, "PNG", optimize=True)
            
            self._frames_written += 1
            logger.debug(f"Saved frame: {filename}")
            return str(filename)
            
        except Exception as e:
            logger.error(f"Error saving frame {filename}: {e}")
            raise
    
    def write_sync(self, image: Image.Image, timestamp_ms: int) -> str:
        """Synchronous write for non-async contexts.
        
        Args:
            image: PIL Image object to save
            timestamp_ms: Unix timestamp in milliseconds
            
        Returns:
            Relative path to saved image file
        """
        extension = "jpg" if self.image_format == "jpeg" else "png"
        filename = f"frame_{timestamp_ms}.{extension}"
        filepath = self.output_directory / filename
        
        try:
            # Convert RGBA to RGB for JPEG format
            if self.image_format == "jpeg" and image.mode == 'RGBA':
                # Create RGB image with white background
                rgb_image = Image.new('RGB', image.size, (255, 255, 255))
                rgb_image.paste(image, mask=image.split()[3])  # Use alpha channel as mask
                image = rgb_image
            
            if self.image_format == "jpeg":
                image.save(filepath, "JPEG", quality=self.image_quality, optimize=True)
            else:
                image.save(filepath, "PNG", optimize=True)
            
            self._frames_written += 1
            return str(filename)
            
        except Exception as e:
            logger.error(f"Error saving frame {filename}: {e}")
            raise
    
    async def flush(self) -> None:
        """Frames are written immediately, no buffering."""
        pass
    
    async def close(self) -> None:
        """Close writer."""
        logger.info(f"Closed frame writer. Total frames written: {self._frames_written}")
    
    def get_frames_count(self) -> int:
        """Get total number of frames written."""
        return self._frames_written
