import { type FC, type ReactNode } from 'react';

interface ModalProps {
    isOpen: boolean;
    onClose: () => void;
    title: string;
    children: ReactNode;
}

export const Modal: FC<ModalProps> = ({ isOpen, onClose, title, children }) => {
    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 overflow-y-auto">
            <div className="flex min-h-screen items-center justify-center p-4">
                {/* Backdrop */}
                <div
                    className="fixed inset-0 bg-black/60 backdrop-blur-sm transition-opacity"
                    onClick={onClose}
                />

                {/* Modal Panel */}
                <div className="relative w-full max-w-lg transform rounded-2xl bg-surface border border-white/10 p-6 shadow-2xl transition-all">
                    <div className="flex items-center justify-between mb-6">
                        <h3 className="text-lg font-semibold text-white">
                            {title}
                        </h3>
                        <button
                            onClick={onClose}
                            className="p-1 rounded-lg text-text-muted hover:text-white hover:bg-white/5 transition-colors"
                        >
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </button>
                    </div>
                    {children}
                </div>
            </div>
        </div>
    );
};
