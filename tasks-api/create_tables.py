# base knows every model, engine is the connection to postgreSQL
from database import engine
from models import Base

# creates every table that doesnt exist yet. existing table are left as they are
Base.metadata.create_all(engine)  # list of tables base has collected from every model
print("Tables created.")
