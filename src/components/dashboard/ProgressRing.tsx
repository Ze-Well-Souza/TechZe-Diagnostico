import React from 'react';

interface ProgressRingProps {
  value: number; // 0-100
  size?: number;
  strokeWidth?: number;
  color?: 'green' | 'yellow' | 'red' | 'blue' | 'purple';
  showValue?: boolean;
  className?: string;
}

export const ProgressRing: React.FC<ProgressRingProps> = ({
  value,
  size = 120,
  strokeWidth = 8,
  color = 'blue',
  showValue = true,
  className = ''
}) => {
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const offset = circumference - (value / 100) * circumference;

  const colorMap = {
    green: 'stroke-green-400',
    yellow: 'stroke-yellow-400', 
    red: 'stroke-red-400',
    blue: 'stroke-blue-400',
    purple: 'stroke-purple-400'
  };

  const glowColorMap = {
    green: 'drop-shadow-[0_0_8px_rgba(34,197,94,0.4)]',
    yellow: 'drop-shadow-[0_0_8px_rgba(251,191,36,0.4)]',
    red: 'drop-shadow-[0_0_8px_rgba(239,68,68,0.4)]',
    blue: 'drop-shadow-[0_0_8px_rgba(59,130,246,0.4)]',
    purple: 'drop-shadow-[0_0_8px_rgba(147,51,234,0.4)]'
  };

  return (
    <div className={`relative inline-flex items-center justify-center ${className}`}>
      <svg
        width={size}
        height={size}
        className="transform -rotate-90"
      >
        {/* Background circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="currentColor"
          strokeWidth={strokeWidth}
          fill="transparent"
          className="text-white/10"
        />
        
        {/* Progress circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="currentColor"
          strokeWidth={strokeWidth}
          fill="transparent"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          className={`${colorMap[color]} ${glowColorMap[color]} transition-all duration-500 ease-in-out`}
        />
      </svg>
      
      {showValue && (
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center">
            <div className="text-2xl font-bold text-white">
              {Math.round(value)}%
            </div>
            <div className="text-xs text-slate-400">
              Saúde
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProgressRing; 