<script setup>
import { ref, computed } from 'vue'
import { useCourseStore } from '../stores/course'
import { useAuthStore } from '../stores/auth'

const courseStore = useCourseStore()
const authStore = useAuthStore()

const currentQuestionIndex = ref(0)
const quiz = computed(() => courseStore.currentQuiz)
const answers = computed(() => courseStore.quizAnswers)
const result = computed(() => courseStore.quizResult)
const isLoading = computed(() => courseStore.isQuizLoading)
const isSubmitting = computed(() => courseStore.isQuizSubmitting)

const questions = computed(() => quiz.value?.questions || [])
const totalQuestions = computed(() => questions.value.length)
const currentQuestion = computed(() => questions.value[currentQuestionIndex.value] || null)

// Javob berilgan savollar soni
const answeredCount = computed(() => Object.keys(answers.value).length)
const progressPercentage = computed(() => {
  if (totalQuestions.value === 0) return 0
  return Math.round((answeredCount.value / totalQuestions.value) * 100)
})

const selectOption = (questionId, optionIndex) => {
  if (result.value) return // Yakunlangan bo'lsa tanlashni bloklash
  answers.value[questionId] = optionIndex
}

const goToQuestion = (idx) => {
  if (idx >= 0 && idx < totalQuestions.value) {
    currentQuestionIndex.value = idx
  }
}

const nextQuestion = () => {
  if (currentQuestionIndex.value < totalQuestions.value - 1) {
    currentQuestionIndex.value++
  }
}

const prevQuestion = () => {
  if (currentQuestionIndex.value > 0) {
    currentQuestionIndex.value--
  }
}

const finishQuiz = () => {
  if (answeredCount.value < totalQuestions.value) {
    const unans = totalQuestions.value - answeredCount.value
    if (!confirm(`Siz hali ${unans} ta savolga javob bermadingiz. Shunda ham testni yakunlamoqchimisiz?`)) {
      return
    }
  }
  courseStore.submitQuiz()
}

const retakeQuiz = () => {
  if (courseStore.activeQuizType === 'lesson') {
    courseStore.openLessonQuiz(courseStore.activeModuleId, courseStore.activeLessonId)
  } else if (courseStore.activeQuizType === 'module') {
    courseStore.openModuleQuiz(courseStore.activeModuleId)
  } else {
    courseStore.openCourseFinalQuiz()
  }
  currentQuestionIndex.value = 0
}

const backToLesson = () => {
  courseStore.activeContentType = 'lesson'
}

const getBadgeStyle = (type) => {
  switch (type) {
    case 'lesson':
      return { text: 'Dars Testi (10 ta savol)', bg: 'bg-emerald-50 text-emerald-700 border-emerald-200' }
    case 'module':
      return { text: 'Modul Yakuniy Testi (25 ta savol)', bg: 'bg-amber-50 text-amber-700 border-amber-200' }
    case 'course_final':
      return { text: 'Kurs Yakuniy Attestatsiyasi (50 ta savol)', bg: 'bg-purple-50 text-purple-700 border-purple-200' }
    default:
      return { text: 'Test Topshirig\'i', bg: 'bg-slate-50 text-slate-700 border-slate-200' }
  }
}
</script>

