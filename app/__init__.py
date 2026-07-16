from flask import Flask, jsonify
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from config import Config
from .extensions import cache, db, limiter, ma


def create_app(config_object=Config):
    app = Flask(__name__)
    app.config.from_object(config_object)

    db.init_app(app)
    ma.init_app(app)
    cache.init_app(app)
    limiter.init_app(app)

    from .blueprints.customers import customers_bp
    from .blueprints.inventory import inventory_bp
    from .blueprints.mechanics import mechanics_bp
    from .blueprints.service_tickets import service_tickets_bp

    app.register_blueprint(customers_bp, url_prefix="/customers")
    app.register_blueprint(mechanics_bp, url_prefix="/mechanics")
    app.register_blueprint(service_tickets_bp, url_prefix="/service-tickets")
    app.register_blueprint(inventory_bp, url_prefix="/inventory")

    @app.get("/health")
    @limiter.exempt
    def health():
        return jsonify({"status": "healthy"})

    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        return jsonify({"message": "Validation failed", "errors": error.messages}), 400

    @app.errorhandler(IntegrityError)
    def handle_integrity_error(error):
        db.session.rollback()
        return jsonify({"message": "Database integrity error"}), 409

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"message": "Resource not found"}), 404

    with app.app_context():
        db.create_all()

    return app
