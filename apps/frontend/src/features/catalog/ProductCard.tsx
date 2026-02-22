import type { Product } from '../../types';
import { useAppSelector } from '../../store/hooks';
import { useDeleteProductMutation } from '../../store/api';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';

interface Props {
    product: Product;
}

export default function ProductCard({ product }: Props) {
    const role = useAppSelector((s) => s.auth.role);
    const [deleteProduct, { isLoading: isDeleting }] = useDeleteProductMutation();

    const tierColors: Record<string, string> = {
        BUDGET: 'from-emerald-500/20 to-emerald-600/20 text-emerald-400 border-emerald-500/30',
        MID: 'from-blue-500/20 to-blue-600/20 text-blue-400 border-blue-500/30',
        PREMIUM: 'from-amber-500/20 to-amber-600/20 text-amber-400 border-amber-500/30',
    };

    const tierColor = tierColors[product.tier] || tierColors.MID;

    return (
        <Card hoverEffect className="relative h-full flex flex-col">
            {/* Image */}
            <div className="relative h-48 overflow-hidden bg-surface-lighter/50 shrink-0">
                <div className="absolute inset-0 bg-gradient-to-br from-primary/10 to-accent/10 flex items-center justify-center">
                    {product.imageUrl && product.imageUrl.startsWith('http') ? (
                        <img src={product.imageUrl} alt={product.title} className="w-full h-full object-cover" />
                    ) : (
                        <svg className="w-16 h-16 text-white/10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                        </svg>
                    )}
                </div>
                {/* Tier badge */}
                <div className={`absolute top-3 right-3 px-2.5 py-1 rounded-full text-[11px] font-semibold uppercase tracking-wider bg-gradient-to-r border backdrop-blur-sm ${tierColor}`}>
                    {product.tier}
                </div>
            </div>

            {/* Content */}
            <div className="p-5 flex-1 flex flex-col space-y-3">
                <div>
                    <p className="text-xs font-medium text-primary-light uppercase tracking-wider mb-1">
                        {product.brandName}
                    </p>
                    <h3 className="text-lg font-semibold text-white leading-tight line-clamp-2 group-hover:text-primary-light transition-colors">
                        {product.title}
                    </h3>
                </div>

                {/* Categories */}
                <div className="flex flex-wrap gap-1.5 mb-auto">
                    {product.categoryNames.map((cat) => (
                        <span
                            key={cat}
                            className="px-2 py-0.5 text-[11px] font-medium rounded-md bg-white/5 text-text-muted border border-white/5"
                        >
                            {cat}
                        </span>
                    ))}
                </div>

                {/* Price */}
                <div className="flex items-center justify-between pt-2 border-t border-white/5 mt-auto">
                    <span className="text-2xl font-bold bg-gradient-to-r from-white to-text-muted bg-clip-text text-transparent">
                        ${product.price.toFixed(2)}
                    </span>
                    <a
                        href={product.productUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-xs text-primary-light hover:text-primary font-medium transition-colors"
                    >
                        View →
                    </a>
                </div>

                {/* Admin delete */}
                {role === 'ADMIN' && (
                    <Button
                        variant="danger"
                        size="sm"
                        onClick={() => deleteProduct(product.publicId)}
                        isLoading={isDeleting}
                        className="w-full mt-2"
                    >
                        Delete Product
                    </Button>
                )}
            </div>
        </Card>
    );
}
