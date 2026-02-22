import { createSlice, type PayloadAction } from '@reduxjs/toolkit';
import type { AuthState } from '../types';

const stored = localStorage.getItem('auth');
const initial: AuthState = stored
    ? JSON.parse(stored)
    : { token: null, username: null, role: null };

const authSlice = createSlice({
    name: 'auth',
    initialState: initial,
    reducers: {
        setCredentials: (state, action: PayloadAction<AuthState>) => {
            state.token = action.payload.token;
            state.username = action.payload.username;
            state.role = action.payload.role;
            localStorage.setItem('auth', JSON.stringify(action.payload));
        },
        logout: (state) => {
            state.token = null;
            state.username = null;
            state.role = null;
            localStorage.removeItem('auth');
        },
    },
});

export const { setCredentials, logout } = authSlice.actions;
export default authSlice.reducer;
