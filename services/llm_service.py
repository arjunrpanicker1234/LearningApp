# import requests
# import json
# from config import Config

# class LLMService:
#     def __init__(self):
#         self.api_url = Config.LLM_API_URL
#         self.model = Config.LLM_MODEL
    
#     def generate_questions(self, skill_name, num_questions=5, difficulty=3):
#         prompt = f"""
#         Generate {num_questions} multiple-choice questions about {skill_name} at difficulty level {difficulty}/5.
#         Format the response as a JSON array with each question object having:
#         - question_text
#         - options (array of 4 choices)
#         - correct_answer (index of correct option)
#         - explanation
#         """
        
#         response = self._call_llm(prompt)
#         try:
#             # Parse the response to extract just the JSON part
#             json_str = self._extract_json(response)
#             questions = json.loads(json_str)
#             return questions
#         except Exception as e:
#             print(f"Error parsing LLM response: {e}")
#             return []
    
#     def assess_proficiency(self, skill_name, user_answers):
#         # Convert user answers to a string format
#         answers_str = "\n".join([f"Q{i+1}: {q['question']}\nUser Answer: {q['user_answer']}\nCorrect Answer: {q['correct_answer']}" 
#                               for i, q in enumerate(user_answers)])
        
#         prompt = f"""
#         The user has answered questions about {skill_name}.
        
#         {answers_str}
        
#         Based on these answers, assess the user's proficiency level on a scale of 1-5, where:
#         1 = Beginner
#         2 = Elementary
#         3 = Intermediate
#         4 = Advanced
#         5 = Expert
        
#         Provide a proficiency score and a brief explanation of your assessment.
#         Format your response as JSON with keys 'score' and 'explanation'.
#         """
        
#         response = self._call_llm(prompt)
#         try:
#             json_str = self._extract_json(response)
#             assessment = json.loads(json_str)
#             return assessment
#         except Exception as e:
#             print(f"Error parsing LLM assessment: {e}")
#             return {"score": 1, "explanation": "Unable to assess accurately"}
    
#     def recommend_resources(self, skill_name, proficiency_level, available_resources):
#         resources_str = "\n".join([f"- {r.title} (Level: {r.proficiency_level})" for r in available_resources])
        
#         prompt = f"""
#         The user has a proficiency level of {proficiency_level}/5 in {skill_name}.
        
#         Available resources:
#         {resources_str}
        
#         Recommend up to 3 resources that would help the user improve their skills.
#         Focus on resources that match their current level or are slightly above.
#         Format the response as a JSON array with resource IDs.
#         """
        
#         response = self._call_llm(prompt)
#         try:
#             json_str = self._extract_json(response)
#             recommendations = json.loads(json_str)
#             return recommendations
#         except Exception as e:
#             print(f"Error parsing LLM recommendations: {e}")
#             return []
    
#     def answer_question(self, skill_name, user_question, context=""):
#         prompt = f"""
#         The user is learning about {skill_name} and has asked the following question:
        
#         "{user_question}"
        
#         Additional context from learning materials:
#         {context}
        
#         Provide a helpful, accurate, and concise answer.
#         """
        
#         response = self._call_llm(prompt)
#         return response
    
#     def _call_llm(self, prompt):
#         payload = {
#             "llama3.2:3b": self.model,
#             "prompt": prompt,
#             "stream": False
#         }
#         # payload =  {
#         # "model": "llama3.2:3b",
#         # "messages": [
#         # {
#         # "role": "user",
#         # "content": prompt
#         # }
#         # ],
#         # "stream": False
#         # }
        
#         response = requests.post(self.api_url, json=payload)
#         print('res=',response)
#         if response.status_code == 200:
#             print('res=',response)
#             return response.json()['response']
#         else:
#             raise Exception(f"LLM API error: {response.status_code}")
    
#     def _extract_json(self, text):
#         # Find JSON content between brackets
#         start = text.find('{')
#         end = text.rfind('}') + 1
#         if start >= 0 and end > start:
#             return text[start:end]
        
