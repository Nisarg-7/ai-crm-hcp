import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import api from '../api/client';
import LogInteractionForm from '../components/LogInteractionForm';
import { renderWithProviders } from './renderWithProviders';

vi.mock('../api/client', () => ({
  default: { post: vi.fn(), get: vi.fn() },
  TOKEN_KEY: 'crm_token',
}));

const HCPS = [{ id: 1, full_name: 'Dr. Rohan Kapoor', specialty: 'Cardiology' }];
const PRODUCTS = [{ id: 5, name: 'CardioSafe 10mg' }];

function mockGets() {
  api.get.mockImplementation((url) => {
    if (url === '/hcps') return Promise.resolve({ data: HCPS });
    if (url === '/products') return Promise.resolve({ data: PRODUCTS });
    return Promise.resolve({ data: [] });
  });
}

describe('LogInteractionForm', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockGets();
  });

  it('asks for an HCP before submitting', async () => {
    renderWithProviders(<LogInteractionForm />);
    await userEvent.click(screen.getByRole('button', { name: 'Log interaction' }));

    expect(screen.getByText('Please select an HCP.')).toBeInTheDocument();
    expect(api.post).not.toHaveBeenCalled();
  });

  it('submits the right payload', async () => {
    api.post.mockResolvedValue({
      data: { id: 9, hcp_id: 1, hcp: { full_name: 'Dr. Rohan Kapoor' } },
    });
    renderWithProviders(<LogInteractionForm />);

    await screen.findByRole('option', { name: /Dr. Rohan Kapoor/ });
    await userEvent.selectOptions(screen.getByLabelText('HCP *'), '1');
    await userEvent.selectOptions(screen.getByLabelText('HCP sentiment'), 'positive');
    await userEvent.click(await screen.findByLabelText('CardioSafe 10mg'));
    await userEvent.type(screen.getByLabelText('Summary'), 'Went well');
    await userEvent.click(screen.getByRole('button', { name: 'Log interaction' }));

    await waitFor(() => expect(api.post).toHaveBeenCalled());
    const [url, payload] = api.post.mock.calls[0];
    expect(url).toBe('/interactions');
    expect(payload).toMatchObject({
      hcp_id: 1,
      interaction_type: 'visit',
      sentiment: 'positive',
      summary: 'Went well',
      notes: null,
      source: 'form',
      product_ids: [5],
      follow_ups: [],
    });
    expect(await screen.findByText(/Interaction logged for Dr. Rohan Kapoor/)).toBeInTheDocument();
  });

  it('shows the server error and keeps the typed values', async () => {
    api.post.mockRejectedValue({ response: { status: 404, data: { detail: 'HCP not found' } } });
    renderWithProviders(<LogInteractionForm />);

    await screen.findByRole('option', { name: /Dr. Rohan Kapoor/ });
    await userEvent.selectOptions(screen.getByLabelText('HCP *'), '1');
    await userEvent.type(screen.getByLabelText('Summary'), 'Keep me');
    await userEvent.click(screen.getByRole('button', { name: 'Log interaction' }));

    expect(await screen.findByText('HCP not found')).toBeInTheDocument();
    expect(screen.getByLabelText('Summary')).toHaveValue('Keep me');
  });
});