from app.database.crdb import engine
from app.models.dbmodel import Base

Base.metadata.create_all(bind=engine)
print("✅ Tables created successfully")
