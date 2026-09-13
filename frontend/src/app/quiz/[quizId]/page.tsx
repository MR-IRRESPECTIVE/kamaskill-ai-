'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { getQuiz, submitQuiz, Quiz } from '@/lib/api';
import { AppShell } from '@/components/layout/AppShell';

export default function QuizPage() {
  const params = useParams();
  const router = useRouter();
  const quizId = parseInt(params.quizId as string, 10);

  const [quiz, setQuiz] = useState<Quiz | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const [currentQuestionIdx, setCurrentQuestionIdx] = useState(0);
  const [answers, setAnswers] = useState<Record<number, string>>({});
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    async function fetchQuizData() {
      if (!quizId || isNaN(quizId)) {
        setError('Invalid quiz ID');
        setLoading(false);
        return;
      }

      try {
        const response = await getQuiz(quizId);
        setQuiz(response.data);
      } catch (err: any) {
        console.error('Failed to load quiz', err);
        setError(err.response?.data?.detail || 'Failed to load quiz data.');
      } finally {
        setLoading(false);
      }
    }
    fetchQuizData();
  }, [quizId]);

  const handleSelectOption = (questionId: number, optionKey: string) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: optionKey
    }));
  };

  const handleNext = () => {
    if (quiz && currentQuestionIdx < quiz.questions.length - 1) {
      setCurrentQuestionIdx(prev => prev + 1);
    }
  };

  const handlePrev = () => {
    if (currentQuestionIdx > 0) {
      setCurrentQuestionIdx(prev => prev - 1);
    }
  };

  const handleSubmit = async () => {
    if (!quiz) return;
    
    // Check if all questions are answered
    const unansweredCount = quiz.questions.length - Object.keys(answers).length;
    if (unansweredCount > 0) {
      const confirmSubmit = window.confirm(`You have ${unansweredCount} unanswered questions. Are you sure you want to submit?`);
      if (!confirmSubmit) return;
    }

    setSubmitting(true);
    setError(null);
    try {
      const answersList = Object.entries(answers).map(([qId, ans]) => ({
        question_id: parseInt(qId, 10),
        answer: ans
      }));

      const response = await submitQuiz(quizId, 1, answersList);
      sessionStorage.setItem(`quiz_result_${quizId}`, JSON.stringify(response.data));
      router.push(`/quiz/${quizId}/result`);
    } catch (err: any) {
      console.error('Submission failed', err);
      setError(err.response?.data?.detail || 'Failed to submit quiz.');
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <AppShell>
        <div className="flex items-center justify-center h-64">
          <div className="animate-pulse text-slate-500 font-medium">Loading Quiz...</div>
        </div>
      </AppShell>
    );
  }

  if (error || !quiz) {
    return (
      <AppShell>
        <div className="p-6 bg-rose-50 border border-rose-200 rounded-xl text-rose-800">
          <h2 className="font-bold mb-2">Error</h2>
          <p className="text-sm">{error || 'Unknown error'}</p>
        </div>
      </AppShell>
    );
  }

  const currentQuestion = quiz.questions[currentQuestionIdx];
  const selectedAnswer = answers[currentQuestion.id];
  const totalQuestions = quiz.questions.length;
  const progressPercent = ((Object.keys(answers).length) / totalQuestions) * 100;
  const isLastQuestion = currentQuestionIdx === totalQuestions - 1;

  return (
    <AppShell>
      <div className="max-w-3xl mx-auto space-y-6 mt-6">
        
        {/* Header & Progress */}
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
          <div className="flex justify-between items-center mb-4">
            <h1 className="text-lg font-bold text-slate-900">{quiz.title}</h1>
            <span className="text-sm font-medium text-slate-500">
              Question {currentQuestionIdx + 1} of {totalQuestions}
            </span>
          </div>
          <div className="relative w-full bg-slate-100 h-2 rounded-full overflow-hidden">
            <div 
              className="absolute left-0 top-0 bottom-0 bg-brand-500 transition-all duration-300"
              style={{ width: `${progressPercent}%` }}
            ></div>
          </div>
        </div>

        {/* Question Card */}
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 lg:p-8">
          <h2 className="text-xl font-bold text-slate-800 leading-relaxed mb-8">
            {currentQuestionIdx + 1}. {currentQuestion.question}
          </h2>

          <div className="space-y-3">
            {Object.entries(currentQuestion.options).map(([key, text]) => {
              const isSelected = selectedAnswer === key;
              return (
                <button
                  key={key}
                  onClick={() => handleSelectOption(currentQuestion.id, key)}
                  className={`w-full text-left p-4 rounded-xl border-2 transition-all ${
                    isSelected 
                      ? 'border-brand-500 bg-brand-50 text-brand-900' 
                      : 'border-slate-100 bg-white hover:border-slate-200 hover:bg-slate-50 text-slate-700'
                  }`}
                >
                  <div className="flex items-start gap-3">
                    <span className={`flex-shrink-0 w-6 h-6 rounded-full border flex items-center justify-center text-xs font-bold ${
                      isSelected ? 'border-brand-500 bg-brand-500 text-white' : 'border-slate-300 text-slate-500'
                    }`}>
                      {key}
                    </span>
                    <span className="font-medium text-sm pt-0.5">{text}</span>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Navigation */}
        <div className="flex items-center justify-between">
          <button
            onClick={handlePrev}
            disabled={currentQuestionIdx === 0}
            className="px-5 py-2.5 bg-white border border-slate-200 text-slate-700 rounded-lg text-sm font-semibold hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Previous
          </button>

          {isLastQuestion ? (
            <button
              onClick={handleSubmit}
              disabled={submitting}
              className="px-6 py-2.5 bg-brand-600 hover:bg-brand-700 text-white rounded-lg text-sm font-semibold shadow-sm transition-colors disabled:opacity-70"
            >
              {submitting ? 'Submitting...' : 'Submit Assessment'}
            </button>
          ) : (
            <button
              onClick={handleNext}
              className="px-6 py-2.5 bg-brand-600 hover:bg-brand-700 text-white rounded-lg text-sm font-semibold shadow-sm transition-colors"
            >
              Next Question
            </button>
          )}
        </div>
      </div>
    </AppShell>
  );
}
