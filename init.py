#!/usr/bin/env python3
"""
🚀 Mercor Search Engineering Setup Script
=========================================
Required setup script for initializing the candidate search system.

This script handles:
- Data loading from MongoDB
- Embedding generation using Voyage AI
- Search index creation (FAISS + BM25)
- Configuration validation
"""

import os
import sys
import argparse
import time
from typing import Dict, List
import json
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.utils.env_loader import load_environment
from src.utils.logger import get_logger
from src.services.embedding_service import EmbeddingService
from src.services.search_service import SearchService
from src.config.settings import config

logger = get_logger(__name__)

class MercorSetup:
    """
    Main setup class for initializing the Mercor search system.
    """
    
    def __init__(self):
        self.start_time = time.time()
        self.embedding_service = None
        self.search_service = None
        
    def load_environment(self) -> bool:
        """
        Load and validate environment variables.
        
        Returns:
            bool: True if all required variables are present
        """
        try:
            logger.info("🔧 Loading environment configuration...")
            
            # Load environment variables
            env_vars = load_environment()
            
            required_vars = [
                'OPENAI_API_KEY',
                'VOYAGEAI_API_KEY', 
                'USER_EMAIL'
            ]
            
            missing_vars = [var for var in required_vars if not os.getenv(var)]
            
            if missing_vars:
                logger.error(f"❌ Missing required environment variables: {missing_vars}")
                logger.error("Please check your .env file configuration")
                return False
            
            logger.info(f"✅ Environment loaded successfully ({len(env_vars)} variables)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Environment loading failed: {e}")
            return False
    
    def verify_services(self) -> bool:
        """
        Verify that all external services are accessible.
        
        Returns:
            bool: True if all services are working
        """
        try:
            logger.info("🔍 Verifying external services...")
            
            # Test OpenAI connection
            try:
                from src.services.gpt_service import gpt_service
                test_response = gpt_service.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": "test"}],
                    max_tokens=5
                )
                logger.info("✅ OpenAI API connection verified")
            except Exception as e:
                logger.error(f"❌ OpenAI API connection failed: {e}")
                return False
            
            # Test Voyage AI connection
            try:
                self.embedding_service = EmbeddingService()
                test_embedding = self.embedding_service.generate_embedding("test query")
                if test_embedding and len(test_embedding) > 0:
                    logger.info("✅ Voyage AI embedding service verified")
                else:
                    raise Exception("Empty embedding returned")
            except Exception as e:
                logger.error(f"❌ Voyage AI connection failed: {e}")
                return False
            
            logger.info("✅ All services verified successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Service verification failed: {e}")
            return False
    
    def initialize_search_index(self, rebuild: bool = False) -> bool:
        """
        Initialize search indices and load candidate data.
        
        Args:
            rebuild: Force rebuild of indices from scratch
            
        Returns:
            bool: True if initialization successful
        """
        try:
            logger.info("🏗️ Initializing search indices...")
            
            # Initialize search service
            self.search_service = SearchService()
            
            if rebuild:
                logger.info("🔄 Rebuilding indices from scratch...")
                
            # Load candidate data and create indices
            start_time = time.time()
            
            # This will automatically handle:
            # - Loading candidates from MongoDB
            # - Generating embeddings if needed
            # - Creating FAISS vector index
            # - Building BM25 text index
            success = self.search_service._initialize_indices(force_rebuild=rebuild)
            
            if success:
                duration = time.time() - start_time
                logger.info(f"✅ Search indices initialized in {duration:.1f}s")
                return True
            else:
                logger.error("❌ Failed to initialize search indices")
                return False
                
        except Exception as e:
            logger.error(f"❌ Index initialization failed: {e}")
            return False
    
    def create_directory_structure(self) -> bool:
        """
        Create required directory structure.
        
        Returns:
            bool: True if directories created successfully
        """
        try:
            logger.info("📁 Creating directory structure...")
            
            directories = [
                'logs',
                'results', 
                'data/cache',
                'data/indices'
            ]
            
            for directory in directories:
                os.makedirs(directory, exist_ok=True)
                logger.debug(f"📂 Created directory: {directory}")
            
            logger.info("✅ Directory structure created")
            return True
            
        except Exception as e:
            logger.error(f"❌ Directory creation failed: {e}")
            return False
    
    def run_setup(self, rebuild_index: bool = False, verify_only: bool = False) -> bool:
        """
        Run complete setup process.
        
        Args:
            rebuild_index: Force rebuild of search indices
            verify_only: Only run verification, skip full setup
            
        Returns:
            bool: True if setup successful
        """
        logger.info("🚀 Starting Mercor Search Engine Setup")
        logger.info("=" * 50)
        
        try:
            # Step 1: Load environment
            if not self.load_environment():
                return False
            
            # Step 2: Create directories
            if not self.create_directory_structure():
                return False
            
            # Step 3: Verify services
            if not self.verify_services():
                return False
            
            # If verify-only mode, stop here
            if verify_only:
                logger.info("✅ Verification complete - all systems ready")
                return True
            
            # Step 4: Initialize search indices
            if not self.initialize_search_index(rebuild=rebuild_index):
                return False
            
            # Step 5: Final validation
            logger.info("🧪 Running final validation...")
            
            # Test a simple search to ensure everything works
            from src.models.candidate import SearchQuery, SearchStrategy
            test_query = SearchQuery(
                query_text="software engineer Python experience",
                job_category="test.yml",
                strategy=SearchStrategy.HYBRID
            )
            
            candidates = self.search_service.search_candidates(test_query)
            
            if candidates and len(candidates) > 0:
                logger.info(f"✅ System validation passed ({len(candidates)} test candidates found)")
            else:
                logger.warning("⚠️ System validation passed but no test candidates found")
            
            # Success!
            total_time = time.time() - self.start_time
            logger.info("=" * 50)
            logger.info(f"🎉 Setup completed successfully in {total_time:.1f}s")
            logger.info("🚀 System ready for candidate search and evaluation")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Setup failed: {e}")
            return False

def main():
    """Main entry point for setup script."""
    parser = argparse.ArgumentParser(
        description="Mercor Search Engine Setup Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python init.py                    # Standard setup
  python init.py --rebuild-index    # Force rebuild of search indices  
  python init.py --verify-only      # Test setup without full initialization
  python init.py --debug            # Enable verbose logging
        """
    )
    
    parser.add_argument(
        '--rebuild-index',
        action='store_true',
        help='Force rebuild of search indices from scratch'
    )
    
    parser.add_argument(
        '--verify-only', 
        action='store_true',
        help='Only verify setup without full initialization'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    
    args = parser.parse_args()
    
    # Configure logging level
    if args.debug:
        import logging
        logging.getLogger().setLevel(logging.DEBUG)
        logger.info("🐛 Debug logging enabled")
    
    # Run setup
    setup = MercorSetup()
    success = setup.run_setup(
        rebuild_index=args.rebuild_index,
        verify_only=args.verify_only
    )
    
    if success:
        print("\n✅ Setup completed successfully!")
        print("🚀 You can now run evaluations with: python src/main.py")
        sys.exit(0)
    else:
        print("\n❌ Setup failed!")
        print("📋 Check the logs above for details")
        sys.exit(1)

if __name__ == "__main__":
    main() 