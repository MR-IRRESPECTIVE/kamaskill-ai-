'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { AppShell } from '@/components/layout/AppShell';
import { QuizSubmissionResponse } from '@/lib/api';

export default function ResultPage() {
  const params = useParams();
  const router = useRouter();
  const quizId = params.quizId as string;
  
  const [resultData, setResultData] = useState<QuizSubmissionResponse | null>(null);
  const [compInfo, setCompInfo] = useState<{ baseline: number, required: number, name: string } | null>(null);

  useEffect(() => {
    // Read submission result
    const stored = sessionStorage.getItem(`quiz_result_${quizId}`);
    if (stored) {
      try {
        const parsed = JSON.parse(stored);
        setResultData(parsed);

        // Try to read competency info if available
        if (parsed.competency_id) {
          const compStored = sessionStorage.getItem(`comp_info_${parsed.competency_id}`);
          if (compStored) {
            setCompInfo(JSON.parse(compStored));
          }
        }
      } catch (e) {
        console.error("Failed to parse result", e);
      }
    }
  }, [quizId]);

  if (!resultData) {
    return (
      <AppShell>
        <div className="flex items-center justify-center h-64">
          <div className="animate-pulse text-slate-500 font-medium">Loading Results...</div>
        </div>
      </AppShell>
    );
  }

  const { result, new_competency_level } = resultData;
  const passed = result.percentage >= 70;

  // Calculate display-only values based on available info
  const baseline = compInfo?.baseline || 0;
  const required = compInfo?.required || 0;
  const updated = new_competency_level ?? baseline;
  const improvement = updated - baseline;
  const remainingGap = Math.max(required - updated, 0);

  return (
    <AppShell>
      <div className="max-w-3xl mx-auto space-y-6 mt-6">
        
        {/* Top Result Card */}
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-8 text-center space-y-4 relative overflow-hidden">
          <div className="absolute top-0 left-0 right-0 h-2 bg-gradient-to-r from-brand-400 to-indigo-500" />
          
          <div className="pt-2">
            <h2 className="text-xs font-bold tracking-widest text-slate-400 uppercase mb-1">Assessment Complete</h2>
            <h1 className="text-2xl font-bold text-slate-900">
              {compInfo?.name || "Competency Assessment"}
            </h1>
          </div>

          <div className="py-6 flex flex-col items-center justify-center">
            <div className="text-5xl font-black text-brand-600 tracking-tight">
              {result.percentage}%
            </div>
            <div className="text-sm font-medium text-slate-500 mt-2">
              {result.score} / {result.total_questions} correct
            </div>
          </div>
        </div>

        {/* Competency Update Card */}
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 lg:p-8">
          <h3 className="text-sm font-bold text-slate-900 mb-6 uppercase tracking-wider">Competency Improvement</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="flex flex-col items-center text-center p-4 bg-slate-50 rounded-xl border border-slate-100 relative">
              <span className="text-xs text-slate-500 font-medium mb-1">Baseline</span>
              <span className="text-3xl font-bold text-slate-800">{baseline}%</span>
              
              {/* Arrow linking to updated */}
              {improvement > 0 && (
                <div className="hidden md:flex absolute -right-3 top-1/2 -translate-y-1/2 z-10 w-6 h-6 bg-brand-100 text-brand-600 rounded-full items-center justify-center shadow-sm">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-4 h-4">
                    <path fillRule="evenodd" d="M3 10a.75.75 0 01.75-.75h10.638L10.23 5.29a.75.75 0 111.04-1.08l5.5 5.25a.75.75 0 010 1.08l-5.5 5.25a.75.75 0 11-1.04-1.08l4.158-3.96H3.75A.75.75 0 013 10z" clipRule="evenodd" />
                  </svg>
                </div>
              )}
            </div>

            <div className="flex flex-col items-center text-center p-4 bg-brand-50 rounded-xl border border-brand-100 relative">
              <span className="absolute -top-3 bg-brand-600 text-white text-[10px] font-bold px-2 py-0.5 rounded-full shadow-sm">
                +{improvement} points
              </span>
              <span className="text-xs text-brand-600/80 font-medium mb-1 pt-1">Updated</span>
              <span className="text-3xl font-bold text-brand-700">{updated}%</span>
            </div>

            <div className="flex flex-col items-center justify-center p-4">
              <div className="w-full text-center">
                <span className="text-xs text-slate-500 block mb-1">Required Level</span>
                <span className="font-bold text-slate-800 text-xl">{required}%</span>
              </div>
              <div className="w-full text-center mt-3 pt-3 border-t border-slate-100">
                <span className="text-xs text-slate-500 block mb-1">Remaining Gap</span>
                <span className="font-bold text-amber-600 text-lg">{remainingGap} points</span>
              </div>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row gap-3 pt-4 border-t border-slate-100">
            <Link 
              href="/learning"
              className="flex-1 px-6 py-3 bg-brand-600 hover:bg-brand-700 text-white text-center rounded-xl text-sm font-semibold shadow-sm transition-colors"
            >
              Continue Learning
            </Link>
            <Link 
              href="/"
              className="flex-1 px-6 py-3 bg-white border-2 border-slate-200 hover:border-slate-300 hover:bg-slate-50 text-slate-700 text-center rounded-xl text-sm font-semibold transition-colors"
            >
              Back to Dashboard
            </Link>
          </div>
        </div>

      </div>
    </AppShell>
  );
}
