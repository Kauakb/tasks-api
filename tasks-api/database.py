# this builds the connection address, create_engine opens the connection pool.
from sqlalchemy import URL, create_engine

# sessionmaker is a factory, calling it gives a new session
#  establishes all conversations with the database
from sqlalchemy.orm import sessionmaker

from config import settings

# the address of the db, built from the values in .env
# postgresql+psycopg means postgresql, using the psycopg driver.
# psycopg driver is a postgre db adapter for python.
database_URL = URL.create(
    drivername="postgresql+psycopg",
    username=settings.db_user,
    password=settings.db_password,
    host=settings.db_host,
    port=settings.db_port,
    database=settings.db_name,
)

# one engine for the whole app
engine = create_engine(database_URL)

# each call to sessionlocal() opens a new session that uses the engine
SessionLocal = sessionmaker(bind=engine)


# gives each request its own session, and closes it when request ends
def get_db():
    with SessionLocal() as db:
        yield db
