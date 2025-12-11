from flask import Blueprint, redirect, render_template, request, send_from_directory, jsonify
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
    return jsonify({'status':'healthy'})