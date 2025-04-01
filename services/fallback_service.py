# Create a new file: services/fallback_service.py

class FallbackService:
    """
    Provides hard-coded fallback responses when the LLM is unavailable
    """
    
    def get_default_questions(self, skill_name):
        """Return default questions for a skill"""
        if skill_name.lower() == "python":
            return [
                {
                    "question_text": "What is Python?",
                    "options": ["A snake", "A high-level programming language", "A database system", "A web framework"],
                    "correct_answer": 1,
                    "explanation": "Python is a high-level, interpreted programming language."
                },
                {
                    "question_text": "Which of the following is not a Python data type?",
                    "options": ["List", "String", "Integer", "Struct"],
                    "correct_answer": 3,
                    "explanation": "Struct is not a built-in Python data type. Python has built-in data types like List, String, Integer, etc."
                }
                # Add more questions as needed
            ]
        # Add more skills and their questions
        
        # Generic fallback
        return [
            {
                "question_text": f"What is {skill_name}?",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "correct_answer": 1,
                "explanation": f"{skill_name} is a subject that can be learned."
            }
        ]
    
    def get_default_assessment(self):
        """Return default assessment when LLM fails"""
        return {
            "score": 1,
            "explanation": "We couldn't fully assess your knowledge due to technical issues. This is a preliminary score."
        }
    
    def get_default_answer(self, question):
        """Return default answer to user question"""
        return f"I'm sorry, I couldn't generate a specific answer to your question about '{question}' due to technical limitations. Please try a different question or check back later."