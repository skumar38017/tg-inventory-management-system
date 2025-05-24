import sys
import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from sqlalchemy.ext.declarative import declarative_base
from app.database.base import Base  # Ensure this imports Base from the correct location
from alembic import context
from app.models.entry_inventory_model import EntryInventory
from app.models.to_event_inventry_model import ToEventInventory
from app.models.assign_inventory_model import AssignmentInventory
from app.models.wastege_inventory_model import WastageInventory

EntryInventory=EntryInventory()
ToEventInventory=ToEventInventory()
AssignmentInventory=AssignmentInventory()
WastageInventory=WastageInventory()

# Add the project's root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.config import SYNC_DB_URL  # This imports the DB URL correctly

# Set the target_metadata to Base.metadata (this will give Alembic access to all models)
target_metadata = Base.metadata

# Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Function to run migrations in 'offline' mode
def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = SYNC_DB_URL  # Get the database URL from config.py
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

# Function to run migrations in 'online' mode
def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    # Here we pass the SYNC_DB_URL from config.py directly to Alembic
    connectable = engine_from_config(
        {
            'sqlalchemy.url': SYNC_DB_URL  # Use the URL directly from config.py
        },
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

# Check if Alembic is running in offline or online mode and call the respective function
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
