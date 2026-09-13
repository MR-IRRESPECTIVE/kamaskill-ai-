from fastapi.testclient import TestClient
from main import app
from database import SessionLocal
from models import QuizQuestion

client = TestClient(app)

def run():
    print("Fetching initial competencies...")
    comp_resp = client.get("/competencies/employee/1")
    comps = comp_resp.json()
    viz_comp = next((c for c in comps if "Data Visualization" in c["competency"]["name"]), None)
    if not viz_comp:
        print("Could not find Data Visualization competency!")
        print(comps)
        return
    print(f"Initial: {viz_comp['competency']['name']} = {viz_comp['current_level']}")
    
    print("Uploading PDF...")
    with open("data_viz_guide.pdf", "rb") as f:
        files = {"file": ("data_viz_guide.pdf", f, "application/pdf")}
        data = {"number_of_questions": 5}
        upload_resp = client.post("/materials/analyze-and-save", files=files, data=data)
    
    if upload_resp.status_code != 200:
        print("Upload failed!", upload_resp.text)
        return
    
    quiz_data = upload_resp.json()
    quiz_id = quiz_data["quiz"]["id"]
    print(f"Quiz created! ID: {quiz_id}")
    
    print("Fetching quiz...")
    quiz_resp = client.get(f"/quizzes/{quiz_id}")
    quiz_info = quiz_resp.json()
    questions = quiz_info["questions"]
    
    # We need to know correct answers. Let's get them from DB.
    db = SessionLocal()
    db_questions = db.query(QuizQuestion).filter(QuizQuestion.quiz_id == quiz_id).all()
    
    # We want 60%, so 3 correct out of 5.
    answers_to_submit = []
    for i, q in enumerate(db_questions):
        correct = q.correct_answer
        # Pick wrong answer for the last 2 questions
        if i >= 3:
            wrong = "A" if correct != "A" else "B"
            answers_to_submit.append({"question_id": q.id, "answer": wrong})
        else:
            answers_to_submit.append({"question_id": q.id, "answer": correct})
    
    db.close()
    
    print("Submitting quiz...")
    payload = {
        "employee_id": 1,
        "answers": answers_to_submit
    }
    submit_resp = client.post(f"/quizzes/{quiz_id}/attempt", json=payload)
    if submit_resp.status_code != 200:
        print("Submit failed!", submit_resp.text)
        return
        
    print("Quiz submitted:", submit_resp.json()["result"])
    print("Competency level after:", submit_resp.json().get("new_competency_level"))
    
run()
