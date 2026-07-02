import os
import json
import sqlite3
from sqlalchemy import create_engine, Column, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

DATABASE_URL = "sqlite:///D:/Python/Exercies_webapp_AI/backend/exercises.db"

Base = declarative_base()

class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(String(10), primary_key=True)
    name = Column(String(255), nullable=False)
    category = Column(String(100))
    body_part = Column(String(100))
    equipment = Column(String(100))
    instructions_en = Column(Text)
    instructions_es = Column(Text)
    instructions_it = Column(Text)
    instructions_tr = Column(Text)
    instructions_ru = Column(Text)
    instructions_zh = Column(Text)
    muscle_group = Column(String(100))
    secondary_muscles = Column(Text)  # Saved as JSON string
    target = Column(String(100))
    image = Column(String(500))
    gif_url = Column(String(500))
    created_at = Column(DateTime)

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    # Check if table already contains data
    if db.query(Exercise).count() > 0:
        print("Database already initialized and contains exercises.")
        db.close()
        return

    json_path = "D:/Python/Exercies_webapp_AI/backend/data/exercises.json"
    if not os.path.exists(json_path):
        print(f"Dataset JSON not found at {json_path}!")
        db.close()
        return

    print("Importing exercises from JSON to SQLite...")
    with open(json_path, "r", encoding="utf-8") as f:
        exercises_data = json.load(f)

    for item in exercises_data:
        # Resolve nested instructions
        instr = item.get("instructions", {})
        instr_en = instr.get("en", "")
        instr_es = instr.get("es", "")
        instr_it = instr.get("it", "")
        instr_tr = instr.get("tr", "")
        instr_ru = instr.get("ru", "")
        instr_zh = instr.get("zh", "")

        # Handle created_at datetime conversion
        created_str = item.get("created_at")
        created_dt = None
        if created_str:
            try:
                # Remove timezone offset if present for datetime.fromisoformat
                if "+" in created_str:
                    created_str = created_str.split("+")[0]
                created_dt = datetime.fromisoformat(created_str)
            except Exception:
                created_dt = datetime.utcnow()

        db_exercise = Exercise(
            id=item.get("id"),
            name=item.get("name"),
            category=item.get("category"),
            body_part=item.get("body_part") or item.get("category"),
            equipment=item.get("equipment"),
            instructions_en=instr_en,
            instructions_es=instr_es,
            instructions_it=instr_it,
            instructions_tr=instr_tr,
            instructions_ru=instr_ru,
            instructions_zh=instr_zh,
            muscle_group=item.get("muscle_group"),
            secondary_muscles=json.dumps(item.get("secondary_muscles", [])),
            target=item.get("target"),
            image=item.get("image"),
            gif_url=item.get("gif_url"),
            created_at=created_dt
        )
        db.add(db_exercise)

    db.commit()
    print(f"Successfully imported {db.query(Exercise).count()} exercises.")
    db.close()

if __name__ == "__main__":
    init_db()
