import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Employee, EmployeeCompetency
from services.assessment_engine import update_employee_competency

# In-memory database setup
engine = create_engine('sqlite:///:memory:')
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)

def test_update_employee_competency_integration(db):
    # Setup initial data
    emp = Employee(id=1, name="Test User", email="test@example.com", department="IT", role="Dev", experience=1.0)
    db.add(emp)
    
    comp = EmployeeCompetency(
        employee_id=1, 
        competency_id=1, 
        current_level=70.0, 
        required_level=88.0
    )
    db.add(comp)
    db.commit()

    # Verify initial level
    assert comp.current_level == 70.0

    # Call update with 60%
    updated = update_employee_competency(employee_id=1, competency_id=1, percentage=60.0, db=db)
    assert updated.current_level == 82.0

    # Test 70 + 0% -> 70
    # Reset level to 70 for the next test
    updated.current_level = 70.0
    db.commit()

    updated2 = update_employee_competency(employee_id=1, competency_id=1, percentage=0.0, db=db)
    assert updated2.current_level == 70.0
