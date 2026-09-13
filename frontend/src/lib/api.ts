import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface Employee {
  id: number;
  name: string;
  department: string;
  role: string;
  experience: number;
}

export interface Competency {
  id: number;
  name: string;
  description: string;
  category: string;
}

export interface EmployeeCompetency {
  competency: Competency;
  current_level: number;
  required_level: number;
}

export interface Recommendation {
  type: string;
  course_id?: number;
  material_id?: number;
  title: string;
  difficulty?: string;
  duration?: number;
  filename?: string;
  pages?: number;
  competency: string;
  current_level: number;
  required_level: number;
  gap: number;
  coverage?: number;
  relevance?: number;
  priority_score: number;
  priority: string;
  reason: string;
}

export interface RecommendationResponse {
  employee_id: number;
  employee_name: string;
  role: string;
  recommendations: Recommendation[];
}

export interface QuizAttemptResult {
  score: number;
  total_questions: number;
  percentage: number;
  new_competency_level?: number;
}

export interface QuizOption {
  A: string;
  B: string;
  C: string;
  D: string;
}

export interface QuizQuestion {
  id: number;
  question: string;
  options: QuizOption;
  difficulty: string;
}

export interface Quiz {
  id: number;
  title: string;
  number_of_questions: number;
  questions: QuizQuestion[];
}

export interface GenerateAssessmentResponse {
  message: string;
  quiz_id: number;
  title: string;
  number_of_questions: number;
}

export interface QuizSubmissionResponse {
  message: string;
  result: QuizAttemptResult;
  new_competency_level?: number;
  competency_id?: number;
}

export const generateAssessment = (employeeId: number, competencyId: number, numberOfQuestions: number = 20) => {
  return api.post<GenerateAssessmentResponse>('/assessments/generate', {
    employee_id: employeeId,
    competency_id: competencyId,
    number_of_questions: numberOfQuestions
  });
};

export const getQuiz = (quizId: number) => {
  return api.get<Quiz>(`/quizzes/${quizId}`);
};

export const submitQuiz = (quizId: number, employeeId: number, answers: { question_id: number, answer: string }[]) => {
  return api.post<QuizSubmissionResponse>(`/quizzes/${quizId}/attempt`, {
    employee_id: employeeId,
    answers: answers
  });
};

export const getRecommendations = (employeeId: number) => {
  return api.get<RecommendationResponse>(`/recommendations/employee/${employeeId}`);
};
