<script setup>
import { ref, computed } from 'vue'
import axios from 'axios'
import { useCourseStore } from '../stores/course'
import { useAuthStore } from '../stores/auth'

const courseStore = useCourseStore()
const authStore = useAuthStore()

const task = computed(() => courseStore.activeTask)
const studentAnswer = ref('')
const isSubmitting = ref(false)
const aiResult = ref(null)
const error = ref(null)

const minChars = 30
const charCount = computed(() => studentAnswer.value.trim().length)
const canSubmit = computed(() => charCount.value >= minChars && !isSubmitting.value)

const submitToAI = async () => {
  if (!canSubmit.value) return
  if (!authStore.isAuthenticated) {
    alert("Javobingizni Sun'iy Intellekt baholashi va XP olish uchun iltimos, tizimga kiring.")
    return
  }

  isSubmitting.value = true
  error.value = null

  try {
    const response = await axios.post('/api/tasks/submit-open', {
      task_id: task.value.id,
      answer_text: studentAnswer.value
    })
    aiResult.value = response.data

    // Gamifikatsiya va XP ballarini Pinia store'da yangilash
    authStore.updateGamification(
      response.data.user_xp,
      response.data.user_level,
      response.data.user_status,
      response.data.new_badge_unlocked
    )
  } catch (err) {
    error.value = err.response?.data?.detail || "Sun'iy intellekt tahlilida xatolik yuz berdi"
  } finally {
    isSubmitting.value = false
  }
}

const getScoreColor = (score) => {
  if (score >= 80) return 'text-emerald-600 bg-emerald-50 border-emerald-300'
  if (score >= 60) return 'text-amber-600 bg-amber-50 border-amber-300'
  return 'text-rose-600 bg-rose-50 border-rose-300'
}
</script>

