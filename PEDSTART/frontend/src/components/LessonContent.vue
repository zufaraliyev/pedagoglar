<script setup>
import { computed } from 'vue'
import { useCourseStore } from '../stores/course'

const courseStore = useCourseStore()
const lesson = computed(() => courseStore.activeLesson)
const activeModule = computed(() => courseStore.activeModule)

const goToQuiz = () => {
  if (lesson.value && activeModule.value) {
    courseStore.openLessonQuiz(activeModule.value.id, lesson.value.id)
  }
}

const goToTask = () => {
  if (lesson.value?.tasks?.length && activeModule.value) {
    courseStore.selectTask(activeModule.value.id, lesson.value.tasks[0].id)
  }
}

// YouTube video embed URL hosil qilish
const embedVideoUrl = computed(() => {
  if (!lesson.value?.video_url) return null
  const url = lesson.value.video_url
  let videoId = ''
  
  if (url.includes('vld=') && url.includes('vid:')) {
    const match = url.match(/vid:([a-zA-Z0-9_-]+)/)
    if (match) videoId = match[1]
  } else if (url.includes('youtube.com/watch?v=')) {
    const match = url.match(/v=([a-zA-Z0-9_-]+)/)
    if (match) videoId = match[1]
  } else if (url.includes('youtu.be/')) {
    const match = url.match(/youtu\.be\/([a-zA-Z0-9_-]+)/)
    if (match) videoId = match[1]
  } else if (!url.includes('http')) {
    videoId = url.trim()
  }

  return videoId ? `https://www.youtube.com/embed/${videoId}?rel=0` : null
})

// Pedagogik komponent nomiga qarab badge stili
const getComponentMeta = (comp) => {
  switch (comp) {
    case 'motivatsion':
      return { title: 'Motivatsion komponent', desc: "O'quvchilarda bilishga qiziqish va ichki rag'batni uyg'otish", color: 'from-rose-500 to-pink-600', text: 'text-rose-700', bg: 'bg-rose-50' }
    case 'kognitiv':
      return { title: 'Kognitiv komponent', desc: "Nazariy-metodologik bilimlar va ilmiy tushunchalar tizimi", color: 'from-blue-500 to-indigo-600', text: 'text-blue-700', bg: 'bg-blue-50' }
    case 'operatsion-faoliyatli':
      return { title: 'Operatsion-faoliyatli', desc: "Amaliy pedagogik ko'nikmalar, interfaol metodlar va dars ishlanmasi", color: 'from-emerald-500 to-teal-600', text: 'text-emerald-700', bg: 'bg-emerald-50' }
    case 'refleksiv':
      return { title: 'Refleksiv komponent', desc: "O'z-o'zini tahlil qilish, pedagogik tahlil va kasbiy o'sish", color: 'from-amber-500 to-orange-600', text: 'text-amber-700', bg: 'bg-amber-50' }
    default:
      return { title: 'Pedagogik komponent', desc: "Kompetensiyani shakllantirish", color: 'from-indigo-500 to-purple-600', text: 'text-indigo-700', bg: 'bg-indigo-50' }
  }
}
</script>

