content = """
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
"""
with open("frontend/src/lib/api.ts", "a") as f:
    f.write(content)
