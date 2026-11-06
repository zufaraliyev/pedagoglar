<script setup>
import { computed } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useCourseStore } from '../stores/course'

const authStore = useAuthStore()
const courseStore = useCourseStore()

const emit = defineEmits(['startLearning', 'goHome'])

const user = computed(() => authStore.user)
const modules = computed(() => courseStore.modules)
const completionRate = computed(() => Math.min(100, Math.max(0, authStore.progressPercentage || 0)))
const nextLevelXp = computed(() => authStore.nextLevelXp || 200)

const statCards = computed(() => [
  { label: 'Level', value: `L${authStore.currentLevel}`, icon: '🏆', tone: 'bg-amber-50 text-amber-700 border-amber-200' },
  { label: 'Umumiy XP', value: `${authStore.currentXp} XP`, icon: '⚡', tone: 'bg-indigo-50 text-indigo-700 border-indigo-200' },
  { label: 'Yakuniy daraja', value: `${completionRate.value}%`, icon: '📈', tone: 'bg-emerald-50 text-emerald-700 border-emerald-200' },
  { label: 'Badges', value: `${authStore.badges.length}`, icon: '🎖️', tone: 'bg-violet-50 text-violet-700 border-violet-200' },
])

const openModule = (moduleId) => {
  emit('startLearning', moduleId)
}
</script>

