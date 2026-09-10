<script setup lang="ts">
import { Pencil, MapPin, Users } from '@lucide/vue'
import Button from '@/shared/ui/components/Button.vue'
import TimeField from '@/shared/ui/components/TimeField.vue'
import DatePicker from '@/shared/ui/components/DatePicker.vue'
import SignalChip from '@/shared/ui/components/SignalChip.vue'
import IconButton from '@/shared/ui/components/IconButton.vue'
import { formatDraftEntryLabel } from '@/modules/events/format'
import type { DraftEntry } from '@/modules/events/types'
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

const date = defineModel<DateValue>('date')
const time = defineModel<TimeValue>('time')
</script>

<template>
  <div class="draft-bar">
    <div class="draft-chips">
      <span class="draft-chip-empty" v-if="entries.length === 0">Select a signal to add to this event</span>
      <SignalChip v-for="entry in entries" :key="entry.id" :signal="entry.signal" :value="formatDraftEntryLabel(entry)"
        :clickable="entry.signal.type !== 'tally'" removable @click="emit('editEntry', entry.id)"
        @remove="emit('removeEntry', entry.id)" />
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
      <Button variant="primary" :disabled="entries.length === 0" @click="emit('save')">Save Entry</Button>
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
  max-height: 150px;
  overflow-y: auto;
}

.draft-chip-empty {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 36px;
  background-color: var(--color-surface-muted);
  border-radius: var(--radius-xl);
  color: var(--color-text);
}

.draft-controls {
  display: flex;
  align-items: center;
  gap: 8px;
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