#         # Try for JSON arrays
#         start = text.find('[')
#         end = text.rfind(']') + 1
#         if start >= 0 and end > start:
#             return text[start:end]
            
#         return "{}"
########2nd version#######
import requests
import json
from config import Config
from services.logging_service import LLMLogger
from services.error_handler import handle_llm_error
from services.cache_service import LLMCache
from services.fallback_service import FallbackService

class LLMService:
    def __init__(self):
        self.api_url = Config.LLM_API_URL
        self.model = Config.LLM_MODEL
        self.max_tokens = Config.LLM_MAX_TOKENS
        self.temperature = Config.LLM_TEMPERATURE
        self.logger = LLMLogger()
        self.cache = LLMCache()
        self.fallback = FallbackService()
    
    @handle_llm_error
    def generate_questions(self, skill_name, num_questions=5, difficulty=3):
        prompt = f"""
        Generate {num_questions} multiple-choice questions about {skill_name} at difficulty level {difficulty}/5.
    
    You MUST format your response as a valid JSON array, with no additional text before or after.
    Each question object in the array must have these exact fields:
    - "question_text": the question being asked
    - "options": an array of 4 possible answer choices
    - "correct_answer": the index (0-3) of the correct option
    - "explanation": explanation of the correct answer
    
    Example format:
    [
      {{
        "question_text": "Sample question?",
        "options": ["Option A", "Option B", "Option C", "Option D"],
        "correct_answer": 1,
        "explanation": "Option B is correct because..."
      }}
    ]
    """
        
        self.logger.log_request("generate_questions", prompt)
        response = self._call_llm(prompt)
        
        try:
            json_str = self._extract_json(response)
            questions = json.loads(json_str)
            self.logger.log_response("generate_questions", json.dumps(questions))
            return questions
        except Exception as e:
            self.logger.log_error("generate_questions", f"JSON parsing error: {str(e)}")
            return self.fallback.get_default_questions(skill_name)[:num_questions]
    
    def assess_proficiency(self, skill_name, user_answers):
        # Convert user answers to a string format
        answers_str = "\n".join([f"Q{i+1}: {q['question']}\nUser Answer: {q['user_answer']}\nCorrect Answer: {q['correct_answer']}" 
                              for i, q in enumerate(user_answers)])
        
        prompt = f"""
        The user has answered questions about {skill_name}.
        
        {answers_str}
        
        Based on these answers, assess the user's proficiency level on a scale of 1-5, where:
        1 = Beginner
        2 = Elementary
        3 = Intermediate
        4 = Advanced
        5 = Expert
        
        Provide a proficiency score and a brief explanation of your assessment.
        Format your response as JSON with keys 'score' and 'explanation'.
        """
        
        response = self._call_llm(prompt)
        try:
            json_str = self._extract_json(response)
            assessment = json.loads(json_str)
            return assessment
        except Exception as e:
            print(f"Error parsing LLM assessment: {e}")
            return {"score": 1, "explanation": "Unable to assess accurately"}
    
    def recommend_resources(self, skill_name, proficiency_level, available_resources):
        resources_str = "\n".join([f"- {r.title} (Level: {r.proficiency_level})" for r in available_resources])
        
        prompt = f"""
        The user has a proficiency level of {proficiency_level}/5 in {skill_name}.
        
        Available resources:
        {resources_str}
        
        Recommend up to 3 resources that would help the user improve their skills.
        Focus on resources that match their current level or are slightly above.
        Format the response as a JSON array with resource IDs.
        """
        
        response = self._call_llm(prompt)
        try:
            json_str = self._extract_json(response)
            recommendations = json.loads(json_str)
            return recommendations
        except Exception as e:
            print(f"Error parsing LLM recommendations: {e}")
            return []
    
    def answer_question(self, skill_name, user_question, context=""):
        prompt = f"""
        The user is learning about {skill_name} and has asked the following question:
        
        "{user_question}"
        
        Additional context from learning materials:
        {context}
        
        Provide a helpful, accurate, and concise answer.
        """
        
        response = self._call_llm(prompt)
        return response
    
    def _call_llm(self, prompt):
        """
        Make API call to Llama model with caching
        """
        # Try to get from cache first
        cached_response = self.cache.get(prompt, self.model)
        if cached_response:
            return cached_response
        
        # If not in cache, make the API call
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        
        try:
            response = requests.post(self.api_url, json=payload, timeout=120)
            
            if response.status_code == 200:
                result = response.json()['response']
                # Cache the result
                self.cache.set(prompt, self.model, result)
                return result
            else:
                error_msg = f"API Error: Status {response.status_code}, Response: {response.text}"
                self.logger.log_error("_call_llm", error_msg)
                raise Exception(error_msg)
        except requests.exceptions.RequestException as e:
            self.logger.log_error("_call_llm", f"Request failed: {str(e)}")
            raise
    
    def _extract_json(self, text):
        """
        Extract JSON from the LLM response text
        This improved method handles various cases where JSON might be embedded in text
        """
        # First, try to find JSON between triple backticks (common in LLM responses)
        import re
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
        if json_match:
            json_content = json_match.group(1).strip()
            # Try parsing this content before proceeding
            try:
                return json_content
            except:
                pass  # Continue to other methods if this fails
        
        # Look for JSON array
        array_match = re.search(r'\[\s*{.*}\s*\]', text, re.DOTALL)
        if array_match:
            return array_match.group(0)
        
        # Look for JSON object
        object_match = re.search(r'{.*}', text, re.DOTALL)
        if object_match:
            return object_match.group(0)
        
        # If we can't find structured JSON, return the original text
        # This will likely cause a JSON parsing error, but that will be caught
        # by the error handler
        return text


