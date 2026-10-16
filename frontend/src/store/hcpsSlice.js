import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../api/client';

export const fetchHcps = createAsyncThunk(
  'hcps/fetchList',
  async (query = '', { rejectWithValue }) => {
    try {
      const params = query.trim() ? { q: query.trim() } : {};
      const { data } = await api.get('/hcps', { params });
      return data;
    } catch (err) {
      return rejectWithValue('Could not load HCPs. Please try again.');
    }
  }
);

export const fetchHcpById = createAsyncThunk(
  'hcps/fetchOne',
  async (id, { rejectWithValue }) => {
    try {
      const { data } = await api.get(`/hcps/${id}`);
      return data;
    } catch (err) {
      if (err.response?.status === 404) {
        return rejectWithValue('HCP not found');
      }
      return rejectWithValue('Could not load this HCP. Please try again.');
    }
  }
);

const hcpsSlice = createSlice({
  name: 'hcps',
  initialState: {
    list: [],
    listStatus: 'idle',
    listError: null,
    selected: null,
    selectedStatus: 'idle',
    selectedError: null,
  },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchHcps.pending, (state) => {
        state.listStatus = 'loading';
        state.listError = null;
      })
      .addCase(fetchHcps.fulfilled, (state, action) => {
        state.listStatus = 'succeeded';
        state.list = action.payload;
      })
      .addCase(fetchHcps.rejected, (state, action) => {
        state.listStatus = 'failed';
        state.listError = action.payload || 'Unknown error';
      })
      .addCase(fetchHcpById.pending, (state) => {
        state.selectedStatus = 'loading';
        state.selectedError = null;
        state.selected = null;
      })
      .addCase(fetchHcpById.fulfilled, (state, action) => {
        state.selectedStatus = 'succeeded';
        state.selected = action.payload;
      })
      .addCase(fetchHcpById.rejected, (state, action) => {
        state.selectedStatus = 'failed';
        state.selectedError = action.payload || 'Unknown error';
      });
  },
});

export default hcpsSlice.reducer;