import axios from 'axios';
import { Tag, TagLocation } from './types';

export type TagLocationGrouped = {
  id: string;
  locations: TagLocation[];
  lastLocation: TagLocation;
};

export async function fetchTagLocation(tags: Tag[]): Promise<TagLocationGrouped[]> {
  try {
    const { data } = await axios.post('/get_locations', {
      keys: tags,
      hours: 7 * 24, // one week
    });
    if (data.error) {
      throw new Error(data.error);
    } else {
      const results = data.results as TagLocation[];
      const groups: { [id: string]: TagLocationGrouped } = {};
      for (const res of results) {
        if (!groups[res.tag_id]) {
          groups[res.tag_id] = {
            id: res.tag_id,
            locations: [],
            lastLocation: res,
          };
        }
        // append new location
        groups[res.tag_id].locations.push(res);
        // update last location
        if (groups[res.tag_id].lastLocation.timestamp < res.timestamp) {
          groups[res.tag_id].lastLocation = res;
        }
      }
      return Object.values(groups);
    }
  } catch (e) {
    console.error(e);
    throw new Error(e?.toString());
  }
}

export async function createNewTag(): Promise<Tag> {
  try {
    const { data } = await axios.post('/generate_key');
    return data;
  } catch (e) {
    console.error(e);
    throw new Error(e?.toString());
  }
}