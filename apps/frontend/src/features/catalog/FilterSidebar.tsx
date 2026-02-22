import { useGetCategoriesQuery, useGetTiersQuery } from '../../store/api';

interface Props {
    selectedTier: number | undefined;
    selectedCategories: number[];
    onTierChange: (tier: number | undefined) => void;
    onCategoryToggle: (id: number) => void;
    onClear: () => void;
    hasFilters: boolean;
}

export default function FilterSidebar({
    selectedTier,
    selectedCategories,
    onTierChange,
    onCategoryToggle,
    onClear,
    hasFilters,
}: Props) {
    const { data: categories = [], isLoading: catLoading } = useGetCategoriesQuery();
    const { data: tiers = [], isLoading: tierLoading } = useGetTiersQuery();

    return (
        <aside className="w-full lg:w-72 shrink-0">
            <div className="sticky top-20 space-y-6 p-5 rounded-2xl bg-surface-light/40 backdrop-blur-sm border border-white/5">
                <div className="flex items-center justify-between">
                    <h2 className="text-lg font-semibold text-white flex items-center gap-2">
                        <svg className="w-5 h-5 text-primary-light" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
                        </svg>
                        Filters
                    </h2>
                    {hasFilters && (
                        <button
                            onClick={onClear}
                            className="text-xs font-medium text-accent hover:text-accent-dark transition-colors cursor-pointer"
                        >
                            Clear all
                        </button>
                    )}
                </div>

                {/* Tier filter */}
                <div>
                    <h3 className="text-sm font-medium text-text-muted uppercase tracking-wider mb-3">
                        Price Tier
                    </h3>
                    {tierLoading ? (
                        <div className="space-y-2">
                            {[1, 2, 3].map((i) => (
                                <div key={i} className="h-10 rounded-lg bg-surface-lighter/50 animate-pulse" />
                            ))}
                        </div>
                    ) : (
                        <div className="space-y-1.5">
                            {tiers.map((t) => (
                                <button
                                    key={t.id}
                                    onClick={() => onTierChange(selectedTier === t.id ? undefined : t.id)}
                                    className={`w-full text-left px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 cursor-pointer ${selectedTier === t.id
                                        ? 'bg-primary/20 text-primary-light border border-primary/30 shadow-sm shadow-primary/10'
                                        : 'text-text-muted hover:text-white hover:bg-white/5 border border-transparent'
                                        }`}
                                >
                                    {t.name}
                                </button>
                            ))}
                        </div>
                    )}
                </div>

                {/* Category filter */}
                <div>
                    <h3 className="text-sm font-medium text-text-muted uppercase tracking-wider mb-3">
                        Categories
                    </h3>
                    {catLoading ? (
                        <div className="space-y-2">
                            {[1, 2, 3, 4].map((i) => (
                                <div key={i} className="h-10 rounded-lg bg-surface-lighter/50 animate-pulse" />
                            ))}
                        </div>
                    ) : (
                        <div className="space-y-1.5 max-h-64 overflow-y-auto pr-1">
                            {categories.map((c) => {
                                const isActive = selectedCategories.includes(c.id);
                                return (
                                    <button
                                        key={c.id}
                                        onClick={() => onCategoryToggle(c.id)}
                                        className={`w-full text-left px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 flex items-center gap-2.5 cursor-pointer ${isActive
                                            ? 'bg-accent/15 text-accent border border-accent/25 shadow-sm shadow-accent/10'
                                            : 'text-text-muted hover:text-white hover:bg-white/5 border border-transparent'
                                            }`}
                                    >
                                        <span
                                            className={`w-4 h-4 rounded flex items-center justify-center border transition-all ${isActive
                                                ? 'bg-accent border-accent text-white'
                                                : 'border-border bg-transparent'
                                                }`}
                                        >
                                            {isActive && (
                                                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                                                </svg>
                                            )}
                                        </span>
                                        {c.name}
                                    </button>
                                );
                            })}
                        </div>
                    )}
                </div>

                {/* Required filter notice */}
                {!hasFilters && (
                    <div className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-400 text-xs">
                        <p className="font-medium">Select at least one filter</p>
                        <p className="mt-0.5 text-amber-400/70">Choose a tier or category to view products</p>
                    </div>
                )}
            </div>
        </aside>
    );
}
