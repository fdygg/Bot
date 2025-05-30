from api.service.settings_service import SettingsService
from api.service.logs_service import LogsService
import gzip
import zlib

class CompressionService:
    def __init__(self):
        self.settings = SettingsService()
        self.logger = LogsService()
        
        # Compression settings
        self.min_size = 1024  # 1KB
        self.compression_level = 6  # 0-9
        
    def should_compress(self, response):
        """Check if response should be compressed"""
        # Check content type
        content_type = response.headers.get('Content-Type', '')
        compressible_types = [
            'text/', 
            'application/json',
            'application/javascript',
            'application/xml'
        ]
        
        is_compressible = any(t in content_type for t in compressible_types)
        content_length = len(response.content)
        
        return is_compressible and content_length > self.min_size
        
    def compress_response(self, response):
        """Compress response content"""
        try:
            if not self.should_compress(response):
                return response
                
            compressed_content = gzip.compress(
                response.content,
                compresslevel=self.compression_level
            )
            
            response.content = compressed_content
            response.headers['Content-Encoding'] = 'gzip'
            response.headers['Content-Length'] = str(len(compressed_content))
            
            return response
            
        except Exception as e:
            self.logger.error(f"Compression failed: {str(e)}")
            return response