export interface Tag {
  tag_id: string;
  priv_key: string;
  adv_key: string;
  adv_hash: string;
  ctype_byte_arr?: string; // only show on create
};

export interface TagLocation {
  timestamp: number;
  isodatetime: string;
  tag_id: string;
  lat: number;
  lon: number;
};