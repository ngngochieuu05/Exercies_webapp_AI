from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import random
import json
from typing import List, Optional
from database import SessionLocal, Exercise, init_db

app = FastAPI(title="Exercises API", description="API serving 1,324 fitness exercises")

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    init_db()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/exercises")
def get_exercises(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    body_part: Optional[str] = None,
    equipment: Optional[str] = None,
    target: Optional[str] = None,
    muscle_group: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Exercise)
    
    # Apply filters
    if category:
        query = query.filter(Exercise.category.like(f"%{category}%"))
    if body_part:
        query = query.filter(Exercise.body_part.like(f"%{body_part}%"))
    if equipment:
        query = query.filter(Exercise.equipment.like(f"%{equipment}%"))
    if target:
        query = query.filter(Exercise.target.like(f"%{target}%"))
    if muscle_group:
        query = query.filter(Exercise.muscle_group.like(f"%{muscle_group}%"))
        
    total = query.count()
    total_pages = (total + limit - 1) // limit
    
    # Pagination
    offset = (page - 1) * limit
    results = query.offset(offset).limit(limit).all()
    
    # Format response
    data = []
    for ex in results:
        data.append({
            "id": ex.id,
            "name": ex.name,
            "category": ex.category,
            "body_part": ex.body_part,
            "equipment": ex.equipment,
            "instructions": {
                "en": ex.instructions_en,
                "es": ex.instructions_es,
                "it": ex.instructions_it,
                "tr": ex.instructions_tr,
                "ru": ex.instructions_ru,
                "zh": ex.instructions_zh
            },
            "muscle_group": ex.muscle_group,
            "secondary_muscles": json.loads(ex.secondary_muscles) if ex.secondary_muscles else [],
            "target": ex.target,
            "image": ex.image,
            "gif_url": ex.gif_url,
            "created_at": ex.created_at.isoformat() if ex.created_at else None
        })
        
    return {
        "data": data,
        "total": total,
        "page": page,
        "limit": limit,
        "totalPages": total_pages
    }

@app.get("/exercises/random")
def get_random_exercise(db: Session = Depends(get_db)):
    exercises_ids = [ex.id for ex in db.query(Exercise.id).all()]
    if not exercises_ids:
        raise HTTPException(status_code=404, detail="No exercises found")
    random_id = random.choice(exercises_ids)
    return get_exercise_by_id(random_id, db)

@app.get("/exercises/{exercise_id}")
def get_exercise_by_id(exercise_id: str, db: Session = Depends(get_db)):
    ex = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    if not ex:
        raise HTTPException(status_code=404, detail="Exercise not found")
        
    return {
        "id": ex.id,
        "name": ex.name,
        "category": ex.category,
        "body_part": ex.body_part,
        "equipment": ex.equipment,
        "instructions": {
            "en": ex.instructions_en,
            "es": ex.instructions_es,
            "it": ex.instructions_it,
            "tr": ex.instructions_tr,
            "ru": ex.instructions_ru,
            "zh": ex.instructions_zh
        },
        "muscle_group": ex.muscle_group,
        "secondary_muscles": json.loads(ex.secondary_muscles) if ex.secondary_muscles else [],
        "target": ex.target,
        "image": ex.image,
        "gif_url": ex.gif_url,
        "created_at": ex.created_at.isoformat() if ex.created_at else None
    }

@app.get("/categories")
def get_categories(db: Session = Depends(get_db)):
    cats = db.query(Exercise.category).distinct().all()
    return sorted([c[0] for c in cats if c[0]])

@app.get("/body-parts")
def get_body_parts(db: Session = Depends(get_db)):
    parts = db.query(Exercise.body_part).distinct().all()
    return sorted([p[0] for p in parts if p[0]])

@app.get("/equipment")
def get_equipment_list(db: Session = Depends(get_db)):
    eqs = db.query(Exercise.equipment).distinct().all()
    return sorted([e[0] for e in eqs if e[0]])
