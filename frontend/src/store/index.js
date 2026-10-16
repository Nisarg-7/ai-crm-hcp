import { configureStore } from '@reduxjs/toolkit';
import authReducer from './authSlice';
import healthReducer from './healthSlice';
import hcpsReducer from './hcpsSlice';
import interactionsReducer from './interactionsSlice';

const store = configureStore({
  reducer: {
    auth: authReducer,
    health: healthReducer,
    hcps: hcpsReducer,
    interactions: interactionsReducer,
  },
});

export default store;