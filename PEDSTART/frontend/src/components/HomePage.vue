<script setup>
import { computed } from 'vue'
import { useCourseStore } from '../stores/course'
import { useAuthStore } from '../stores/auth'

const courseStore = useCourseStore()
const authStore = useAuthStore()

const emit = defineEmits(['startLearning', 'openAuth', 'openDashboard'])

const modules = computed(() => courseStore.modules)

const handleModuleClick = (moduleId) => {
  if (!authStore.isAuthenticated) {
    emit('openAuth', 'Modul darslariga kirish uchun iltimos, tizimga kiring yoki ro\'yxatdan o\'ting.')
    return
  }
  emit('startLearning', moduleId)
}

const getComponentMeta = (comp) => {
  switch (comp) {
    case 'motivatsion':
      return { 
        name: 'Motivatsion komponent', 
        badge: 'bg-rose-50 text-rose-700 border-rose-200',
        gradient: 'from-rose-500 to-pink-600',
        icon: '❤️',
        desc: "Bo'lajak o'qituvchining kasbga sadoqati, bolalarga mehr va darsda bilish motivatsiyasini shakllantirish."
      }
    case 'kognitiv':
      return { 
        name: 'Kognitiv komponent', 
        badge: 'bg-blue-50 text-blue-700 border-blue-200',
        gradient: 'from-blue-500 to-indigo-600',
        icon: '🧠',
        desc: "Pedagogika, didaktika, ta'lim prinsiplari va fanlararo integratsiyaning ilmiy-nazariy asoslarini bilish."
      }
    case 'operatsion-faoliyatli':
      return { 
        name: 'Operatsion-faoliyatli', 
        badge: 'bg-emerald-50 text-emerald-700 border-emerald-200',
        gradient: 'from-emerald-500 to-teal-600',
        icon: '🛠️',
        desc: "Zamonaviy interfaol metodlar, loyihalash texnologiyalari va raqamli vositalarni darsda qo'llash ko'nikmasi."
      }
    case 'refleksiv':
      return { 
        name: 'Refleksiv komponent', 
        badge: 'bg-amber-50 text-amber-700 border-amber-200',
        gradient: 'from-amber-500 to-orange-600',
        icon: '🪞',
        desc: "O'z pedagogik faoliyatini xolisona baholash, xatolarni tahlil qilish va kreativ kasbiy rivojlanish."
      }
    default:
      return { 
        name: 'Pedagogik komponent', 
        badge: 'bg-indigo-50 text-indigo-700 border-indigo-200',
        gradient: 'from-indigo-500 to-purple-600',
        icon: '✨',
        desc: "Pedagogik kompetensiyani tizimli shakllantirish."
      }
  }
}
</script>

