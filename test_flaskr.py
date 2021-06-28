import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import false

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_user = os.getenv('DB_USER', "student")
        self.database_password = os.getenv('DB_PASSWORD', "student")
        self.database_host = os.getenv('DB_HOST', "127.0.0.1:5432")
        self.database_name = os.getenv('DB_NAME', "trivia_test")
        self.database_path = "postgresql://{}:{}@{}/{}".format(self.database_user, self.database_password, self.database_host, self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_questions(self):
        """Test to check if the endpoint gets all questions"""
        response = self.client().get('/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['categories'])
        self.assertTrue(data['current_category'])
        self.assertTrue(data['questions'])
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])

    def test_get_questions_404(self):
        """Test to check if the endpoint shows 404 error when accessing pages that dont exist"""
        response = self.client().get('/questions?page=1000')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['message'], 'resource not found')
        self.assertEqual(data['success'], False)

    def test_get_specific_question(self):
        """Test to check if the endpoint returns 405 when accessing a specific question"""
        response = self.client().get('/questions/1')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 405)
        self.assertEqual(data['message'], 'method not allowed')
        self.assertEqual(data['success'], False)

    def test_get_categories(self):
        """Test to check if the endpoint gets all categories"""
        response = self.client().get('/categories')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['categories'])
        self.assertEqual(data['success'], True)

    def test_get_categories_404(self):
        """Test to check if the endpoint shows 404 error when accessing categories that dont exist"""
        response = self.client().get('/categories/9999')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['message'], 'resource not found')
        self.assertEqual(data['success'], False)

    def test_delete_question(self):
        """Test to check if the endpoint deletes the question and returns a success message"""
        question = Question(question='Am i getting deleted?', answer='Yes, You are.', difficulty=5, category=1)
        question.insert()
        question_id = question.id

        response = self.client().delete(f'/questions/{question_id}')
        data = json.loads(response.data)

        question = Question.query.filter(Question.id == question_id).one_or_none()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['deleted'], str(question_id))
        self.assertEqual(data['success'], True)

    def test_delete_question_422(self):
        """Test to check if the endpoint returns 422 for performing delete on question that is not found"""
        response = self.client().delete('/questions/a')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['message'], 'unprocessable')
        self.assertEqual(data['success'], False)

    def test_create_question(self):
        """Test to check if the endpoint allows to create a new question"""
        question = {
            'question': 'Can I stay?',
            'answer': 'Ok. We wont delete you.',
            'difficulty': 1,
            'category': 1
        }
        response = self.client().post('/questions', json=question)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_create_question_400(self):
        """Test to check if the endpoint returns 400 on create request with formatting mistake"""
        question = {
            'question': 'Can I join?',
            'answer': 'No',
            'difficulty': 1,
        }
        response = self.client().post('/questions', json=question)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["message"], "bad request")
        self.assertEqual(data["success"], False)

    def test_search_questions(self):
        """Test to check if the endpoint returns a collection of questions with matching search term"""
        new_search = {'searchTerm': '?'}
        response = self.client().post('/questions/search', json=new_search)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])

    def test_get_category_questions(self):
        """Test to check if the endpoint returns a specific category of questions"""
        response = self.client().get('/categories/1/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['current_category'])
        self.assertTrue(data['questions'])
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])

    def test_get_category_questions_404(self):
        """Test to check if the endpoint returns 404 on an unknown category"""
        response = self.client().get('/categories/a/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["message"], "resource not found")
        self.assertEqual(data["success"], False)

    def test_get_question(self):
        """Test to check if the endpoint returns a question that is related to the category and was not previous returned"""
        quiz = {
            'previous_questions': [],
            'quiz_category': {
                'type': 'Science',
                'id': 1
            }}
        response = self.client().post('/quizzes', json=quiz)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_get_question_404(self):
        """Test to check if the endpoint returns 422 on wrongly formatted request"""
        quiz = {
            'previous_questions': []
        }
        response = self.client().post('/quizzes', json=quiz)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data["message"], "unprocessable")
        self.assertEqual(data["success"], False)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()