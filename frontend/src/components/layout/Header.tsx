import { Search, Bell } from 'lucide-react';
import { useEffect, useState } from 'react';
import { api, Employee } from '@/lib/api';

export function Header() {
  const [employee, setEmployee] = useState<Employee | null>(null);

  useEffect(() => {
    api.get('/employees/1')
      .then(res => setEmployee(res.data))
      .catch(err => console.error('Failed to fetch employee', err));
  }, []);

  return (
    <header className="h-16 bg-white border-b border-slate-200 px-6 flex items-center justify-between flex-shrink-0 z-20">
      <div className="w-80 md:w-96">
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
            <Search className="w-4 h-4" />
          </div>
          <input 
            className="w-full pl-9 pr-4 py-1.5 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:bg-white transition-all shadow-inner" 
            placeholder="Search skills, competencies, courses..." 
            type="text"
          />
        </div>
      </div>
      
      <div className="flex items-center gap-3">
        <button aria-label="Notifications" className="relative p-2 rounded-xl text-slate-500 hover:bg-slate-100 transition-colors focus:outline-none" type="button">
          <Bell className="w-5 h-5" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-rose-500 rounded-full border-2 border-white"></span>
        </button>
        <div className="h-6 w-px bg-slate-200"></div>
        
        <div className="flex items-center gap-2.5 pl-1 cursor-pointer group">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-brand-800 to-slate-900 text-white flex items-center justify-center font-bold text-xs shadow-sm ring-2 ring-slate-100">
            {employee ? employee.name.split(' ').map(n => n[0]).join('') : 'RS'}
          </div>
          <div className="text-left hidden sm:block">
            <span className="text-xs font-bold text-slate-800 leading-none group-hover:text-brand-600 transition-colors block">
              {employee ? employee.name : 'Loading...'}
            </span>
            <p className="text-[11px] text-slate-400 leading-tight mt-0.5">
              {employee ? (employee.role + ' • S' + (100 + employee.id)) : '...'}
            </p>
          </div>
        </div>
      </div>
    </header>
  );
}
