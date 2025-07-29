"""
Reliable .env File Loader
========================

Always reads directly from .env file instead of environment variables
to avoid corruption and ensure consistency.
"""

import os
from typing import Dict, Optional


class EnvLoader:
    """Reliable .env file loader that bypasses environment variables."""
    
    def __init__(self, env_file_path: str = ".env"):
        """Initialize with path to .env file."""
        self.env_file_path = env_file_path
        self._env_vars = {}
        self.load_env_file()
    
    def load_env_file(self) -> None:
        """Load environment variables directly from .env file."""
        try:
            if not os.path.exists(self.env_file_path):
                print(f"Warning: .env file not found at {self.env_file_path}")
                return
            
            with open(self.env_file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    
                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue
                    
                    # Parse key=value pairs
                    if '=' in line:
                        try:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip()
                            
                            # Remove quotes if present
                            if value.startswith('"') and value.endswith('"'):
                                value = value[1:-1]
                            elif value.startswith("'") and value.endswith("'"):
                                value = value[1:-1]
                            
                            self._env_vars[key] = value
                            
                        except ValueError:
                            print(f"Warning: Invalid line {line_num} in .env file: {line}")
            
            print(f"✅ Loaded {len(self._env_vars)} variables from {self.env_file_path}")
            
        except Exception as e:
            print(f"Error loading .env file: {e}")
    
    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get environment variable directly from .env file."""
        value = self._env_vars.get(key, default)
        
        # Additional validation for API keys
        if key == 'OPENAI_API_KEY' and value:
            # Clean any potential corruption
            value = value.strip()
            
            # Remove common corruptions
            corruptions = ['export', 'OPENAI_API_KEY=']
            for corruption in corruptions:
                if value.endswith(corruption):
                    value = value[:-len(corruption)]
            
            # Validate format
            if not value.startswith('sk-'):
                print(f"Warning: {key} doesn't start with 'sk-'")
            
            print(f"✅ {key}: Loaded from .env (length: {len(value)} chars)")
        
        return value
    
    def get_all(self) -> Dict[str, str]:
        """Get all environment variables."""
        return self._env_vars.copy()
    
    def reload(self) -> None:
        """Reload .env file."""
        self._env_vars.clear()
        self.load_env_file()


# Global instance
env_loader = EnvLoader() 