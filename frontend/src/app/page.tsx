'use client';

import { useEffect, useState } from 'react';
import { api, Employee, EmployeeCompetency, RecommendationResponse } from '@/lib/api';
import Link from 'next/link';
import { AppShell } from '@/components/layout/AppShell';

export default function Dashboard() {
  const [employee, setEmployee] = useState<Employee | null>(null);
  const [competencies, setCompetencies] = useState<EmployeeCompetency[]>([]);
  const [recommendations, setRecommendations] = useState<RecommendationResponse | null>(null);
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadData() {
      try {
        const empRes = await api.get('/employees/1');
        setEmployee(empRes.data);

        const compRes = await api.get('/competencies/employee/1');
        setCompetencies(compRes.data);

        const recRes = await api.get('/recommendations/employee/1');
        setRecommendations(recRes.data);
      } catch (err: any) {
        console.error('Failed to load dashboard data', err);
        setError(err.message || 'Failed to load dashboard data');
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  if (loading) {
    return (
      <AppShell>
        <div className="flex items-center justify-center h-full">
          <div className="animate-pulse text-slate-500 font-medium">Loading Dashboard...</div>
        </div>
      </AppShell>
    );
  }

  if (error) {
    return (
      <AppShell>
        <div className="p-6 bg-rose-50 border border-rose-200 rounded-xl text-rose-800">
          <h2 className="font-bold mb-2">Error Loading Dashboard</h2>
          <p className="text-sm">{error}</p>
          <p className="text-xs mt-2 opacity-70">Check console for details. Make sure FastAPI is running on port 8000.</p>
        </div>
      </AppShell>
    );
  }
  
  return (
    <AppShell>
      {/* Hero Banner */}
      <section className="bg-gradient-to-r from-brand-900 via-brand-800 to-indigo-950 rounded-2xl p-6 text-white shadow-sm relative overflow-hidden">
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-5">
          <div className="space-y-1">
            <h1 className="text-2xl font-bold tracking-tight text-white sm:text-3xl">
              Good Morning, {employee?.name.split(' ')[0]}!
            </h1>
            <p className="text-sm text-brand-100 max-w-xl">
              Keep learning. Keep growing. Build a stronger tomorrow.
            </p>
          </div>
          <div className="bg-white/10 backdrop-blur-md rounded-xl p-3.5 border border-white/15 max-w-sm flex-shrink-0">
            <p className="text-xs italic text-brand-50 leading-relaxed font-normal">
              &quot;Continuous learning builds a stronger, more capable public service.&quot;
            </p>
          </div>
        </div>
      </section>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left Column (7 cols) */}
        <div className="lg:col-span-7 space-y-6">
          <section className="bg-white rounded-2xl border border-slate-200/80 shadow-sm p-5">
            <h3 className="text-sm font-bold text-slate-900 mb-4">Priority Competency Gaps</h3>
            <div className="space-y-4">
              {competencies.length === 0 && (
                <p className="text-sm text-slate-500">No competencies found.</p>
              )}
              {competencies.map((comp, idx) => {
                const required = comp.required_level;
                const current = comp.current_level;
                const gap = required - current;
                const isCritical = gap >= 15;
                
                if (gap <= 0) return null;

                return (
                  <div key={idx} className={'p-4 rounded-xl border ' + (isCritical ? 'border-rose-200/70 bg-rose-50/20' : 'border-amber-200/70 bg-amber-50/20')}>
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                      <div className="flex items-center gap-2">
                        <span className={'w-2.5 h-2.5 rounded-full flex-shrink-0 ' + (isCritical ? 'bg-rose-500' : 'bg-amber-500')}></span>
                        <h3 className="text-sm font-bold text-slate-900">{comp.competency.name}</h3>
                        <span className={'px-2 py-0.5 text-[10px] font-bold rounded ' + (isCritical ? 'bg-rose-100 text-rose-800' : 'bg-amber-100 text-amber-800')}>
                          {isCritical ? 'Critical Gap' : 'Moderate Gap'}
                        </span>
                      </div>
                      <Link 
                        href={`/assessment?competencyId=${comp.competency.id}`}
                        className="text-xs font-semibold bg-white border border-slate-300 text-slate-700 px-3 py-1.5 rounded-lg hover:bg-slate-50 inline-block text-center"
                      >
                        Take Assessment
                      </Link>
                    </div>
                    
                    <div className="grid grid-cols-3 gap-2 mt-3 text-center py-2 px-3 bg-white/70 rounded-lg border border-slate-200/60 text-xs">
                      <div>
                        <span className="text-[11px] text-slate-500 block">Current</span>
                        <span className="font-bold text-slate-800">{current}%</span>
                      </div>
                      <div>
                        <span className="text-[11px] text-slate-500 block">Required</span>
                        <span className="font-bold text-slate-800">{required}%</span>
                      </div>
                      <div>
                        <span className="text-[11px] text-slate-500 block">Gap</span>
                        <span className={'font-bold ' + (isCritical ? 'text-rose-600' : 'text-amber-600')}>-{gap}%</span>
                      </div>
                    </div>

                    <div className="mt-3">
                      <div className="relative w-full bg-slate-100 h-2.5 rounded-full overflow-hidden">
                        <div className="absolute left-0 top-0 bottom-0 bg-slate-200 rounded-full" style={{ width: required + '%' }}></div>
                        <div className={'absolute left-0 top-0 bottom-0 rounded-full ' + (isCritical ? 'bg-rose-500' : 'bg-amber-500')} style={{ width: current + '%' }}></div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </section>
        </div>

        {/* Right Column (5 cols) */}
        <div className="lg:col-span-5 space-y-6">
          <section id="recommendations" className="bg-white rounded-2xl border border-slate-200/80 shadow-sm p-5">
            <h3 className="text-sm font-bold text-slate-900 mb-4">Recommended Learning</h3>
            <div className="space-y-3.5">
              {recommendations?.recommendations?.length === 0 && (
                <p className="text-sm text-slate-500">No recommendations currently available.</p>
              )}
              {recommendations?.recommendations?.map((rec, idx) => (
                <div key={idx} className="p-3.5 rounded-xl border border-slate-200 bg-slate-50/50 hover:bg-white hover:border-brand-300 hover:shadow-sm transition-all">
                  <div className="flex items-center justify-between gap-2">
                    <span className={'text-[10px] font-bold px-2 py-0.5 rounded border ' + (rec.priority === 'High' ? 'text-rose-700 bg-rose-50 border-rose-200' : 'text-amber-700 bg-amber-50 border-amber-200')}>
                      Addresses: {rec.competency} • Gap: {rec.gap}%
                    </span>
                    <span className="text-[11px] text-slate-400">{rec.duration} weeks • {rec.difficulty}</span>
                  </div>
                  <h4 className="text-xs font-bold text-slate-900 mt-2">{rec.title}</h4>
                  <p className="text-[11px] text-slate-500 mt-1 leading-relaxed line-clamp-2">
                    {rec.reason}
                  </p>
                  <div className="mt-3 flex justify-end">
                    <button className="px-3 py-1 bg-brand-600 hover:bg-brand-700 text-white rounded-lg text-xs font-semibold shadow-sm transition-colors">
                      Start Learning
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </section>
        </div>
      </div>
    </AppShell>
  );
}
