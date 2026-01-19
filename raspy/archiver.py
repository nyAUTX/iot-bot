import os
import shutil
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class Archiver:
    """Handle archiving of files with timestamps."""
    
    @staticmethod
    def archive_file(source_file, archive_dir):
        """
        Archive a file with timestamp.
        
        Args:
            source_file: Path to the file to archive
            archive_dir: Directory to archive to
        """
        if not Path(source_file).exists():
            logger.warning(f"File not found: {source_file}")
            return None
        
        Path(archive_dir).mkdir(parents=True, exist_ok=True)
        
        # Get file extension
        file_ext = Path(source_file).suffix
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        archived_name = f"{Path(source_file).stem}_{timestamp}{file_ext}"
        archived_path = os.path.join(archive_dir, archived_name)
        
        try:
            shutil.copy2(source_file, archived_path)
            logger.info(f"File archived: {source_file} -> {archived_path}")
            return archived_path
        except Exception as e:
            logger.error(f"Error archiving file: {e}")
            return None
