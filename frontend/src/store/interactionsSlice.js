import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../api/client';

export const fetchInteractions = createAsyncThunk(
  'interactions/fetchList',
  async (hcpId, { rejectWithValue }) => {
    try {
      const params = hcpId ? { hcp_id: hcpId } : {};
      const { data } = await api.get('/interactions', { params });
      return data;
    } catch (err) {
      return rejectWithValue('Could not load interactions. Please try again.');
    }
  }
);

const interactionsSlice = createSlice({
  name: 'interactions',
  initialState: {
    list: [],
    status: 'idle',
    error: null,
  },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchInteractions.pending, (state) => {
        state.status = 'loading';
        state.error = null;
        state.list = [];
      })
      .addCase(fetchInteractions.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.list = action.payload;
      })
      .addCase(fetchInteractions.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload || 'Unknown error';
      });
  },
});

export default interactionsSlice.reducer;