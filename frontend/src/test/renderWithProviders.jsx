import { configureStore } from '@reduxjs/toolkit';
import { render } from '@testing-library/react';
import { Provider } from 'react-redux';
import { MemoryRouter } from 'react-router-dom';
import authReducer from '../store/authSlice';
import chatReducer from '../store/chatSlice';
import dashboardReducer from '../store/dashboardSlice';
import healthReducer from '../store/healthSlice';
import hcpsReducer from '../store/hcpsSlice';
import interactionsReducer from '../store/interactionsSlice';
import productsReducer from '../store/productsSlice';

export function makeStore(preloadedState) {
  return configureStore({
    reducer: {
      auth: authReducer,
      chat: chatReducer,
      dashboard: dashboardReducer,
      health: healthReducer,
      hcps: hcpsReducer,
      interactions: interactionsReducer,
      products: productsReducer,
    },
    preloadedState,
  });
}

export function renderWithProviders(ui, { preloadedState, route = '/' } = {}) {
  const store = makeStore(preloadedState);
  return {
    store,
    ...render(
      <Provider store={store}>
        <MemoryRouter initialEntries={[route]}>{ui}</MemoryRouter>
      </Provider>
    ),
  };
}