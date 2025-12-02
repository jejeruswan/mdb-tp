// TypeScript type definitions

export type EventCategory = 'work' | 'social' | 'sports' | 'arts' | 'leisure';

export interface Event {
  id: string;
  title: string;
  description: string | null;
  category: EventCategory;
  location: string;
  latitude?: number | null;
  longitude?: number | null;
  start_time?: string | null;
  end_time?: string | null;
  image_url: string | null;
  source_url: string;
  club_name?: string | null;
  created_at: string;
  scraped_at: string;
}

export interface CategoryChipData {
  id: EventCategory;
  label: string;
  emoji: string;
}

export const CATEGORIES: CategoryChipData[] = [
  { id: 'work', label: 'career', emoji: '💼' },
  { id: 'social', label: 'social', emoji: '🎉' },
  { id: 'sports', label: 'sports', emoji: '⚽' },
  { id: 'arts', label: 'arts', emoji: '🎨' },
  { id: 'leisure', label: 'leisure', emoji: '📚' },
];

export const DEFAULT_EVENT_IMAGE = 'https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=800&q=80'; // Berkeley campus placeholder