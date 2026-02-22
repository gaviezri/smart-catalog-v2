import { memo } from 'react';

interface Props {
    currentPage: number;
    totalPages: number;
    onPageChange: (page: number) => void;
}

// Check types via memo to prevent unnecessary re-renders
const Pagination = memo(function Pagination({ currentPage, totalPages, onPageChange }: Props) {
    if (totalPages <= 1) return null;

    const getPages = () => {
        const pages: (number | string)[] = [];
        const delta = 2;
        const left = Math.max(0, currentPage - delta);
        const right = Math.min(totalPages - 1, currentPage + delta);

        if (left > 0) {
            pages.push(0);
            if (left > 1) pages.push('...');
        }
        for (let i = left; i <= right; i++) {
            pages.push(i);
        }
        if (right < totalPages - 1) {
            if (right < totalPages - 2) pages.push('...');
            pages.push(totalPages - 1);
        }
        return pages;
    };

    return (
        <div className="flex items-center justify-center gap-1.5 mt-8">
            <button
                type="button"
                onClick={() => onPageChange(currentPage - 1)}
                disabled={currentPage === 0}
                className="px-3 py-2 rounded-lg text-sm font-medium bg-white/5 hover:bg-white/10 text-text-muted hover:text-white border border-white/10 transition-all disabled:opacity-30 disabled:cursor-not-allowed cursor-pointer"
            >
                ← Prev
            </button>

            {getPages().map((p, idx) =>
                typeof p === 'string' ? (
                    <span key={`e-${idx}`} className="px-2 text-text-muted">
                        …
                    </span>
                ) : (
                    <button
                        key={p}
                        type="button"
                        onClick={() => onPageChange(p)}
                        className={`w-10 h-10 rounded-lg text-sm font-medium transition-all cursor-pointer ${p === currentPage
                            ? 'bg-primary text-white shadow-lg shadow-primary/30'
                            : 'bg-white/5 hover:bg-white/10 text-text-muted hover:text-white border border-white/10'
                            }`}
                    >
                        {p + 1}
                    </button>
                )
            )}

            <button
                type="button"
                onClick={() => onPageChange(currentPage + 1)}
                disabled={currentPage >= totalPages - 1}
                className="px-3 py-2 rounded-lg text-sm font-medium bg-white/5 hover:bg-white/10 text-text-muted hover:text-white border border-white/10 transition-all disabled:opacity-30 disabled:cursor-not-allowed cursor-pointer"
            >
                Next →
            </button>
        </div>
    );
});

export default Pagination;
