from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from services.assessment_engine import update_employee_competency

from database import get_db
from models import (
    Assessment,
    Employee,
    Competency,
    EmployeeCompetency
)
from schemas import AssessmentCreate, AssessmentResponse

router = APIRouter(
    prefix="/assessments",
    tags=["Assessments"]
)


@router.post("/", response_model=AssessmentResponse)
def create_assessment(
    assessment: AssessmentCreate,
    db: Session = Depends(get_db)
):

    # Check employee
    employee = db.query(Employee).filter(
        Employee.id == assessment.employee_id
    ).first()

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    # Check competency
    competency = db.query(Competency).filter(
        Competency.id == assessment.competency_id
    ).first()

    if not competency:
        raise HTTPException(
            status_code=404,
            detail="Competency not found"
        )

    # Validate assessment
    if assessment.total_questions <= 0:
        raise HTTPException(
            status_code=400,
            detail="Total questions must be greater than 0"
        )

    if assessment.score < 0 or assessment.score > assessment.total_questions:
        raise HTTPException(
            status_code=400,
            detail="Score must be between 0 and total questions"
        )

    # Calculate percentage
    percentage = (
        assessment.score / assessment.total_questions
    ) * 100

    # Store assessment
    new_assessment = Assessment(
        employee_id=assessment.employee_id,
        competency_id=assessment.competency_id,
        score=assessment.score,
        total_questions=assessment.total_questions,
        percentage=round(percentage, 2)
    )

    db.add(new_assessment)

    # Update current competency level
    db.commit()
    db.refresh(new_assessment)

    update_employee_competency(
    assessment.employee_id,
    assessment.competency_id,
    db
)

    return new_assessment


@router.get(
    "/employee/{employee_id}",
    response_model=list[AssessmentResponse]
)
def get_employee_assessments(
    employee_id: int,
    db: Session = Depends(get_db)
):

    employee = db.query(Employee).filter(
        Employee.id == employee_id
    ).first()

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    return db.query(Assessment).filter(
        Assessment.employee_id == employee_id
    ).all()
from schemas import AssessmentGenerateRequest
from models import LearningMaterial, Quiz, QuizQuestion, MaterialCompetency
from services.mcq_engine import generate_mcqs_from_sections

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

    material_mapping = db.query(MaterialCompetency).filter(
        MaterialCompetency.competency_id == req.competency_id
    ).order_by(MaterialCompetency.relevance.desc()).first()

    if not material_mapping or not material_mapping.material:
        raise HTTPException(
            status_code=404,
            detail="No substantive learning material found for this competency"
        )
    
    material = material_mapping.material
    material_text = material.extracted_text

    try:
        quiz_result = generate_mcqs_from_sections(material_text, req.number_of_questions)
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