<template>
  <div class="space-y-6">
    <!-- Yuklanmoqda holati -->
    <div v-if="isLoading" class="p-12 text-center bg-white rounded-3xl border border-slate-200 shadow-xs">
      <div class="animate-spin text-4xl mb-3">📝</div>
      <div class="text-slate-700 font-bold text-sm">Test savollari yuklanmoqda...</div>
    </div>

    <!-- Test oynasi -->
    <div v-else-if="quiz" class="space-y-6">
      <!-- 1. Header & Progress -->
      <div class="bg-white rounded-3xl p-6 border border-slate-200 shadow-xs space-y-4">
        <div class="flex flex-wrap items-center justify-between gap-3">
          <div>
            <span
              class="inline-block px-3 py-1 rounded-full text-xs font-extrabold border mb-2"
              :class="getBadgeStyle(quiz.quiz_type).bg"
            >
              {{ getBadgeStyle(quiz.quiz_type).text }}
            </span>
            <h2 class="text-xl sm:text-2xl font-black text-slate-900 leading-snug">
              {{ quiz.title }}
            </h2>
          </div>

          <div class="flex items-center gap-3">
            <div class="text-right">
              <div class="text-xs text-slate-500 font-semibold">Javob berildi</div>
              <div class="text-base font-extrabold text-indigo-700">
                {{ answeredCount }} / {{ totalQuestions }} ta
              </div>
            </div>
            <div class="w-12 h-12 rounded-2xl bg-indigo-50 text-indigo-700 flex items-center justify-center font-black text-sm">
              {{ progressPercentage }}%
            </div>
          </div>
        </div>

        <!-- Progress bar -->
        <div class="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
          <div
            class="bg-gradient-to-r from-indigo-500 to-emerald-500 h-2 rounded-full transition-all duration-300"
            :style="{ width: `${progressPercentage}%` }"
          ></div>
        </div>

        <!-- Savollar Navigator Grid (1..10, 1..25, 1..50) -->
        <div class="pt-2 border-t border-slate-100">
          <div class="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-2">
            Savollar navigatori:
          </div>
          <div class="flex flex-wrap gap-1.5 sm:gap-2 max-h-36 overflow-y-auto pr-1">
            <button
              v-for="(q, idx) in questions"
              :key="q.id"
              @click="goToQuestion(idx)"
              class="w-8 h-8 rounded-xl text-xs font-extrabold flex items-center justify-center transition-all cursor-pointer"
              :class="[
                currentQuestionIndex === idx
                  ? 'ring-2 ring-indigo-600 bg-indigo-600 text-white shadow-xs'
                  : answers[q.id] !== undefined
                    ? 'bg-emerald-100 text-emerald-800 border border-emerald-300 font-black'
                    : 'bg-slate-100 hover:bg-slate-200 text-slate-600'
              ]"
            >
              {{ idx + 1 }}
            </button>
          </div>
        </div>
      </div>

      <!-- 2. AKTIV TEST SAVOLI (Agar hali topshirilmagan bo'lsa) -->
      <div v-if="!result && currentQuestion" class="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200 shadow-xs space-y-6">
        <!-- Savol matni -->
        <div class="space-y-2">
          <div class="text-xs font-bold text-indigo-600 uppercase tracking-wider">
            Savol #{{ currentQuestionIndex + 1 }} / {{ totalQuestions }}
          </div>
          <h3 class="text-lg sm:text-xl font-bold text-slate-900 leading-snug">
            {{ currentQuestion.question }}
          </h3>
        </div>

        <!-- 4 ta Variant -->
        <div class="space-y-3">
          <div
            v-for="(opt, optIdx) in currentQuestion.options"
            :key="optIdx"
            @click="selectOption(currentQuestion.id, optIdx)"
            class="p-4 rounded-2xl border transition-all cursor-pointer flex items-center justify-between text-sm sm:text-base font-medium select-none"
            :class="[
              answers[currentQuestion.id] === optIdx
                ? 'bg-indigo-50 border-indigo-600 text-indigo-950 font-bold shadow-xs'
                : 'bg-white border-slate-200 hover:border-indigo-300 hover:bg-slate-50/70 text-slate-700'
            ]"
          >
            <div class="flex items-center gap-3">
              <span
                class="w-8 h-8 rounded-xl flex items-center justify-center font-extrabold text-xs"
                :class="answers[currentQuestion.id] === optIdx ? 'bg-indigo-600 text-white' : 'bg-slate-100 text-slate-600'"
              >
                {{ String.fromCharCode(65 + optIdx) }}
              </span>
              <span>{{ opt }}</span>
            </div>
            <span v-if="answers[currentQuestion.id] === optIdx" class="text-indigo-600 font-extrabold text-sm">
              ✓
            </span>
          </div>
        </div>

        <!-- Navigatsiya va Yakunlash tugmalari -->
        <div class="pt-4 border-t border-slate-100 flex flex-wrap items-center justify-between gap-3">
          <div class="flex items-center gap-2">
            <button
              @click="prevQuestion"
              :disabled="currentQuestionIndex === 0"
              class="px-4 py-2.5 rounded-xl border border-slate-200 hover:bg-slate-100 disabled:opacity-40 text-slate-700 text-xs font-bold transition flex items-center gap-1.5"
            >
              ← Oldingi
            </button>
            <button
              @click="nextQuestion"
              :disabled="currentQuestionIndex === totalQuestions - 1"
              class="px-4 py-2.5 rounded-xl border border-slate-200 hover:bg-slate-100 disabled:opacity-40 text-slate-700 text-xs font-bold transition flex items-center gap-1.5"
            >
              Keyingi →
            </button>
          </div>

          <button
            @click="finishQuiz"
            :disabled="isSubmitting"
            class="px-6 py-3 rounded-2xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white font-extrabold text-sm shadow-md shadow-emerald-200 transition flex items-center gap-2"
          >
            <span v-if="isSubmitting" class="animate-spin">⏳</span>
            <span>Testni yakunlash va tekshirish ({{ answeredCount }}/{{ totalQuestions }})</span>
          </button>
        </div>
      </div>

      <!-- 3. TEST NATIJALARI VA TAHLILI (SUBMITTED RESULT) -->
      <div v-else-if="result" class="space-y-6 animate-fadeIn">
        <!-- Natija Kartasi -->
        <div class="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200 shadow-md space-y-6">
          <div class="flex flex-wrap items-center justify-between gap-4 pb-6 border-b border-slate-100">
            <div>
              <span class="text-xs font-extrabold text-slate-400 uppercase tracking-wider">
                Natijalar xulosasi
              </span>
              <h3 class="text-2xl font-black text-slate-900 mt-1">
                {{ result.title }}
              </h3>
            </div>

            <!-- Katta Ball Doirasi -->
            <div class="flex items-center gap-4">
              <div
                class="px-6 py-3 rounded-3xl border text-center font-black"
                :class="result.passed ? 'bg-emerald-50 text-emerald-700 border-emerald-300' : 'bg-rose-50 text-rose-700 border-rose-300'"
              >
                <div class="text-3xl leading-none">{{ result.score_percentage }}%</div>
                <div class="text-xs font-bold mt-1">
                  {{ result.correct_answers }} / {{ result.total_questions }} ta to'g'ri
                </div>
              </div>

              <div>
                <span class="inline-block px-4 py-1.5 rounded-full text-xs font-black bg-amber-100 text-amber-800 border border-amber-300">
                  ✨ +{{ result.xp_earned }} XP berildi!
                </span>
                <div class="text-[11px] text-slate-500 mt-1 font-semibold">
                  Yangi umumiy ball: {{ result.user_xp }} XP ({{ result.user_status }})
                </div>
              </div>
            </div>
          </div>

          <!-- Yangi Nishon Ochilgan bo'lsa -->
          <div
            v-if="result.new_badge_unlocked"
            class="p-4 rounded-2xl bg-gradient-to-r from-amber-400 to-amber-500 text-slate-950 font-bold text-sm flex items-center justify-between shadow-sm animate-bounce"
          >
            <div class="flex items-center gap-3">
              <span class="text-3xl">🏆</span>
              <div>
                <div class="text-xs font-bold uppercase tracking-wider text-slate-800">Yangi Yutuq Nishoni Ochildi!</div>
                <div class="text-base font-black text-slate-950">"{{ result.new_badge_unlocked }}"</div>
              </div>
            </div>
            <span class="text-2xl">🎉</span>
          </div>

          <!-- Qayta urinish yoki Darsga qaytish -->
          <div class="flex items-center justify-between pt-2">
            <button
              @click="backToLesson"
              class="px-5 py-2.5 rounded-xl border border-slate-200 hover:bg-slate-50 text-slate-700 text-xs font-bold transition"
            >
              ← Darsga qaytish
            </button>
            <button
              @click="retakeQuiz"
              class="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold transition shadow-xs"
            >
              🔄 Testni qayta topshirish
            </button>
          </div>
        </div>

        <!-- 4. HAR BIR SAVOL BO'YICHA PEDAGOGIK TAHLIL (REVIEW) -->
        <div class="space-y-4">
          <div class="flex items-center justify-between">
            <h4 class="text-base font-extrabold text-slate-900 flex items-center gap-2">
              <span>📋</span> Barcha savollar tahlili va to'g'ri javoblar:
            </h4>
            <span class="text-xs text-slate-500 font-semibold">
              To'g'ri: {{ result.correct_answers }}, Noto'g'ri: {{ result.total_questions - result.correct_answers }}
            </span>
          </div>

          <div
            v-for="(rev, idx) in result.questions_review"
            :key="rev.id"
            class="bg-white rounded-3xl p-6 border transition-all space-y-4"
            :class="rev.is_correct ? 'border-emerald-200 bg-emerald-50/20' : 'border-rose-200 bg-rose-50/20'"
          >
            <div class="flex items-start justify-between gap-3">
              <div class="flex items-start gap-3">
                <span
                  class="w-7 h-7 rounded-lg flex items-center justify-center font-black text-xs flex-shrink-0"
                  :class="rev.is_correct ? 'bg-emerald-600 text-white' : 'bg-rose-600 text-white'"
                >
                  {{ idx + 1 }}
                </span>
                <h5 class="text-sm font-bold text-slate-900 leading-snug">
                  {{ rev.question }}
                </h5>
              </div>

              <span
                class="px-2.5 py-0.5 rounded-full text-[11px] font-black"
                :class="rev.is_correct ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-100 text-rose-800'"
              >
                {{ rev.is_correct ? "To'g'ri (+XP)" : "Xato" }}
              </span>
            </div>

            <!-- Variantlar ko'rinishi -->
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
              <div
                v-for="(opt, optIdx) in rev.options"
                :key="optIdx"
                class="p-3 rounded-xl border flex items-center justify-between"
                :class="[
                  optIdx === rev.correct_option
                    ? 'bg-emerald-100/80 border-emerald-400 text-emerald-950 font-bold'
                    : optIdx === rev.selected_option && !rev.is_correct
                      ? 'bg-rose-100/80 border-rose-400 text-rose-950 font-bold'
                      : 'bg-white border-slate-200 text-slate-600 opacity-70'
                ]"
              >
                <div class="flex items-center gap-2">
                  <span class="font-bold">{{ String.fromCharCode(65 + optIdx) }})</span>
                  <span>{{ opt }}</span>
                </div>
                <span v-if="optIdx === rev.correct_option" class="text-emerald-700 font-black">✓ To'g'ri</span>
                <span v-else-if="optIdx === rev.selected_option && !rev.is_correct" class="text-rose-700 font-black">✕ Sizning javobingiz</span>
              </div>
            </div>

            <!-- Pedagogik Izoh -->
            <div class="p-3 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-700 leading-relaxed">
              <strong class="text-slate-900">Pedagogik sharh:</strong> {{ rev.explanation }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
