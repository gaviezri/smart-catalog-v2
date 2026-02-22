import { useState } from 'react';
import { useCreateProductMutation } from '../../store/api';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';
import { Modal } from '../../components/ui/Modal';

interface Props {
    isOpen: boolean;
    onClose: () => void;
}

export default function AddProductModal({ isOpen, onClose }: Props) {
    const [createProduct, { isLoading }] = useCreateProductMutation();
    const [formData, setFormData] = useState({
        title: '',
        brandName: '',
        price: '',
        productUrl: '',
        imageUrl: '',
    });
    const [categoryNames, setCategoryNames] = useState<string[]>([]);
    const [categoryInput, setCategoryInput] = useState('');

    const handleAddCategory = (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            const value = categoryInput.trim();
            if (value && !categoryNames.includes(value)) {
                setCategoryNames([...categoryNames, value]);
            }
            setCategoryInput('');
        }
    };

    const handleRemoveCategory = (name: string) => {
        setCategoryNames(categoryNames.filter((c) => c !== name));
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (categoryNames.length === 0) return;
        try {
            await createProduct({
                ...formData,
                price: parseFloat(formData.price),
                categoryNames,
            }).unwrap();
            onClose();
            // Reset form
            setFormData({
                title: '',
                brandName: '',
                price: '',
                productUrl: '',
                imageUrl: '',
            });
            setCategoryNames([]);
            setCategoryInput('');
        } catch {
            // Error handled by RTK Query
        }
    };

    return (
        <Modal isOpen={isOpen} onClose={onClose} title="Add New Product">
            <form onSubmit={handleSubmit} className="space-y-4">
                <Input
                    label="Title"
                    value={formData.title}
                    onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                    required
                />

                <div className="grid grid-cols-2 gap-4">
                    <Input
                        label="Brand"
                        value={formData.brandName}
                        onChange={(e) => setFormData({ ...formData, brandName: e.target.value })}
                        required
                    />

                    <div className="space-y-1.5">
                        <label className="block text-sm font-medium text-text-muted">Price</label>
                        <div className="relative">
                            <span className="absolute left-3 top-2.5 text-text-muted">$</span>
                            <input
                                type="number"
                                step="0.01"
                                className="w-full pl-7 pr-4 py-2.5 rounded-xl bg-surface-lighter/50 border border-white/10 text-white focus:outline-none focus:ring-2 focus:ring-primary/20"
                                value={formData.price}
                                onChange={(e) => setFormData({ ...formData, price: e.target.value })}
                                required
                            />
                        </div>
                    </div>
                </div>

                <div className="space-y-1.5">
                    <label className="block text-sm font-medium text-text-muted">Categories</label>
                    <div className="flex flex-wrap gap-2 mb-2">
                        {categoryNames.map((name) => (
                            <span
                                key={name}
                                className="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-primary/20 text-primary text-sm border border-primary/30"
                            >
                                {name}
                                <button
                                    type="button"
                                    onClick={() => handleRemoveCategory(name)}
                                    className="ml-0.5 hover:text-white transition-colors"
                                    aria-label={`Remove ${name}`}
                                >
                                    ×
                                </button>
                            </span>
                        ))}
                    </div>
                    <input
                        type="text"
                        className="w-full px-4 py-2.5 rounded-xl bg-surface-lighter/50 border border-white/10 text-white placeholder-text-muted/50 focus:outline-none focus:ring-2 focus:ring-primary/20 transition-all"
                        value={categoryInput}
                        onChange={(e) => setCategoryInput(e.target.value)}
                        onKeyDown={handleAddCategory}
                        placeholder="Type a category and press Enter"
                    />
                    {categoryNames.length === 0 && (
                        <p className="text-xs text-text-muted mt-1">At least one category is required</p>
                    )}
                </div>

                <Input
                    label="Product URL"
                    type="url"
                    value={formData.productUrl}
                    onChange={(e) => setFormData({ ...formData, productUrl: e.target.value })}
                />

                <Input
                    label="Image URL"
                    type="url"
                    value={formData.imageUrl}
                    onChange={(e) => setFormData({ ...formData, imageUrl: e.target.value })}
                />

                <div className="flex justify-end gap-3 pt-4">
                    <Button variant="ghost" onClick={onClose} type="button">
                        Cancel
                    </Button>
                    <Button type="submit" isLoading={isLoading}>
                        Create Product
                    </Button>
                </div>
            </form>
        </Modal>
    );
}
