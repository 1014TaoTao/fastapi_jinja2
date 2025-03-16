
from alembic.config import Config
from alembic import context
from sqlmodel import SQLModel
from logging.config import fileConfig

from app.core.config import settings
from app.core.database import engine
from app.model.user import *

config: Config = context.config

if config.config_file_name is not None:
    fileConfig(fname=config.config_file_name)

target_metadata = SQLModel.metadata

config.set_main_option(name="sqlalchemy.url", value=settings.DATABASE_URL)

def run_migrations_offline() -> None:
    url: str | None = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:

    with engine.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
