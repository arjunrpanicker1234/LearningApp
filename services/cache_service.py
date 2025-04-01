# Create a new file: services/cache_service.py

import json
import hashlib
import os
import time
from datetime import datetime, timedelta

class LLMCache:
    def __init__(self, cache_dir="cache", ttl=3600):  # 1 hour TTL by default
        self.cache_dir = cache_dir
        self.ttl = ttl
        os.makedirs(cache_dir, exist_ok=True)
    
    def _get_cache_key(self, prompt, model):
        """Generate a cache key based on prompt and model"""
        hash_input = f"{prompt}_{model}"
        return hashlib.md5(hash_input.encode()).hexdigest()
    
    def _get_cache_path(self, key):
        """Get the file path for a cache key"""
        return os.path.join(self.cache_dir, f"{key}.json")
    
    def get(self, prompt, model):
        """Get cached response if available and not expired"""
        key = self._get_cache_key(prompt, model)
        path = self._get_cache_path(key)
        
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    data = json.load(f)
                
                # Check if cache is expired
                cache_time = datetime.fromisoformat(data['timestamp'])
                if datetime.now() - cache_time < timedelta(seconds=self.ttl):
                    return data['response']
            except Exception as e:
                print(f"Cache error: {e}")
        
        return None
    
    def set(self, prompt, model, response):
        """Cache a response"""
        key = self._get_cache_key(prompt, model)
        path = self._get_cache_path(key)
        
        try:
            with open(path, 'w') as f:
                json.dump({
                    'response': response,
                    'timestamp': datetime.now().isoformat(),
                    'prompt': prompt[:100] + "..." if len(prompt) > 100 else prompt,
                    'model': model
                }, f)
            return True
        except Exception as e:
            print(f"Cache write error: {e}")
            return False