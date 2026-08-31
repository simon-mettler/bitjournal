<script setup lang="ts">
import {
  CalendarCell,
  CalendarCellTrigger,
  CalendarGrid,
  CalendarGridBody,
  CalendarGridHead,
  CalendarGridRow,
  CalendarHeadCell,
  CalendarHeader,
  CalendarHeading,
  CalendarNext,
  CalendarPrev,
  CalendarRoot,
  MonthPickerCell,
  MonthPickerCellTrigger,
  MonthPickerGrid,
  MonthPickerGridBody,
  MonthPickerGridRow,
  MonthPickerHeader,
  MonthPickerHeading,
  MonthPickerNext,
  MonthPickerPrev,
  MonthPickerRoot,
  YearPickerCell,
  YearPickerCellTrigger,
  YearPickerGrid,
  YearPickerGridBody,
  YearPickerGridRow,
  YearPickerHeader,
  YearPickerHeading,
  YearPickerNext,
  YearPickerPrev,
  YearPickerRoot,
} from 'reka-ui'
import { computed, ref, type Ref, watch } from 'vue'
import { ArrowLeft, ArrowRight, CalendarDays } from '@lucide/vue'
import Drawer from '@/shared/ui/components/Drawer.vue'
import IconButton from '@/shared/ui/components/IconButton.vue'
import { getLocalTimeZone, today, type DateValue } from '@internationalized/date'

type View = 'day' | 'month' | 'year'

// see https://github.com/unovue/reka-ui/issues/1641
const selectedDate = defineModel<DateValue>({ default: () => today(getLocalTimeZone()) }) as Ref<DateValue>
const placeholder = ref<DateValue>(selectedDate.value) as Ref<DateValue>

const drawerOpen = ref(false)
const view = ref<View>('day')

function openMonthView() {
  view.value = 'month'
}

function openYearView() {
  view.value = 'year'
}

function onMonthSelect(month: DateValue | DateValue[] | undefined) {
  if (!month || Array.isArray(month)) return

  placeholder.value = month
  view.value = 'day'
}

function onYearSelect(year: DateValue | DateValue[] | undefined) {
  if (!year || Array.isArray(year)) return

  placeholder.value = year
  view.value = 'month'
}

watch(selectedDate, (value) => {
  placeholder.value = value
})

function openDrawer() {
  placeholder.value = selectedDate.value
  view.value = 'day'
  drawerOpen.value = true
}

function selectDate(date: DateValue | DateValue[] | undefined) {
  if (!date || Array.isArray(date)) return

  selectedDate.value = date
  drawerOpen.value = false
}

const monthLabels = [
  'JAN',
  'FEB',
  'MAR',
  'APR',
  'MAY',
  'JUN',
  'JUL',
  'AUG',
  'SEP',
  'OCT',
  'NOV',
  'DEC',
]

const monthLabel = computed(
  () => monthLabels[placeholder.value.month - 1],
)

const yearLabel = computed(() => String(placeholder.value.year))

</script>

