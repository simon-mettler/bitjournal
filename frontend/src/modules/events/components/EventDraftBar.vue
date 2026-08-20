<script setup lang="ts">
import { Pencil, MapPin, Users, X } from '@lucide/vue'
import Button from '@/shared/ui/components/Button.vue'
import TimeField from '@/shared/ui/components/TimeField.vue'
import DatePicker from '@/shared/ui/components/DatePicker.vue'
import type { DraftEntry } from '@/modules/events/types'
import { formatDraftEntryLabel } from '@/modules/events/format'
import type { DateValue } from '@internationalized/date'
import type { TimeValue } from 'reka-ui'

defineProps<{
  entries: DraftEntry[]
  participantCount?: number
}>()

const emit = defineEmits<{
  editEntry: [entryId: string]
  removeEntry: [entryId: string]
  noteClick: []
  locationClick: []
  peopleClick: []
  cancel: []
  save: []
}>()

function editEntry(entry: DraftEntry) {
  if (entry.signal.type === 'tally') return
  emit('editEntry', entry.id)
}

const date = defineModel<DateValue>('date')
const time = defineModel<TimeValue>('time')
</script>

<template>
  <div class="draft-bar">
    <div class="draft-chips">
      <button v-for="entry in entries" :key="entry.id" type="button" class="draft-chip" @click="editEntry(entry)">
        <span class="draft-chip-dot" :style="{ backgroundColor: entry.signal.color }" />
        <span class="draft-chip-label">{{ formatDraftEntryLabel(entry) }}</span>
        <span class="draft-chip-remove" role="button" :aria-label="`Remove ${entry.signal.name}`"
          @click.stop="emit('removeEntry', entry.id)">
          <X :size="14" />
        </span>
      </button>
    </div>

    <div class="draft-controls">
      <button type="button" class="draft-icon-btn" aria-label="Add note" @click="emit('noteClick')">
        <Pencil :size="18" />
      </button>
      <button type="button" class="draft-icon-btn" aria-label="Set location" @click="emit('locationClick')">
        <MapPin :size="18" />
      </button>
      <button type="button" class="draft-icon-btn" aria-label="Tag people" @click="emit('peopleClick')">
        <Users :size="18" />
        <span v-if="participantCount" class="draft-icon-badge">{{ participantCount }}</span>
      </button>

      <span class="draft-spacer" />

      <div class="draft-time-input">
        <DatePicker v-model="date" />
        <TimeField v-model="time" />
      </div>
    </div>

    <div class="draft-footer">
      <Button variant="secondary" @click="emit('cancel')">Cancel</Button>
      <Button variant="primary" @click="emit('save')">Save Entry</Button>
    </div>
  </div>
</template>

<style scoped>
.draft-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 25;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
  background-color: var(--color-surface);
  border-top: var(--input-border);
  border-radius: var(--radius-lg) var(--radius-lg) 0 0;
  padding: var(--spacing-md) var(--spacing-md) calc(var(--spacing-md) + env(safe-area-inset-bottom));
  box-shadow: var(--shadow-md);
}

.draft-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.draft-chip {
  all: unset;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 8px 6px 10px;
  border-radius: var(--radius-xl);
  background-color: var(--color-surface-muted);
  font-size: var(--font-size-sm);
  color: var(--color-text);
  cursor: pointer;
}

.draft-chip-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.draft-chip-remove {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: var(--input-color-label);
  cursor: pointer;
}

.draft-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.draft-icon-btn {
  all: unset;
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: var(--input-radius);
  border: var(--input-border);
  color: var(--input-color-text);
  cursor: pointer;
}

.draft-icon-btn:hover {
  background-color: var(--color-surface-muted);
}

.draft-icon-badge {
  position: absolute;
  top: -4px;
  right: -4px;
  min-width: 16px;
  height: 16px;
  padding: 0 3px;
  border-radius: 999px;
  background-color: var(--color-primary);
  color: var(--color-surface);
  font-size: 10px;
  font-weight: var(--font-weight-bold);
  display: flex;
  align-items: center;
  justify-content: center;
}

.draft-spacer {
  flex: 1;
}

.draft-date-input,
.draft-time-field {
  border: var(--input-border);
  border-radius: var(--input-radius);
  color: var(--input-color-text);
  background-color: var(--input-color-background);
  height: 40px;
  font-size: var(--font-size-sm);
}

.draft-date-input {
  padding: 0 8px;
}

.draft-time-input {
  display: flex;
  align-items: center;
}

.draft-time-field {
  all: unset;
  box-sizing: border-box;
  width: 32px;
  text-align: center;
  padding: 0 4px;
}

.draft-time-divider {
  width: 1px;
  height: 20px;
  background-color: var(--input-color-border);
}

.draft-footer {
  display: flex;
  gap: var(--spacing-sm);
}

.draft-footer> :deep(*) {
  flex: 1;
}
</style>
