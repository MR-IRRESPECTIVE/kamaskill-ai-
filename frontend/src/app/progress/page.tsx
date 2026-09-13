'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { AppShell } from '@/components/layout/AppShell';
import { api, EmployeeCompetency, QuizSubmissionResponse } from '@/lib/api';

export default function ProgressPage() {
  const [competencies, setCompetencies] = useState<EmployeeCompetency[]>([]);
  const [latestAssessment, setLatestAssessment] = useState<{ result: QuizSubmissionResponse, compInfo: any } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadData() {
      try {
        const compRes = await api.get('/competencies/employee/1');
        setCompetencies(compRes.data);

        // Find the latest assessment from sessionStorage
        // (Iterate through keys looking for quiz_result_)
        let foundResult = null;
        let foundCompInfo = null;
        
        for (let i = 0; i < sessionStorage.length; i++) {
          const key = sessionStorage.key(i);
          if (key && key.startsWith('quiz_result_')) {
            try {
              const resParsed = JSON.parse(sessionStorage.getItem(key) || '{}');
              if (resParsed && resParsed.competency_id) {
                foundResult = resParsed;
                const compInfoStr = sessionStorage.getItem(`comp_info_${resParsed.competency_id}`);
                if (compInfoStr) {
                  foundCompInfo = JSON.parse(compInfoStr);
                }
                break; // Just grab the first one we find for demo purposes
              }
            } catch (e) {
              // ignore parse errors
            }
          }
        }

        if (foundResult) {
          setLatestAssessment({ result: foundResult, compInfo: foundCompInfo });
        }
        
      } catch (err: any) {
        console.error('Failed to load progress data', err);
        setError(err.message || 'Failed to load progress data');
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  if (loading) {
    return (
      <AppShell>
        <div className="flex items-center justify-center h-64">
          <div className="animate-pulse text-slate-500 font-medium">Loading Progress...</div>
        </div>
      </AppShell>
    );
  }

  if (error) {
    return (
      <AppShell>
        <div className="p-6 bg-rose-50 border border-rose-200 rounded-xl text-rose-800">
          <h2 className="font-bold mb-2">Error Loading Progress</h2>
          <p className="text-sm">{error}</p>
        </div>
      </AppShell>
    );
  }

  // Find the primary competency we want to highlight (e.g. Data Visualization)
  // For demo purposes we can just use the first one, or the one from the latest assessment.
  const targetCompId = latestAssessment?.result.competency_id || competencies[0]?.competency.id;
  const primaryCompetency = competencies.find(c => c.competency.id === targetCompId) || competencies[0];

  return (
    <AppShell>
      <div className="max-w-5xl mx-auto space-y-6 mt-4">
        
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Your Progress</h1>
            <p className="text-sm text-slate-500 mt-1">Track your competency growth over time</p>
          </div>
          <div className="flex gap-3">
            <Link 
              href="/learning"
              className="px-4 py-2 bg-brand-50 text-brand-700 border border-brand-200 hover:bg-brand-100 rounded-lg text-sm font-semibold transition-colors"
            >
              Learning Plan
            </Link>
            <Link 
              href="/"
              className="px-4 py-2 bg-white border border-slate-300 hover:bg-slate-50 text-slate-700 rounded-lg text-sm font-semibold transition-colors"
            >
              Dashboard
            </Link>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          {/* Left Column: Overall Progress & Latest Assessment */}
          <div className="lg:col-span-1 space-y-6">
            
            <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 relative overflow-hidden">
              <div className="absolute top-0 left-0 right-0 h-1 bg-brand-500" />
              <h3 className="text-sm font-bold text-slate-900 mb-2">Overall Competency</h3>
              <div className="flex items-baseline gap-2">
                <span className="text-4xl font-black text-brand-600 tracking-tight">
                  {primaryCompetency?.current_level || 0}%
                </span>
                <span className="text-sm text-slate-500 font-medium">average</span>
              </div>
              <p className="text-xs text-slate-500 mt-3 leading-relaxed">
                Your combined competency score across all assigned domains.
              </p>
            </div>

            {latestAssessment ? (
              <div className="bg-gradient-to-br from-indigo-900 to-brand-900 rounded-2xl p-6 text-white shadow-md">
                <h3 className="text-xs font-bold text-indigo-200 uppercase tracking-wider mb-4">Latest Assessment</h3>
                <h4 className="text-lg font-bold mb-1">{latestAssessment.compInfo?.name || "Competency Assessment"}</h4>
                <div className="text-3xl font-black text-white mb-2">{latestAssessment.result.result.percentage}%</div>
                <p className="text-sm text-indigo-100/80 mb-6">{latestAssessment.result.result.score} / {latestAssessment.result.result.total_questions} correct</p>
                
                <div className="bg-white/10 rounded-xl p-4 border border-white/10">
                  <div className="text-xs text-indigo-200 mb-1">Competency Improvement</div>
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-lg">{latestAssessment.compInfo?.baseline || 0}%</span>
                    <span className="text-brand-300 font-bold">
                      +{ (latestAssessment.result.new_competency_level || 0) - (latestAssessment.compInfo?.baseline || 0) }
                    </span>
                    <span className="font-bold text-lg">{latestAssessment.result.new_competency_level || 0}%</span>
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-slate-50 rounded-2xl border border-slate-200 shadow-sm p-6 text-center">
                <h3 className="text-sm font-bold text-slate-900 mb-2">No Recent Assessments</h3>
                <p className="text-xs text-slate-500 mb-4">Take an assessment to track your progress and update your competency levels.</p>
                <Link href="/" className="inline-block px-4 py-2 bg-brand-600 text-white rounded-lg text-xs font-bold">
                  Go to Dashboard
                </Link>
              </div>
            )}
            
          </div>

          {/* Right Column: Competency Breakdown */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 h-full">
              <h3 className="text-base font-bold text-slate-900 mb-6">Competency Breakdown</h3>
              
              <div className="space-y-6">
                {competencies.length === 0 && (
                  <p className="text-sm text-slate-500 text-center py-8">No competencies found.</p>
                )}
                
                {competencies.map((comp, idx) => {
                  const current = comp.current_level;
                  const required = comp.required_level;
                  const gap = Math.max(required - current, 0);
                  const isCritical = gap >= 15;
                  
                  return (
                    <div key={idx} className="relative">
                      <div className="flex justify-between items-end mb-2">
                        <div>
                          <h4 className="text-sm font-bold text-slate-900">{comp.competency.name}</h4>
                          <span className="text-xs text-slate-500">{comp.competency.category}</span>
                        </div>
                        <div className="text-right">
                          <div className="text-sm font-bold text-slate-800">{current}% <span className="text-slate-400 font-normal text-xs">/ {required}% target</span></div>
                          {gap > 0 && (
                            <div className={`text-xs font-semibold ${isCritical ? 'text-rose-500' : 'text-amber-500'}`}>
                              {gap} points remaining
                            </div>
                          )}
                        </div>
                      </div>
                      
                      {/* Progress Bar */}
                      <div className="w-full bg-slate-100 h-3 rounded-full overflow-hidden relative">
                        {/* Target Marker */}
                        <div 
                          className="absolute top-0 bottom-0 w-0.5 bg-slate-400 z-10"
                          style={{ left: `${required}%` }}
                        ></div>
                        {/* Current Level */}
                        <div 
                          className={`absolute top-0 bottom-0 left-0 rounded-full transition-all duration-500 ${gap === 0 ? 'bg-emerald-500' : (isCritical ? 'bg-rose-500' : 'bg-brand-500')}`}
                          style={{ width: `${current}%` }}
                        ></div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
          
        </div>

      </div>
    </AppShell>
  );
}
