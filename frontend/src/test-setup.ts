import '@testing-library/jest-dom/vitest';
import { vi } from 'vitest';

vi.mock('$app/navigation', () => ({
  goto: vi.fn(),
}));

vi.mock('$app/stores', () => ({
  page: { subscribe: vi.fn(() => () => {}) },
  navigating: { subscribe: vi.fn(() => () => {}) },
}));

vi.mock('$lib/stores', () => ({
  currentUser: { id_usuario: 1, nome: 'Test User', email: 'test@test.com' },
  isLoggedIn: true,
  ui: {
    focusMode: false,
    darkMode: false,
    enterFocusMode: () => {},
    exitFocusMode: () => {},
  },
}));
