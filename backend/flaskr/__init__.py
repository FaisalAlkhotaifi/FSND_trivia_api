import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_question(request, selection):
  page = request.args.get('page', 1, type=int)
  start =  (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  books = [book.format() for book in selection]
  current_books = books[start:end]

  return current_books

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

  @app.after_request
  def after_request(response):
      response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
      response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
      return response

  @app.route('/categories')
  def get_categories():
      categories = Category.query.order_by(Category.id).all()
      if categories is None or len(categories) == 0:
        abort(404)

      categories_dictionary = {}
      for c in categories:
        categories_dictionary[c.id] = c.type

      return jsonify({
        "success": True,
        "categories": categories_dictionary
      })

  @app.route('/questions')
  def get_questions():
      questions = Question.query.order_by(Question.id).all()
      current_questions = paginate_question(request, questions)

      if len(current_questions) == 0:
        abort(404)

      categories = Category.query.order_by(Category.id).all()
      formatted_categories = [category.format() for category in categories]

      categories_dictionary = {}
      for c in categories:
        categories_dictionary[c.id] = c.type

      return jsonify({
        "success": True,
        "questions": current_questions,
        "totalQuestions": len(Question.query.all()),
        "categories": categories_dictionary
      })

  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
      try:
        question = Question.query.filter(Question.id == question_id).one_or_none()

        if question is None:
          abort(404)

        question.delete()

        questions = Question.query.order_by(Question.id).all()
        current_questions = paginate_question(request, questions)

        return jsonify({
          "success": True,
          "deleted_id": question_id,
          "questions": current_questions,
          "totalQuestions": len(Question.query.all()),
        })

      except:
        abort(422)

  @app.route('/questions', methods=['POST'])
  def create_question():
      body = request.get_json()

      if body is None:
        abort(422)

      question = body.get('question', None)
      answer = body.get('answer', None)
      difficulty = body.get('difficulty', None)
      category = body.get('category', None)
      searchTerm = body.get('searchTerm', None)
      
      try:
        if searchTerm:
          print(f'searchTerm: {searchTerm}')
          questions = Question.query.filter(Question.question.ilike(f'%{searchTerm}%')).all()
          
          for q in questions:
            print(f'question: {question.question}')

          current_questions = paginate_question(request, questions)

          if len(current_questions) == 0:
            abort(404)

          return jsonify({
            "success": True,
            "questions": current_questions,
            "totalQuestions": len(questions),
          })

        else:
          if question is None or answer is None or difficulty is None or category is None:
            abort(422)

          question = Question(question=question, answer=answer, difficulty=difficulty, category=int(category))
          question.insert()

          questions = Question.query.order_by(Question.id).all()
          current_questions = paginate_question(request, questions)

          if len(current_questions) == 0:
            abort(404)

          categories = Category.query.order_by(Category.id).all()
          formatted_categories = [category.format() for category in categories]

          categories_dictionary = {}
          for c in categories:
            categories_dictionary[c.id] = c.type

          return jsonify({
            "success": True,
            "questions": current_questions,
            "totalQuestions": len(Question.query.all()),
            "categories": categories_dictionary
          })

      except:
        abort(422)

  @app.route('/categories/<int:category_id>/questions')
  def get_questions_by_category(category_id):
      category = Category.query.filter(Category.id == category_id).one_or_none()
      if category is None:
        abort(404)
      
      formatted_category = category.format()

      questions = Question.query.filter(Question.category == category.id).all()
      current_questions = paginate_question(request, questions)

      if len(current_questions) == 0:
        abort(404)

      return jsonify({
        "success": True,
        "questions": current_questions,
        "total_questions": len(questions),
        "currentCategory": formatted_category
      })

  @app.route('/quizzes', methods=['POST'])
  def get_quiz_quetion():
      body = request.get_json()
      previous_questions_ids = body.get('previous_questions')
      category_id = body.get('quiz_category')['id']

      print(f'body: {body}')

      questions = []
      formatted_next_question = None

      if category_id == 0:
        questions = Question.query.all()
      else:
        questions = Question.query.filter(Question.category == category_id, Question.id.notin_(previous_questions_ids)).all()

        if len(questions) == 0:
          abort(404)
      
      if len(questions) > 0:
        next_question = random.choice(questions)
        formatted_next_question = next_question.format()

      return jsonify({
        "success": True,
        "question": formatted_next_question
      })

  # ------- Handle error section -------

  @app.errorhandler(404)
  def not_found(error):
      return jsonify({
        "success": False, 
        "error": 404,
        "message": "resource not found"
      }), 404

  @app.errorhandler(422)
  def unprocessable(error):
      return jsonify({
        "success": False, 
        "error": 422,
        "message": "unprocessable"
      }), 422

  @app.errorhandler(405)
  def not_allowed_method(error):
      return jsonify({
        "success": False, 
        "error": 405,
        "message": "not allowed method"
      }), 405
  
  return app

    