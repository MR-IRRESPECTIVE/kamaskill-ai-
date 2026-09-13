import os

content = """
from schemas import AssessmentGenerateRequest
from models import LearningMaterial, Quiz, QuizQuestion
from services.mcq_engine import generate_mcqs

@router.post("/generate")
def generate_assessment(
    req: AssessmentGenerateRequest,
    db: Session = Depends(get_db)
):
    employee = db.query(Employee).filter(Employee.id == req.employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    competency = db.query(Competency).filter(Competency.id == req.competency_id).first()
    if not competency:
        raise HTTPException(status_code=404, detail="Competency not found")

    # Satisfy Quiz foreign key by creating a dummy LearningMaterial
    material_text = f"Competency: {competency.name}\\nDescription: {competency.description}\\nPlease generate a comprehensive professional assessment covering various aspects of {competency.name}."
    
    material = LearningMaterial(
        filename="system_generated.txt",
        title=f"Assessment Material - {competency.name}",
        extracted_text=material_text,
        pages=1
    )
    db.add(material)
    db.commit()
    db.refresh(material)

    try:
        quiz_result = generate_mcqs(material_text, req.number_of_questions)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    quiz = Quiz(
        material_id=material.id,
        title=f"{competency.name} - AI Assessment",
        number_of_questions=len(quiz_result["questions"])
    )
    db.add(quiz)
    db.commit()
    db.refresh(quiz)

    for q in quiz_result["questions"]:
        question_record = QuizQuestion(
            quiz_id=quiz.id,
            question=q["question"],
            option_a=q["options"]["A"],
            option_b=q["options"]["B"],
            option_c=q["options"]["C"],
            option_d=q["options"]["D"],
            correct_answer=q["correct_answer"],
            explanation=q.get("explanation", ""),
            difficulty=q.get("difficulty", "Medium"),
            competency_id=competency.id
        )
        db.add(question_record)

    db.commit()

    return {
        "message": "Quiz generated successfully",
        "quiz_id": quiz.id,
        "title": quiz.title,
        "number_of_questions": quiz.number_of_questions
    }
"""

with open("backend/routers/assessments.py", "a") as f:
    f.write(content)
