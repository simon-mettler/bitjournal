<script setup lang="ts">
import { LogOut, MoreVertical } from '@lucide/vue'
import SignalChip from '@/shared/ui/components/SignalChip.vue'
import IconButton from '@/shared/ui/components/IconButton.vue'
import DropdownMenu from '@/shared/ui/components/DropdownMenu.vue'
import { formatEventTime } from '@/modules/journal/format'
import { formatDraftEntryLabel } from '@/modules/events/format'
import type { DropdownMenuOption } from '@/shared/ui/components/DropdownMenu.vue'
import type { Event } from '@/modules/events/types'
import { useRouter } from 'vue-router'

const router = useRouter()

const props = defineProps<{
  event: Event
}>()

const options: DropdownMenuOption[] = [
  {
    label: 'Edit entry',
    value: 'edit-entry',
    icon: LogOut,
    onSelect: () => router.push({ name: 'track', params: { eventId: props.event.id } })
  },
]
</script>

<template>
  <div class="journal-card">
    <div class="journal-card-top">

      <span class="journal-card-time">{{ formatEventTime(props.event.occurred_at) }}</span>

      <DropdownMenu :options="options">
        <template #trigger>
          <IconButton class="journal-card-menu" variant="tertiary"
            :aria-label="`Options for entry at ${formatEventTime(props.event.occurred_at)}`">
            <MoreVertical :size="18" />
          </IconButton>
        </template>
      </DropdownMenu>

    </div>

    <p v-if="props.event.note" class="journal-card-note">{{ props.event.note }}</p>

    <div class="journal-card-chips">
      <SignalChip v-for="entry in props.event.entries" :key="entry.signal.id" :signal="entry.signal"
        :value="formatDraftEntryLabel(entry)" />
    </div>
  </div>
</template>

<style scoped>
.journal-card {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px;
  border-radius: var(--input-radius);
  background-color: var(--input-color-background);
  box-shadow: var(--shadow-md);
}

.journal-card-top {
  display: flex;
  justify-content: space-between;
}

.journal-card-time {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-normal);
  color: var(--color-text);
}

.journal-card-menu {
  margin-top: -13px;
  margin-right: -13px;
}

.journal-card-note {
  margin: 0;
  font-size: var(--font-size-sm);
  color: var(--color-text);
}

.journal-card-divider {
  height: 1px;
  background-color: var(--input-color-border);
}

.journal-card-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
</style>
