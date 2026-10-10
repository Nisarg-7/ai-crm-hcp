import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../api/client';

export const fetchHealth = createAsyncThunk(
  'health/fetch',
  async (_, { rejectWithValue }) => {
    try {
      const { data } = await api.get('/health');
      return data;
    } catch (err) {
      return rejectWithValue('Cannot reach the backend');
    }
  }
);

const healthSlice = createSlice({
  name: 'health',
  initialState: { data: null, status: 'idle', error: null },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchHealth.pending, (state) => {
        state.status = 'loading';
        state.error = null;
      })
      .addCase(fetchHealth.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.data = action.payload;
      })
      .addCase(fetchHealth.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload || 'Unknown error';
      });
  },
});

export default healthSlice.reducer;