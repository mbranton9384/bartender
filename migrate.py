from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database
from alembic.config import Config
from alembic import command

# Assuming you have a Flask app and SQLAlchemy db object already created
from your_app import app, db

# Define the database URI
SQLALCHEMY_DATABASE_URI = app.config['SQLALCHEMY_DATABASE_URI']

# Create an SQLAlchemy engine
engine = create_engine(SQLALCHEMY_DATABASE_URI)

# Check if the database exists, if not create it
if not database_exists(engine.url):
    create_database(engine.url)

# Bind the engine to the SQLAlchemy db session
db.session.configure(bind=engine)

# Use Alembic to create the migration environment
alembic_cfg = Config("migrations/alembic.ini")  # Specify your Alembic configuration file path
command.upgrade(alembic_cfg, "head")  # Upgrade to the latest migration

# Optionally, you can create a new migration
# command.revision(alembic_cfg, autogenerate=True)
