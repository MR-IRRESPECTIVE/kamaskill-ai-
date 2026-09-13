# API Contract - KarmaSkill AI

## Base URL
http://localhost:8000

## Core Endpoints

### 1. Health
METHOD: GET
PATH: /health
PURPOSE: Check backend status.

### 2. Get Employee
METHOD: GET
PATH: /employees/{employee_id}
PURPOSE: Retrieve employee profile.
RESPONSE:
{ "id": 1, "name": "Rahul Sharma", "email": "rahul.sharma@gov.in", "department": "Statistics Department", "role": "Statistical Officer", "experience": 4.0 }

### 3. Get Employee Competencies
METHOD: GET
PATH: /employees/{employee_id}/competencies
PURPOSE: Retrieve gap analysis data.
RESPONSE:
[ { "competency": { "id": 1, "name": "Data Analysis", "description": "...", "category": "Technical" }, "current_level": 72.0, "required_level": 85.0 } ]

### 4. Get Recommendations
METHOD: GET
PATH: /recommendations/{employee_id}
PURPOSE: Get prioritized learning paths based on gaps.
RESPONSE:
[ { "type": "course", "title": "Advanced Data Analysis", "difficulty": "Advanced", "competency": "Data Analysis", "current_level": 72.0, "required_level": 85.0, "gap": 13.0, "coverage": 95.0, "priority_score": 12.35, "priority": "Low", "reason": "..." } ]

### 5. Fetch Quiz
METHOD: GET
PATH: /quizzes/{quiz_id}
PURPOSE: Fetch quiz for attempt (HIDES ANSWER KEY).
RESPONSE:
{ "id": 1, "title": "AI Assessment", "number_of_questions": 5, "questions": [ { "id": 1, "question": "...", "options": { "A": "...", "B": "...", "C": "...", "D": "..." }, "difficulty": "Medium" } ] }

### 6. Submit Quiz
METHOD: POST
PATH: /quizzes/{quiz_id}/attempt
PURPOSE: Grade quiz, persist assessment, and update employee competency safely.
REQUEST BODY:
{ "employee_id": 1, "answers": [ { "question_id": 1, "answer": "A" } ] }
RESPONSE:
{ "message": "Quiz submitted successfully", "employee": { "id": 1, "name": "Rahul Sharma" }, "quiz": { "id": 1, "title": "AI Assessment" }, "result": { "score": 4, "total_questions": 5, "percentage": 80.0 }, "question_results": [ { "question_id": 1, "your_answer": "A", "correct": true } ], "assessment_created": true, "competency_id": 1, "new_competency_level": 74.4 }
