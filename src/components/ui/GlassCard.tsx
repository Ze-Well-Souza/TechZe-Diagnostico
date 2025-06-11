import React from 'react';
import { cn } from '@/lib/utils';

interface GlassCardProps {
  children: React.ReactNode;
  className?: string;
  hover?: boolean;
  glow?: boolean;
}

export const GlassCard: React.FC<GlassCardProps> = ({ 
  children, 
  className = '', 
  hover = true,
  glow = false
}) => {
  return (
    <div className={cn(
      // Base glassmorphism styles
      "backdrop-blur-xl bg-white/5 dark:bg-black/10",
      "border border-white/10 dark:border-white/5",
      "rounded-2xl",
      "shadow-xl shadow-black/20",
      
      // Hover effects
      hover && "hover:scale-[1.02] hover:shadow-2xl hover:shadow-black/30 transition-all duration-300",
      hover && "hover:bg-white/10 dark:hover:bg-black/20",
      
      // Glow effect
      glow && "ring-1 ring-electric/20 shadow-electric/10",
      
      className
    )}>
      {children}
    </div>
  );
};

export default GlassCard; 