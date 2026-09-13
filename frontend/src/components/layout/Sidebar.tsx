import Link from 'next/link';
import { Home, Target, ClipboardList, BookOpen, TrendingUp, User, Settings, LogOut } from 'lucide-react';

export function Sidebar() {
  return (
    <aside className="w-64 bg-white border-r border-slate-200 flex flex-col flex-shrink-0 z-30 select-none">
      {/* Brand Header */}
      <div className="p-5 border-b border-slate-100 flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-700 via-brand-600 to-blue-500 flex items-center justify-center shadow-md shadow-brand-500/20 text-white flex-shrink-0">
          <Target className="w-6 h-6" />
        </div>
        <div>
          <div className="flex items-center gap-1.5">
            <span className="font-bold text-lg text-slate-900 tracking-tight">KarmaSkill</span>
            <span className="bg-brand-50 text-brand-700 font-extrabold text-xs px-1.5 py-0.5 rounded border border-brand-200">AI</span>
          </div>
          <p className="text-[11px] font-medium text-slate-400 leading-none mt-0.5">Learn. Grow. Serve Better.</p>
        </div>
      </div>
      
      {/* Navigation Menu */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        <Link href="/dashboard" className="flex items-center justify-between px-3.5 py-2.5 rounded-xl bg-brand-50/80 text-brand-700 font-semibold text-sm transition-all duration-150 group shadow-sm border border-brand-100">
          <div className="flex items-center gap-3">
            <Home className="w-5 h-5 text-brand-600" />
            <span>Dashboard</span>
          </div>
          <span className="w-1.5 h-4 bg-brand-600 rounded-full"></span>
        </Link>
        <Link href="/competencies" className="flex items-center justify-between px-3.5 py-2.5 rounded-xl text-slate-600 hover:bg-slate-50 hover:text-slate-900 font-medium text-sm transition-colors">
          <div className="flex items-center gap-3">
            <Target className="w-5 h-5 text-slate-400" />
            <span>Competency & Gaps</span>
          </div>
        </Link>
        <Link href="/assessments" className="flex items-center justify-between px-3.5 py-2.5 rounded-xl text-slate-600 hover:bg-slate-50 hover:text-slate-900 font-medium text-sm transition-colors">
          <div className="flex items-center gap-3">
            <ClipboardList className="w-5 h-5 text-slate-400" />
            <span>Assessments</span>
          </div>
        </Link>
        <Link href="/learning" className="flex items-center justify-between px-3.5 py-2.5 rounded-xl text-slate-600 hover:bg-slate-50 hover:text-slate-900 font-medium text-sm transition-colors">
          <div className="flex items-center gap-3">
            <BookOpen className="w-5 h-5 text-slate-400" />
            <span>Learning</span>
          </div>
        </Link>
        <Link href="/progress" className="flex items-center justify-between px-3.5 py-2.5 rounded-xl text-slate-600 hover:bg-slate-50 hover:text-slate-900 font-medium text-sm transition-colors">
          <div className="flex items-center gap-3">
            <TrendingUp className="w-5 h-5 text-slate-400" />
            <span>Progress</span>
          </div>
        </Link>
        <Link href="/profile" className="flex items-center justify-between px-3.5 py-2.5 rounded-xl text-slate-600 hover:bg-slate-50 hover:text-slate-900 font-medium text-sm transition-colors">
          <div className="flex items-center gap-3">
            <User className="w-5 h-5 text-slate-400" />
            <span>Profile</span>
          </div>
        </Link>
      </nav>

      {/* Sidebar Bottom: Settings & Logout */}
      <div className="p-3 border-t border-slate-100 space-y-1">
        <button className="w-full flex items-center gap-3 px-3.5 py-2 rounded-lg text-slate-600 hover:bg-slate-100 text-sm font-medium transition-colors">
          <Settings className="w-4 h-4 text-slate-400" />
          <span>Settings</span>
        </button>
        <button className="w-full flex items-center gap-3 px-3.5 py-2 rounded-lg text-slate-500 hover:text-rose-600 hover:bg-rose-50 text-sm font-medium transition-colors">
          <LogOut className="w-4 h-4" />
          <span>Logout</span>
        </button>
      </div>
    </aside>
  );
}
