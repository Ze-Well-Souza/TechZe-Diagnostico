import React from 'react';

interface BentoGridProps {
  children: React.ReactNode;
  className?: string;
}

export const BentoGrid: React.FC<BentoGridProps> = ({ children, className = '' }) => {
  return (
    <div className={`grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-6 auto-rows-min ${className}`}>
      {children}
    </div>
  );
};

interface BentoItemProps {
  children: React.ReactNode;
  className?: string;
  cols?: 1 | 2 | 3 | 4;
  rows?: 1 | 2 | 3;
}

export const BentoItem: React.FC<BentoItemProps> = ({ 
  children, 
  className = '', 
  cols = 1, 
  rows = 1 
}) => {
  const colSpanClasses = {
    1: 'col-span-1',
    2: 'col-span-1 md:col-span-2',
    3: 'col-span-1 md:col-span-2 lg:col-span-3',
    4: 'col-span-1 md:col-span-3 lg:col-span-4'
  };

  const rowSpanClasses = {
    1: 'row-span-1',
    2: 'row-span-2',
    3: 'row-span-3'
  };

  return (
    <div className={`${colSpanClasses[cols]} ${rowSpanClasses[rows]} ${className}`}>
      {children}
    </div>
  );
};

export default BentoGrid; 