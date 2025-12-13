from flask import Blueprint, redirect, render_template, request, send_from_directory, jsonify
from sqlalchemy import text, inspect

from App.database import db
from App.controllers import create_user, initialize

index_views = Blueprint('index_views', __name__, template_folder='../templates')

@index_views.route('/', methods=['GET'])
def index_page():
    return render_template('index.html')


@index_views.route('/dashboard', methods=['GET'])
def dashboard_page():
    return render_template('dashboard.html')


@index_views.route('/portal/resident', methods=['GET'])
def portal_resident_page():
    return render_template('portal_resident.html')


@index_views.route('/portal/driver', methods=['GET'])
def portal_driver_page():
    return render_template('portal_driver.html')


@index_views.route('/portal/admin', methods=['GET'])
def portal_admin_page():
    return render_template('portal_admin.html')

@index_views.route('/init', methods=['GET'])
def init():
    initialize()
    return jsonify(message='db initialized!')

@index_views.route('/health', methods=['GET'])
def health_check():
    result = {'status': 'healthy'}
    # Optional DB check: helps debug Render deployments.
    try:
        db.session.execute(text('SELECT 1'))
        result['db_ok'] = True

        try:
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            result['tables'] = len(tables)
            result['has_users_table'] = any(t in {'user', 'users'} for t in tables)
        except Exception as e:
            # Don't fail health if inspection isn't available.
            result['schema_check_error'] = f"{type(e).__name__}: {str(e)[:180]}"
    except Exception as e:
        result['db_ok'] = False
        result['db_error'] = f"{type(e).__name__}: {str(e)[:220]}"
        result['hint'] = 'If this is a fresh deploy, ensure DATABASE_URL/FLASK_SQLALCHEMY_DATABASE_URI is set and visit /init once.'
        return jsonify(result), 503

    return jsonify(result), 200