from dotenv import load_dotenv
import os
from flask import Flask, render_template, request
from logging.handlers import RotatingFileHandler
import logging
from datetime import datetime

load_dotenv()



def datetimeformat(value, format='%d/%m/%Y %H:%M:%S'):
    if not value:
        return ''
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value)
        except ValueError:
            return value  # Si no es ISO, devuelve la cadena tal cual
    return value.strftime(format)

def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get('FLASK_SECRET_KEY')
    if not app.secret_key:
        raise RuntimeError("La clave secreta no está configurada. Define FLASK_SECRET_KEY en el archivo .env")

    app.jinja_env.filters['datetimeformat'] = datetimeformat

    # Registro de blueprints con prefijos
    from routes import scan_api, scan_web, reports, status, modules, scripts, vpn_profiles

    app.register_blueprint(scan_api.bp_api, url_prefix='/api')
    app.register_blueprint(scan_web.bp_web)
    app.register_blueprint(reports.bp_reports)
    app.register_blueprint(status.bp_status)
    app.register_blueprint(modules.bp_modules)
    app.register_blueprint(scripts.bp_scripts)
    app.register_blueprint(vpn_profiles.bp_vpn)

    # Configuración de logging
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/webscanner.log', maxBytes=10*1024*1024, backupCount=5)
    file_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(module)s - %(message)s')
    file_handler.setFormatter(formatter)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Aplicación iniciada')

    # Manejo de errores personalizado con logging
    @app.errorhandler(404)
    def not_found_error(error):
        app.logger.warning(f'404 Not Found: {request.url}')
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'500 Internal Server Error: {request.url} - {error}')
        return render_template('errors/500.html'), 500

    @app.errorhandler(503)
    def service_unavailable_error(error):
        app.logger.warning(f'503 Service Unavailable: {request.url}')
        return render_template('errors/503.html'), 503

    return app
