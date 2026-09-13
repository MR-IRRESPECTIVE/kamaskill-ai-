'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { AppShell } from '@/components/layout/AppShell';
import { getRecommendations, RecommendationResponse, Recommendation } from '@/lib/api';

export default function LearningPage() {
  const [data, setData] = useState<RecommendationResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Hardcoded employee_id 1 for demo purposes
    getRecommendations(1)
      .then(res => {
        setData(res.data);
      })
      .catch(err => {
        console.error("Failed to load recommendations", err);
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <AppShell>
        <div className="flex items-center justify-center h-64">
          <div className="animate-pulse text-slate-500 font-medium">Loading Learning Recommendations...</div>
        </div>
      </AppShell>
    );
  }

  // Find the highest priority recommendation to highlight the gap
  // For the demo, we expect "Data Visualization" to be heavily prioritized if there's a gap
  const topRec = data?.recommendations?.[0];
  const primaryCompetency = topRec?.competency;
  const current = topRec?.current_level;
  const required = topRec?.required_level;
  const gap = topRec?.gap;

  return (
    <AppShell>
      <div className="max-w-4xl mx-auto space-y-8 mt-4">
        
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Your Priority Learning</h1>
            <p className="text-sm text-slate-500 mt-1">AI-curated content to bridge your competency gaps</p>
          </div>
          <Link 
            href="/"
            className="px-4 py-2 bg-white border border-slate-300 hover:bg-slate-50 text-slate-700 rounded-lg text-sm font-semibold transition-colors"
          >
            Back to Dashboard
          </Link>
        </div>

        {primaryCompetency && gap && gap > 0 ? (
          <div className="bg-brand-600 rounded-2xl p-6 text-white shadow-md relative overflow-hidden">
            <div className="absolute right-0 top-0 bottom-0 w-1/3 bg-gradient-to-l from-white/10 to-transparent pointer-events-none" />
            <div className="relative z-10">
              <h2 className="text-brand-100 text-sm font-bold tracking-wider uppercase mb-2">Primary Focus</h2>
              <h3 className="text-2xl font-bold mb-4">{primaryCompetency}</h3>
              
              <div className="flex items-center gap-6">
                <div>
                  <div className="text-brand-100 text-xs mb-1">Current Level</div>
                  <div className="text-xl font-bold">{current}%</div>
                </div>
                <div className="text-brand-300">→</div>
                <div>
                  <div className="text-brand-100 text-xs mb-1">Required Level</div>
                  <div className="text-xl font-bold">{required}%</div>
                </div>
                <div className="border-l border-brand-400/50 pl-6 ml-2">
                  <div className="text-brand-100 text-xs mb-1">Remaining Gap</div>
                  <div className="text-xl font-bold text-white">{gap} points</div>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="bg-white rounded-2xl border border-slate-200 p-6 text-center">
            <h3 className="text-slate-900 font-bold mb-2">You're all caught up!</h3>
            <p className="text-slate-500 text-sm">You currently meet or exceed all required competency levels.</p>
          </div>
        )}

        <div className="space-y-4">
          <h2 className="text-lg font-bold text-slate-900">Recommended Courses & Materials</h2>
          
          {data?.recommendations && data.recommendations.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {data.recommendations.map((rec: Recommendation, index: number) => (
                <div key={index} className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm hover:shadow-md transition-shadow relative overflow-hidden flex flex-col">
                  {/* Card Header */}
                  <div className="flex items-start justify-between mb-3">
                    <span className="inline-block px-2.5 py-1 bg-brand-50 text-brand-700 text-xs font-bold rounded-lg border border-brand-100">
                      {rec.type === 'course' ? 'Course' : 'Material'}
                    </span>
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wide
                      ${rec.priority === 'High' ? 'bg-amber-100 text-amber-700' : 
                        rec.priority === 'Medium' ? 'bg-blue-100 text-blue-700' : 
                        'bg-slate-100 text-slate-600'}
                    `}>
                      {rec.priority} Priority
                    </span>
                  </div>
                  
                  {/* Title & Competency */}
                  <h4 className="font-bold text-slate-900 text-base leading-tight mb-1">{rec.title}</h4>
                  <div className="text-xs text-brand-600 font-medium mb-3">Targeting: {rec.competency}</div>
                  
                  {/* Details / Meta */}
                  <div className="flex items-center gap-4 text-xs text-slate-500 mb-4">
                    {rec.type === 'course' ? (
                      <>
                        <div className="flex items-center gap-1">
                          <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                          {rec.duration} mins
                        </div>
                        <div className="flex items-center gap-1">
                          <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                          {rec.difficulty}
                        </div>
                        <div className="flex items-center gap-1">
                          <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
                          {rec.coverage}% coverage
                        </div>
                      </>
                    ) : (
                      <>
                        <div className="flex items-center gap-1">
                          <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
                          {rec.pages} pages
                        </div>
                        <div className="flex items-center gap-1">
                          <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" /></svg>
                          {rec.relevance}% relevance
                        </div>
                      </>
                    )}
                  </div>
                  
                  {/* Reason */}
                  <div className="mt-auto bg-slate-50 p-3 rounded-lg border border-slate-100">
                    <p className="text-xs text-slate-600 leading-relaxed italic">"{rec.reason}"</p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
             <div className="p-8 text-center bg-slate-50 rounded-xl border border-slate-200">
               <p className="text-slate-500">No recommendations available at this time.</p>
             </div>
          )}
        </div>

      </div>
    </AppShell>
  );
}
