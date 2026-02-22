import { type FC, type ReactNode } from 'react';

interface CardProps {
    children: ReactNode;
    className?: string;
    hoverEffect?: boolean;
}

export const Card: FC<CardProps> = ({ children, className = '', hoverEffect = false }) => {
    return (
        <div
            className={`
        bg-surface-light/40 border border-white/5 rounded-2xl overflow-hidden backdrop-blur-sm
        ${hoverEffect ? 'hover:border-primary/30 hover:shadow-lg hover:shadow-primary/5 transition-all duration-300 group' : ''}
        ${className}
      `}
        >
            {children}
        </div>
    );
};