<template>
  <div v-if="task" class="space-y-6">
    <!-- Topshiriq Sarlovhasi va Mezonlar -->
    <div class="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-slate-200">
      <div>
        <div class="flex items-center gap-2">
          <span class="text-xs font-bold text-purple-600 uppercase tracking-wide">
            Ochiq Savol va Amaliy Topshiriq
          </span>
          <span v-if="task.is_module_final" class="px-2 py-0.5 rounded text-[10px] font-extrabold bg-amber-100 text-amber-800 border border-amber-300">
            Modul Yakuniy
          </span>
        </div>
        <h2 class="text-xl sm:text-2xl font-extrabold text-slate-900 mt-1">
          {{ task.title }}
        </h2>
      </div>
      <div class="flex items-center gap-3">
        <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-amber-50 text-amber-700 border border-amber-200">
          🏆 Maks. +{{ task.xp_reward }} XP
        </span>
      </div>
    </div>

    <!-- Topshiriq Sharti & Pedagogik Rubrika Kartasi -->
    <div class="bg-gradient-to-br from-slate-900 to-indigo-950 text-white rounded-3xl p-6 sm:p-8 shadow-md space-y-4">
      <div class="flex items-center gap-3 text-indigo-300 text-xs font-bold uppercase tracking-wider">
        <span class="text-lg">📋</span> Topshiriq yo'riqnomasi va keys holati
      </div>
      <p class="text-base sm:text-lg font-medium text-slate-100 leading-relaxed">
        {{ task.prompt }}
      </p>

      <!-- Pedagogik Baholash Mezoni (Muxamadaliyeva 4 komponenti) -->
      <div class="pt-4 border-t border-indigo-900/80 flex items-start gap-3 text-xs text-indigo-200 bg-indigo-950/40 p-4 rounded-2xl">
        <span class="text-base">🎯</span>
        <div>
          <span class="font-bold text-indigo-300">Pedagogik baholash mezoni:</span>
          <p class="mt-0.5 text-slate-300 leading-normal">{{ task.pedagogical_criteria }}</p>
        </div>
      </div>
    </div>

    <!-- Javob Yozish Textarea Paneli -->
    <div class="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200 shadow-xs space-y-4">
      <div class="flex items-center justify-between">
        <label for="student-answer" class="text-sm font-bold text-slate-800 flex items-center gap-2">
          <span>✍️</span> Sizning pedagogik yechimingiz va tahliliy javobingiz:
        </label>
        <span class="text-xs font-semibold" :class="charCount >= minChars ? 'text-emerald-600' : 'text-slate-400'">
          {{ charCount }} belgi (kamida {{ minChars }})
        </span>
      </div>

      <textarea
        id="student-answer"
        v-model="studentAnswer"
        rows="7"
        class="w-full p-4 rounded-2xl border border-slate-200 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-100 outline-none text-slate-800 text-sm leading-relaxed transition placeholder:text-slate-400"
        placeholder="Boshlang'ich ta'lim didaktikasi va metodikasiga tayangan holda o'z yechimingizni batafsil bayon eting... (Masalan: o'quvchilar motivatsiyasini oshirish, didaktik vositalar, amaliy metodlar va refleksiv savollar)"
      ></textarea>

      <!-- Xatolik xabari -->
      <div v-if="error" class="p-4 rounded-2xl bg-rose-50 border border-rose-200 text-rose-700 text-xs font-semibold">
        {{ error }}
      </div>

      <!-- Yuborish tugmasi -->
      <div class="flex flex-wrap items-center justify-between gap-4 pt-2">
        <p class="text-xs text-slate-500">
          🤖 Javobingiz <strong>OpenRouter API</strong> (Claude / GPT) orqali pedagogik mezonlar bo'yicha tahlil qilinadi.
        </p>

        <button
          @click="submitToAI"
          :disabled="!canSubmit"
          class="px-7 py-3.5 rounded-2xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold text-sm shadow-md shadow-indigo-200 transition flex items-center gap-3"
        >
          <span v-if="isSubmitting" class="animate-spin text-lg">⚙️</span>
          <span v-else class="text-lg">🚀</span>
          <span>{{ isSubmitting ? "Sun'iy Intellekt tahlil qilmoqda..." : "SI tahliliga yuborish" }}</span>
        </button>
      </div>
    </div>

    <!-- SUN'IY INTELLEKT (OPENROUTER) TAHLILI VA BAHOLASH NATIJASI -->
    <div
      v-if="aiResult"
      class="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200 shadow-md space-y-6 transition-all animate-fadeIn"
    >
      <!-- Sarlovha va Ball -->
      <div class="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-slate-100">
        <div class="flex items-center gap-3">
          <div class="w-12 h-12 rounded-2xl bg-indigo-50 text-indigo-600 flex items-center justify-center text-2xl font-bold">
            🤖
          </div>
          <div>
            <h3 class="text-lg font-extrabold text-slate-900">
              Sun'iy Intellekt Pedagogik Tahlili
            </h3>
            <p class="text-xs text-slate-500">
              OpenRouter orqali o'tkazilgan metodik ekspertiza
            </p>
          </div>
        </div>

        <!-- Ball indikatori -->
        <div class="flex items-center gap-3">
          <div
            class="px-5 py-2 rounded-2xl border text-center font-extrabold"
            :class="getScoreColor(aiResult.score)"
          >
            <div class="text-2xl leading-none">{{ aiResult.score }}</div>
            <div class="text-[10px] uppercase tracking-wider font-bold">100 balldan</div>
          </div>
          <div class="text-right">
            <span class="inline-block px-3 py-1 rounded-full text-xs font-black bg-amber-100 text-amber-800 border border-amber-300">
              +{{ aiResult.xp_earned }} XP berildi!
            </span>
          </div>
        </div>
      </div>

      <!-- Yangi nishon ochilgan bo'lsa (Celebration Banner) -->
      <div
        v-if="aiResult.new_badge_unlocked"
        class="p-4 rounded-2xl bg-gradient-to-r from-amber-400 to-amber-500 text-slate-950 font-bold text-sm flex items-center justify-between shadow-sm animate-bounce"
      >
        <div class="flex items-center gap-3">
          <span class="text-2xl">🎉</span>
          <div>
            <div>Yangi Nishon ochildi!</div>
            <div class="text-xs font-extrabold text-white">"{{ aiResult.new_badge_unlocked }}"</div>
          </div>
        </div>
        <span class="text-xl">🏆</span>
      </div>

      <!-- Pedagogik 4 ta Komponent bo'yicha Tahlil (M.B. Muxamadaliyeva) -->
      <div class="space-y-3 bg-slate-50 p-5 rounded-2xl border border-slate-200">
        <h4 class="text-xs font-extrabold text-slate-700 uppercase tracking-wider flex items-center gap-2">
          <span>📊</span> Pedagogik tayyorgarlik komponentlari bo'yicha ko'rsatkichlar:
        </h4>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
          <!-- Motivatsion -->
          <div class="bg-white p-3.5 rounded-xl border border-slate-200 shadow-2xs">
            <div class="flex justify-between text-xs font-bold mb-1.5 text-rose-800">
              <span>Motivatsion komponent</span>
              <span>{{ aiResult.pedagogical_components?.motivatsion }}%</span>
            </div>
            <div class="w-full bg-slate-100 rounded-full h-2">
              <div
                class="bg-rose-500 h-2 rounded-full transition-all duration-700"
                :style="{ width: `${aiResult.pedagogical_components?.motivatsion}%` }"
              ></div>
            </div>
          </div>

          <!-- Kognitiv -->
          <div class="bg-white p-3.5 rounded-xl border border-slate-200 shadow-2xs">
            <div class="flex justify-between text-xs font-bold mb-1.5 text-blue-800">
              <span>Kognitiv komponent</span>
              <span>{{ aiResult.pedagogical_components?.kognitiv }}%</span>
            </div>
            <div class="w-full bg-slate-100 rounded-full h-2">
              <div
                class="bg-blue-500 h-2 rounded-full transition-all duration-700"
                :style="{ width: `${aiResult.pedagogical_components?.kognitiv}%` }"
              ></div>
            </div>
          </div>

          <!-- Operatsion-faoliyatli -->
          <div class="bg-white p-3.5 rounded-xl border border-slate-200 shadow-2xs">
            <div class="flex justify-between text-xs font-bold mb-1.5 text-emerald-800">
              <span>Operatsion-faoliyatli</span>
              <span>{{ aiResult.pedagogical_components?.operatsion }}%</span>
            </div>
            <div class="w-full bg-slate-100 rounded-full h-2">
              <div
                class="bg-emerald-500 h-2 rounded-full transition-all duration-700"
                :style="{ width: `${aiResult.pedagogical_components?.operatsion}%` }"
              ></div>
            </div>
          </div>

          <!-- Refleksiv -->
          <div class="bg-white p-3.5 rounded-xl border border-slate-200 shadow-2xs">
            <div class="flex justify-between text-xs font-bold mb-1.5 text-amber-800">
              <span>Refleksiv komponent</span>
              <span>{{ aiResult.pedagogical_components?.refleksiv }}%</span>
            </div>
            <div class="w-full bg-slate-100 rounded-full h-2">
              <div
                class="bg-amber-500 h-2 rounded-full transition-all duration-700"
                :style="{ width: `${aiResult.pedagogical_components?.refleksiv}%` }"
              ></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Konstruktiv Pedagogik Fikr (Feedback) -->
      <div class="p-5 rounded-2xl bg-indigo-50/70 border border-indigo-200 text-indigo-950 space-y-1">
        <h4 class="text-xs font-extrabold uppercase tracking-wider text-indigo-800 flex items-center gap-1.5">
          <span>💬</span> Ekspert xulosasi:
        </h4>
        <p class="text-sm leading-relaxed font-normal">
          {{ aiResult.feedback }}
        </p>
      </div>

      <!-- Kuchli tomonlar va Tavsiyalar -->
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <!-- Kuchli tomonlar -->
        <div class="p-4 rounded-2xl bg-emerald-50/60 border border-emerald-200 space-y-2">
          <h5 class="text-xs font-extrabold uppercase tracking-wider text-emerald-800 flex items-center gap-1.5">
            <span>✅</span> Kuchli tomonlar:
          </h5>
          <ul class="text-xs text-slate-700 space-y-1.5 list-disc pl-4">
            <li v-for="(item, idx) in aiResult.strengths" :key="idx">
              {{ item }}
            </li>
          </ul>
        </div>

        <!-- Rivojlantirish bo'yicha tavsiyalar -->
        <div class="p-4 rounded-2xl bg-amber-50/60 border border-amber-200 space-y-2">
          <h5 class="text-xs font-extrabold uppercase tracking-wider text-amber-800 flex items-center gap-1.5">
            <span>💡</span> Metodik tavsiyalar:
          </h5>
          <ul class="text-xs text-slate-700 space-y-1.5 list-disc pl-4">
            <li v-for="(item, idx) in aiResult.improvements" :key="idx">
              {{ item }}
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>
