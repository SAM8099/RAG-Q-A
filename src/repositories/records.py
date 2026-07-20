from src.modules.records import GenerationRecord 
from src.repositories.config import SessionLocal


class RecordRepository:
    def __init__(self):
        self.db = SessionLocal()

    def add_record(
        self,
        record: GenerationRecord
    ):
        try:
            self.db.add(record)
            self.db.commit()
            self.db.refresh(record)
            return record
        except Exception as e:
            self.db.rollback()
            raise RuntimeError(f"Database upload failed: {e}")
        finally:
            self.db.close()