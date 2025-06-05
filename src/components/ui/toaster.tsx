import React from 'react';

interface ToasterProps {
  className?: string;
}

export const Toaster: React.FC<ToasterProps> = ({ className }) => {
  return (
    <div className={`fixed bottom-4 right-4 z-50 ${className || ''}`}>
      {/* Toaster implementation will be added later */}
    </div>
  );
};

export default Toaster; 