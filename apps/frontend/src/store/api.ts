import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import type { RootState } from './store';
import type {
    LoginRequest,
    LoginResponse,
    ProductsResponse,
    ProductFilters,
    Category,
    Tier,
    Product,
    CreateProductRequest,
    SimilarityRequest,
} from '../types';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const api = createApi({
    reducerPath: 'api',
    baseQuery: fetchBaseQuery({
        baseUrl: API_BASE,
        prepareHeaders: (headers, { getState }) => {
            const token = (getState() as RootState).auth.token;
            if (token) {
                headers.set('Authorization', `Bearer ${token}`);
            }
            return headers;
        },
    }),
    tagTypes: ['Products'],
    endpoints: (builder) => ({
        login: builder.mutation<LoginResponse, LoginRequest>({
            query: (body) => ({
                url: '/api/auth/login',
                method: 'POST',
                body,
            }),
            transformResponse: (response: { access: string; refresh: string; username: string; role: string }) => ({
                token: response.access,
                username: response.username,
                role: response.role,
            }),
        }),

        getProducts: builder.query<ProductsResponse, ProductFilters>({
            query: ({ tier, categories, page, size }) => {
                const params = new URLSearchParams();
                if (tier !== undefined && tier !== -1) params.append('tier', String(tier));
                if (categories && categories.length > 0) {
                    categories.forEach((c) => params.append('category', String(c)));
                }
                params.append('page', String(page));
                params.append('size', String(size));
                return `/api/products/filter?${params.toString()}`;
            },
            providesTags: ['Products'],
        }),

        getCategories: builder.query<Category[], void>({
            query: () => '/api/products/categories',
        }),

        getTiers: builder.query<Tier[], void>({
            query: () => '/api/products/tiers',
        }),

        createProduct: builder.mutation<Product, CreateProductRequest>({
            query: (body) => ({
                url: '/api/products',
                method: 'POST',
                body,
            }),
            invalidatesTags: ['Products'],
        }),

        deleteProduct: builder.mutation<void, string>({
            query: (publicId) => ({
                url: `/api/products/${publicId}`,
                method: 'DELETE',
            }),
            invalidatesTags: ['Products'],
        }),

        getSimilarProducts: builder.mutation<ProductsResponse, SimilarityRequest>({
            query: (body) => ({
                url: '/api/products/similarity',
                method: 'POST',
                body,
            }),
        }),
    }),
});

export const {
    useLoginMutation,
    useGetProductsQuery,
    useGetCategoriesQuery,
    useGetTiersQuery,
    useCreateProductMutation,
    useDeleteProductMutation,
    useGetSimilarProductsMutation,
} = api;
