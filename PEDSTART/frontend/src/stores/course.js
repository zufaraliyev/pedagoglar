import { defineStore } from 'pinia'
import axios from 'axios'
import { useAuthStore } from './auth'

export const useCourseStore = defineStore('course', {
  state: () => ({
    modules: [],
    activeModuleId: null,
    activeLessonId: null,
    activeTaskId: null,
    activeContentType: 'lesson', // 'lesson' | 'quiz' | 'task'
    
    // Quiz state
    activeQuizType: 'lesson', // 'lesson' | 'module' | 'course_final'
    currentQuiz: null, // { quiz_type, title, total_questions, questions: [] }
    quizAnswers: {}, // { test_id: selected_option }
    quizResult: null, // QuizSubmitResponse
    isQuizLoading: false,
    isQuizSubmitting: false,

    isLoading: false,
    error: null,
  }),

  getters: {
    activeModule: (state) => state.modules.find(m => m.id === state.activeModuleId) || null,
    activeLesson: (state) => {
      const mod = state.modules.find(m => m.id === state.activeModuleId)
      return mod?.lessons.find(l => l.id === state.activeLessonId) || null
    },
    activeTask: (state) => {
      const mod = state.modules.find(m => m.id === state.activeModuleId)
      if (!mod) return null
      for (const lesson of mod.lessons) {
        const t = lesson.tasks?.find(tk => tk.id === state.activeTaskId)
        if (t) return t
      }
      return mod.final_tasks?.find(tk => tk.id === state.activeTaskId) || null
    }
  },

  actions: {
    async fetchModules() {
      this.isLoading = true
      try {
        const response = await axios.get('/api/modules')
        this.modules = response.data
        if (this.modules.length > 0 && !this.activeModuleId) {
          const firstMod = this.modules[0]
          this.activeModuleId = firstMod.id
          if (firstMod.lessons?.length > 0) {
            this.activeLessonId = firstMod.lessons[0].id
            this.activeContentType = 'lesson'
          }
        }
      } catch (err) {
        this.error = "Modullarni yuklab bo'lmadi"
      } finally {
        this.isLoading = false
      }
    },

    selectLesson(moduleId, lessonId) {
      this.activeModuleId = moduleId
      this.activeLessonId = lessonId
      this.activeTaskId = null
      this.activeContentType = 'lesson'
    },

    selectTask(moduleId, taskId) {
      this.activeModuleId = moduleId
      this.activeTaskId = taskId
      this.activeContentType = 'task'
    },

    // 1. Dars yakunidagi 10 talik test topshirig'i
    async openLessonQuiz(moduleId, lessonId) {
      this.activeModuleId = moduleId
      this.activeLessonId = lessonId
      this.activeQuizType = 'lesson'
      this.activeContentType = 'quiz'
      this.quizAnswers = {}
      this.quizResult = null
      this.isQuizLoading = true

      try {
        const res = await axios.get(`/api/quizzes/lesson/${lessonId}`)
        this.currentQuiz = res.data
      } catch (err) {
        alert("Dars test savollarini yuklab bo'lmadi")
      } finally {
        this.isQuizLoading = false
      }
    },

    // 2. Modul yakunidagi 25 talik test topshirig'i
    async openModuleQuiz(moduleId) {
      this.activeModuleId = moduleId
      this.activeQuizType = 'module'
      this.activeContentType = 'quiz'
      this.quizAnswers = {}
      this.quizResult = null
      this.isQuizLoading = true

      try {
        const res = await axios.get(`/api/quizzes/module/${moduleId}`)
        this.currentQuiz = res.data
      } catch (err) {
        alert("Modul yakuniy testlarini yuklab bo'lmadi")
      } finally {
        this.isQuizLoading = false
      }
    },

    // 3. Kurs yakunidagi 50 talik katta attestatsiya testi
    async openCourseFinalQuiz() {
      this.activeQuizType = 'course_final'
      this.activeContentType = 'quiz'
      this.quizAnswers = {}
      this.quizResult = null
      this.isQuizLoading = true

      try {
        const res = await axios.get('/api/quizzes/course-final')
        this.currentQuiz = res.data
      } catch (err) {
        alert("Kurs yakuniy attestatsiya testlarini yuklab bo'lmadi")
      } finally {
        this.isQuizLoading = false
      }
    },

    // Test topshirig'ini yakunlash va jo'natish
    async submitQuiz() {
      if (!this.currentQuiz) return
      const authStore = useAuthStore()

      if (!authStore.isAuthenticated) {
        alert("Test natijasi va XP ballarini saqlash uchun tizimga kiring.")
        return
      }

      this.isQuizSubmitting = true
      try {
        const payload = {
          quiz_type: this.activeQuizType,
          lesson_id: this.activeQuizType === 'lesson' ? this.activeLessonId : null,
          module_id: this.activeQuizType === 'module' ? this.activeModuleId : null,
          answers: this.quizAnswers
        }

        const res = await axios.post('/api/quizzes/submit', payload)
        this.quizResult = res.data

        // Gamifikatsiya va XP ballarini Pinia store'da yangilash
        authStore.updateGamification(
          res.data.user_xp,
          res.data.user_level,
          res.data.user_status,
          res.data.new_badge_unlocked
        )
      } catch (err) {
        alert(err.response?.data?.detail || "Testni tekshirishda xatolik yuz berdi")
      } finally {
        this.isQuizSubmitting = false
      }
    }
  }
})
