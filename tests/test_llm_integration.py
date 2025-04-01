# Create a new file: tests/test_llm_integration.py

import sys
import os
import unittest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.llm_service import LLMService

class TestLLMIntegration(unittest.TestCase):
    
    def setUp(self):
        self.llm = LLMService()
    
    def test_question_generation(self):
        """Test question generation for Python skill"""
        questions = self.llm.generate_questions("Python", num_questions=2)
        
        self.assertIsInstance(questions, list)
        self.assertTrue(len(questions) > 0)
        
        for q in questions:
            self.assertIn('question_text', q)
            self.assertIn('options', q)
            self.assertIn('correct_answer', q)
    
    def test_proficiency_assessment(self):
        """Test proficiency assessment"""
        user_answers = [
            {"question": "What is Python?", "user_answer": "A programming language", "correct_answer": "A programming language"},
            {"question": "What is a list in Python?", "user_answer": "A mutable sequence", "correct_answer": "A mutable sequence"}
        ]
        
        assessment = self.llm.assess_proficiency("Python", user_answers)
        
        self.assertIsInstance(assessment, dict)
        self.assertIn('score', assessment)
        self.assertIn('explanation', assessment)
        self.assertTrue(1 <= assessment['score'] <= 5)
    
    def test_answer_question(self):
        """Test Q&A functionality"""
        response = self.llm.answer_question("Python", "What is a variable in Python?")
        
        self.assertIsInstance(response, str)
        self.assertTrue(len(response) > 0)

if __name__ == '__main__':
    unittest.main()