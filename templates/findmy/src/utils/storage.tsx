import { Tag } from './types';

export function getSavedTags(): Tag[] {
  const raw = localStorage.getItem('MY_TAGS') || '[]';
  try {
    return JSON.parse(raw);
  } catch (e) {
    return [];
  }
}

export function putSavedTags(tags: Tag[]) {
  localStorage.setItem('MY_TAGS', JSON.stringify(tags));
}