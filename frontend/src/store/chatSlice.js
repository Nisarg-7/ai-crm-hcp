import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../api/client';

function mapChatError(err) {
  const status = err.response?.status;
  if (status === 401) {
    return 'Your session expired. Please log in again.';
  }
  if (status === 422) {
    return 'That message could not be sent. Please shorten or rephrase it.';
  }
  if (!err.response) {
    return 'Cannot reach the server. Please check your connection and retry.';
  }
  return 'The assistant had a problem. Please retry.';
}

async function postConversation(messages, rejectWithValue) {
  try {
    const { data } = await api.post('/agent/chat', { messages });
    return data.reply;
  } catch (err) {
    return rejectWithValue(mapChatError(err));
  }
}

export const sendMessage = createAsyncThunk(
  'chat/send',
  async (text, { getState, rejectWithValue }) => {
    const existing = getState().chat.messages;
    const messages = [...existing, { role: 'user', content: text }];
    return postConversation(messages, rejectWithValue);
  }
);

export const retryLast = createAsyncThunk(
  'chat/retry',
  async (_, { getState, rejectWithValue }) => {
    const messages = getState().chat.messages;
    return postConversation(messages, rejectWithValue);
  }
);

const chatSlice = createSlice({
  name: 'chat',
  initialState: {
    messages: [],
    status: 'idle',
    error: null,
  },
  reducers: {
    clearChat(state) {
      state.messages = [];
      state.status = 'idle';
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(sendMessage.pending, (state, action) => {
        state.messages.push({ role: 'user', content: action.meta.arg });
        state.status = 'loading';
        state.error = null;
      })
      .addCase(sendMessage.fulfilled, (state, action) => {
        state.messages.push({ role: 'assistant', content: action.payload });
        state.status = 'idle';
      })
      .addCase(sendMessage.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload || 'Something went wrong. Please retry.';
      })
      .addCase(retryLast.pending, (state) => {
        state.status = 'loading';
        state.error = null;
      })
      .addCase(retryLast.fulfilled, (state, action) => {
        state.messages.push({ role: 'assistant', content: action.payload });
        state.status = 'idle';
      })
      .addCase(retryLast.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload || 'Something went wrong. Please retry.';
      });
  },
});

export const { clearChat } = chatSlice.actions;
export default chatSlice.reducer;