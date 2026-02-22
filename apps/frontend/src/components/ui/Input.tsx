import { type InputHTMLAttributes, type FC } from 'react';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
    label?: string;
    error?: string;
}

export const Input: FC<InputProps> = ({ label, error, className = '', ...props }) => {
    return (
        <div className="space-y-1.5">
            {label && (
                <label className="block text-sm font-medium text-text-muted">
                    {label}
                </label>
            )}
            <input
                className={`
          w-full px-4 py-2.5 rounded-xl bg-surface-lighter/50 border 
          text-white placeholder-text-muted/50 focus:outline-none focus:ring-2 transition-all
          ${error
                        ? 'border-danger/50 focus:border-danger focus:ring-danger/20'
                        : 'border-white/10 focus:border-primary/50 focus:ring-primary/20'
                    }
          ${className}
        `}
                {...props}
            />
            {error && (
                <p className="text-xs text-danger">{error}</p>
            )}
        </div>
    );
};
