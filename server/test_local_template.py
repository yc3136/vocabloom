#!/usr/bin/env python3
"""
Template for local test script for Gemini API integration
Copy this file to test_local.py and add your API key
"""
import asyncio
import os
import sys
import httpx
import json

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from main import call_gemini_api

async def test_gemini_api():
    """Test the Gemini API integration locally"""
    
    # Set the API key for local testing
    # IMPORTANT: Replace with your actual API key or set as environment variable
    # For security, never commit API keys to version control
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ Error: GEMINI_API_KEY environment variable not set")
        print("Please set your Gemini API key as an environment variable:")
        print("export GEMINI_API_KEY='your-api-key-here'")
        return
    
    os.environ["GEMINI_API_KEY"] = api_key
    
    print("🧪 Testing Gemini API Integration...")
    print("=" * 50)
    
    # Test cases - testing different languages
    test_cases = [
        {"term": "hello", "language": "Spanish"},
        {"term": "computer", "language": "French"},
        {"term": "beautiful", "language": "Japanese"},
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: '{test_case['term']}' → {test_case['language']}")
        print("-" * 40)
        
        try:
            result = await call_gemini_api(test_case['term'], test_case['language'])
            
            print(f"✅ Translation: {result['translation']}")
            print(f"📚 Explanation: {result['explanation']}")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎉 Local testing completed!")

if __name__ == "__main__":
    asyncio.run(test_gemini_api()) 