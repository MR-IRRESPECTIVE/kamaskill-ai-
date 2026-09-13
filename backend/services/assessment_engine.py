
def calculate_new_competency(current_level: float, required_level: float, percentage: float) -> float:
    """
    Assessment provides up to 20 competency points. Points are applied fully while 
    the employee has a competency gap. Once the required competency is reached, 
    additional gains receive diminishing returns to reduce competency inflation.
    """
    # Clamp percentage between 0.0 and 100.0
    percentage = max(0.0, min(100.0, percentage))
    
    base_gain = (percentage / 100.0) * 20.0
    gap = max(0.0, required_level - current_level)
    
    if base_gain <= gap:
        gain = base_gain
    else:
        gain = gap + ((base_gain - gap) * 0.25)
        
    new_level = current_level + gain
    return min(100.0, new_level)

from sqlalchemy.orm import Session

from models import Assessment, EmployeeCompetency


def calculate_current_competency(
    employee_id: int,
    competency_id: int,
    db: Session
):
    """
    Calculate current competency level using assessment history.

    Most recent assessment gets the highest weight.
    """

    assessments = (
        db.query(Assessment)
        .filter(
            Assessment.employee_id == employee_id,
            Assessment.competency_id == competency_id
        )
        .order_by(Assessment.id.desc())
        .limit(3)
        .all()
    )

    if not assessments:
        return 0

    weights = [0.5, 0.3, 0.2]

    weighted_score = 0
    total_weight = 0

    for index, assessment in enumerate(assessments):

        weight = weights[index]

        weighted_score += (
            assessment.percentage * weight
        )

        total_weight += weight

    current_level = weighted_score / total_weight

    return round(current_level, 2)


def update_employee_competency(
    employee_id: int,
    competency_id: int,
    percentage: float,
    db: Session
):
    """
    Recalculate and update employee competency level.
    """

    employee_competency = (
        db.query(EmployeeCompetency)
        .filter(
            EmployeeCompetency.employee_id == employee_id,
            EmployeeCompetency.competency_id == competency_id
        )
        .first()
    )

    if not employee_competency:
        return None

    new_level = calculate_new_competency(
        current_level=employee_competency.current_level,
        required_level=employee_competency.required_level,
        percentage=percentage
    )

    employee_competency.current_level = new_level

    db.commit()
    db.refresh(employee_competency)

    return employee_competency