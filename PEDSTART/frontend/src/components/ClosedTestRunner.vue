<script setup>
import { ref, computed } from 'vue'
import axios from 'axios'
import { useCourseStore } from '../stores/course'
import { useAuthStore } from '../stores/auth'

const courseStore = useCourseStore()
const authStore = useAuthStore()

const test = computed(() => courseStore.activeTest)
const selectedOption = ref(null)
const isSubmitting = ref(false)
const result = ref(null)
const error = ref(null)

const selectOption = (idx) => {
  if (result.value) return // Allaqaqachon topshirilgan bo'lsa tanlashni bloklash
  selectedOption.value = idx
}

const submitTest = async () => {
  if (selectedOption.value === null) return
  if (!authStore.isAuthenticated) {
    alert("Test natijasi va XP ballarini saqlash uchun tizimga kiring.")
    return
  }

  isSubmitting.value = true
  error.value = null

  try {
    const response = await axios.post('/api/tests/submit-closed', {
      test_id: test.value.id,
      selected_option: selectedOption.value
    })
    result.value = response.data

    // Gamifikatsiyani yangilash
    authStore.updateGamification(
      response.data.user_xp,
      response.data.user_level,
      response.data.user_status
    )
  } catch (err) {
    error.value = err.response?.data?.detail || "Testni tekshirishda xatolik yuz berdi"
  } finally {
    isSubmitting.value = false
  }
}

const resetTest = () => {
  selectedOption.value = null
  result.value = null
  error.value = null
}
</script>

<template>
  <div v-if="test" class="space-y-6">
    <!-- Test sarlovhasi -->
    <div class="flex items-center justify-between pb-4 border-b border-slate-200">
      <div>
        <span class="text-xs font-bold text-emerald-600 uppercase tracking-wide">
          Yopiq Test Savoli (Avtomatik Baholash)
        </span>
        <h2 class="text-xl sm:text-2xl font-bold text-slate-900 mt-1">
          Bilimlarni tekshirish
        </h2>
      </div>
      <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-amber-50 text-amber-700 border border-amber-200">
        +{{ test.xp_reward }} XP
      </span>
    </div>

    <!-- Savol kartasi -->
    <div class="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200 shadow-xs space-y-6">
      <h3 class="text-lg font-bold text-slate-900 leading-snug">
        {{ test.question }}
      </h3>

      <!-- Variantlar -->
      <div class="space-y-3">
        <div
          v-for="(option, idx) in test.options"
          :key="idx"
          @click="selectOption(idx)"
          class="p-4 rounded-2xl border transition-all cursor-pointer flex items-center justify-between text-sm sm:text-base font-medium select-none"
          :class="[
            result
              ? idx === result.correct_option
                ? 'bg-emerald-50 border-emerald-500 text-emerald-900 font-bold'
                : selectedOption === idx
                  ? 'bg-rose-50 border-rose-500 text-rose-900'
                  : 'bg-slate-50/50 border-slate-200 text-slate-400 opacity-60'
              : selectedOption === idx
                ? 'bg-indigo-50 border-indigo-600 text-indigo-900 shadow-xs'
                : 'bg-white border-slate-200 hover:border-indigo-200 hover:bg-slate-50/70 text-slate-700'
          ]"
        >
          <div class="flex items-center gap-3">
            <span
              class="w-8 h-8 rounded-xl flex items-center justify-center font-bold text-xs"
              :class="selectedOption === idx ? 'bg-indigo-600 text-white' : 'bg-slate-100 text-slate-600'"
            >
              {{ String.fromCharCode(65 + idx) }}
            </span>
            <span>{{ option }}</span>
          </div>

          <!-- Natija ikonkalari -->
          <span v-if="result && idx === result.correct_option" class="text-emerald-600 font-bold text-lg">
            ✓
          </span>
          <span v-else-if="result && selectedOption === idx && !result.is_correct" class="text-rose-600 font-bold text-lg">
            ✕
          </span>
        </div>
      </div>

      <!-- Xatolik xabari -->
      <div v-if="error" class="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs font-semibold">
        {{ error }}
      </div>

      <!-- Tekshirish / Qayta yechish tugmalari -->
      <div class="pt-4 flex items-center justify-between">
        <button
          v-if="!result"
          @click="submitTest"
          :disabled="selectedOption === null || isSubmitting"
          class="px-6 py-3 rounded-2xl bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-200 disabled:text-slate-400 text-white font-bold text-sm shadow-sm transition flex items-center gap-2"
        >
          <span v-if="isSubmitting" class="animate-spin">⏳</span>
          <span>Javobni tekshirish</span>
        </button>

        <button
          v-else
          @click="resetTest"
          class="px-5 py-2.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-xs transition"
        >
          Qayta urinib ko'rish
        </button>
      </div>
    </div>

    <!-- Natija va Pedagogik Izoh (Feedback) -->
    <div
      v-if="result"
      class="rounded-3xl p-6 border transition-all animate-fadeIn"
      :class="result.is_correct ? 'bg-emerald-50/80 border-emerald-200 text-emerald-950' : 'bg-rose-50/80 border-rose-200 text-rose-950'"
    >
      <div class="flex items-start gap-4">
        <div class="w-12 h-12 rounded-2xl flex items-center justify-center text-2xl flex-shrink-0"
          :class="result.is_correct ? 'bg-emerald-600 text-white' : 'bg-rose-600 text-white'"
        >
          {{ result.is_correct ? '🎯' : '💡' }}
        </div>
        <div class="space-y-1">
          <div class="flex items-center gap-3">
            <h4 class="text-lg font-extrabold">
              {{ result.is_correct ? "To'g'ri javob!" : "Noto'g'ri javob!" }}
            </h4>
            <span v-if="result.xp_earned > 0" class="px-2.5 py-0.5 rounded-full text-xs font-black bg-emerald-200 text-emerald-800">
              +{{ result.xp_earned }} XP berildi!
            </span>
          </div>
          <p class="text-sm text-slate-700 pt-1 leading-relaxed">
            <span class="font-bold">Pedagogik izoh:</span> {{ result.explanation }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
