import os
from flask import Flask
from config import Config
from authlib.integrations.flask_client import OAuth

oauth = OAuth()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Ensure secret key for session-based auth
    app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-insecure-key")

    # Optional Azure AD SSO
    if app.config.get("AZURE_SSO"):
        oauth.init_app(app)
        oauth.register(
            name='azure',
            client_id=app.config["AZURE_CLIENT_ID"],
            client_secret=app.config["AZURE_CLIENT_SECRET"],
            server_metadata_url=f'https://login.microsoftonline.com/{app.config["AZURE_TENANT_ID"]}/v2.0/.well-known/openid-configuration',
            client_kwargs={'scope': 'openid email profile'}
        )

    # Make oauth globally accessible if needed in routes
    app.oauth = oauth

    # Register routes
    from .routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    return app
