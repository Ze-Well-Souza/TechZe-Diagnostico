
import React from 'react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

interface TechCardProps {
  children: React.ReactNode;
  className?: string;
  variant?: 'glass' | 'solid' | 'gradient';
  hover?: boolean;
  animate?: boolean;
}

export const TechCard: React.FC<TechCardProps> = ({
  children,
  className,
  variant = 'glass',
  hover = true,
  animate = true
}) => {
  const baseClasses = 'rounded-xl p-6 transition-all duration-300';
  
  const variantClasses = {
    glass: 'glass-card',
    solid: 'bg-gray-900 border border-gray-800',
    gradient: 'bg-gradient-to-br from-blue-600/20 to-green-600/20 border border-blue-500/30'
  };

  const CardComponent = animate ? motion.div : 'div';

  return (
    <CardComponent
      className={cn(
        baseClasses,
        variantClasses[variant],
        hover && 'tech-hover',
        className
      )}
      {...(animate && {
        initial: { opacity: 0, y: 20 },
        animate: { opacity: 1, y: 0 },
        transition: { duration: 0.5 }
      })}
    >
      {children}
    </CardComponent>
  );
};
