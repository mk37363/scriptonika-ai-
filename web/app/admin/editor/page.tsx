'use client';
import { useEffect, useState } from 'react';

type Item = {
  id:number; status:string; specialty?:string; intent?:string; audience?:string;
  tone?:string; text?:string; tags?:string[]; created_at?:number;
};

export default function Page() {
  const API = process.env.NEXT_PUBLIC_API_BASE || '';
  const [token, setToken] = useState('');
  const [specialty, setSpecialty] = useState('стоматология');
  const [intent, setIntent] = useState('общение');
  const [audience, setAudience] = useState('оператор');
  const [tone, setTone] = useState('дружелюбный, профессиональный');
  const [text, setText] = useState('');
  const [tags, setTags] = useState('скрипт, пример');
  const [items, setItems] = useState<Item[]>([]);
  const [msg, setMsg] = useState('');

  useEffect(()=>{
    const t = localStorage.getItem('skr_token') || '';
    setToken(t);
    if (t) refresh(t);
  },[]);

  const refresh = async (t:string) => {
    setMsg('Загружаю список...');
    const r = await fetch(`${API}/api/admin/kb/list`, {
      headers: { 'Authorization': `Bearer ${t}` }
    });
    const data = await r.json();
    setItems(data.items || []);
    setMsg('');
  };

  const createDraft = async () => {
    if (!token) { setMsg('Сначала войдите на /admin/login'); return; }
    setMsg('Сохраняю черновик...');
    const payload = {
      specialty, intent, audience, tone,
      text,
      tags: tags.split(',').map(s=>s.trim()).filter(Boolean),
      status: 'draft'
    };
    const r = await fetch(`${API}/api/admin/kb/create`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type':'application/json'
      },
      body: JSON.stringify(payload)
    });
    const data = await r.json();
    setMsg('Создано: id=' + data.id);
    await refresh(token);
    setText('');
  };

  const publish = async (id:number) => {
    setMsg('Публикую...');
    await fetch(`${API}/api/admin/kb/publish/${id}`, {
      method:'POST',
      headers: { 'Authorization': `Bearer ${token}` }
    });
    setMsg('Опубликовано.');
    await refresh(token);
  };

  const reindex = async () => {
    setMsg('Индексация...');
    await fetch(`${API}/api/admin/reindex`, {
      method:'POST',
      headers: { 'Authorization': `Bearer ${token}` }
    });
    setMsg('Индекс обновлён.');
  };

  return (
    <div className="p-6 max-w-3xl mx-auto space-y-6">
      <h1 className="text-2xl font-semibold">Редактор знаний</h1>
      <div className="space-y-3 border p-4 rounded">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <input className="border p-2 rounded" value={specialty} onChange={e=>setSpecialty(e.target.value)} placeholder="Специальность" />
          <input className="border p-2 rounded" value={intent} onChange={e=>setIntent(e.target.value)} placeholder="Намерение (тема)" />
          <input className="border p-2 rounded" value={audience} onChange={e=>setAudience(e.target.value)} placeholder="Аудитория" />
          <input className="border p-2 rounded" value={tone} onChange={e=>setTone(e.target.value)} placeholder="Тон" />
        </div>
        <textarea className="w-full border p-2 rounded min-h-40"
          placeholder="Напишите правило/пример как в чате (это и есть обучение)"
          value={text} onChange={e=>setText(e.target.value)} />
        <input className="border p-2 rounded w-full" value={tags} onChange={e=>setTags(e.target.value)} placeholder="Теги через запятую" />
        <div className="flex gap-2">
          <button onClick={createDraft} className="px-4 py-2 rounded bg-black text-white">Сохранить черновик</button>
          <button onClick={reindex} className="px-4 py-2 rounded bg-gray-800 text-white">Переиндексировать</button>
        </div>
        <p className="text-sm text-gray-600">{msg}</p>
      </div>

      <div className="space-y-2">
        <h2 className="font-semibold">Черновики и опубликованное</h2>
        <ul className="space-y-2">
          {items.map(it=>(
            <li key={it.id} className="border rounded p-3">
              <div className="text-sm text-gray-500">#{it.id} · {it.status}</div>
              <div className="font-medium">{it.specialty} — {it.intent}</div>
              <div className="whitespace-pre-wrap text-sm mt-1">{it.text}</div>
              <div className="flex gap-2 mt-2">
                {it.status !== 'published' &&
                  <button onClick={()=>publish(it.id)} className="px-3 py-1 rounded bg-green-600 text-white">Опубликовать</button>}
              </div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
