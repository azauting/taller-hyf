from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config
from dotenv import load_dotenv
import os

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()


from app.models import Usuario
@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))


def create_app():
    app = Flask(__name__)
    # configuraciones
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    from app import models
    # Login redirect default
    login_manager.login_view = "auth.login"
    # ruta de los Blueprints
    from app.auth import auth_bp
    from app.routes.inventario import inventario_bp
    from app.routes.cliente import cliente_bp
    from app.routes.errors import errors_bp
    from app.routes.vehiculo import vehiculo_bp
    from app.routes.ticket_servicio import ticket_servicio_bp
    from app.routes.ticket_repuesto import ticket_repuesto_bp
    from app.routes.taller import taller_bp
    from app.routes.estadisticas import estadisticas_bp

    # Aquí se registrarán los Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(errors_bp)
    app.register_blueprint(inventario_bp)
    app.register_blueprint(cliente_bp)
    app.register_blueprint(vehiculo_bp)
    app.register_blueprint(ticket_servicio_bp)
    app.register_blueprint(ticket_repuesto_bp)
    app.register_blueprint(taller_bp)
    app.register_blueprint(estadisticas_bp)


    @app.context_processor
    def inject_user():
        from flask_login import current_user
        return dict(current_user=current_user)
    
    return app