<template>
  <div class="space-y-6 pb-12">
    <section class="rounded-3xl border border-indigo-100 bg-gradient-to-br from-indigo-950 via-indigo-900 to-slate-950 p-6 sm:p-8 text-white shadow-xl">
      <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
        <div class="space-y-4">
          <div class="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/10 border border-white/15 text-xs font-black uppercase tracking-[0.18em] text-amber-300">
            <span>👤</span> Shaxsiy kabinet
          </div>

          <div>
            <h1 class="text-2xl sm:text-4xl font-black tracking-tight">
              Salom, {{ user?.full_name || user?.username || 'Talaba' }}!
            </h1>
            <p class="mt-2 text-sm text-indigo-100 max-w-2xl">
              O'quv jarayoningizni kuzatib boring, modullarni davom ettiring va bilim darajangizni oshirishga doimiy e'tibor qiling.
            </p>
          </div>
        </div>

        <div class="flex flex-wrap gap-3">
          <button
            type="button"
            @click="emit('goHome')"
            class="px-5 py-3 rounded-2xl bg-white/10 border border-white/15 text-white font-bold text-sm hover:bg-white/15 transition"
          >
            Bosh sahifa
          </button>
          <button
            type="button"
            @click="emit('startLearning', modules[0]?.id)"
            class="px-5 py-3 rounded-2xl bg-gradient-to-r from-amber-400 to-amber-500 text-indigo-950 font-black text-sm shadow-lg shadow-amber-500/25 hover:-translate-y-0.5 transition"
          >
            Modullarga o'tish
          </button>
        </div>
      </div>
    </section>

    <section class="grid grid-cols-2 xl:grid-cols-4 gap-4">
      <div
        v-for="card in statCards"
        :key="card.label"
        class="rounded-3xl border border-slate-200 bg-white p-5 shadow-xs"
      >
        <div class="flex items-center justify-between mb-4">
          <div class="w-11 h-11 rounded-2xl flex items-center justify-center text-xl shadow-xs" :class="card.tone">
            {{ card.icon }}
          </div>
        </div>
        <div class="text-2xl font-black text-slate-900">{{ card.value }}</div>
        <div class="mt-1 text-[11px] font-bold uppercase tracking-[0.15em] text-slate-500">{{ card.label }}</div>
      </div>
    </section>

    <section class="grid grid-cols-1 xl:grid-cols-[1.35fr_0.65fr] gap-6">
      <div class="rounded-3xl border border-slate-200 bg-white p-6 shadow-xs">
        <div class="flex items-center justify-between gap-3 mb-5">
          <div>
            <p class="text-[11px] font-black uppercase tracking-[0.18em] text-indigo-600">Tarix</p>
            <h2 class="text-2xl font-black text-slate-900">Modullarim</h2>
          </div>
          <div class="text-xs font-bold text-slate-500">{{ modules.length }} ta</div>
        </div>

        <div class="space-y-4">
          <div
            v-for="module in modules"
            :key="module.id"
            class="rounded-2xl border border-slate-200 p-4 hover:border-indigo-300 hover:shadow-md transition-all"
          >
            <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
              <div>
                <div class="text-[10px] font-black uppercase tracking-[0.16em] text-indigo-600">
                  {{ module.pedagogical_component || 'Pedagogik komponent' }}
                </div>
                <h3 class="mt-1 text-lg font-black text-slate-900">{{ module.title }}</h3>
              </div>
              <button
                type="button"
                @click="openModule(module.id)"
                class="px-3 py-2 rounded-xl bg-indigo-600 text-white text-xs font-bold hover:bg-indigo-700 transition"
              >
                O'rganishni davom ettirish
              </button>
            </div>

            <p class="mt-3 text-sm text-slate-600 leading-relaxed">
              {{ module.description }}
            </p>

            <div class="mt-4">
              <div class="flex items-center justify-between mb-1">
                <span class="text-[11px] font-bold text-slate-500">Progress</span>
                <span class="text-[11px] font-black text-indigo-700">{{ Math.min(100, ((module.id || 0) % 5) * 20 + 20) }}%</span>
              </div>
              <div class="h-2.5 w-full overflow-hidden rounded-full bg-slate-100">
                <div
                  class="h-full rounded-full bg-gradient-to-r from-indigo-500 to-amber-500 transition-all"
                  :style="{ width: `${Math.min(100, ((module.id || 0) % 5) * 20 + 20)}%` }"
                ></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="space-y-6">
        <div class="rounded-3xl border border-slate-200 bg-white p-6 shadow-xs">
          <p class="text-[11px] font-black uppercase tracking-[0.18em] text-indigo-600">O'quv maqsadi</p>
          <h3 class="mt-2 text-xl font-black text-slate-900">Keyingi daraja</h3>

          <div class="mt-4 rounded-2xl bg-slate-50 p-4 border border-slate-200">
            <div class="flex items-center justify-between text-sm font-bold text-slate-600">
              <span>Progress</span>
              <span>{{ completionRate }}%</span>
            </div>
            <div class="mt-3 h-2.5 w-full overflow-hidden rounded-full bg-slate-200">
              <div
                class="h-full rounded-full bg-gradient-to-r from-emerald-500 to-amber-500"
                :style="{ width: `${completionRate}%` }"
              ></div>
            </div>
            <div class="mt-3 text-xs text-slate-500">
              Keyingi level uchun {{ Math.max(0, nextLevelXp - authStore.currentXp) }} XP qoldi.
            </div>
          </div>
        </div>

        <div class="rounded-3xl border border-slate-200 bg-white p-6 shadow-xs">
          <p class="text-[11px] font-black uppercase tracking-[0.18em] text-amber-600">Nishonlar</p>
          <div v-if="authStore.badges.length" class="mt-4 space-y-2">
            <div
              v-for="(badge, index) in authStore.badges"
              :key="index"
              class="flex items-center gap-3 rounded-2xl bg-amber-50 border border-amber-200 px-3 py-2"
            >
              <span class="text-lg">🏅</span>
              <span class="text-sm font-bold text-amber-800">{{ badge }}</span>
            </div>
          </div>
          <div v-else class="mt-4 rounded-2xl border border-dashed border-slate-300 bg-slate-50 p-4 text-sm text-slate-500">
            Hali nishonlar yo'q. Darslarni davom ettirib, birinchisini qo'lga kiriting.
          </div>
        </div>
      </div>
    </section>
  </div>
</template>
