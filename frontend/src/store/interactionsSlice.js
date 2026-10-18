import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../api/client';

function mapError(err, fallback) {
  const status = err.response?.status;
  const detail = err.response?.data?.detail;
  if (status === 422 && Array.isArray(detail) && detail.length > 0) {
    const first = detail[0];
    const field = first.loc?.[first.loc.length - 1] ?? 'input';
    return `Invalid ${field}: ${first.msg}`;
  }
  if (typeof detail === 'string') {
    return detail;
  }
  return fallback;
}

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

export const fetchInteractionById = createAsyncThunk(
  'interactions/fetchOne',
  async (id, { rejectWithValue }) => {
    try {
      const { data } = await api.get(`/interactions/${id}`);
      return data;
    } catch (err) {
      return rejectWithValue(
        mapError(err, 'Could not load this interaction. Please try again.')
      );
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
      return rejectWithValue(
        mapError(err, 'Could not save the interaction. Please try again.')
      );
    }
  }
);

export const updateInteraction = createAsyncThunk(
  'interactions/update',
  async ({ id, changes }, { rejectWithValue }) => {
    try {
      const { data } = await api.patch(`/interactions/${id}`, changes);
      return data;
    } catch (err) {
      return rejectWithValue(
        mapError(err, 'Could not update the interaction. Please try again.')
      );
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
    current: null,
    currentStatus: 'idle',
    currentError: null,
    updateStatus: 'idle',
    updateError: null,
  },
  reducers: {
    resetCreate(state) {
      state.createStatus = 'idle';
      state.createError = null;
      state.lastCreated = null;
    },
    resetUpdate(state) {
      state.updateStatus = 'idle';
      state.updateError = null;
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
      .addCase(fetchInteractionById.pending, (state) => {
        state.currentStatus = 'loading';
        state.currentError = null;
        state.current = null;
      })
      .addCase(fetchInteractionById.fulfilled, (state, action) => {
        state.currentStatus = 'succeeded';
        state.current = action.payload;
      })
      .addCase(fetchInteractionById.rejected, (state, action) => {
        state.currentStatus = 'failed';
        state.currentError = action.payload || 'Unknown error';
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
      })
      .addCase(updateInteraction.pending, (state) => {
        state.updateStatus = 'loading';
        state.updateError = null;
      })
      .addCase(updateInteraction.fulfilled, (state, action) => {
        state.updateStatus = 'succeeded';
        state.current = action.payload;
      })
      .addCase(updateInteraction.rejected, (state, action) => {
        state.updateStatus = 'failed';
        state.updateError = action.payload || 'Could not update the interaction.';
      });
  },
});

export const { resetCreate, resetUpdate } = interactionsSlice.actions;
export default interactionsSlice.reducer;