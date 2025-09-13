'use client';
import { useState } from 'react';

export default function Page() {
  const API = process.env.NEXT_PUBLIC_API_BASE || '';
  const [q, setQ] = useState('Пациент сомневается записываться — что сказать?');
  const [res, setRes] = useState<any>(null);
  const [msg, setMsg] = useState('');

  const ask = async () => {
    setMsg('Спрашиваю...');
    const r = await fetch(`${API}/api/ask`, {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({question: q, top_k: 3})
    });
    const data = await r.json();
    setRes(data);
    setMsg('');
  };

  return (
    <div className="p-6 max-w-3xl mx-auto space-y-4">
      <h1 className="text-2xl font-semibold">Проверка ответов</h1>
      <textarea className="w-full border p-2 rounded min-h-32"
        value={q} onChange={e=>setQ(e.target.value)} />
      <button onClick={ask} className="px-4 py-2 rounded bg-black text-white">Спросить</button>
      <p className="text-sm text-gray-600">{msg}</p>
      {res && (
        <div className="space-y-3">
          <div className="border rounded p-3">
            <div className="font-medium mb-1">Ответ</div>
            <pre className="whitespace-pre-wrap text-sm">{res.answer || JSON.stringify(res, null, 2)}</pre>
          </div>
          {res.contexts && (
            <div className="border rounded p-3">
              <div className="font-medium mb-1">Контексты</div>
              <ul className="list-disc pl-5 text-sm space-y-2">
                {res.contexts.map((c:string, i:number)=>(
                  <li key={i}><pre className="whitespace-pre-wrap">{c}</pre></li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