<template>
  <div v-if="lesson" class="space-y-6">
    <!-- 1. Dars Sarlovhasi va Meta Paneli -->
    <div class="bg-white rounded-3xl p-6 sm:p-7 border border-slate-200/90 shadow-xs space-y-4">
      <div class="flex flex-wrap items-center justify-between gap-3">
        <div class="flex items-center gap-2">
          <span
            class="px-3 py-1 rounded-full text-xs font-black uppercase tracking-wider border"
            :class="lesson.lesson_type === 'lecture' ? 'bg-indigo-50 text-indigo-700 border-indigo-200' : 'bg-emerald-50 text-emerald-800 border-emerald-200'"
          >
            {{ lesson.lesson_type === 'lecture' ? '📖 Ma\'ruza Mashg\'uloti' : '🛠️ Amaliy Mashg\'ulot' }}
          </span>
          <span class="text-xs text-slate-400 font-semibold">•</span>
          <span class="text-xs font-bold text-slate-500">
            {{ activeModule?.title }}
          </span>
        </div>

        <div class="flex items-center gap-2 sm:gap-3 text-xs">
          <span class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl font-bold bg-slate-100 text-slate-700">
            <span>⏱️</span> {{ lesson.reading_time_minutes }} daqiqa
          </span>
          <span class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl font-black bg-amber-50 text-amber-800 border border-amber-200">
            <span>✨</span> +{{ lesson.xp_reward }} XP
          </span>
        </div>
      </div>

      <h1 class="text-xl sm:text-2xl lg:text-3xl font-black text-slate-900 leading-tight">
        {{ lesson.title }}
      </h1>
    </div>

    <!-- 2. Video Darslik Pleyeri (Agar video mavjud bo'lsa) -->
    <div v-if="embedVideoUrl" class="bg-white rounded-3xl p-5 sm:p-6 border border-slate-200 shadow-xs space-y-3">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <div class="w-8 h-8 rounded-xl bg-rose-50 text-rose-600 flex items-center justify-center font-bold text-base">
            ▶️
          </div>
          <div>
            <h3 class="text-sm font-extrabold text-slate-900">Mavzuning Video Darsligi</h3>
            <p class="text-[11px] text-slate-500">Mavzuni mustahkamlash uchun videoni diqqat bilan tomosha qiling</p>
          </div>
        </div>
        <span class="px-2.5 py-1 rounded-md bg-rose-100/70 text-rose-800 font-bold text-[11px]">
          YouTube HD
        </span>
      </div>

      <div class="relative w-full aspect-video rounded-2xl overflow-hidden bg-slate-950 shadow-md">
        <iframe
          :src="embedVideoUrl"
          title="PedStart Video Darsi"
          class="w-full h-full border-0"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
          allowfullscreen
        ></iframe>
      </div>
    </div>

    <!-- 3. Metodik Infografika: 4 ta Pedagogik Tayyorgarlik Komponenti -->
    <div class="bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-900 text-white rounded-3xl p-5 sm:p-7 shadow-md space-y-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2.5">
          <span class="text-2xl">💡</span>
          <div>
            <h4 class="text-sm sm:text-base font-black text-white">
              M.B. Muxamadaliyeva: Pedagogik Tayyorgarlikning 4 Komponenti
            </h4>
            <p class="text-xs text-indigo-200">
              Ushbu mavzuda rivojlantiriladigan kasbiy kompetensiyalar tizimi
            </p>
          </div>
        </div>
        <span class="hidden sm:inline-block px-3 py-1 rounded-full text-[11px] font-black bg-amber-400 text-indigo-950 uppercase">
          Ekotizim
        </span>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 pt-1">
        <!-- 1. Motivatsion -->
        <div class="p-3.5 rounded-2xl bg-white/5 border border-white/10 hover:border-rose-400/50 transition">
          <div class="w-7 h-7 rounded-lg bg-rose-500/20 text-rose-300 flex items-center justify-center font-bold text-xs mb-2">
            ❤️
          </div>
          <div class="text-xs font-black text-rose-300">1. Motivatsion</div>
          <p class="text-[11px] text-slate-300 mt-1 leading-snug">
            O'qituvchining kasbiy xohishi, bolalarga mehr va ta'limiy qiziqish uyg'otish.
          </p>
        </div>

        <!-- 2. Kognitiv -->
        <div class="p-3.5 rounded-2xl bg-white/5 border border-white/10 hover:border-blue-400/50 transition">
          <div class="w-7 h-7 rounded-lg bg-blue-500/20 text-blue-300 flex items-center justify-center font-bold text-xs mb-2">
            🧠
          </div>
          <div class="text-xs font-black text-blue-300">2. Kognitiv</div>
          <p class="text-[11px] text-slate-300 mt-1 leading-snug">
            Pedagogika, didaktika va integratsiya qonuniyatlarini chuqur ilmiy bilish.
          </p>
        </div>

        <!-- 3. Operatsion-faoliyatli -->
        <div class="p-3.5 rounded-2xl bg-white/5 border border-white/10 hover:border-emerald-400/50 transition">
          <div class="w-7 h-7 rounded-lg bg-emerald-500/20 text-emerald-300 flex items-center justify-center font-bold text-xs mb-2">
            🛠️
          </div>
          <div class="text-xs font-black text-emerald-300">3. Operatsion</div>
          <p class="text-[11px] text-slate-300 mt-1 leading-snug">
            Interfaol metodlar, keyslar va dars ishlanmasini amaliyotda qo'llay olish.
          </p>
        </div>

        <!-- 4. Refleksiv -->
        <div class="p-3.5 rounded-2xl bg-white/5 border border-white/10 hover:border-amber-400/50 transition">
          <div class="w-7 h-7 rounded-lg bg-amber-500/20 text-amber-300 flex items-center justify-center font-bold text-xs mb-2">
            🪞
          </div>
          <div class="text-xs font-black text-amber-300">4. Refleksiv</div>
          <p class="text-[11px] text-slate-300 mt-1 leading-snug">
            O'z faoliyatini xolisona baholash, xatolarni to'g'rilash va kreativ izlanish.
          </p>
        </div>
      </div>
    </div>

    <!-- 4. Dars Matni (Boyitilgan, formatlangan maqola) -->
    <article class="bg-white rounded-3xl p-6 sm:p-9 border border-slate-200/90 shadow-xs space-y-6">
      <div class="flex items-center justify-between pb-4 border-b border-slate-100">
        <h3 class="text-base font-extrabold text-slate-900 flex items-center gap-2">
          <span>📑</span> Darsning Nazariy-Metodik Mazmuni
        </h3>
        <span class="text-xs text-slate-400 font-semibold">PedStart Ilmiy Kutubxonasi</span>
      </div>

      <div class="text-slate-700 leading-relaxed space-y-4 font-normal text-sm sm:text-base whitespace-pre-line">
        {{ lesson.content }}
      </div>

      <!-- Xulosa qutisi (Infografik xulosa) -->
      <div class="p-5 rounded-2xl bg-indigo-50/60 border border-indigo-200 flex items-start gap-3.5 mt-6">
        <span class="text-2xl flex-shrink-0">📌</span>
        <div>
          <h4 class="text-xs sm:text-sm font-black text-indigo-950 uppercase tracking-wide">
            Bo'lajak pedagog uchun amaliy tavsiya:
          </h4>
          <p class="text-xs sm:text-sm text-indigo-900 mt-1 leading-normal">
            Har bir darsni o'rgangach, darhol mavzu yuzasidan <strong>10 talik test topshirig'ini</strong> bajaring va Sun'iy Intellekt baholovchi ochiq keys savoliga o'z fikringizni yozib jo'nating. Bu sizning 4 ta komponent bo'yicha amaliy kompetensiyangizni mustahkamlaydi!
          </p>
        </div>
      </div>
    </article>

    <!-- 5. Keyingi Qadamlar: 10 talik Test Topshirig'i va SI Topshirig'i -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
      <!-- 10 talik Test Topshirig'i tugmasi -->
      <div
        @click="goToQuiz"
        class="p-6 rounded-3xl bg-gradient-to-br from-emerald-50 via-teal-50/60 to-emerald-100/50 border border-emerald-200 hover:border-emerald-400 hover:shadow-md cursor-pointer transition-all flex items-center justify-between group"
      >
        <div class="space-y-1">
          <span class="inline-block px-2.5 py-0.5 rounded-md bg-emerald-600 text-white text-[10px] font-black uppercase tracking-wider">
            1-QADAM: BILIMLARNI TEKSHIRISH
          </span>
          <h4 class="text-base sm:text-lg font-black text-slate-900 group-hover:text-emerald-800 transition">
            Dars yuzasidan Test Topshirig'i
          </h4>
          <p class="text-xs text-slate-600 leading-snug">
            Mavzuni to'liq o'zlashtirish uchun <strong>10 ta test</strong> savoli (+50 XP gacha)
          </p>
        </div>
        <div class="w-13 h-13 rounded-2xl bg-emerald-600 text-white flex items-center justify-center font-black text-2xl group-hover:scale-110 transition-transform shadow-xs flex-shrink-0 ml-3">
          📝
        </div>
      </div>

      <!-- SI ochiq topshirig'i -->
      <div
        v-if="lesson.tasks?.length"
        @click="goToTask"
        class="p-6 rounded-3xl bg-gradient-to-br from-indigo-50 via-purple-50/60 to-indigo-100/50 border border-indigo-200 hover:border-indigo-400 hover:shadow-md cursor-pointer transition-all flex items-center justify-between group"
      >
        <div class="space-y-1">
          <span class="inline-block px-2.5 py-0.5 rounded-md bg-purple-600 text-white text-[10px] font-black uppercase tracking-wider">
            2-QADAM: PEDAGOGIK KEYS VA AMALIYOT
          </span>
          <h4 class="text-base sm:text-lg font-black text-slate-900 group-hover:text-indigo-800 transition">
            Sun'iy Intellekt Tahlil Topshirig'i
          </h4>
          <p class="text-xs text-slate-600 leading-snug">
            M.B. Muxamadaliyeva 4 komponenti bo'yicha AI ekspertizasi (+50 XP)
          </p>
        </div>
        <div class="w-13 h-13 rounded-2xl bg-indigo-600 text-white flex items-center justify-center font-black text-2xl group-hover:scale-110 transition-transform shadow-xs flex-shrink-0 ml-3">
          🤖
        </div>
      </div>
    </div>
  </div>
</template>