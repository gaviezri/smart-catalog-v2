import { useState } from 'react';
import { useGetProductsQuery } from '../../store/api';
import { useAppSelector } from '../../store/hooks';
import FilterSidebar from './FilterSidebar';
import ProductCard from './ProductCard';
import Pagination from './Pagination';
import AddProductModal from '../admin/AddProductModal';
import { Button } from '../../components/ui/Button';

export default function ProductListContainer() {
    const role = useAppSelector((s) => s.auth.role);
    const [selectedTier, setSelectedTier] = useState<number | undefined>(undefined);
    const [selectedCategories, setSelectedCategories] = useState<number[]>([]);
    const [page, setPage] = useState(0);
    const [pageSize, setPageSize] = useState(12);
    const [showAddModal, setShowAddModal] = useState(false);

    const hasFilters = selectedTier !== undefined || selectedCategories.length > 0;

    const { data, isLoading, isFetching, error } = useGetProductsQuery(
        {
            tier: selectedTier,
            categories: selectedCategories,
            page,
            size: pageSize,
        },
        { skip: !hasFilters }
    );

    const handleTierChange = (tier: number | undefined) => {
        setSelectedTier(tier);
        setPage(0);
    };

    const handleCategoryToggle = (id: number) => {
        setSelectedCategories((prev) =>
            prev.includes(id) ? prev.filter((c) => c !== id) : [...prev, id]
        );
        setPage(0);
    };

    const handlePageSizeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
        setPageSize(Number(e.target.value));
        setPage(0);
    };

    const handleClear = () => {
        setSelectedTier(undefined);
        setSelectedCategories([]);
        setPage(0);
    };

    return (
        <div className="flex-1">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                {/* Header */}
                <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-8">
                    <div>
                        <h1 className="text-3xl font-bold text-white">
                            Product Catalog
                        </h1>
                        <p className="mt-1 text-text-muted">
                            {hasFilters && data ? `${data.totalElements} products found` : 'Select filters to browse products'}
                        </p>
                    </div>
                    <div className="flex items-center gap-4">
                        {/* Page Size Selector */}
                        {hasFilters && (
                            <div className="flex items-center gap-2">
                                <label htmlFor="page-size" className="text-sm font-medium text-text-muted">Show:</label>
                                <select
                                    id="page-size"
                                    value={pageSize}
                                    onChange={handlePageSizeChange}
                                    className="bg-surface-light border border-white/10 rounded-lg px-2 py-1 text-sm text-white focus:outline-none focus:ring-1 focus:ring-primary cursor-pointer"
                                >
                                    <option value={12}>12</option>
                                    <option value={24}>24</option>
                                    <option value={48}>48</option>
                                </select>
                            </div>
                        )}

                        {role === 'ADMIN' && (
                            <Button onClick={() => setShowAddModal(true)} className="gap-2">
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                                </svg>
                                Add Product
                            </Button>
                        )}
                    </div>
                </div>

                {/* Layout */}
                <div className="flex flex-col lg:flex-row gap-8">
                    <FilterSidebar
                        selectedTier={selectedTier}
                        selectedCategories={selectedCategories}
                        onTierChange={handleTierChange}
                        onCategoryToggle={handleCategoryToggle}
                        onClear={handleClear}
                        hasFilters={hasFilters}
                    />

                    {/* Product grid */}
                    <main className="flex-1 min-w-0">
                        {!hasFilters ? (
                            <div className="flex flex-col items-center justify-center py-24 text-center">
                                <div className="w-20 h-20 rounded-2xl bg-surface-lighter/50 flex items-center justify-center mb-6">
                                    <svg className="w-10 h-10 text-text-muted/40" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                                    </svg>
                                </div>
                                <h3 className="text-xl font-semibold text-white mb-2">Start exploring</h3>
                                <p className="text-text-muted max-w-sm">
                                    Select a price tier or category from the filters to discover products
                                </p>
                            </div>
                        ) : isLoading ? (
                            <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-5">
                                {Array.from({ length: 6 }).map((_, i) => (
                                    <div key={i} className="rounded-2xl bg-surface-light/40 border border-white/5 overflow-hidden animate-pulse">
                                        <div className="h-48 bg-surface-lighter/50" />
                                        <div className="p-5 space-y-3">
                                            <div className="h-3 bg-surface-lighter/50 rounded w-1/3" />
                                            <div className="h-5 bg-surface-lighter/50 rounded w-3/4" />
                                            <div className="h-3 bg-surface-lighter/50 rounded w-1/2" />
                                            <div className="h-8 bg-surface-lighter/50 rounded w-1/3 mt-4" />
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : error ? (
                            <div className="flex flex-col items-center justify-center py-24 text-center">
                                <div className="w-16 h-16 rounded-full bg-danger/10 flex items-center justify-center mb-4">
                                    <svg className="w-8 h-8 text-danger" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
                                    </svg>
                                </div>
                                <h3 className="text-lg font-semibold text-white">Something went wrong</h3>
                                <p className="text-text-muted mt-1">Failed to load products. Please try again.</p>
                            </div>
                        ) : data && data.content.length === 0 ? (
                            <div className="flex flex-col items-center justify-center py-24 text-center">
                                <div className="w-16 h-16 rounded-full bg-surface-lighter/50 flex items-center justify-center mb-4">
                                    <svg className="w-8 h-8 text-text-muted/40" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                                    </svg>
                                </div>
                                <h3 className="text-lg font-semibold text-white">No products found</h3>
                                <p className="text-text-muted mt-1">Try adjusting your filters</p>
                            </div>
                        ) : (
                            <>
                                <div className={`grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-5 transition-opacity ${isFetching ? 'opacity-50' : ''}`}>
                                    {data?.content.map((product) => (
                                        <ProductCard key={product.publicId} product={product} />
                                    ))}
                                </div>
                                {data && (
                                    <Pagination
                                        currentPage={data.page}
                                        totalPages={data.totalPages}
                                        onPageChange={setPage}
                                    />
                                )}
                            </>
                        )}
                    </main>
                </div>
            </div>

            <AddProductModal isOpen={showAddModal} onClose={() => setShowAddModal(false)} />
        </div>
    );
}
