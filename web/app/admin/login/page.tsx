'use client';
import { useState } from 'react';

export default function Page() {
  const [email, setEmail] = useState('marika@khlud.ru');
  const [password, setPassword] = useState('');
  const [msg, setMsg] = useState('');
  const API = process.env.NEXT_PUBLIC_API_BASE || '';

  const onLogin = async (e: any) => {
    e.preventDefault();
    setMsg('Вход...');
    try {
      const r = await fetch(`${API}/api/admin/login`, {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({email, password})
      });
      const data = await r.json();
      if (data.token) {
        localStorage.setItem('skr_token', data.token);
        setMsg('Готово. Токен сохранён. Перейдите в редактор.');
      } else {
        setMsg('Ошибка входа: ' + JSON.stringify(data));
      }
    } catch (e:any) {
      setMsg('Сеть/сервер: ' + e.message);
    }
  };

  return (
    <div className="p-6 max-w-md mx-auto space-y-4">
      <h1 className="text-2xl font-semibold">Вход администратора</h1>
      <form onSubmit={onLogin} className="space-y-3">
        <input className="w-full border p-2 rounded" placeholder="Email"
               value={email} onChange={e=>setEmail(e.target.value)} />
        <input className="w-full border p-2 rounded" placeholder="Пароль" type="password"
               value={password} onChange={e=>setPassword(e.target.value)} />
        <button className="px-4 py-2 rounded bg-black text-white">Войти</button>
      </form>
      <p className="text-sm text-gray-600">{msg}</p>
      <p className="text-sm">Дальше: /admin/editor и /admin/check</p>
    </div>
  );
}