<template>
  <IconButton variant="secondary" @click="openDrawer">
    <CalendarDays />
  </IconButton>

  <Drawer v-model:open="drawerOpen" title="Select date">
    <div ref="containerRef" class="dp-container">

      <!-- Day View -->
      <CalendarRoot v-if="view === 'day'" v-slot="{ weekDays, grid }" v-model="selectedDate"
        v-model:placeholder="placeholder" class="dp-root" fixed-weeks>
        <CalendarHeader class="dp-header">
          <CalendarPrev class="dp-nav-button">
            <ArrowLeft />
          </CalendarPrev>

          <CalendarHeading class="dp-heading-group">
            <button type="button" class="dp-month-button dp-heading-inactive" aria-label="Select month view"
              @click="openMonthView">
              {{ monthLabel }}
            </button>

            <button type="button" class="dp-year-button dp-heading-inactive" aria-label="Select year view"
              @click="openYearView">
              {{ yearLabel }}
            </button>
          </CalendarHeading>

          <CalendarNext class="dp-nav-button">
            <ArrowRight />
          </CalendarNext>
        </CalendarHeader>

        <CalendarGrid v-for="month in grid" :key="month.value.toString()" class="dp-calendar-grid">
          <CalendarGridHead>
            <CalendarGridRow class="dp-grid-row dp-grid-row-head">
              <CalendarHeadCell v-for="day in weekDays" :key="day" class="dp-head-cell">
                {{ day }}
              </CalendarHeadCell>
            </CalendarGridRow>
          </CalendarGridHead>

          <CalendarGridBody class="dp-grid-body">
            <CalendarGridRow v-for="(weekDates, index) in month.rows" :key="`weekDate-${index}`" class="dp-grid-row">
              <CalendarCell v-for="weekDate in weekDates" :key="weekDate.toString()" :date="weekDate" class="dp-cell">
                <CalendarCellTrigger :day="weekDate" :month="month.value" class="dp-cell-trigger dp-day-trigger"
                  @click="selectDate(weekDate)" />
              </CalendarCell>
            </CalendarGridRow>
          </CalendarGridBody>
        </CalendarGrid>
      </CalendarRoot>

      <!-- Month View -->
      <MonthPickerRoot v-else-if="view === 'month'" v-slot="{ grid }" v-model:placeholder="placeholder" class="dp-root"
        @update:model-value="onMonthSelect">
        <MonthPickerHeader class="dp-header">
          <MonthPickerPrev class="dp-nav-button">
            <ArrowLeft />
          </MonthPickerPrev>

          <MonthPickerHeading class="dp-heading-group">
            <button type="button" class="dp-month-button" :class="{ 'dp-heading-inactive': view !== 'month' }"
              :aria-pressed="view === 'month'" aria-label="Select month view" @click="openMonthView">
              {{ monthLabel }}
            </button>

            <button type="button" class="dp-year-button dp-heading-inactive" aria-label="Select year view"
              @click="openYearView">
              {{ yearLabel }}
            </button>
          </MonthPickerHeading>

          <MonthPickerNext class="dp-nav-button">
            <ArrowRight />
          </MonthPickerNext>
        </MonthPickerHeader>

        <MonthPickerGrid class="dp-picker-grid">
          <MonthPickerGridBody>
            <MonthPickerGridRow v-for="(monthRow, rowIndex) in grid.rows" :key="`monthRow-${rowIndex}`"
              class="dp-picker-row">
              <MonthPickerCell v-for="month in monthRow" :key="month.toString()" :date="month">
                <MonthPickerCellTrigger :month="month" class="dp-cell-trigger dp-picker-trigger" />
              </MonthPickerCell>
            </MonthPickerGridRow>
          </MonthPickerGridBody>
        </MonthPickerGrid>
      </MonthPickerRoot>

      <!-- Year View -->
      <YearPickerRoot v-else v-slot="{ grid }" v-model:placeholder="placeholder" class="dp-root"
        @update:model-value="onYearSelect">
        <YearPickerHeader class="dp-header">
          <YearPickerPrev class="dp-nav-button">
            <ArrowLeft />
          </YearPickerPrev>

          <YearPickerHeading class="dp-heading-group">
            <button type="button" class="dp-month-button dp-heading-inactive" aria-label="Select month view"
              @click="openMonthView">
              {{ monthLabel }}
            </button>

            <button type="button" class="dp-year-button" :class="{ 'dp-heading-inactive': view !== 'year' }"
              :aria-pressed="view === 'year'" aria-label="Select year view" @click="openYearView">
              {{ yearLabel }}
            </button>
          </YearPickerHeading>

          <YearPickerNext class="dp-nav-button">
            <ArrowRight />
          </YearPickerNext>
        </YearPickerHeader>

        <YearPickerGrid class="dp-picker-grid">
          <YearPickerGridBody>
            <YearPickerGridRow v-for="(yearRow, rowIndex) in grid.rows" :key="`yearRow-${rowIndex}`"
              class="dp-picker-row">
              <YearPickerCell v-for="year in yearRow" :key="year.toString()" :date="year">
                <YearPickerCellTrigger :year="year" class="dp-cell-trigger dp-picker-trigger" />
              </YearPickerCell>
            </YearPickerGridRow>
          </YearPickerGridBody>
        </YearPickerGrid>
      </YearPickerRoot>
    </div>

  </Drawer>
</template>

<style scoped>
.dp-container {
  width: 100%;
  background-color: var(--color-surface);
}

.dp-root {
  display: flex;
  flex-direction: column;
}

.dp-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
}

.dp-heading-group {
  display: flex;
  align-items: center;
}

.dp-nav-button {
  all: unset;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  color: var(--color-text);
}

.dp-month-button,
.dp-year-button {
  all: unset;
  color: var(--color-text);
}

.dp-calendar-grid {
  width: 100%;
  border-collapse: collapse;
  user-select: none;
}

.dp-grid-row {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  width: 100%;
}

.dp-grid-row-head {
  margin-bottom: 0.25rem;
}

.dp-head-cell {
  text-align: center;
  font-size: 0.75rem;
  color: #78716c;
  border-radius: 0.375rem;
}

.dp-grid-body {
  display: grid;
}

.dp-cell {
  position: relative;
  text-align: center;
  font-size: 0.875rem;
}

.dp-cell-trigger {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.375rem;
  white-space: nowrap;
  font-size: 0.875rem;
  font-weight: 400;
  color: #000000;
  outline: none;
  cursor: default;
  background-color: transparent;
  border: none;
}

.dp-cell-trigger:hover {
  background-color: var(--color-surface-muted);
}

.dp-cell-trigger[data-selected] {
  background-color: var(--color-primary) !important;
  color: var(--color-surface);
}

.dp-cell-trigger[data-today] {
  font-weight: 600;
  background-color: var(--color-surface-muted);
}

.dp-day-trigger {
  width: 2rem;
  height: 2rem;
  border-radius: 9999px;
}

.dp-day-trigger[data-outside-view] {
  color: rgba(0, 0, 0, 0.3);
}

.dp-picker-grid {
  width: 100%;
}

.dp-picker-row {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0.25rem;
}

.dp-picker-trigger {
  width: 100%;
  padding: 0.5rem 0;
}
</style>
