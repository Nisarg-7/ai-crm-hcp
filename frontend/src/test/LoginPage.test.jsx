import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import api from '../api/client';
import LoginPage from '../pages/LoginPage';
import { renderWithProviders } from './renderWithProviders';

vi.mock('../api/client', () => ({
  default: { post: vi.fn(), get: vi.fn() },
  TOKEN_KEY: 'crm_token',
}));

describe('LoginPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('shows an error for a wrong password', async () => {
    api.post.mockRejectedValue({ response: { status: 401 } });
    renderWithProviders(<LoginPage />);

    await userEvent.type(screen.getByLabelText('Email'), 'rep1@democrm.com');
    await userEvent.type(screen.getByLabelText('Password'), 'wrong');
    await userEvent.click(screen.getByRole('button', { name: 'Sign in' }));

    expect(await screen.findByText('Incorrect email or password')).toBeInTheDocument();
  });

  it('stores the token on success', async () => {
    api.post.mockResolvedValue({
      data: {
        access_token: 'abc123',
        user: { id: 1, email: 'rep1@democrm.com', full_name: 'Aarav Mehta' },
      },
    });
    const { store } = renderWithProviders(<LoginPage />);

    await userEvent.type(screen.getByLabelText('Email'), 'rep1@democrm.com');
    await userEvent.type(screen.getByLabelText('Password'), 'Demo@1234');
    await userEvent.click(screen.getByRole('button', { name: 'Sign in' }));

    await waitFor(() => expect(store.getState().auth.token).toBe('abc123'));
    expect(localStorage.getItem('crm_token')).toBe('abc123');
  });
});