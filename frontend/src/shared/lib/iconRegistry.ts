import {
  BedDouble, Book, Brain, Briefcase, Bike, Camera, Car, Cat, Coffee, Dog,
  Droplet, Dumbbell, Flame, Gamepad2, Heart, Home, Leaf, Moon, Music, Pencil,
  Pill, Plane, ShoppingCart, Smile, Star, Sun, Target, Utensils, Wallet,
} from '@lucide/vue'

export const icons = {
  Camera, Heart, Star, Book, Coffee, Dumbbell, Droplet, Moon, Sun, Smile,
  Music, Pencil, Target, Wallet, ShoppingCart, Utensils, Bike, Car, Plane,
  Home, Briefcase, Brain, Pill, BedDouble, Flame, Leaf, Dog, Cat, Gamepad2,
} as const

export type IconName = keyof typeof icons

export function isIconName(name: string | undefined): name is IconName {
  return !!name && name in icons
}

export function resolveIcon(name: string | undefined) {
  return isIconName(name) ? icons[name] : null
}