#######3rd version #####
# Updated services/llm_service.py

# import requests
# import json
# from config import Config
# from services.logging_service import LLMLogger
# from services.error_handler import handle_llm_error

# class LLMService:
#     def __init__(self):
#         self.api_url = Config.LLM_API_URL
#         self.model = Config.LLM_MODEL
#         self.max_tokens = Config.LLM_MAX_TOKENS
#         self.temperature = Config.LLM_TEMPERATURE
#         self.logger = LLMLogger()
    
#     @handle_llm_error
#     def generate_questions(self, skill_name, num_questions=5, difficulty=3):
#         prompt = f"""
#         Generate {num_questions} multiple-choice questions about {skill_name} at difficulty level {difficulty}/5.
#         Format the response as a JSON array with each question object having:
#         - question_text
#         - options (array of 4 choices)
#         - correct_answer (index of correct option)
#         - explanation
#         """
        
#         self.logger.log_request("generate_questions", prompt)
#         response = self._call_llm(prompt)
        
#         try:
#             json_str = self._extract_json(response)
#             questions = json.loads(json_str)
#             self.logger.log_response("generate_questions", json.dumps(questions))
#             return questions
#         except Exception as e:
#             self.logger.log_error("generate_questions", f"JSON parsing error: {str(e)}")
#             raise
    
#     # Similar updates for other methods...
    
#     def _call_llm(self, prompt):
#         """
#         Make API call to Llama model using the specified format
#         """
#         payload = {
#             "model": self.model,
#             "prompt": prompt,
#             "stream": False
#         }
        
#         try:
#             response = requests.post(self.api_url, json=payload, timeout=60)
            
#             if response.status_code == 200:
#                 return response.json()['response']
#             else:
#                 error_msg = f"API Error: Status {response.status_code}, Response: {response.text}"
#                 self.logger.log_error("_call_llm", error_msg)
#                 raise Exception(error_msg)
#         except requests.exceptions.RequestException as e:
#             self.logger.log_error("_call_llm", f"Request failed: {str(e)}")
#             raise