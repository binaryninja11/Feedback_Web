from app.database.crdb import SessionLocal

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()  # Rollback if any error occurs
        raise e
    finally:
        db.close()


# dependencies.py