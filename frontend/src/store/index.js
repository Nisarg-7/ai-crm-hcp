import { configureStore } from '@reduxjs/toolkit';
import authReducer from './authSlice';
import chatReducer from './chatSlice';
import dashboardReducer from './dashboardSlice';
import healthReducer from './healthSlice';
import hcpsReducer from './hcpsSlice';
import interactionsReducer from './interactionsSlice';
import productsReducer from './productsSlice';

const store = configureStore({
  reducer: {
    auth: authReducer,
    chat: chatReducer,
    dashboard: dashboardReducer,
    health: healthReducer,
    hcps: hcpsReducer,
    interactions: interactionsReducer,
    products: productsReducer,
  },
});

export default store;