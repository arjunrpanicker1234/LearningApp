# Create a new file: services/error_handler.py

class LLMServiceError(Exception):
    """Exception raised for LLM service errors"""
    pass

def handle_llm_error(func):
    """Decorator to handle LLM service errors"""
    def wrapper(*args, **kwargs):
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                retry_count += 1
                print(f"LLM service error (attempt {retry_count}): {e}")
                
                if retry_count >= max_retries:
                    # Fallback behavior
                    if func.__name__ == 'generate_questions':
                        return [{"question_text": "What is Python?", 
                                 "options": ["A snake", "A programming language", "A game", "A food"],
                                 "correct_answer": 1,
                                 "explanation": "Python is a high-level programming language."}]
                    elif func.__name__ == 'assess_proficiency':
                        return {"score": 1, "explanation": "Unable to assess due to service error"}
                    elif func.__name__ == 'recommend_resources':
                        return []
                    elif func.__name__ == 'answer_question':
                        return "I'm sorry, I couldn't process your question due to a technical issue. Please try again later."
                    else:
                        return None
        
    return wrapper