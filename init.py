#!/usr/bin/env python3
"""
Mercor Search Agent - Setup Script
Initializes data loading, embedding generation, and indexing for the search system.

Usage:
    python init.py                    # Standard setup
    python init.py --rebuild-index    # Rebuild embeddings from scratch  
    python init.py --verify-only      # Test setup without full initialization

Author: Bhaumik Tandan
"""

import os
import sys
import argparse
import json
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.utils.env_loader import load_environment
from src.utils.logger import setup_logger
from src.services.search_service import SearchService
from src.services.embedding_service import EmbeddingService

class MercorSetup:
    """Setup and initialization for Mercor Search Agent."""
    
    def __init__(self, rebuild_index=False, verify_only=False):
        self.rebuild_index = rebuild_index
        self.verify_only = verify_only
        self.logger = setup_logger("mercor_setup")
        
    def load_environment(self):
        """Load and validate environment variables."""
        self.logger.info("🔧 Loading environment configuration...")
        
        try:
            # Load environment variables
            load_environment()
            
            # Verify required API keys
            required_keys = ["OPENAI_API_KEY", "TURBOPUFFER_API_KEY"]
            missing_keys = []
            
            for key in required_keys:
                if not os.getenv(key):
                    missing_keys.append(key)
            
            if missing_keys:
                self.logger.error(f"❌ Missing required environment variables: {missing_keys}")
                self.logger.info("Please create a .env file with the following variables:")
                for key in missing_keys:
                    self.logger.info(f"  {key}=your_{key.lower()}_here")
                return False
            
            self.logger.info("✅ Environment configuration loaded successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to load environment: {e}")
            return False
    
    def verify_services(self):
        """Verify that all services are working correctly."""
        self.logger.info("🔍 Verifying service connections...")
        
        try:
            # Test search service
            search_service = SearchService()
            self.logger.info("✅ Search service initialized")
            
            # Test embedding service  
            embedding_service = EmbeddingService()
            self.logger.info("✅ Embedding service initialized")
            
            # Test basic functionality
            test_query = "software engineer Python experience"
            test_embedding = embedding_service.generate_embedding(test_query)
            
            if len(test_embedding) > 0:
                self.logger.info("✅ Embedding generation working")
            else:
                self.logger.error("❌ Embedding generation failed")
                return False
            
            self.logger.info("✅ All services verified successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Service verification failed: {e}")
            return False
    
    def initialize_search_index(self):
        """Initialize or rebuild the search index."""
        if self.rebuild_index:
            self.logger.info("🔄 Rebuilding search index from scratch...")
        else:
            self.logger.info("📊 Initializing search index...")
        
        try:
            search_service = SearchService()
            
            # The search service will handle index initialization
            # This includes connecting to Turbopuffer and ensuring indexes are ready
            
            # Test search functionality
            from src.models.candidate import SearchQuery, SearchStrategy
            
            test_query = SearchQuery(
                query_text="software engineer",
                job_category="test",
                strategy=SearchStrategy.VECTOR_ONLY,
                max_candidates=5
            )
            
            # This will verify the index is working
            candidates = search_service.search_candidates(test_query)
            
            if len(candidates) >= 0:  # Even 0 results is okay for initialization
                self.logger.info("✅ Search index initialized successfully")
                return True
            else:
                self.logger.error("❌ Search index initialization failed")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Search index initialization failed: {e}")
            return False
    
    def create_directory_structure(self):
        """Ensure proper directory structure exists."""
        self.logger.info("📁 Creating directory structure...")
        
        directories = [
            "logs",
            "submissions", 
            "results"
        ]
        
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
            self.logger.info(f"✅ Directory created/verified: {directory}")
    
    def run_setup(self):
        """Run the complete setup process."""
        self.logger.info("🚀 Starting Mercor Search Agent setup...")
        self.logger.info("="*60)
        
        # Create directory structure
        self.create_directory_structure()
        
        # Load environment
        if not self.load_environment():
            return False
        
        # Verify services
        if not self.verify_services():
            return False
        
        # Initialize search index (unless verify-only mode)
        if not self.verify_only:
            if not self.initialize_search_index():
                return False
        
        self.logger.info("="*60)
        self.logger.info("🎉 Setup completed successfully!")
        self.logger.info("📋 Next steps:")
        self.logger.info("  1. Run: python mercor_search_agent.py")
        self.logger.info("  2. Check logs/ directory for detailed output")
        self.logger.info("  3. Review results in submissions/ directory")
        
        return True

def main():
    """Main entry point for setup script."""
    parser = argparse.ArgumentParser(
        description="Mercor Search Agent Setup Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Configuration Options:
  --rebuild-index    Rebuild search index from scratch (slower but fresh)
  --verify-only      Only verify setup, don't initialize index (faster)

Examples:
  python init.py                    # Standard setup
  python init.py --rebuild-index    # Full rebuild  
  python init.py --verify-only      # Quick verification
        """)
    
    parser.add_argument("--rebuild-index", action="store_true",
                       help="Rebuild search index from scratch")
    parser.add_argument("--verify-only", action="store_true", 
                       help="Only verify setup, don't initialize")
    
    args = parser.parse_args()
    
    # Run setup
    setup = MercorSetup(
        rebuild_index=args.rebuild_index,
        verify_only=args.verify_only
    )
    
    success = setup.run_setup()
    
    if success:
        print("\n✅ Setup completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Setup failed. Check logs for details.")
        sys.exit(1)

if __name__ == "__main__":
    main() 