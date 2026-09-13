# Frontend Handoff - KarmaSkill AI

## 1. Backend Quick Start
- **Base URL:** http://localhost:8000
- **Swagger Documentation:** http://localhost:8000/docs
- **CORS Configuration:** Allows http://localhost:3000 and http://127.0.0.1:3000 with credentials.

### Setup Backend Locally
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python seed.py
uvicorn main:app --reload

## 2. Global Context
- **Authentication**: Not implemented. Hardcode employee_id = 1 in your global state (maps to "Rahul Sharma" from seed data).

## 3. Endpoints Frontend Should Call

### A. Get Employee Profile
- **Method:** GET /employees/{employee_id}
- **Purpose:** Fetch the user profile.

### B. Get Competencies & Gap Analysis
- **Method:** GET /employees/{employee_id}/competencies
- **Purpose:** Fetch the list of competencies and gaps to build radar chart.

### C. Get Learning Recommendations
- **Method:** GET /recommendations/{employee_id}
- **Purpose:** Get prioritized list of courses/materials based on gap severity.

### D. Upload Material & Generate AI Quiz
- **Method:** POST /materials/analyze-and-save
- **Content-Type:** multipart/form-data
- **Request:** file, number_of_questions
- **Response:** Returns saved material details and generated quiz (including correct answers, since this is an upload action).

### E. Fetch Quiz for Attempt
- **Method:** GET /quizzes/{quiz_id}
- **Purpose:** Fetch questions for user to answer.
- **Security:** Intentionally DOES NOT EXPOSE the correct_answer field.

### F. Submit Quiz
- **Method:** POST /quizzes/{quiz_id}/attempt
- **Purpose:** Submit user answers, evaluate score, and automatically update competency level.
- **Request Body:** {"employee_id": 1, "answers": [{"question_id": 10, "answer": "A"}]}

## 4. Frontend Types (TypeScript)
export interface Employee { id: number; name: string; email: string; department: string; role: string; experience: number; }
export interface EmployeeCompetency { competency: { id: number; name: string; description: string; category: string; }; current_level: number; required_level: number; }
export interface Recommendation { type: "course" | "learning_material"; title: string; competency: string; current_level: number; required_level: number; gap: number; priority_score: number; priority: "High" | "Medium" | "Low"; reason: string; }
export interface QuizQuestion { id: number; question: string; options: { A: string; B: string; C: string; D: string; }; difficulty: string; }
export interface Quiz { id: number; title: string; number_of_questions: number; questions: QuizQuestion[]; }
export interface QuizSubmission { employee_id: number; answers: { question_id: number; answer: string }[]; }

## 5. Things to NOT Assume
1. Do not assume all competencies update at once. A quiz updates exactly ONE primary competency.
2. The user profile is statically loaded from employee_id = 1 for the demo.
3. API errors will return a 4xx or 5xx with a JSON payload: {"detail": "Error message"}. Build your error handling around this.