<template>
  <div class="space-y-12 pb-12 animate-fadeIn">
    <!-- 1. HERO BANNER -->
    <section class="relative overflow-hidden rounded-3xl bg-gradient-to-br from-indigo-950 via-indigo-900 to-slate-950 text-white p-8 sm:p-12 lg:p-16 shadow-xl border border-indigo-800/40">
      <!-- Orqa fon nurlari -->
      <div class="absolute -top-24 -right-24 w-96 h-96 bg-indigo-500/20 rounded-full blur-3xl pointer-events-none"></div>
      <div class="absolute -bottom-24 -left-24 w-96 h-96 bg-amber-500/10 rounded-full blur-3xl pointer-events-none"></div>

      <div class="relative max-w-4xl space-y-6">
        <div class="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-indigo-500/20 border border-indigo-400/30 text-amber-300 text-xs font-black tracking-wider uppercase backdrop-blur-xs">
          <span>🎓</span> "PEDSTART" RAQAMLI EKOTIZIMI
        </div>

        <h1 class="text-3xl sm:text-5xl lg:text-6xl font-black tracking-tight text-white leading-tight">
          Bo'lajak pedagoglar uchun <br />
          <span class="bg-gradient-to-r from-amber-300 via-amber-200 to-indigo-200 bg-clip-text text-transparent">
            muvaffaqiyatli start
          </span> va raqamli tayyorgarlik makoni
        </h1>

        <p class="text-base sm:text-lg text-indigo-200/90 leading-relaxed max-w-3xl font-normal">
          Bo'lajak boshlang'ich sinf o'qituvchilarining pedagogik tayyorgarligini oshirish, nazariy va amaliy bilimlarini raqamli muhitda uzluksiz rivojlantirish hamda bilimlarni Sun'iy Intellekt (AI) yordamida baholovchi zamonaviy ekotizim.
        </p>

        <!-- Ilmiy-metodik asos yorlig'i -->
        <div class="p-4 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-xs max-w-2xl flex items-start gap-3">
          <span class="text-2xl flex-shrink-0">📜</span>
          <div class="text-xs sm:text-sm text-slate-300 leading-normal">
            <strong class="text-amber-300 font-bold">Ilmiy-metodik asos:</strong>
            M.B. Muxamadaliyeva konsepsiyasidagi 4 ta pedagogik tayyorgarlik komponenti:
            <span class="text-white font-semibold">Motivatsion, Kognitiv, Operatsion-faoliyatli va Refleksiv.</span>
          </div>
        </div>

        <!-- Tugmalar -->
        <div class="flex flex-wrap items-center gap-4 pt-4">
          <button
            v-if="!authStore.isAuthenticated"
            @click="emit('openAuth')"
            class="px-8 py-4 rounded-2xl bg-gradient-to-r from-amber-400 to-amber-500 hover:from-amber-500 hover:to-amber-600 text-indigo-950 font-black text-sm sm:text-base shadow-lg shadow-amber-500/25 transition-all transform hover:-translate-y-0.5 cursor-pointer flex items-center gap-2"
          >
            <span>🚀</span>
            <span>Tizimga Kirish / Ro'yxatdan O'tish</span>
          </button>

          <button
            v-else
            @click="emit('startLearning')"
            class="px-8 py-4 rounded-2xl bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-600 hover:to-teal-600 text-white font-black text-sm sm:text-base shadow-lg shadow-emerald-500/25 transition-all transform hover:-translate-y-0.5 cursor-pointer flex items-center gap-2"
          >
            <span>📚</span>
            <span>Darslarni Boshlash (O'quv Maydoni)</span>
          </button>

          <button
            v-if="authStore.isAuthenticated"
            @click="emit('openDashboard')"
            class="px-6 py-4 rounded-2xl bg-white/10 hover:bg-white/15 text-white font-bold text-sm sm:text-base border border-white/20 transition-all cursor-pointer flex items-center gap-2"
          >
            <span>📊</span>
            <span>Mening Shaxsiy Kabinetim</span>
          </button>
        </div>
      </div>
    </section>

    <!-- 2. STATISTIK MA'LUMOTLAR -->
    <section class="grid grid-cols-2 md:grid-cols-4 gap-4 sm:gap-6">
      <div class="bg-white rounded-3xl p-6 border border-slate-200/90 shadow-xs text-center space-y-2">
        <div class="w-12 h-12 rounded-2xl bg-indigo-50 text-indigo-600 flex items-center justify-center text-2xl mx-auto font-black">
          📚
        </div>
        <div class="text-3xl sm:text-4xl font-black text-slate-900">4 ta</div>
        <div class="text-xs sm:text-sm font-bold text-slate-500 uppercase tracking-wider">Asosiy O'quv Moduli</div>
      </div>

      <div class="bg-white rounded-3xl p-6 border border-slate-200/90 shadow-xs text-center space-y-2">
        <div class="w-12 h-12 rounded-2xl bg-emerald-50 text-emerald-600 flex items-center justify-center text-2xl mx-auto font-black">
          📖
        </div>
        <div class="text-3xl sm:text-4xl font-black text-slate-900">30 ta</div>
        <div class="text-xs sm:text-sm font-bold text-slate-500 uppercase tracking-wider">15 Ma'ruza + 15 Amaliyot</div>
      </div>

      <div class="bg-white rounded-3xl p-6 border border-slate-200/90 shadow-xs text-center space-y-2">
        <div class="w-12 h-12 rounded-2xl bg-amber-50 text-amber-600 flex items-center justify-center text-2xl mx-auto font-black">
          📝
        </div>
        <div class="text-3xl sm:text-4xl font-black text-slate-900">450 ta</div>
        <div class="text-xs sm:text-sm font-bold text-slate-500 uppercase tracking-wider">Avtomatlashtirilgan Test</div>
      </div>

      <div class="bg-white rounded-3xl p-6 border border-slate-200/90 shadow-xs text-center space-y-2">
        <div class="w-12 h-12 rounded-2xl bg-purple-50 text-purple-600 flex items-center justify-center text-2xl mx-auto font-black">
          🤖
        </div>
        <div class="text-3xl sm:text-4xl font-black text-slate-900">AI-Ekspert</div>
        <div class="text-xs sm:text-sm font-bold text-slate-500 uppercase tracking-wider">Ochiq Keyslar Baholashi</div>
      </div>
    </section>

    <!-- 3. M.B. MUXAMADALIYEVA 4 TA KOMPONENTI -->
    <section class="space-y-6">
      <div class="text-center max-w-3xl mx-auto space-y-2">
        <span class="text-xs font-black text-indigo-600 uppercase tracking-widest bg-indigo-50 border border-indigo-200 px-3 py-1 rounded-full">
          METODIK MEZONLAR
        </span>
        <h2 class="text-2xl sm:text-3xl font-black text-slate-900">
          Pedagogik Tayyorgarlikning 4 Asosiy Komponenti
        </h2>
        <p class="text-xs sm:text-sm text-slate-500">
          Platformadagi har bir modul, ma'ruza, amaliyot va SI topshirig'i ushbu 4 komponentni o'zaro integratsiyalashgan holda rivojlantirishga xizmat qiladi.
        </p>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <div
          v-for="compKey in ['motivatsion', 'kognitiv', 'operatsion-faoliyatli', 'refleksiv']"
          :key="compKey"
          class="bg-white rounded-3xl p-6 border border-slate-200/90 shadow-xs hover:shadow-md transition-all space-y-3 flex flex-col"
        >
          <div class="w-12 h-12 rounded-2xl flex items-center justify-center text-2xl bg-gradient-to-tr text-white shadow-xs" :class="getComponentMeta(compKey).gradient">
            {{ getComponentMeta(compKey).icon }}
          </div>
          <h3 class="text-base font-extrabold text-slate-900">
            {{ getComponentMeta(compKey).name }}
          </h3>
          <p class="text-xs text-slate-600 leading-relaxed flex-1">
            {{ getComponentMeta(compKey).desc }}
          </p>
          <div class="pt-2 border-t border-slate-100 flex items-center justify-between text-[11px] font-bold text-slate-500">
            <span>Amaliy ko'rsatkich</span>
            <span class="text-indigo-600 font-extrabold">0 — 100%</span>
          </div>
        </div>
      </div>
    </section>

    <!-- 4. MODULLAR RO'YXATI VA KIRISH (AVTORIZATSIYA TALAB QILINADI) -->
    <section class="space-y-6">
      <div class="flex flex-col sm:flex-row sm:items-end justify-between gap-3">
        <div>
          <span class="text-xs font-black text-indigo-600 uppercase tracking-widest bg-indigo-50 border border-indigo-200 px-3 py-1 rounded-full">
            O'QUV DASTURI
          </span>
          <h2 class="text-2xl sm:text-3xl font-black text-slate-900 mt-2">
            Kurs Modullari
          </h2>
          <p class="text-xs sm:text-sm text-slate-500 mt-1">
            Modullarga kirish va darslarni o'zlashtirish uchun avtorizatsiyadan o'tgan bo'lishingiz lozim.
          </p>
        </div>

        <div v-if="!authStore.isAuthenticated" class="text-xs font-bold text-amber-700 bg-amber-50 border border-amber-200 px-3 py-1.5 rounded-xl flex items-center gap-1.5">
          <span>🔒</span> Modullarga kirish uchun tizimga kiring
        </div>
      </div>

      <!-- Modullar kartalari -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div
          v-for="mod in modules"
          :key="mod.id"
          @click="handleModuleClick(mod.id)"
          class="bg-white rounded-3xl p-6 sm:p-7 border border-slate-200/90 shadow-xs hover:border-indigo-400 hover:shadow-lg transition-all cursor-pointer group flex flex-col justify-between"
        >
          <div class="space-y-4">
            <div class="flex items-center justify-between">
              <span
                class="text-[10px] uppercase font-black tracking-wider px-2.5 py-1 rounded-md border"
                :class="getComponentMeta(mod.pedagogical_component).badge"
              >
                {{ getComponentMeta(mod.pedagogical_component).name }}
              </span>

              <div class="flex items-center gap-2">
                <span class="text-xs font-black text-amber-800 bg-amber-50 border border-amber-200 px-2.5 py-1 rounded-full">
                  +{{ mod.xp_reward }} XP
                </span>
                <span v-if="!authStore.isAuthenticated" class="text-slate-400 group-hover:text-amber-500 transition-colors" title="Avtorizatsiya talab etiladi">
                  🔒
                </span>
              </div>
            </div>

            <h3 class="text-lg sm:text-xl font-black text-slate-900 group-hover:text-indigo-600 transition-colors leading-snug">
              {{ mod.title }}
            </h3>

            <p class="text-xs sm:text-sm text-slate-600 leading-relaxed">
              {{ mod.description }}
            </p>

            <!-- Darslar soni va xususiyatlar -->
            <div class="grid grid-cols-3 gap-2 pt-2 text-center">
              <div class="p-2 rounded-xl bg-slate-50 border border-slate-100">
                <div class="text-xs font-bold text-slate-400">Darslar</div>
                <div class="text-sm font-black text-slate-800">{{ mod.lessons?.length || 0 }} ta</div>
              </div>
              <div class="p-2 rounded-xl bg-emerald-50/60 border border-emerald-100">
                <div class="text-xs font-bold text-emerald-600">Dars Testi</div>
                <div class="text-sm font-black text-emerald-800">10 talik</div>
              </div>
              <div class="p-2 rounded-xl bg-amber-50/60 border border-amber-100">
                <div class="text-xs font-bold text-amber-600">Modul Testi</div>
                <div class="text-sm font-black text-amber-800">25 talik</div>
              </div>
            </div>
          </div>

          <!-- Pastki harakat tugmasi -->
          <div class="pt-5 mt-4 border-t border-slate-100 flex items-center justify-between">
            <span class="text-xs font-bold text-slate-500 group-hover:text-indigo-600 transition">
              {{ authStore.isAuthenticated ? "Modul darslarini ochish →" : "Kirish va o'rganishni boshlash 🔒" }}
            </span>
            <div class="w-9 h-9 rounded-xl bg-slate-100 group-hover:bg-indigo-600 group-hover:text-white text-slate-700 flex items-center justify-center font-black transition-all">
              →
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 5. 3 BOSQICHLI TEST VA BAHOLASH TIZIMI -->
    <section class="bg-gradient-to-br from-slate-900 to-indigo-950 text-white rounded-3xl p-8 sm:p-12 shadow-xl space-y-6">
      <div class="max-w-2xl space-y-2">
        <span class="text-xs font-black text-amber-400 uppercase tracking-widest">
          STANDARTLASHTIRILGAN TEST TIZIMI
        </span>
        <h2 class="text-2xl sm:text-3xl font-black text-white">
          Bilimlarni Nazorat Qilish va Attestatsiya
        </h2>
        <p class="text-xs sm:text-sm text-indigo-200">
          Platformada talabalar bilimi 3 bosqichli qat'iy mezonlar asosida sinovdan o'tkaziladi:
        </p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 pt-2">
        <!-- 10 talik -->
        <div class="p-6 rounded-2xl bg-white/5 border border-white/10 space-y-2">
          <div class="w-10 h-10 rounded-xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-black text-lg">
            10
          </div>
          <h4 class="text-base font-bold text-white">Har bir dars so'ngida</h4>
          <p class="text-xs text-slate-300 leading-relaxed">
            Har bir ma'ruza va amaliy mashg'ulotdan keyin <strong>10 ta test</strong> savoli. Natijalar darhol tahlil qilinadi va to'g'ri javoblar ko'rsatiladi.
          </p>
        </div>

        <!-- 25 talik -->
        <div class="p-6 rounded-2xl bg-white/5 border border-white/10 space-y-2">
          <div class="w-10 h-10 rounded-xl bg-amber-500/20 text-amber-400 flex items-center justify-center font-black text-lg">
            25
          </div>
          <h4 class="text-base font-bold text-white">Har bir modul yakunida</h4>
          <p class="text-xs text-slate-300 leading-relaxed">
            Modul bo'yicha umumlashtiruvchi <strong>25 ta test</strong> savoli. Modul materiallarini to'liq qamrab oladi va XP ball beradi.
          </p>
        </div>

        <!-- 50 talik -->
        <div class="p-6 rounded-2xl bg-white/5 border border-white/10 space-y-2">
          <div class="w-10 h-10 rounded-xl bg-purple-500/20 text-purple-400 flex items-center justify-center font-black text-lg">
            50
          </div>
          <h4 class="text-base font-bold text-white">Kurs Yakuniy Attestatsiyasi</h4>
          <p class="text-xs text-slate-300 leading-relaxed">
            Barcha 4 ta modul bo'yicha <strong>50 ta test</strong>dan iborat katta yakuniy davlat attestatsiyasi testi (+100 XP va oliy nishon).
          </p>
        </div>
      </div>
    </section>
  </div>
</template>
