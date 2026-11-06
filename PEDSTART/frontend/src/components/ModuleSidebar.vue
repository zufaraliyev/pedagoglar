<script setup>
import { ref, computed } from 'vue'
import { useCourseStore } from '../stores/course'

const courseStore = useCourseStore()

const modules = computed(() => courseStore.modules)
const activeModuleId = computed(() => courseStore.activeModuleId)
const activeLessonId = computed(() => courseStore.activeLessonId)
const activeTaskId = computed(() => courseStore.activeTaskId)
const activeContentType = computed(() => courseStore.activeContentType)
const activeQuizType = computed(() => courseStore.activeQuizType)

// Ochilgan modullarni saqlash (Akkordeon)
const openedModules = ref({})

const toggleModule = (modId) => {
  openedModules.value[modId] = !openedModules.value[modId]
}

const isModuleOpen = (modId) => {
  if (openedModules.value[modId] !== undefined) {
    return openedModules.value[modId]
  }
  // Standart holatda tanlangan modul ochiq bo'ladi
  return activeModuleId.value === modId
}

const getComponentBadge = (comp) => {
  switch (comp) {
    case 'motivatsion':
      return { label: 'Motivatsion', bg: 'bg-rose-50 text-rose-700 border-rose-200' }
    case 'kognitiv':
      return { label: 'Kognitiv', bg: 'bg-blue-50 text-blue-700 border-blue-200' }
    case 'operatsion-faoliyatli':
      return { label: 'Operatsion', bg: 'bg-emerald-50 text-emerald-700 border-emerald-200' }
    case 'refleksiv':
      return { label: 'Refleksiv', bg: 'bg-amber-50 text-amber-700 border-amber-200' }
    default:
      return { label: 'Komponent', bg: 'bg-slate-50 text-slate-700 border-slate-200' }
  }
}
</script>

