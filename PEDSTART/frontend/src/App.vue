<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from './stores/auth'
import { useCourseStore } from './stores/course'

import HeaderGamification from './components/HeaderGamification.vue'
import HomePage from './components/HomePage.vue'
import UserDashboard from './components/UserDashboard.vue'
import ModuleSidebar from './components/ModuleSidebar.vue'
import LessonContent from './components/LessonContent.vue'
import QuizRunner from './components/QuizRunner.vue'
import OpenTaskSection from './components/OpenTaskSection.vue'
import AuthModal from './components/AuthModal.vue'

const authStore = useAuthStore()
const courseStore = useCourseStore()

const showAuthModal = ref(false)
const currentView = ref('home')

const openHome = () => {
  currentView.value = 'home'
}

const openDashboard = () => {
  if (!authStore.isAuthenticated) {
    showAuthModal.value = true
    return
  }
  currentView.value = 'dashboard'
}

const startLearning = (moduleId = null) => {
  if (!authStore.isAuthenticated) {
    showAuthModal.value = true
    return
  }

  currentView.value = 'learning'

  if (moduleId && courseStore.modules.length) {
    courseStore.activeModuleId = moduleId
    const module = courseStore.modules.find((item) => item.id === moduleId)
    if (module?.lessons?.length) {
      courseStore.activeLessonId = module.lessons[0].id
      courseStore.activeContentType = 'lesson'
    }
  }
}

onMounted(async () => {
  if (authStore.token) {
    await authStore.fetchProfile()
  }
  await courseStore.fetchModules()
})
</script>

<template>
  <div class="min-h-screen bg-slate-50 flex flex-col font-sans text-slate-800">
    <HeaderGamification
      @open-auth="showAuthModal = true"
      @go-home="openHome"
      @open-dashboard="openDashboard"
    />

    <section v-if="currentView !== 'learning'" class="bg-gradient-to-r from-indigo-950 via-indigo-900 to-indigo-950 text-white py-2.5 px-4 sm:px-6 border-b border-indigo-800/60 shadow-xs">
      <div class="max-w-[1600px] mx-auto flex flex-col md:flex-row items-center justify-between gap-2 text-xs">
        <div class="flex items-center gap-2">
          <span class="px-2 py-0.5 rounded bg-amber-400 text-indigo-950 font-black text-[10px] tracking-wider uppercase">
            METODIK ASOS
          </span>
          <span class="text-indigo-200">
            <!-- M.B. Muxamadaliyeva konsepsiyasi: -->
          </span>
          <span class="font-bold text-white hidden sm:inline">
            4 ta tayyorgarlik komponenti (Motivatsion, Kognitiv, Operatsion, Refleksiv)
          </span>
        </div>

        <div class="flex items-center gap-3 text-xs font-semibold text-indigo-200">
          <span class="flex items-center gap-1.5">
            <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            Test tizimi test rejimida ishlamoqda...
          </span>
        </div>
      </div>
    </section>

    <main v-if="currentView === 'home'" class="max-w-[1600px] w-full mx-auto px-4 sm:px-6 py-6 flex-1">
      <HomePage
        @open-auth="showAuthModal = true"
        @start-learning="startLearning"
        @open-dashboard="openDashboard"
      />
    </main>

    <main v-else-if="currentView === 'dashboard'" class="max-w-[1600px] w-full mx-auto px-4 sm:px-6 py-6 flex-1">
      <UserDashboard @start-learning="startLearning" @go-home="openHome" />
    </main>

    <main v-else class="max-w-[1600px] w-full mx-auto px-4 sm:px-6 py-5 flex-1 flex flex-col lg:flex-row gap-6 items-start">
      <ModuleSidebar class="w-full lg:w-[340px] lg:shrink-0" />

      <div class="flex-1 w-full min-w-0">
        <div v-if="courseStore.isLoading" class="p-12 text-center bg-white rounded-3xl border border-slate-200 shadow-xs">
          <div class="animate-spin text-4xl mb-3">🎓</div>
          <div class="text-slate-600 font-bold text-sm">PedTayyor modullari yuklanmoqda...</div>
        </div>

        <div v-else-if="!courseStore.activeModule && courseStore.activeContentType !== 'quiz'" class="p-12 text-center bg-white rounded-3xl border border-slate-200 shadow-xs">
          <div class="text-4xl mb-3">📖</div>
          <h3 class="text-base font-bold text-slate-800">Boshlash uchun modulni tanlang</h3>
          <p class="text-xs text-slate-500 mt-1">Chap menyudan o'rganmoqchi bo'lgan ma'ruza yoki amaliy topshiriqni bosing.</p>
        </div>

        <div v-else class="w-full">
          <LessonContent v-if="courseStore.activeContentType === 'lesson'" />
          <QuizRunner v-else-if="courseStore.activeContentType === 'quiz'" />
          <OpenTaskSection v-else-if="courseStore.activeContentType === 'task'" />
        </div>
      </div>
    </main>

    <footer class="bg-white border-t border-slate-200 py-4 text-center text-xs text-slate-500 mt-auto">
      <div class="max-w-[1600px] mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
        <div>
          <span class="font-bold text-slate-700">PedTayyor</span> — Bo'lajak pedagoglar uchun muvaffaqiyatli start va raqamli tayyorgarlik makoni.
        </div>
        <div class="text-[11px] text-slate-400">
          FastAPI + Vue.js 3 + PostgreSQL + OpenRouter API
        </div>
      </div>
    </footer>

    <AuthModal v-if="showAuthModal" @close="showAuthModal = false" />
  </div>
</template>
