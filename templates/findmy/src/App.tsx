import { useEffect, useState } from 'react';
import Map from './components/Map';
import { getSavedTags } from './utils/storage';
import { TagLocationGrouped, fetchTagLocation } from './utils/api';
import { Tag } from './utils/types';
import ListTags from './components/ListTags';

function App() {
  const [tags, setTags] = useState<Tag[]>(getSavedTags());
  const [loc, setLoc] = useState<TagLocationGrouped[] | null>([]);

  const onRefreshLocations = async () => {
    try {
      setLoc(null);
      const newLoc = await fetchTagLocation(tags);
      setLoc(newLoc);
    } catch (err) {
      console.error(err);
      window.alert((err as any)?.message || 'Unknown error');
      setLoc([]);
    }
  }

  useEffect(() => {
    // run on mounted
    onRefreshLocations();
  }, []);

  return <>
    <ListTags
      tags={tags}
      onListChanged={() => {
        setTags(getSavedTags());
      }}
      onRefreshLocations={onRefreshLocations}
      loadingLocations={loc === null}
    />
    <Map tagLocationsGrouped={loc || []} />
  </>;
};

export default App;
