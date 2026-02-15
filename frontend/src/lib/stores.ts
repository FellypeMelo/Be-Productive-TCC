import { writable, derived } from 'svelte/store';
import type { User } from './api';

// Auth store
interface AuthState {
    user: User | null;
    token: string | null;
    isAuthenticated: boolean;
    isLoading: boolean;
}

function createAuthStore() {
    const { subscribe, set, update } = writable<AuthState>({
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: true,
    });

    return {
        subscribe,

        // Initialize from localStorage
        init: () => {
            const token = localStorage.getItem('auth_token');
            const userJson = localStorage.getItem('user');

            if (token && userJson) {
                try {
                    const user = JSON.parse(userJson);
                    set({
                        user,
                        token,
                        isAuthenticated: true,
                        isLoading: false,
                    });
                } catch {
                    localStorage.removeItem('auth_token');
                    localStorage.removeItem('user');
                    set({ user: null, token: null, isAuthenticated: false, isLoading: false });
                }
            } else {
                set({ user: null, token: null, isAuthenticated: false, isLoading: false });
            }
        },

        // Login
        login: (user: User, token: string) => {
            localStorage.setItem('auth_token', token);
            localStorage.setItem('user', JSON.stringify(user));
            set({
                user,
                token,
                isAuthenticated: true,
                isLoading: false,
            });
        },

        // Logout
        logout: () => {
            localStorage.removeItem('auth_token');
            localStorage.removeItem('user');
            set({
                user: null,
                token: null,
                isAuthenticated: false,
                isLoading: false,
            });
        },

        // Update user
        updateUser: (user: User) => {
            localStorage.setItem('user', JSON.stringify(user));
            update(state => ({ ...state, user }));
        },
    };
}

export const auth = createAuthStore();

// UI Store
interface UIState {
    theme: 'dark' | 'light';
    sidebarOpen: boolean;
    focusMode: boolean;
    currentCategory: 'PRODUTIVIDADE' | 'ENTRETENIMENTO' | null;
}

function createUIStore() {
    const { subscribe, update } = writable<UIState>({
        theme: 'dark',
        sidebarOpen: true,
        focusMode: false,
        currentCategory: null,
    });

    return {
        subscribe,

        toggleSidebar: () => update(s => ({ ...s, sidebarOpen: !s.sidebarOpen })),

        setCategory: (category: 'PRODUTIVIDADE' | 'ENTRETENIMENTO' | null) =>
            update(s => ({ ...s, currentCategory: category })),

        enterFocusMode: () => update(s => ({ ...s, focusMode: true })),

        exitFocusMode: () => update(s => ({ ...s, focusMode: false })),
    };
}

export const ui = createUIStore();

// Derived stores
export const isLoggedIn = derived(auth, $auth => $auth.isAuthenticated);
export const currentUser = derived(auth, $auth => $auth.user);
