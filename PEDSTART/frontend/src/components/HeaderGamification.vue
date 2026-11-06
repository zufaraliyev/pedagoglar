<script setup>
import { computed } from 'vue'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()

const user = computed(() => authStore.user)
const level = computed(() => authStore.currentLevel)
const xp = computed(() => authStore.currentXp)
const statusTitle = computed(() => authStore.statusTitle)
const progress = computed(() => authStore.progressPercentage)
const nextXp = computed(() => authStore.nextLevelXp)
const badges = computed(() => authStore.badges)

const emit = defineEmits(['openAuth', 'goHome', 'openDashboard'])

const handleLogout = () => {
  authStore.logout()
  emit('goHome')
}
</script>

<template>
  <header class="bg-white border-b border-slate-200 sticky top-0 z-30 shadow-xs">
    <div class="max-w-[1600px] mx-auto px-4 sm:px-6">
      <div class="flex items-center justify-between h-14 sm:h-16">
        <button
          type="button"
          @click="emit('goHome')"
          class="flex items-center space-x-3 text-left cursor-pointer hover:opacity-90 transition-opacity"
        >
          <div class="w-9 h-9 sm:w-10 sm:h-10 rounded-xl bg-gradient-to-tr from-indigo-600 to-indigo-500 flex items-center justify-center text-white shadow-xs text-xl sm:text-2xl font-bold flex-shrink-0">
            🎓
          </div>
          <div>
            <div class="flex items-center gap-2">
              <span class="text-xl sm:text-2xl font-black tracking-tight bg-gradient-to-r from-indigo-700 to-indigo-500 bg-clip-text text-transparent">
                PedStart
              </span>
              <span class="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-bold bg-indigo-50 text-indigo-700 border border-indigo-200">
                v1.0 AI
              </span>
            </div>
            <p class="text-[11px] text-slate-500 font-medium hidden md:block leading-tight">
              Bo'lajak pedagoglar uchun muvaffaqiyatli start va raqamli tayyorgarlik makoni
            </p>
          </div>
        </button>

        <div v-if="authStore.isAuthenticated" class="flex items-center space-x-3 sm:space-x-5">
          <div class="bg-slate-50/80 border border-slate-200 rounded-xl px-3 py-1.5 hidden sm:flex items-center space-x-3">
            <div class="flex items-center space-x-2">
              <div class="w-7 h-7 rounded-lg bg-amber-500 text-white font-black flex items-center justify-center shadow-2xs text-xs">
                L{{ level }}
              </div>
              <div>
                <div class="text-[11px] font-black text-slate-800 leading-none">
                  {{ statusTitle }}
                </div>
                <div class="text-[10px] text-slate-500 mt-0.5 font-semibold">
                  {{ xp }} XP / <span class="text-slate-400">{{ nextXp }} XP</span>
                </div>
              </div>
            </div>

            <div class="w-24 sm:w-28">
              <div class="flex justify-between text-[9px] text-slate-500 mb-0.5 font-bold">
                <span>Progress</span>
                <span>{{ progress }}%</span>
              </div>
              <div class="w-full bg-slate-200 rounded-full h-1.5 overflow-hidden">
                <div
                  class="bg-gradient-to-r from-indigo-500 to-amber-500 h-1.5 rounded-full transition-all duration-700 ease-out"
                  :style="{ width: `${progress}%` }"
                ></div>
              </div>
            </div>

            <div v-if="badges.length" class="flex items-center pl-2 border-l border-slate-200 gap-1 text-base">
              <span
                v-for="(b, idx) in badges"
                :key="idx"
                class="hover:scale-125 transition-transform cursor-pointer"
                :title="'Nishon: ' + b"
              >
                {{ b }}
              </span>
            </div>
          </div>

          <button
            type="button"
            @click="emit('openDashboard')"
            class="hidden sm:inline-flex items-center px-3 py-1.5 rounded-xl border border-indigo-200 bg-indigo-50 text-indigo-700 hover:bg-indigo-100 text-xs font-bold transition"
          >
            Kabinet
          </button>

          <div class="flex items-center space-x-2.5">
            <div class="text-right hidden sm:block">
              <div class="text-xs font-bold text-slate-800 leading-tight">{{ user?.full_name || user?.username }}</div>
              <div class="text-[10px] text-emerald-600 font-bold flex items-center justify-end gap-1">
                <span class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                Faol talaba
              </div>
            </div>
            <button
              @click="handleLogout"
              title="Tizimdan chiqish"
              class="px-2.5 py-1 text-xs font-bold text-slate-600 hover:text-rose-600 hover:bg-rose-50 border border-slate-200 hover:border-rose-200 rounded-lg transition"
            >
              Chiqish
            </button>
          </div>
        </div>

        <div v-else class="flex items-center space-x-3">
          <button
            @click="emit('openAuth')"
            class="px-4 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs shadow-xs transition"
          >
            Kirish / Ro'yxatdan o'tish
          </button>
        </div>
      </div>
    </div>
  </header>
</template>
