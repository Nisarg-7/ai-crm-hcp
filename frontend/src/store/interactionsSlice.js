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

export const createInteraction = createAsyncThunk(
  'interactions/create',
  async (payload, { rejectWithValue }) => {
    try {
      const { data } = await api.post('/interactions', payload);
      return data;
    } catch (err) {
      const status = err.response?.status;
      const detail = err.response?.data?.detail;
      if (status === 422 && Array.isArray(detail) && detail.length > 0) {
        const first = detail[0];
        const field = first.loc?.[first.loc.length - 1] ?? 'input';
        return rejectWithValue(`Invalid ${field}: ${first.msg}`);
      }
      if (typeof detail === 'string') {
        return rejectWithValue(detail);
      }
      return rejectWithValue('Could not save the interaction. Please try again.');
    }
  }
);

const interactionsSlice = createSlice({
  name: 'interactions',
  initialState: {
    list: [],
    status: 'idle',
    error: null,
    createStatus: 'idle',
    createError: null,
    lastCreated: null,
  },
  reducers: {
    resetCreate(state) {
      state.createStatus = 'idle';
      state.createError = null;
      state.lastCreated = null;
    },
  },
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
      })
      .addCase(createInteraction.pending, (state) => {
        state.createStatus = 'loading';
        state.createError = null;
        state.lastCreated = null;
      })
      .addCase(createInteraction.fulfilled, (state, action) => {
        state.createStatus = 'succeeded';
        state.lastCreated = action.payload;
      })
      .addCase(createInteraction.rejected, (state, action) => {
        state.createStatus = 'failed';
        state.createError = action.payload || 'Could not save the interaction.';
      });
  },
});

export const { resetCreate } = interactionsSlice.actions;
export default interactionsSlice.reducer;