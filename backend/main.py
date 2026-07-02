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

# Pydantic models for A2UI Chat
from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str
    a2ui_messages: Optional[List[str]] = None

@app.get("/a2ui/dashboard")
def get_a2ui_dashboard():
    # Return A2UI messages to construct a dynamic dashboard surface
    return [
        """{
            "version": "v0.10",
            "createSurface": {
                "surfaceId": "dashboard_surface",
                "catalogId": "https://a2ui.org/specification/v0_10/standard_catalog.json"
            }
        }""",
        """{
            "version": "v0.10",
            "updateComponents": {
                "surfaceId": "dashboard_surface",
                "components": [
                    {"id": "root", "component": "Column", "children": ["header", "stats_card", "divider", "tip_card"], "justify": "start", "align": "stretch"},
                    {"id": "header", "component": "Text", "text": "Thống kê Thể thao Hôm nay", "variant": "h2"},
                    {"id": "stats_card", "component": "Card", "child": "stats_content"},
                    {"id": "stats_content", "component": "Column", "children": ["stats_title", "calories_text", "time_text"], "justify": "start", "align": "stretch"},
                    {"id": "stats_title", "component": "Text", "text": "📊 Tiến độ hoạt động", "variant": "subtitle"},
                    {"id": "calories_text", "component": "Text", "text": "🔥 Lượng calo tiêu thụ: 350 kcal", "variant": "body"},
                    {"id": "time_text", "component": "Text", "text": "⏱️ Thời gian tập luyện: 45 phút", "variant": "body"},
                    {"id": "divider", "component": "Divider"},
                    {"id": "tip_card", "component": "Card", "child": "tip_content"},
                    {"id": "tip_content", "component": "Column", "children": ["tip_title", "tip_text"], "justify": "start", "align": "stretch"},
                    {"id": "tip_title", "component": "Text", "text": "💡 Lời khuyên tập luyện", "variant": "subtitle"},
                    {"id": "tip_text", "component": "Text", "text": "Bạn đang thực hiện rất tốt! Hãy duy trì uống ít nhất 2 lít nước mỗi ngày và khởi động kỹ trước khi tập cardio nhé.", "variant": "body"}
                ]
            }
        }"""
    ]

@app.post("/a2ui/chat", response_model=ChatResponse)
def a2ui_chat(request: ChatRequest):
    msg = request.message.lower()
    
    # Custom response based on keywords
    if "bài tập" in msg or "gợi ý" in msg or "tập" in msg or "exercise" in msg:
        reply = "Chào bạn! Đây là một bài tập rất phù hợp cho bạn hôm nay: Push-up (Hít đất). Bạn có thể xem chi tiết bài tập và nhấn nút hoàn thành bên dưới để tôi ghi nhận nhé!"
        a2ui_messages = [
            """{
                "version": "v0.10",
                "createSurface": {
                    "surfaceId": "chat_surface",
                    "catalogId": "https://a2ui.org/specification/v0_10/standard_catalog.json"
                }
            }""",
            """{
                "version": "v0.10",
                "updateComponents": {
                    "surfaceId": "chat_surface",
                    "components": [
                        {"id": "root", "component": "Card", "child": "exercise_card_content"},
                        {"id": "exercise_card_content", "component": "Column", "children": ["ex_title", "ex_desc", "ex_action"], "justify": "start", "align": "stretch"},
                        {"id": "ex_title", "component": "Text", "text": "Bài tập đề xuất: Push-Up (Hít đất)", "variant": "subtitle"},
                        {"id": "ex_desc", "component": "Text", "text": "Tác động chính vào cơ ngực, vai và cơ tay sau. Thực hiện 3 hiệp, mỗi hiệp 12-15 lần.", "variant": "body"},
                        {"id": "ex_action", "component": "Button", "text": "Báo cáo hoàn thành", "variant": "primary", "action": {"event": {"name": "complete_exercise", "context": {"exerciseId": "push_up"}}}}
                    ]
                }
            }"""
        ]
    elif "mệt" in msg or "đau" in msg or "mỏi" in msg:
        reply = "Tôi hiểu rồi. Bạn nên dành hôm nay để nghỉ ngơi (Rest Day) hoặc thực hiện các bài giãn cơ nhẹ nhàng. Tránh nâng tạ nặng nhé!"
        a2ui_messages = [
            """{
                "version": "v0.10",
                "createSurface": {
                    "surfaceId": "chat_surface",
                    "catalogId": "https://a2ui.org/specification/v0_10/standard_catalog.json"
                }
            }""",
            """{
                "version": "v0.10",
                "updateComponents": {
                    "surfaceId": "chat_surface",
                    "components": [
                        {"id": "root", "component": "Card", "child": "rest_card_content"},
                        {"id": "rest_card_content", "component": "Column", "children": ["rest_title", "rest_desc"], "justify": "start", "align": "stretch"},
                        {"id": "rest_title", "component": "Text", "text": "⚠️ Đề xuất: Ngày Nghỉ Ngơi (Rest Day)", "variant": "subtitle"},
                        {"id": "rest_desc", "component": "Text", "text": "Hãy tập trung vào việc ngủ đủ giấc, ăn uống giàu protein và uống đủ nước để cơ bắp phục hồi tốt nhất.", "variant": "body"}
                    ]
                }
            }"""
        ]
    else:
        reply = "Chào bạn! Tôi là trợ lý AI Coach. Bạn có thể hỏi tôi về các bài tập, nhờ tôi đề xuất bài tập hôm nay, hoặc báo cáo tình trạng thể lực để nhận lời khuyên nhé!"
        a2ui_messages = None
        
    return ChatResponse(reply=reply, a2ui_messages=a2ui_messages)

