# Create a new file: services/logging_service.py

import logging
import os
import json
from datetime import datetime

class LLMLogger:
    def __init__(self, log_dir="logs"):
        # Create logs directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)
        
        # Configure logger
        self.logger = logging.getLogger("llm_service")
        self.logger.setLevel(logging.INFO)
        
        # Log file handler
        log_file = os.path.join(log_dir, f"llm_api_{datetime.now().strftime('%Y%m%d')}.log")
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # Format
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        # Add handler to logger
        self.logger.addHandler(file_handler)
    
    def log_request(self, function_name, prompt, params=None):
        self.logger.info(f"LLM Request - Function: {function_name}")
        self.logger.info(f"Prompt: {prompt[:100]}...")  # Log first 100 chars of prompt
        if params:
            self.logger.info(f"Params: {json.dumps(params)}")
    
    def log_response(self, function_name, response, success=True):
        status = "Success" if success else "Failure"
        self.logger.info(f"LLM Response - Function: {function_name} - Status: {status}")
        if success:
            self.logger.info(f"Response: {response[:100]}...")  # Log first 100 chars of response
        else:
            self.logger.error(f"Error: {response}")
    
    def log_error(self, function_name, error_message):
        self.logger.error(f"LLM Error - Function: {function_name} - Error: {error_message}")