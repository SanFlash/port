'use strict';
let active = 'Profile', items = [], requestNumber = 0;
const $ = id => document.getElementById(id);
const collection = () => active.toLowerCase().replaceAll(' ', '-');
function notice(text) { $('notice').textContent = text; $('notice').hidden = !text; }
async function api(url, options) {
  const r = await fetch(url, options);
  if (!r.ok) throw new Error('Request failed');
  return r.json();
}
function draw() {
  const container = $('items'); container.replaceChildren();
  if (!items.length) {
    const p = document.createElement('p'); p.className = 'empty';
    p.textContent = 'Nothing here yet. Create your first item above.'; container.append(p);
  }
  for (const item of items) {
    const article = document.createElement('article'); article.className = 'row';
    const details = document.createElement('div'), actions = document.createElement('div');
    const title = document.createElement('strong'), status = document.createElement('small');
    title.textContent = item.title; status.textContent = item.status; details.append(title, status);
    for (const action of ['Publish', 'Delete']) {
      const button = document.createElement('button'); button.textContent = action;
      button.onclick = async () => {
        if (action === 'Delete' && !confirm('Delete this item?')) return;
        button.disabled = true;
        try {
          await api(`/api/cms/${encodeURIComponent(item.id)}`, action === 'Delete' ? {method:'DELETE'} :
            {method:'PATCH', headers:{'content-type':'application/json'}, body:JSON.stringify({status:'PUBLISHED'})});
          if (action === 'Delete') items = items.filter(i => i.id !== item.id); else item.status = 'PUBLISHED';
          draw();
        } catch { notice('Connect the database to save CMS content.'); button.disabled = false; }
      };
      actions.append(button);
    }
    article.append(details, actions); container.append(article);
  }
}
async function load() {
  const n = ++requestNumber;
  try { const x = await api(`/api/cms?collection=${encodeURIComponent(collection())}`); if (n === requestNumber) { items = x.items || []; draw(); } }
  catch { if(n === requestNumber) { items = []; draw(); } }
}
if ($('login')) $('login').onsubmit = async e => {
  e.preventDefault();
  try { await api('/api/auth/login', {method:'POST',body:new FormData(e.currentTarget)}); location.reload(); }
  catch { notice('Sign-in failed. Check the configured email and password.'); }
};
if ($('save')) {
  document.querySelectorAll('[data-section]').forEach(button => button.onclick = () => {
    active = button.dataset.section;
    document.querySelectorAll('[data-section]').forEach(b => b.classList.toggle('selected', b === button));
    $('breadcrumb').textContent = `CMS / ${active}`; $('active').textContent = active;
    $('save').elements.title.placeholder = `New ${active.slice(0,-1)}`; load();
  });
  $('save').onsubmit = async e => {
    e.preventDefault(); const input = e.currentTarget.elements.title, title = input.value;
    if (!title.trim()) return;
    const savedCollection = collection();
    try {
      const x = await api('/api/cms', {method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({collection:savedCollection,title,status:'DRAFT',data:{}})});
      input.value = ''; if (savedCollection === collection()) { items = [x.item,...items]; draw(); } notice('Saved as draft.');
    } catch { notice('Connect the database to save CMS content.'); }
  };
  load();
}

if ($('logout')) $('logout').onclick = async () => {
  await api('/api/auth/logout', {method:'POST'}); location.reload();
};
