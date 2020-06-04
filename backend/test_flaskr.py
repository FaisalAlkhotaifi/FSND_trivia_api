import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category

class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {
            'question': 'What is the best e-education platform?',
            'answer': 'Udacity',
            'difficulty': '1',
            'category': '1'
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass
    
    # ------------------- #
    ### HELPER METHODS ###
    # -------------------#

    def assertNotEmpty(self, object):
        self.assertTrue(object)

    def assertSuccess(self, data, statusCode):
        self.assertEqual(statusCode, 200)
        self.assertEqual(data['success'], True)

    def assert404request(self, data, statusCode):
        self.assertEqual(statusCode, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')
    
    def assert405request(self, data, statusCode):
        self.assertEqual(statusCode, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'not allowed method')

    def assert422request(self, data, statusCode):
        self.assertEqual(statusCode, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    # ------------------------------- #
    ### TEST GET CATEGORIES REQUEST ###
    # --------------------------------#

    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertSuccess(data, res.status_code)
        self.assertNotEmpty(len(data['categories']))

    # ------------------------------ #
    ### TEST GET QUESTIONS REQUEST ###
    # -------------------------------#

    def test_get_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertSuccess(data, res.status_code)
        self.assertNotEmpty(len(data['questions']))
        self.assertNotEmpty(data['totalQuestions'])
        self.assertNotEmpty(data['categories'])

    def test_get_paginated_questions(self):
        res = self.client().get('/questions?page=1')
        data = json.loads(res.data)

        self.assertSuccess(data, res.status_code)
        self.assertNotEmpty(len(data['questions']))
        self.assertNotEmpty(data['totalQuestions'])
        self.assertNotEmpty(data['categories'])

    def test_404_get_paginated_questions_beyond_valid_page(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assert404request(data, res.status_code)

    # ---------------------------------- #
    ### TEST DELELTE QUESTIONS REQUEST ###
    # -----------------------------------#

    def test_delete_question(self):
        last_question = Question.query.order_by(Question.id.desc()).first()

        if last_question is None:
            res = self.client().delete(f'/questions/{last_question.id}')
            data = json.loads(res.data)

            question = Question.query.filter(Question.id == last_question.id).one_or_none()

            self.assertSuccess(data, res.status_code)
            self.assertEqual(data['deleted_id'], last_question.id)
            self.assertNotEmpty(len(data['questions']))
            self.assertNotEmpty(data['totalQuestions'])
            self.assertEqual(question, None)
        else:
            pass


    def test_422_delete_not_exist_question(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)

        self.assert422request(data, res.status_code)

    # ------------------------------- #
    ### TEST POST QUESTIONS REQUEST ###
    # ------------------------------- #

    def test_create_new_question(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        self.assertSuccess(data, res.status_code)
        self.assertNotEmpty(len(data['questions']))
        self.assertNotEmpty(data['totalQuestions'])
        self.assertNotEmpty(data['categories'])

    def test_422_if_create_new_question_has_no_body(self):
        res = self.client().post('/questions')
        data = json.loads(res.data)

        self.assert422request(data, res.status_code)

    def test_422_if_create_new_question_has_empty_body(self):
        res = self.client().post('/questions', json={})
        data = json.loads(res.data)

        self.assert422request(data, res.status_code)
    
    def test_search_question(self):
        res = self.client().post('/questions', json={'searchTerm': 'What'})
        data = json.loads(res.data)

        self.assertSuccess(data, res.status_code)
        self.assertNotEmpty(len(data['questions']))
        self.assertNotEmpty(data['totalQuestions'])

    def test_422_if_fail_search_question(self):
        res = self.client().post('/questions', json={'searchTerm': 'emptyQuestion'})
        data = json.loads(res.data)

        self.assert422request(data, res.status_code)

    # ------------------------------------------ #
    ### TEST GET QUESTIONS BY CATEGORY REQUEST ###
    # ------------------------------------------ #

    def test_get_questions_by_category(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertSuccess(data, res.status_code)
        self.assertNotEmpty(len(data['questions']))
        self.assertNotEmpty(data['total_questions'])
        self.assertNotEmpty(data['currentCategory']) 

    def test_404_not_exist_category(self):
        res = self.client().get('/categories/100/questions')
        data = json.loads(res.data)

        self.assert404request(data, res.status_code)

    # ---------------------------- #
    ### TEST GET QUIZZED REQUEST ###
    # ---------------------------- #

    def test_get_questions_by_category_with_no_previous_question(self):
        res = self.client().post('/quizzes', json={'previous_questions': [], 'quiz_category': {'type': 'Science', 'id': '1'}})
        data = json.loads(res.data)

        self.assertSuccess(data, res.status_code)
        self.assertNotEmpty(data['question'])

    def test_get_questions_by_category_with_previous_question(self):
        res = self.client().post('/quizzes', json={'previous_questions': [20], 'quiz_category': {'type': 'Science', 'id': '1'}})
        data = json.loads(res.data)

        self.assertSuccess(data, res.status_code)
        self.assertNotEmpty(data['question'])


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()