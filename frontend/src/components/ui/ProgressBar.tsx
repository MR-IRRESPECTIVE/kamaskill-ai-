import { cn } from '@/lib/utils';

interface ProgressBarProps {
  progress: number;
  className?: string;
  colorClass?: string;
}

export function ProgressBar({ progress, className, colorClass = 'bg-brand-600' }: ProgressBarProps) {
  return (
    <div className={cn('h-2 w-full bg-slate-100 rounded-full overflow-hidden', className)}>
      <div 
        className={cn('h-full rounded-full transition-all duration-500 ease-out', colorClass)} 
        style={{ width: progress + '%' }}
      />
    </div>
  );
}
