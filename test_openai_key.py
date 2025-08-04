#!/usr/bin/env python3
"""
Test OpenAI API Key
==================

Simple script to validate the OpenAI API key in .env file.
"""

import os
import sys
import requests
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.utils.env_loader import env_loader

def test_openai_key():
    """Test the OpenAI API key with a simple request."""
    print("🔍 Testing OpenAI API Key...")
    
    # Load the API key
    api_key = env_loader.get('OPENAI_API_KEY', '')
    
    if not api_key:
        print("❌ No OpenAI API key found in .env file")
        return False
    
    print(f"✅ API Key loaded (length: {len(api_key)} characters)")
    print(f"🔑 Key starts with: {api_key[:20]}...")
    
    # Test with OpenAI API
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Simple test payload with gpt-4.1-nano
    data = {
        "model": "gpt-4.1-nano",
        "messages": [
            {"role": "user", "content": "Hello! This is a test message. Please respond with 'API key is working correctly.'"}
        ],
        "max_tokens": 50
    }
    
    try:
        print("🌐 Making test request to OpenAI API...")
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            message = result['choices'][0]['message']['content']
            print(f"✅ API Key is working correctly!")
            print(f"📝 Response: {message}")
            return True
        else:
            print(f"❌ API request failed with status code: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
            # Try to get available models
            print("\n🔍 Checking available models...")
            models_response = requests.get(
                "https://api.openai.com/v1/models",
                headers=headers,
                timeout=30
            )
            
            if models_response.status_code == 200:
                models = models_response.json()
                available_models = [model['id'] for model in models['data'] if 'gpt' in model['id'].lower()]
                print(f"✅ Available GPT models: {available_models[:5]}...")
            else:
                print(f"❌ Could not fetch available models: {models_response.status_code}")
            
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Main function."""
    print("🚀 OpenAI API Key Validation Test")
    print("=" * 50)
    
    success = test_openai_key()
    
    if success:
        print("\n🎉 OpenAI API key is valid and working!")
    else:
        print("\n💥 OpenAI API key validation failed!")
    
    return success

if __name__ == "__main__":
    main() 