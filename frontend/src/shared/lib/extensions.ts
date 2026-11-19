import { markRaw, shallowReactive, type App, type Component } from 'vue'
import type { Router } from 'vue-router'
import type { AxiosInstance } from 'axios'

/**
 * Optional extensions: any `src/extensions/<name>/index.ts` that exports `setup(context)` is
 * loaded at startup. Without an extensions folder nothing happens. An extension can add routes
 * and guards (`router`), HTTP interceptors (`api`), and render components into named slots.
 */
export type ExtensionSlotName = 'app' | 'account'

export interface ExtensionContext {
  app: App
  router: Router
  api: AxiosInstance
  registerSlot: (slot: ExtensionSlotName, component: Component) => void
}

interface ExtensionModule {
  setup?: (context: ExtensionContext) => void
}

const slots = shallowReactive<Partial<Record<ExtensionSlotName, Component[]>>>({})

function registerSlot(slot: ExtensionSlotName, component: Component) {
  ;(slots[slot] ??= []).push(markRaw(component))
}

export function slotComponents(slot: ExtensionSlotName): Component[] {
  return slots[slot] ?? []
}

export function loadExtensions(context: Omit<ExtensionContext, 'registerSlot'>) {
  const modules = import.meta.glob<ExtensionModule>('../../extensions/*/index.ts', { eager: true })
  for (const module of Object.values(modules)) {
    module.setup?.({ ...context, registerSlot })
  }
}
