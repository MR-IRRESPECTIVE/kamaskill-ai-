# KarmaSkill AI Platform

Welcome to the newly structured **KarmaSkill AI Platform** repository! 

This repository has undergone a massive architectural upgrade from its initial version. We have transitioned from a standalone backend API to a full-stack monorepo featuring a production-ready Next.js frontend and a significantly enhanced FastAPI backend.

## 🚀 Major Changes & Fixes

Here is everything that has changed from the initial repository:

### 1. Monorepo Restructuring
- **Separation of Concerns:** The codebase is now cleanly divided into `backend/` and `frontend/` directories.
- **Clean Root:** All original backend files have been migrated to `backend/`, making the root directory a true monorepo orchestrator.

### 2. Brand New Next.js Frontend
- **Modern Tech Stack:** Built from scratch using Next.js (App Router), React, and Tailwind CSS.
- **Features Included:** 
  - Comprehensive layouts (Sidebar, Header, AppShell) for easy navigation.
  - Dedicated pages for `Assessment`, `Learning`, `Progress Tracking`, and dynamic `Quizzes`.
  - API integration hooks and utilities (`src/lib/api.ts`).

### 3. Backend AI Provider Abstraction & Mocking
- **Provider Pattern:** Refactored the monolithic `gemini_service` to use a flexible provider architecture (`backend/services/providers`).
- **Mock Provider Introduced:** Added a `MockProvider` that simulates Gemini AI responses. 
  - *Why?* This allows the team to run the application, develop features, and execute tests instantly **without requiring an internet connection or consuming Gemini API credits**.
- **Selector Utility:** Easily toggle between `MockProvider` and `GeminiProvider` via configuration.

### 4. Comprehensive Testing Suite
- **Massive Testing Expansion:** Added extensive test files including:
  - `test_e2e.py` & `test_g7_e2e.py`: End-to-end flow validation.
  - `test_competency_math.py` & `test_competency_update_integration.py`: Ensuring algorithms for skill calculation are perfectly accurate.
  - API Mock tests (`test_g5_batch_mock.py`, `test_g6_api.py`) for bulletproof reliability.

### 5. Documentation & Team Handoff
- Added **`API_CONTRACT.md`** and **`FRONTEND_HANDOFF.md`** inside `backend/docs/`.
- These documents serve as the single source of truth for API request/response structures, ensuring the frontend and backend teams are always in sync.

### 6. Realistic Demo Data & Seeding
- Added sample learning materials (e.g., `data_viz_fundamentals.pdf`).
- Introduced new seeding scripts (`seed_demo_learning_material.py`) so new developers can instantly populate a local database with rich, realistic data.

## 🛠️ Getting Started

### Prerequisites
- Python 3.9+
- Node.js 18+

### Running the Backend
1. Navigate to the backend directory: `cd backend`
2. Create a virtual environment: `python -m venv venv`
3. Activate it:
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Run the server: `uvicorn main:app --reload`

### Running the Frontend
1. Navigate to the frontend directory: `cd frontend`
2. Install dependencies: `npm install`
3. Start the development server: `npm run dev`
4. Open [http://localhost:3000](http://localhost:3000) in your browser.

## 🤝 Contributing
Please make sure to review `API_CONTRACT.md` when adding new endpoints or modifying existing data structures to ensure the frontend doesn't break!
