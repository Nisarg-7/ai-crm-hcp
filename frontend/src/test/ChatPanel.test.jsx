import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import api from '../api/client';
import ChatPanel from '../components/ChatPanel';
import { renderWithProviders } from './renderWithProviders';

vi.mock('../api/client', () => ({
  default: { post: vi.fn(), get: vi.fn() },
  TOKEN_KEY: 'crm_token',
}));

const CARD = {
  action: 'logged',
  interaction_id: 7,
  hcp_id: 3,
  hcp_name: 'Dr. Test',
  interaction_type: 'visit',
  interaction_date: '2026-10-21T10:00:00Z',
  sentiment: 'positive',
  products: ['CardioSafe 10mg'],
  follow_ups: ['Send PDF (due 2026-10-30)'],
};

describe('ChatPanel', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('shows example prompts when empty', () => {
    renderWithProviders(<ChatPanel />);
    expect(screen.getByText('Find me cardiologists')).toBeInTheDocument();
  });

  it('shows the user message, the reply and a result card', async () => {
    api.post.mockResolvedValue({ data: { reply: 'Saved it.', actions: [CARD] } });
    renderWithProviders(<ChatPanel />);

    await userEvent.type(screen.getByPlaceholderText(/Type a message/), 'I met Dr. Test');
    await userEvent.click(screen.getByRole('button', { name: 'Send' }));

    expect(await screen.findByText('Saved it.')).toBeInTheDocument();
    expect(screen.getByText('I met Dr. Test')).toBeInTheDocument();
    expect(screen.getByText('Interaction logged')).toBeInTheDocument();
    expect(screen.getByText('Dr. Test')).toBeInTheDocument();
  });

  it('sends only role and content to the API', async () => {
    api.post.mockResolvedValue({ data: { reply: 'ok', actions: [CARD] } });
    renderWithProviders(<ChatPanel />);

    const box = screen.getByPlaceholderText(/Type a message/);
    await userEvent.type(box, 'first');
    await userEvent.click(screen.getByRole('button', { name: 'Send' }));
    await screen.findByText('ok');

    await userEvent.type(box, 'second');
    await userEvent.click(screen.getByRole('button', { name: 'Send' }));
    await screen.findAllByText('ok');

    const lastCall = api.post.mock.calls.at(-1);
    expect(lastCall[0]).toBe('/agent/chat');
    for (const m of lastCall[1].messages) {
      expect(Object.keys(m).sort()).toEqual(['content', 'role']);
    }
  });

  it('shows an error and retries without duplicating the message', async () => {
    api.post.mockRejectedValueOnce({}).mockResolvedValueOnce({
      data: { reply: 'Recovered.', actions: [] },
    });
    renderWithProviders(<ChatPanel />);

    await userEvent.type(screen.getByPlaceholderText(/Type a message/), 'hello');
    await userEvent.click(screen.getByRole('button', { name: 'Send' }));

    expect(await screen.findByText(/Cannot reach the server/)).toBeInTheDocument();
    await userEvent.click(screen.getByRole('button', { name: 'Retry' }));

    expect(await screen.findByText('Recovered.')).toBeInTheDocument();
    expect(screen.getAllByText('hello')).toHaveLength(1);
  });
});