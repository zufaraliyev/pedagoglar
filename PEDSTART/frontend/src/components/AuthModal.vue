<script setup>
import { ref } from 'vue'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()

const isLoginMode = ref(true)
const username = ref('talaba')
const password = ref('talaba123')
const fullName = ref('Dilnoza Rahimova')

const emit = defineEmits(['close'])

const handleSubmit = async () => {
  let success = false
  if (isLoginMode.value) {
    success = await authStore.login(username.value, password.value)
  } else {
    success = await authStore.register(username.value, password.value, fullName.value)
  }

  if (success) {
    emit('close')
  }
}
</script>

<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs">
    <div class="bg-white rounded-3xl max-w-md w-full p-6 sm:p-8 shadow-2xl border border-slate-100 relative">
      <!-- Yopish tugmasi -->
      <button
        @click="emit('close')"
        class="absolute top-5 right-5 w-8 h-8 rounded-full bg-slate-100 hover:bg-slate-200 flex items-center justify-center text-slate-500 font-bold transition"
      >
        ✕
      </button>

      <!-- Sarlovha -->
      <div class="text-center mb-6">
        <div class="w-14 h-14 rounded-2xl bg-indigo-50 text-indigo-600 flex items-center justify-center text-3xl mx-auto mb-3 shadow-xs">
          🎓
        </div>
        <h3 class="text-2xl font-extrabold text-slate-900">
          {{ isLoginMode ? "PedStart tizimiga kirish" : "Ro'yxatdan o'tish" }}
        </h3>
        <p class="text-xs text-slate-500 mt-1">
          Faqat Login va Parol kifoya. Email yoki SMS tasdiqlash talab qilinmaydi.
        </p>
      </div>

      <!-- Xatolik -->
      <div v-if="authStore.error" class="mb-4 p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs font-semibold">
        {{ authStore.error }}
      </div>

      <!-- Forma -->
      <form @submit.prevent="handleSubmit" class="space-y-4">
        <div v-if="!isLoginMode">
          <label class="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
            F.I.Sh. (To'liq ism)
          </label>
          <input
            v-model="fullName"
            type="text"
            required
            placeholder="Masalan: Dilnoza Rahimova"
            class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-indigo-600 focus:ring-4 focus:ring-indigo-50 outline-none text-sm transition"
          />
        </div>

        <div>
          <label class="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
            Login (Foydalanuvchi nomi)
          </label>
          <input
            v-model="username"
            type="text"
            required
            placeholder="Login kiriting..."
            class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-indigo-600 focus:ring-4 focus:ring-indigo-50 outline-none text-sm transition"
          />
        </div>

        <div>
          <label class="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
            Parol
          </label>
          <input
            v-model="password"
            type="password"
            required
            placeholder="Parol kiriting..."
            class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-indigo-600 focus:ring-4 focus:ring-indigo-50 outline-none text-sm transition"
          />
        </div>

        <button
          type="submit"
          :disabled="authStore.isLoading"
          class="w-full py-3.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-sm shadow-md shadow-indigo-100 transition flex items-center justify-center gap-2 mt-2"
        >
          <span v-if="authStore.isLoading" class="animate-spin">⏳</span>
          <span>{{ isLoginMode ? "Kirish" : "Ro'yxatdan o'tish" }}</span>
        </button>
      </form>

      <!-- Rejimni almashtirish -->
      <div class="text-center mt-5 pt-4 border-t border-slate-100">
        <button
          @click="isLoginMode = !isLoginMode"
          class="text-xs text-indigo-600 hover:text-indigo-800 font-bold transition"
        >
          {{ isLoginMode ? "Akkountingiz yo'qmi? Ro'yxatdan o'ting" : "Akkountingiz bormi? Tizimga kiring" }}
        </button>
      </div>
    </div>
  </div>
</template>
