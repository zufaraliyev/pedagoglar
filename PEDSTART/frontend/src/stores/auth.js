import { defineStore } from 'pinia'
import axios from 'axios'

const USER_STORAGE_KEY = 'pedtayyor_user'
const TOKEN_STORAGE_KEY = 'pedtayyor_token'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: JSON.parse(localStorage.getItem(USER_STORAGE_KEY) || 'null'),
    token: localStorage.getItem(TOKEN_STORAGE_KEY) || null,
    isLoading: false,
    error: null,
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
    currentLevel: (state) => state.user?.level || 1,
    currentXp: (state) => state.user?.xp || 0,
    statusTitle: (state) => state.user?.status_title || "Pedagog-izlanuvchi",
    progressPercentage: (state) => state.user?.progress_percentage || 0,
    nextLevelXp: (state) => state.user?.next_level_xp || 200,
    badges: (state) => state.user?.badges || [],
  },

  actions: {
    async login(username, password) {
      this.isLoading = true
      this.error = null
      try {
        const response = await axios.post('/api/auth/login', { username, password })
        this.token = response.data.access_token
        this.user = response.data.user
        localStorage.setItem(TOKEN_STORAGE_KEY, this.token)
        localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(this.user))
        axios.defaults.headers.common['Authorization'] = `Bearer ${this.token}`
        return true
      } catch (err) {
        this.error = err.response?.data?.detail || "Kirishda xatolik yuz berdi"
        return false
      } finally {
        this.isLoading = false
      }
    },

    async register(username, password, fullName) {
      this.isLoading = true
      this.error = null
      try {
        const response = await axios.post('/api/auth/register', {
          username,
          password,
          full_name: fullName || "Bo'lajak Pedagog"
        })
        this.token = response.data.access_token
        this.user = response.data.user
        localStorage.setItem(TOKEN_STORAGE_KEY, this.token)
        localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(this.user))
        axios.defaults.headers.common['Authorization'] = `Bearer ${this.token}`
        return true
      } catch (err) {
        this.error = err.response?.data?.detail || "Ro'yxatdan o'tishda xatolik yuz berdi"
        return false
      } finally {
        this.isLoading = false
      }
    },

    async fetchProfile() {
      if (!this.token) return
      try {
        axios.defaults.headers.common['Authorization'] = `Bearer ${this.token}`
        const response = await axios.get('/api/auth/me')
        this.user = response.data
        localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(this.user))
      } catch (err) {
        if (err.response?.status === 401) {
          this.logout()
        }
      }
    },

    updateGamification(newXp, newLevel, newStatus, newBadge) {
      if (!this.user) return
      this.user.xp = newXp
      this.user.level = newLevel
      this.user.status_title = newStatus
      if (newBadge && !this.user.badges.includes(newBadge)) {
        this.user.badges.push(newBadge)
      }
      localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(this.user))
      this.fetchProfile()
    },

    logout() {
      this.token = null
      this.user = null
      localStorage.removeItem(TOKEN_STORAGE_KEY)
      localStorage.removeItem(USER_STORAGE_KEY)
      delete axios.defaults.headers.common['Authorization']
    }
  }
})
