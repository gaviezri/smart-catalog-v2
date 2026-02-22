import { useState } from 'react';
import { useGetCategoriesQuery, useGetTiersQuery, useGetSimilarProductsMutation } from '../../store/api';
import { Button } from '../../components/ui/Button';
import type { Product } from '../../types';

const generateMockBase64Vector = () => {
    const floats = new Float32Array(1536);
    for (let i = 0; i < 1536; i++) {
        floats[i] = Math.random() * 2 - 1;
    }
    const bytes = new Uint8Array(floats.buffer);
    let binary = '';
    for (let i = 0; i < bytes.byteLength; i++) {
        binary += String.fromCharCode(bytes[i]);
    }
    return btoa(binary);
};

interface MixAndMatchModalProps {
    isOpen: boolean;
    onClose: () => void;
    onResults: (results: Product[]) => void;
}

export default function MixAndMatchModal({ isOpen, onClose, onResults }: MixAndMatchModalProps) {
    const { data: categories = [] } = useGetCategoriesQuery();
    const { data: tiers = [] } = useGetTiersQuery();
    const [getSimilarProducts, { isLoading }] = useGetSimilarProductsMutation();

    const [selectedTier, setSelectedTier] = useState<number | undefined>();
    const [selectedCategories, setSelectedCategories] = useState<number[]>([]);
    const [maxPrice, setMaxPrice] = useState<number | ''>('');

    const activeFiltersCount =
        (selectedTier !== undefined ? 1 : 0) +
        (selectedCategories.length > 0 ? 1 : 0) +
        (maxPrice !== '' ? 1 : 0);

    const isReady = activeFiltersCount >= 2;

    const handleCategoryToggle = (id: number) => {
        setSelectedCategories(prev =>
            prev.includes(id) ? prev.filter(c => c !== id) : [...prev, id]
        );
    };

    const handleMatch = async () => {
        if (!isReady) return;
        try {
            const vector = generateMockBase64Vector();
            const request: any = { vector, limit: 5 };
            if (selectedTier !== undefined) request.tier = selectedTier;
            if (selectedCategories.length > 0) request.categories = selectedCategories;
            if (maxPrice !== '') request.maxPrice = Number(maxPrice);

            const response = await getSimilarProducts(request).unwrap();
            onResults(response.content);
            onClose();
        } catch (error) {
            console.error('Failed to get similar products:', error);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-[60] flex items-center justify-center p-4">
            <div className="absolute inset-0 bg-background/80 backdrop-blur-sm" onClick={onClose} />
            <div className="relative bg-surface border border-white/10 rounded-2xl shadow-2xl w-full max-w-lg p-6 flex flex-col max-h-[90vh]">
                <h2 className="text-2xl font-bold text-white mb-4">Mix & Match</h2>
                <div className="mb-6 p-4 bg-primary/10 border border-primary/20 rounded-xl shrink-0">
                    <p className="text-sm text-primary-light">
                        this triggers the similarity search API with some mock data.
                        select desired filters (atleast 2!) and click on <span className="font-mono bg-primary/20 px-1 rounded text-primary-lighter">`Let's Match!`</span> a mock embedding will be generated and will be used with the specified filters to get 5 similar products.
                    </p>
                </div>

                <div className="space-y-6 mb-8 overflow-y-auto pr-2 custom-scrollbar">
                    <div>
                        <label className="block text-sm font-medium text-text-muted mb-2">Price Tier</label>
                        <div className="flex flex-wrap gap-2">
                            {tiers.map(tier => (
                                <button
                                    key={tier.id}
                                    onClick={() => setSelectedTier(selectedTier === tier.id ? undefined : tier.id)}
                                    className={`px-3 py-1.5 rounded-lg text-sm transition-colors ${selectedTier === tier.id ? 'bg-primary text-white border-transparent' : 'bg-surface-lighter text-text-muted hover:text-white border border-white/5'}`}
                                >
                                    {tier.name}
                                </button>
                            ))}
                        </div>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-text-muted mb-2">Categories</label>
                        <div className="flex flex-wrap gap-2">
                            {categories.map(cat => (
                                <button
                                    key={cat.id}
                                    onClick={() => handleCategoryToggle(cat.id)}
                                    className={`px-3 py-1.5 rounded-lg text-sm transition-colors ${selectedCategories.includes(cat.id) ? 'bg-primary text-white border-transparent' : 'bg-surface-lighter text-text-muted hover:text-white border border-white/5'}`}
                                >
                                    {cat.name}
                                </button>
                            ))}
                        </div>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-text-muted mb-2">Maximum Price (Optional)</label>
                        <input
                            type="number"
                            value={maxPrice}
                            onChange={(e) => setMaxPrice(e.target.value ? Number(e.target.value) : '')}
                            placeholder="e.g. 500"
                            className="w-full bg-surface-lighter/50 border border-white/10 rounded-lg px-4 py-2.5 text-white placeholder:text-text-muted/50 focus:outline-none focus:ring-2 focus:ring-primary/50"
                        />
                    </div>
                </div>

                <div className="flex items-center justify-between mt-auto pt-4 border-t border-white/10 shrink-0">
                    <span className="text-sm text-text-muted">
                        {activeFiltersCount} / 2 filters selected
                    </span>
                    <div className="flex gap-3">
                        <Button variant="secondary" onClick={onClose}>Cancel</Button>
                        <Button
                            onClick={handleMatch}
                            disabled={!isReady || isLoading}
                            className={!isReady ? 'opacity-50 cursor-not-allowed' : ''}
                        >
                            {isLoading ? 'Matching...' : "Let's Match!"}
                        </Button>
                    </div>
                </div>
            </div>
        </div>
    );
}
