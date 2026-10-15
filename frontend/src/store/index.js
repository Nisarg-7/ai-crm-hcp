import { configureStore } from '@reduxjs/toolkit';
import authReducer from './authSlice';
import healthReducer from './healthSlice';

const store = configureStore({
  reducer: {
    auth: authReducer,
    health: healthReducer,
  },
});

export default store;