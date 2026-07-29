import type { Component } from 'vue'
import {
  LayoutDashboard,
  ListChecks,
  BookOpen,
  MoreHorizontal,
  User,
  Settings,
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
  { label: 'Journal', icon: BookOpen, to: { name: '' } },
]

export const moreNavIcon = MoreHorizontal

export const sidebarGroups: NavGroup[] = [
  {
    label: 'Settings',
    items: [
      { label: 'Account', icon: User, to: { name: '' } },
    ],
  },
  {
    label: 'Configuration',
    items: [
      { label: 'General', icon: Settings, to: { name: '' } },
      { label: 'Signals', icon: Radio, to: { name: 'managesignals' } },
      { label: 'Signal boards', icon: LayoutGrid, to: { name: 'manage-boards' } },
    ],
  },
]
