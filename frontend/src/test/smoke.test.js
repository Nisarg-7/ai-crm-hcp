import { describe, expect, it } from 'vitest';
import { makeStore } from './renderWithProviders';

describe('test setup', () => {
  it('creates a store with all slices', () => {
    const state = makeStore().getState();
    expect(Object.keys(state)).toEqual(
      expect.arrayContaining(['auth', 'chat', 'dashboard', 'hcps', 'interactions', 'products'])
    );
  });
});