<template>
  <aside class="w-full lg:w-[320px] xl:w-[350px] lg:shrink-0 bg-white rounded-2xl border border-slate-200/90 shadow-xs p-3.5 space-y-3.5">
    <!-- Sarlovha -->
    <div class="flex items-center justify-between pb-2.5 border-b border-slate-100">
      <h2 class="text-xs font-black text-slate-900 uppercase tracking-wider flex items-center gap-2">
        <span class="text-base">📚</span> O'quv Modullari
      </h2>
      <span class="text-[11px] bg-indigo-50 text-indigo-700 border border-indigo-100 px-2 py-0.5 rounded-full font-bold">
        {{ modules.length }} ta modul
      </span>
    </div>

    <!-- Modullar ro'yxati -->
    <div class="space-y-2.5 max-h-[calc(100vh-230px)] overflow-y-auto pr-1">
      <div
        v-for="mod in modules"
        :key="mod.id"
        class="border rounded-xl transition-all duration-200 overflow-hidden"
        :class="activeModuleId === mod.id ? 'border-indigo-400 ring-2 ring-indigo-50 shadow-xs' : 'border-slate-200 hover:border-slate-300'"
      >
        <!-- Modul Sarlovhasi (Akkordeon toggle) -->
        <div
          class="p-2.5 bg-slate-50/95 cursor-pointer select-none flex flex-col gap-1 hover:bg-slate-100/70 transition"
          @click="toggleModule(mod.id); courseStore.activeModuleId = mod.id"
        >
          <div class="flex items-center justify-between">
            <span
              class="text-[9px] uppercase font-black tracking-wider px-1.5 py-0.5 rounded border"
              :class="getComponentBadge(mod.pedagogical_component).bg"
            >
              {{ getComponentBadge(mod.pedagogical_component).label }}
            </span>
            <div class="flex items-center gap-1.5">
              <span class="text-[10px] font-bold text-amber-700 bg-amber-50 px-1.5 py-0.5 rounded-full border border-amber-200">
                +{{ mod.xp_reward }} XP
              </span>
              <span class="text-slate-400 text-xs font-bold transition-transform" :class="isModuleOpen(mod.id) ? 'rotate-180' : ''">
                ▼
              </span>
            </div>
          </div>
          <h3 class="text-xs font-extrabold text-slate-900 leading-snug">
            {{ mod.title }}
          </h3>
        </div>

        <!-- Modul elementlari (Akkordeon ochilganda) -->
        <div v-show="isModuleOpen(mod.id)" class="p-2 space-y-1 bg-white border-t border-slate-100 text-xs">
          <!-- Har bir dars (Ma'ruza va Amaliyot) -->
          <div v-for="lesson in mod.lessons" :key="lesson.id" class="space-y-1 pb-1">
            <!-- 1. Dars Matni -->
            <button
              @click="courseStore.selectLesson(mod.id, lesson.id)"
              class="w-full text-left px-2 py-1.5 rounded-lg font-medium flex items-center justify-between transition text-xs"
              :class="activeLessonId === lesson.id && activeContentType === 'lesson'
                ? 'bg-indigo-600 text-white font-bold shadow-xs'
                : 'text-slate-700 hover:bg-slate-100/80'"
            >
              <div class="flex items-center gap-1.5 truncate">
                <span class="text-xs">{{ lesson.lesson_type === 'lecture' ? '📖' : '🛠️' }}</span>
                <span class="truncate">{{ lesson.title }}</span>
              </div>
            </button>

            <!-- 2. HAR BIR MA'RUZA VA AMALIYOTDAN SO'NG 10 TA TEST TOPSHIRIG'I -->
            <button
              @click="courseStore.openLessonQuiz(mod.id, lesson.id)"
              class="w-full text-left px-2 py-1.5 rounded-lg flex items-center justify-between transition ml-1.5 border text-[11px]"
              :class="activeLessonId === lesson.id && activeContentType === 'quiz' && activeQuizType === 'lesson'
                ? 'bg-emerald-600 text-white font-black border-emerald-600 shadow-xs'
                : 'bg-emerald-50/70 text-emerald-800 hover:bg-emerald-100 border-emerald-200'"
            >
              <div class="flex items-center gap-1.5 truncate">
                <span>📝</span>
                <span class="truncate font-bold">Test (10 ta savol)</span>
              </div>
              <span
                class="text-[9px] px-1.5 py-0.5 rounded font-black"
                :class="activeLessonId === lesson.id && activeContentType === 'quiz' && activeQuizType === 'lesson' ? 'bg-emerald-800 text-white' : 'bg-emerald-200/70 text-emerald-900'"
              >
                10 test
              </span>
            </button>

            <!-- 3. SI Ochiq topshirig'i (agar mavjud bo'lsa) -->
            <button
              v-if="lesson.tasks?.length"
              @click="courseStore.selectTask(mod.id, lesson.tasks[0].id)"
              class="w-full text-left px-2 py-1.5 rounded-lg flex items-center justify-between transition ml-1.5 border text-[11px]"
              :class="activeTaskId === lesson.tasks[0].id && activeContentType === 'task'
                ? 'bg-purple-600 text-white font-bold border-purple-600 shadow-xs'
                : 'bg-purple-50/60 text-purple-800 hover:bg-purple-100 border-purple-200'"
            >
              <div class="flex items-center gap-1.5 truncate">
                <span>🤖</span>
                <span class="truncate font-semibold">SI Topshirig'i</span>
              </div>
              <span class="text-[9px] font-black text-purple-700 bg-purple-100 px-1 py-0.5 rounded">+50 XP</span>
            </button>
          </div>

          <!-- 4. HAR BIR MODUL YAKUNIDA 25 TA TEST TOPSHIRIG'I -->
          <div class="pt-2 mt-1 border-t border-dashed border-slate-200 space-y-1">
            <button
              @click="courseStore.openModuleQuiz(mod.id)"
              class="w-full text-left px-2.5 py-2 rounded-xl flex items-center justify-between transition border text-xs"
              :class="activeModuleId === mod.id && activeContentType === 'quiz' && activeQuizType === 'module'
                ? 'bg-amber-500 text-amber-950 font-black border-amber-600 shadow-xs'
                : 'bg-amber-50 hover:bg-amber-100 text-amber-950 border-amber-200 font-extrabold'"
            >
              <div class="flex items-center gap-1.5 truncate">
                <span>🏆</span>
                <span class="truncate">Modul Yakuniy Testi</span>
              </div>
              <span class="text-[10px] bg-amber-200 text-amber-900 font-black px-1.5 py-0.5 rounded">
                25 test
              </span>
            </button>

            <!-- Modul Yakuniy SI topshirig'i -->
            <button
              v-if="mod.final_tasks?.length"
              @click="courseStore.selectTask(mod.id, mod.final_tasks[0].id)"
              class="w-full text-left px-2 py-1.5 rounded-lg text-xs flex items-center justify-between transition text-slate-700 hover:bg-slate-100"
              :class="activeTaskId === mod.final_tasks[0].id && activeContentType === 'task' ? 'bg-slate-200 font-bold' : ''"
            >
              <div class="flex items-center gap-1.5 truncate">
                <span>🌟</span>
                <span class="truncate">Modul Yakuniy SI Topshirig'i</span>
              </div>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 5. KURS YAKUNIDA 50 TA TESTLI YAKUNIY TEST TOPSHIRIG'I (ATTESTATSIYA) -->
    <div class="pt-2 border-t border-slate-200">
      <div class="bg-gradient-to-br from-indigo-900 via-indigo-950 to-slate-900 text-white rounded-2xl p-3.5 shadow-sm space-y-2.5">
        <div class="flex items-center justify-between">
          <span class="text-[9px] uppercase font-black tracking-widest text-amber-400">
            KATTA ATTESTATSIYA
          </span>
          <span class="text-[9px] font-black bg-amber-400 text-indigo-950 px-1.5 py-0.5 rounded">
            50 ta test
          </span>
        </div>
        <h4 class="text-xs font-black leading-snug text-white">
          Kurs Yakuniy Attestatsiya Testi
        </h4>
        <p class="text-[10px] text-indigo-200 leading-tight">
          Barcha modullar bo'yicha yakuniy 50 talik davlat attestatsiyasi testi.
        </p>
        <button
          @click="courseStore.openCourseFinalQuiz()"
          class="w-full py-2 rounded-xl bg-gradient-to-r from-amber-400 to-amber-500 hover:from-amber-500 hover:to-amber-600 text-indigo-950 font-black text-xs shadow-xs transition flex items-center justify-center gap-1.5 cursor-pointer"
        >
          <span>🎓</span>
          <span>50 talik Testni Boshlash</span>
        </button>
      </div>
    </div>
  </aside>
</template>
