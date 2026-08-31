<script setup lang="ts">
import { Pencil, MapPin, Users, X } from '@lucide/vue'
import Button from '@/shared/ui/components/Button.vue'
import TimeField from '@/shared/ui/components/TimeField.vue'
import DatePicker from '@/shared/ui/components/DatePicker.vue'
import SignalChip from '@/shared/ui/components/SignalChip.vue'
import IconButton from '@/shared/ui/components/IconButton.vue'
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
      <button v-for="entry in entries" :key="entry.id" class="draft-chip-wrapper" type="button"
        @click="editEntry(entry)">
        <SignalChip :signal="entry.signal" :value="formatDraftEntryLabel(entry)">
          <template #suffix>
            <span class="draft-chip-remove" role="button" :aria-label="`Remove ${entry.signal.name}`"
              @click.stop="emit('removeEntry', entry.id)">
              <X :size="14" />
            </span>
          </template>
        </SignalChip>
      </button>
    </div>

    <div class="draft-controls">
      <IconButton variant="secondary" aria-label="Add note" @click="emit('noteClick')">
        <Pencil />
      </IconButton>
      <IconButton variant="secondary" aria-label="Set location" @click="emit('locationClick')">
        <MapPin />
      </IconButton>
      <IconButton variant="secondary" aria-label="Tag people" @click="emit('peopleClick')">
        <Users />
        <span v-if="participantCount" class="draft-icon-badge">{{ participantCount }}</span>
      </IconButton>

      <span class="draft-spacer" />

      <div class="draft-datetime-input">
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
  padding: var(--spacing-md);
  padding-bottom: calc(var(--spacing-md) + env(safe-area-inset-bottom));
  box-shadow: var(--shadow-md);
}

.draft-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.draft-chip-wrapper {
  all: unset;
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

.draft-datetime-input {
  display: flex;
  gap: var(--spacing-sm);
  align-items: center;
}

.draft-footer {
  display: flex;
  gap: var(--spacing-sm);
}

.draft-footer> :deep(*) {
  flex: 1;
}
</style>
