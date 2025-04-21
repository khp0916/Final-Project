import { createSlice } from "@reduxjs/toolkit";

const storedUser = localStorage.getItem("user");
const storedToken = localStorage.getItem("token");

const initialState = {
  isLogin: !!storedUser && !!storedToken,
  loading: false,
  error: null,
  message: null,
  user: storedUser ? JSON.parse(storedUser) : null,
  favoriteList: storedUser ? JSON.parse(storedUser).favoriteList || [] : [],
};

const loginSlice = createSlice({
  name: "login",
  initialState,
  reducers: {
    loginStart: (state) => {
      state.loading = true;
      state.error = null;
    },
    loginSuccess: (state, action) => {
      state.isLogin = true;
      state.loading = false;
      state.error = null;
      state.user = action.payload;
      state.message = action.payload.message;
      state.favoriteList = action.payload.favoriteList || [];
      
      localStorage.setItem("user", JSON.stringify({
        ...action.payload,
        favoriteList: action.payload.favoriteList || []
      }));
    },
    loginFailure: (state, action) => {
      state.loading = false;
      state.error = action.payload;
    },
    logout: (state) => {
      state.isLogin = false;
      state.user = null;
      state.favoriteList = [];
      
      localStorage.removeItem("user");
      localStorage.removeItem("token");
      localStorage.removeItem("isLoggedIn");
      localStorage.removeItem("userId");
    },
    clearError: (state) => {
      state.error = null;
      state.message = null;
    },
    updateFavorites: (state, action) => {
      state.favoriteList = action.payload;
      
      if (state.user) {
        localStorage.setItem("user", JSON.stringify({
          ...state.user,
          favoriteList: action.payload
        }));
      }
    }
  },
});

export const { loginStart, loginSuccess, loginFailure, logout, clearError, updateFavorites } = loginSlice.actions;
export default loginSlice.reducer;