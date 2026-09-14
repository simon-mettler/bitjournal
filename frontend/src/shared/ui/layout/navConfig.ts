import type { Component } from 'vue'
import {
  LayoutDashboard,
  ListChecks,
  BookOpen,
  MoreHorizontal,
  Radio,
  LayoutGrid,
} from '@lucide/vue'

export interface NavItem {
  label: string
  icon: Component
  to: { name: string }
}

export interface NavGroup {
  label: string
  items: NavItem[]
}

export const primaryNavItems: NavItem[] = [
  { label: 'Dashboard', icon: LayoutDashboard, to: { name: '' } },
  { label: 'Track', icon: ListChecks, to: { name: 'track' } },
  { label: 'Journal', icon: BookOpen, to: { name: 'journal' } },
]

export const moreNavIcon = MoreHorizontal

export const sidebarGroups: NavGroup[] = [
  {
    label: 'Configuration',
    items: [
      { label: 'Manage signals', icon: Radio, to: { name: 'manage-signals' } },
      { label: 'Manage boards', icon: LayoutGrid, to: { name: 'manage-boards' } },
    ],
  },
]
