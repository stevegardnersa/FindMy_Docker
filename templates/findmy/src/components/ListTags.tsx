import { useState } from 'react';
import { Tag } from '../utils/types';
import { createNewTag } from '../utils/api';
import { putSavedTags } from '../utils/storage';
import ColorHash from 'color-hash';

const colorHash = new ColorHash();

function ListTags({ tags, onListChanged, onRefreshLocations, loadingLocations }: {
  tags: Tag[],
  onListChanged(): any,
  onRefreshLocations(): any,
  loadingLocations: boolean,
}) {
  const [showAdd, setShowAdd] = useState(false);

  return <div className='card my-tags'>
    {!showAdd && <>
      <h4>
        Your tags
        &nbsp;&nbsp;

        <button className='btn btn-sm btn-outline-primary' onClick={onRefreshLocations} disabled={loadingLocations}>
          {loadingLocations ? 'Fetching data...' : 'Refresh location'}
        </button>
      </h4>

      {tags.length === 0 && <p>
        (You don't have any tags yet)
      </p>}

      {tags.map((tag, i) => <div className='tag-entry'>
        tag_id: <b style={{ color: colorHash.hex(tag.tag_id) }}>{tag.tag_id}</b>
        <br/>
        <button className='btn btn-sm btn-outline-danger' onClick={() => {
          if (window.confirm(`Delete ${tag.tag_id}?`)) {
            const newList = tags.filter((_, j) => i !== j);
            putSavedTags(newList);
            onListChanged();
          }
        }}>
          Delete
        </button>
      </div>)}

      <br />
      <button className='btn btn-primary' onClick={() => setShowAdd(true)}>
        + Add tag
      </button>
    </>}

    {showAdd && <AddTag
      tags={tags}
      onListChanged={onListChanged}
      onClose={() => setShowAdd(false)}
    />}
  </div>;
}

function AddTag({ tags, onListChanged, onClose }: {
  tags: Tag[],
  onListChanged(): any,
  onClose(): any,
}) {
  const [mode, setMode] = useState<null | 'generate' | 'import'>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [tag, setTag] = useState<Tag>({
    tag_id: '',
    priv_key: '',
    adv_key: '',
    adv_hash: '',
  });

  const onInput = (field: keyof Tag) => (e: any) => setTag(t => ({
    ...t,
    [field]: e.target.value,
  }));

  if (mode === null) {
    return <>
      <h4>Add a tag</h4>
      <br/>
      <button className='btn btn-primary full-width' onClick={async () => {
        setLoading(true);
        const newTag = await createNewTag();
        setTag(newTag);
        setMode('generate');
        setLoading(false);
      }} disabled={loading}>
        Generate a new one
      </button>
      <br/>
      <br/>
      <button className='btn btn-primary full-width' onClick={() => setMode('import')} disabled={loading}>
        Import an existing
      </button>
      <br/>
      <br/>
      <br/>
      <button className='btn btn-outline-primary' onClick={onClose} disabled={loading}>
        Cancel
      </button>
    </>;
  }

  return <>
    <h4>Add a tag</h4>
    {tag.ctype_byte_arr && <div className='alert alert-warning'>
      <b>IMPORTANT</b>: The data below will be saved to your browser. Please also save it to a safe place, because they will gone if you clear browser's data.
    </div>}
    <div className='form-group'>
      <label>
        tag_id<br/>
        <small>(you can customize it)</small>
      </label>
      <input className='form-control' placeholder='a_customizable_id' onChange={onInput('tag_id')} value={tag.tag_id}></input>
    </div>
    <div className='form-group'>
      <label>priv_key</label>
      <input className='form-control' placeholder='base64 string...' onChange={onInput('priv_key')} value={tag.priv_key}></input>
    </div>
    <div className='form-group'>
      <label>
        adv_key<br/>
        <small>(to de deployed to the micro-controller)</small>
      </label>
      <input className='form-control' placeholder='base64 string...' onChange={onInput('adv_key')} value={tag.adv_key}></input>
    </div>
    {tag.ctype_byte_arr && <div className='alert alert-info'>
      <small>This is the <b>adv_key</b> in byte array format: <br/>
        <span className='monospace'>{tag.ctype_byte_arr}</span>
      </small>
    </div>}
    <div className='form-group'>
      <label>adv_hash</label>
      <input className='form-control' placeholder='base64 string...' onChange={onInput('adv_hash')} value={tag.adv_hash}></input>
    </div>
    <br/>
    <button className='btn btn-primary' onClick={() => {
      // TODO: check for duplications
      putSavedTags([...tags, tag]);
      onListChanged();
      onClose();
    }}>
      Save
    </button>
    &nbsp;&nbsp;
    <button className='btn btn-outline-primary' onClick={onClose} disabled={loading}>
      Cancel
    </button>
  </>;
}

export default ListTags;