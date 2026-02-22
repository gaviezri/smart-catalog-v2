export interface Product {
    publicId: string;
    title: string;
    brandName: string;
    categoryNames: string[];
    price: number;
    tier: string;
    productUrl: string;
    imageUrl: string;
    createdAt: string;
}

export interface ProductsResponse {
    content: Product[];
    totalElements: number;
    totalPages: number;
    page: number;
    size: number;
}

export interface Category {
    id: number;
    name: string;
}

export interface Tier {
    id: number;
    name: string;
}

export interface LoginRequest {
    username: string;
    password: string;
}

export interface LoginResponse {
    token: string;
    username: string;
    role: string;
}

export interface AuthState {
    token: string | null;
    username: string | null;
    role: string | null;
}

export interface ProductFilters {
    tier?: number;
    categories?: number[];
    page: number;
    size: number;
}

export interface CreateProductRequest {
    title: string;
    brandName: string;
    categoryNames: string[];
    price: number;
    productUrl: string;
    imageUrl: string;
}

export interface SimilarityRequest {
    vector: string;
    maxPrice?: number;
    categories?: number[];
    tier?: number;
    gender?: string;
    limit?: number;
}
