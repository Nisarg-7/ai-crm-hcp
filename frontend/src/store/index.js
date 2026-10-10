import { configureStore } from '@reduxjs/toolkit';
import healthReducer from './healthSlice';

const store = configureStore({
  reducer: {
    health: healthReducer,
  },
});

export default store;