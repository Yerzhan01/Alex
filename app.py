import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging for debugging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # needed for url_for to generate with https

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///health_reports.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the app with the extension
db.init_app(app)

# Add custom template filters
def nl2br(value):
    """Convert newlines to <br> tags and clean formatting"""
    if not value:
        return value
    # Remove markdown formatting
    value = value.replace('**', '')
    value = value.replace('*', '')
    # Convert newlines to HTML breaks
    return value.replace('\n', '<br>\n')

def clean_report(value):
    """Clean report content from markdown and unnecessary symbols"""
    if not value:
        return value
    
    # Remove markdown bold formatting
    value = value.replace('**', '')
    
    # Remove single asterisks used as bullets and replace with proper bullets
    lines = value.split('\n')
    cleaned_lines = []
    
    for line in lines:
        line = line.strip()
        if line.startswith('• ') or line.startswith('- '):
            # Keep existing bullets
            cleaned_lines.append(line)
        elif line.startswith('*') and not line.startswith('**'):
            # Replace asterisk bullets with proper bullets
            cleaned_lines.append('• ' + line[1:].strip())
        else:
            cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)

app.jinja_env.filters['nl2br'] = nl2br
app.jinja_env.filters['clean_report'] = clean_report

# Import routes after app creation to avoid circular imports
with app.app_context():
    # Import models so their tables are created
    import models  # noqa: F401
    import routes  # noqa: F401
    
    # Create all database tables
    db.create_all()
