import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
  page = request.args.get('page', 1, type=int)
  start =  (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  questions = [question.format() for question in selection]
  current_questions = questions[start:end]

  return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)

  CORS(app)

  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

  # RETURNS ALL AVAILABLE CATEGORIES

  @app.route('/categories', methods=['GET'])
  def get_categories():
    try:
      categories = Category.query.order_by(Category.id).all()
      return jsonify({
        'success': True,
        'categories': {
          category.id: category.type for category in categories
        }
      })
    except:
      abort(404)

  # RETURNS ALL AVAILABLE QUESTIONS

  @app.route('/questions', methods=['GET'])
  def get_questions():
    try:
      questions = Question.query.order_by(Question.id).all()
      current_questions = paginate_questions(request, questions)

      categories = Category.query.order_by(Category.id).all()
      current_category = Category.query.get(current_questions[0]["category"])

      if len(current_questions) == 0:
        abort(404)

      return jsonify({
        'success': True,
        'questions': current_questions,
        'total_questions': len(questions),
        'categories': {
          category.id: category.type for category in categories
        },
        'current_category': current_category.type
      })
    except:
      abort(404)

  # DELETES A SPECIFIC QUESTION BASED ON ID

  @app.route('/questions/<question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.filter(Question.id == question_id).one_or_none()

      if question is None:
        abort(422)

      question.delete()

      return jsonify({
        'success': True,
        'deleted': question_id
      })

    except:
      abort(422)

  # CREATES A NEW QUESTION

  @app.route('/questions', methods=['POST'])
  def create_question():
    body = request.get_json()

    if not ('question' in body and 'answer' in body and 'difficulty' in body and 'category' in body):
      abort(422)

    question = body.get('question')
    answer = body.get('answer')
    difficulty = body.get('difficulty')
    category = body.get('category')
    try:
      new_question = Question(question=question, answer=answer, difficulty=difficulty, category=category)
      new_question.insert()

      return jsonify({
        'success': True
      })

    except:
      abort(422)

  # RETURNS ALL POSSIBLE QUESTIONS CONTAINING THE SEARCH TERM

  @app.route('/questions/search', methods=['POST'])
  def search_questions():
    body = request.get_json()
    search_term = body.get('searchTerm', None)
    try:
      if search_term:
        search_results = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
        return jsonify({
          'success': True,
          'questions': [question.format() for question in search_results],
          'total_questions': len(search_results),
          'current_category': None
        })
      else:
        abort(404)
    except:
      abort(404)

  # RETURNS ALL QUESTIONS THAT BELONG TO A SPECIFIC CATEGORY

  @app.route('/categories/<category_id>/questions', methods=['GET'])
  def get_category_questions(category_id):
    try:
      questions = Question.query.filter(Question.category==category_id).order_by(Question.id).all()
      current_questions = paginate_questions(request, questions)

      current_category = Category.query.get(category_id)

      if len(current_questions) == 0:
        abort(404)

      return jsonify({
        'success': True,
        'questions': current_questions,
        'total_questions': len(questions),
        'current_category': current_category.type
      })
    except:
      abort(404)

  # RETURNS A RANDOM QUESTION

  @app.route('/quizzes', methods=['POST'])
  def get_new_question():
    body = request.get_json()

    if not ('previous_questions' in body and 'quiz_category' in body):
      abort(422)

    previous_questions = body.get('previous_questions')
    quiz_category = body.get('quiz_category')

    try:
      if quiz_category['type'] == 'click':
        available_questions = Question.query.filter(Question.id.notin_((previous_questions))).all()
      else:
        available_questions = Question.query.filter_by(category=quiz_category['id']).filter(Question.id.notin_((previous_questions))).all()
      next_question = available_questions[random.randrange(0, len(available_questions))].format() if len(available_questions) > 0 else None

      return jsonify({
        'success': True,
        'question': next_question
      })
    except:
      abort(422)

  # ERROR HANDLERS

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      "success": False,
      "error": 400,
      "message": "bad request"
      }), 400

  @app.errorhandler(404)
  def resource_not_found(error):
    return jsonify({
      "success": False,
      "error": 404,
      "message": "resource not found"
      }), 404

  @app.errorhandler(405)
  def methos_not_allowed(error):
    return jsonify({
      "success": False,
      "error": 405,
      "message": "method not allowed"
      }), 405

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False,
      "error": 422,
      "message": "unprocessable"
      }), 422

  return app

app = create_app()

if __name__ == '__main__':
    app.run()