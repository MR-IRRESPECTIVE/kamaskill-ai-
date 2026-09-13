'use client';

import { useState, useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { api, EmployeeCompetency, generateAssessment } from '@/lib/api';
import { AppShell } from '@/components/layout/AppShell';

function AssessmentContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const competencyId = searchParams.get('competencyId');

  const [competencyInfo, setCompetencyInfo] = useState<EmployeeCompetency | null>(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadData() {
      if (!competencyId) {
        setError("No competency specified.");
        setLoading(false);
        return;
      }

      try {
        const compRes = await api.get('/competencies/employee/1');
        const comps: EmployeeCompetency[] = compRes.data;
        const target = comps.find(c => c.competency.id.toString() === competencyId);
        
        if (target) {
          setCompetencyInfo(target);
        } else {
          setError("Competency not found for this employee.");
        }
      } catch (err: any) {
        console.error('Failed to load competency', err);
        setError('Failed to load competency data.');
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [competencyId]);

  const handleStartAssessment = async () => {
    if (!competencyId || !competencyInfo) return;
    
    setGenerating(true);
    setError(null);
    try {
      sessionStorage.setItem(`comp_info_${competencyId}`, JSON.stringify({
        baseline: competencyInfo.current_level,
        required: competencyInfo.required_level,
        name: competencyInfo.competency.name
      }));

      const response = await generateAssessment(1, parseInt(competencyId, 10), 20);
      const quizId = response.data.quiz_id;
      if (quizId) {
        router.push(`/quiz/${quizId}`);
      } else {
        setError('Failed to retrieve quiz ID from generation response.');
        setGenerating(false);
      }
    } catch (err: any) {
      console.error('Failed to generate assessment', err);
      setError(err.response?.data?.detail || err.message || 'Failed to generate assessment.');
      setGenerating(false);
    }
  };

  if (loading) {
    return (
      <AppShell>
        <div className="flex items-center justify-center h-64">
          <div className="animate-pulse text-slate-500 font-medium">Loading Assessment Info...</div>
        </div>
      </AppShell>
    );
  }

  return (
    <AppShell>
      <div className="max-w-3xl mx-auto space-y-6 mt-6">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">
            Start Assessment
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Complete this assessment to close your competency gap.
          </p>
        </div>

        {error && (
          <div className="p-4 bg-rose-50 border border-rose-200 rounded-xl text-rose-800 text-sm">
            {error}
          </div>
        )}

        {competencyInfo && (
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 space-y-6">
            <div>
              <h2 className="text-xl font-bold text-slate-900">
                {competencyInfo.competency.name}
              </h2>
              <p className="text-sm text-slate-600 mt-2">
                {competencyInfo.competency.description}
              </p>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-4 bg-slate-50 rounded-xl border border-slate-100">
              <div>
                <span className="text-xs text-slate-500 block">Current Level</span>
                <span className="font-bold text-slate-800 text-lg">{competencyInfo.current_level}%</span>
              </div>
              <div>
                <span className="text-xs text-slate-500 block">Required Level</span>
                <span className="font-bold text-slate-800 text-lg">{competencyInfo.required_level}%</span>
              </div>
              <div>
                <span className="text-xs text-slate-500 block">Questions</span>
                <span className="font-bold text-slate-800 text-lg">20</span>
              </div>
              <div>
                <span className="text-xs text-slate-500 block">Est. Duration</span>
                <span className="font-bold text-slate-800 text-lg">25 mins</span>
              </div>
            </div>

            <div className="pt-4 border-t border-slate-100 flex justify-end">
              <button
                onClick={handleStartAssessment}
                disabled={generating}
                className="px-6 py-2.5 bg-brand-600 hover:bg-brand-700 disabled:bg-brand-400 text-white rounded-lg text-sm font-semibold shadow-sm transition-colors flex items-center justify-center min-w-[200px]"
              >
                {generating ? 'Generating Quiz...' : 'Start Assessment'}
              </button>
            </div>
            {generating && (
              <div className="text-xs text-slate-500 text-right mt-2 animate-pulse">
                Please wait, AI is generating your unique assessment...
              </div>
            )}
          </div>
        )}
      </div>
    </AppShell>
  );
}

export default function AssessmentPage() {
  return (
    <Suspense fallback={
      <AppShell>
        <div className="flex items-center justify-center h-64">
          <div className="animate-pulse text-slate-500 font-medium">Loading...</div>
        </div>
      </AppShell>
    }>
      <AssessmentContent />
    </Suspense>
  );
}
