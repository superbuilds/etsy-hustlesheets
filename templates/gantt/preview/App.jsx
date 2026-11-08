import React, { useState, useMemo, useRef } from 'react';
import { Table as TableIcon, Calendar, CheckCircle2, Clock, AlertCircle, Plus, X, User, Layers, Search, ArrowUpDown, ChevronDown, ChevronRight, Trash2, Edit2, MoveUp, MoveDown, Info } from 'lucide-react';

function parseDateSafe(v) {
  if (!v) return null;
  if (v instanceof Date) return isNaN(v.getTime()) ? null : v;
  if (typeof v === 'string') {
    const t = v.trim(); const p = t.split('-');
    if (p.length === 3) { const y = +p[0], m = +p[1], d = +p[2]; if (!isNaN(y) && !isNaN(m) && !isNaN(d)) return new Date(y, m - 1, d); }
    const s = t.split('/');
    if (s.length === 3) { const m = +s[0], d = +s[1], y = +s[2]; if (!isNaN(y) && !isNaN(m) && !isNaN(d)) return new Date(y, m - 1, d); }
  }
  return null;
}
function formatDateISO(d) { if (!d || isNaN(d.getTime())) return ''; return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`; }
function getInitials(n) { if (!n) return '?'; const p = n.trim().split(/\s+/); return p.length === 1 ? p[0].substring(0, 2).toUpperCase() : (p[0][0] + p[p.length - 1][0]).toUpperCase(); }
const PHASE_COLORS = {
  Initiation: { bg: 'bg-purple-50 text-purple-700 border-purple-200', dot: 'bg-purple-500', bar: 'bg-purple-500', barBg: 'bg-purple-100 border-purple-300' },
  Planning: { bg: 'bg-sky-50 text-sky-700 border-sky-200', dot: 'bg-sky-500', bar: 'bg-sky-500', barBg: 'bg-sky-100 border-sky-300' },
  Execution: { bg: 'bg-blue-50 text-blue-700 border-blue-200', dot: 'bg-blue-500', bar: 'bg-blue-500', barBg: 'bg-blue-100 border-blue-300' },
  Launch: { bg: 'bg-emerald-50 text-emerald-700 border-emerald-200', dot: 'bg-emerald-500', bar: 'bg-emerald-500', barBg: 'bg-emerald-100 border-emerald-300' }
};
const badge = (s) => s === 'Completed' ? 'bg-emerald-50 text-emerald-700 border-emerald-200' : s === 'In Progress' ? 'bg-blue-50 text-blue-700 border-blue-200' : s === 'Blocked' ? 'bg-rose-50 text-rose-700 border-rose-200' : 'bg-slate-50 text-slate-600 border-slate-200';
const DAY = 86400000;

export default function App({ data }) {
  const [activeView, setActiveView] = useState(window.__view || 'Timeline');
  const [zoom, setZoom] = useState('Week');
  const [modal, setModal] = useState(null);
  const [collapsed, setCollapsed] = useState({});
  const ref = useRef(null);

  const P = useMemo(() => {
    const rows = data[0].data; let title = 'Project Schedule & Tracker', sub = 'Cross-functional roadmap, task execution milestones, and live timeline', lead = 'Michael Heap', target = '', today = '';
    rows.forEach((e) => { const r = e.row || []; if (e.index_ === 0 && r[0]) title = String(r[0]); if (e.index_ === 1 && r[0]) sub = String(r[0]);
      r.forEach((c, i) => { if (typeof c === 'string') { const l = c.toLowerCase(); if (l.includes('project lead') && r[i + 1]) lead = String(r[i + 1]); if (l.includes('target delivery') && r[i + 1]) target = String(r[i + 1]); if (l.includes('today:') && r[i + 1]) today = String(r[i + 1]); } }); });
    const h = rows.find((it) => it.row.some((c) => typeof c === 'string' && c.toLowerCase().includes('task name')));
    const hi = h ? h.index_ : 7; const C = { phase: 0, name: 1, owner: 2, start: 3, end: 4, dur: 5, pct: 6, status: 7 };
    (h ? h.row : []).forEach((c, i) => { if (!c) return; const s = String(c).toLowerCase().trim(); if (s === 'phase') C.phase = i; else if (s.includes('task name')) C.name = i; else if (s.includes('owner')) C.owner = i; else if (s.includes('start date')) C.start = i; else if (s.includes('end date')) C.end = i; else if (s.includes('duration')) C.dur = i; else if (s.includes('complete')) C.pct = i; else if (s.includes('status')) C.status = i; });
    const tasks = [];
    rows.forEach((it) => {
      if (it.index_ > hi && it.row.length > 1) { const r = it.row; if (!r[C.name] && !r[C.phase]) return;
        let pct = typeof r[C.pct] === 'number' ? r[C.pct] : (parseFloat(String(r[C.pct] || '').replace('%', '')) || 0); if (pct > 1) pct /= 100;
        const s = parseDateSafe(String(r[C.start] || '')), e = parseDateSafe(String(r[C.end] || ''));
        let dur = r[C.dur] ? parseFloat(r[C.dur]) : null; if ((dur == null || isNaN(dur)) && s && e) dur = Math.round((e - s) / DAY) + 1;
        tasks.push({ id: it.index_, phase: r[C.phase] || 'General', taskName: r[C.name] || 'Untitled Task', owner: r[C.owner] || '', startDateStr: r[C.start] || '', endDateStr: r[C.end] || '', startDate: s, endDate: e, duration: dur, percentComplete: Math.min(1, Math.max(0, pct)), status: r[C.status] || 'Not Started' }); }
    });
    return { tasks, title, sub, lead, target, today };
  }, [data]);
  const { tasks } = P;
  const allPhases = [...new Set(tasks.map((t) => t.phase))], allOwners = [...new Set(tasks.map((t) => t.owner).filter(Boolean))];
  const todayRef = parseDateSafe(P.today) || new Date();
  const m = { total: tasks.length, completed: tasks.filter((t) => t.status === 'Completed').length, inProgress: tasks.filter((t) => t.status === 'In Progress').length, notStarted: tasks.filter((t) => t.status === 'Not Started').length,
    overdue: tasks.filter((t) => t.endDate && t.endDate < todayRef && t.status !== 'Completed').length };
  m.avgPct = Math.round((tasks.reduce((a, t) => a + t.percentComplete, 0) / (tasks.length || 1)) * 1000) / 10;
  const groups = tasks.reduce((a, t) => { (a[t.phase] = a[t.phase] || []).push(t); return a; }, {});
  let minD = null, maxD = null; tasks.forEach((t) => { if (t.startDate && (!minD || t.startDate < minD)) minD = t.startDate; if (t.endDate && (!maxD || t.endDate > maxD)) maxD = t.endDate; });
  const totalDays = Math.max(1, Math.round((maxD - minD) / DAY) + 1);
  const ppd = zoom === 'Week' ? 24 : 10, gridW = Math.max(600, totalDays * ppd);
  const inRange = todayRef >= minD && todayRef <= maxD, todayX = Math.round((todayRef - minD) / DAY) * ppd;
  const openEdit = (t) => setModal({ mode: 'edit', t, v: { phase: t.phase, taskName: t.taskName, owner: t.owner, startDate: t.startDateStr, endDate: t.endDateStr, pct: Math.round(t.percentComplete * 100), status: t.status } });
  const openCreate = () => setModal({ mode: 'create', v: { phase: allPhases[0], taskName: '', owner: '', startDate: formatDateISO(new Date()), endDate: formatDateISO(new Date(Date.now() + 7 * DAY)), pct: 0, status: 'Not Started' } });
  window.__openEdit = () => openEdit(tasks[2]);
  const sel = 'bg-slate-50 border border-slate-200 rounded-md px-2 py-1 text-xs text-slate-700 font-medium';
  const kpi = (cls, lcls, label, Icon, icls, val, sub, subcls) => (
    <div className={`${cls} rounded-lg p-2.5`}><div className={`text-[11px] font-semibold ${lcls} uppercase tracking-wider flex items-center justify-between`}><span>{label}</span><Icon className={`w-3.5 h-3.5 ${icls}`} /></div>
      <div className="text-xl font-bold text-slate-900 mt-1">{val}</div><div className={`text-[11px] ${subcls} mt-0.5`}>{sub}</div></div>);
  const inp = 'w-full border border-slate-300 rounded-lg px-3 py-2 text-xs text-slate-800';

  return (
    <div className="min-h-screen w-full bg-slate-50/50 flex flex-col font-sans text-slate-800">
      <div className="bg-white border-b border-slate-200 shadow-xs sticky top-0 z-30"><div className="w-full px-6 py-3.5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center gap-2.5"><div className="p-2 rounded-lg bg-blue-50 text-blue-600 border border-blue-100"><TableIcon className="w-5 h-5" /></div>
            <div><h1 className="text-lg font-bold text-slate-900 tracking-tight leading-tight">{P.title}</h1><p className="text-xs text-slate-500 mt-0.5">{P.sub}</p></div></div>
          <div className="flex flex-wrap items-center gap-2 text-xs">
            <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-slate-100/80 border border-slate-200/80 text-slate-600 font-medium"><User className="w-3.5 h-3.5 text-slate-400" /><span>Lead:</span><span className="font-semibold text-slate-800">{P.lead}</span></div>
            {P.target && <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-slate-100/80 border border-slate-200/80 text-slate-600 font-medium"><Calendar className="w-3.5 h-3.5 text-slate-400" /><span>Target:</span><span className="font-semibold text-slate-800">{P.target}</span></div>}
            {P.today && <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-blue-50/80 border border-blue-200/80 text-blue-700 font-medium"><Clock className="w-3.5 h-3.5 text-blue-500" /><span>Today:</span><span className="font-semibold text-blue-900">{P.today}</span></div>}
            <button onClick={openCreate} className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-blue-600 text-white rounded-md font-semibold text-xs shadow-xs"><Plus className="w-4 h-4" /><span>Add Task</span></button>
          </div></div>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3 mt-4 pt-4 border-t border-slate-100">
          {kpi('bg-slate-50/70 border border-slate-200/70', 'text-slate-500', 'Total Tasks', Layers, 'text-slate-400', m.total, `${m.total} scheduled items`, 'text-slate-400')}
          {kpi('bg-emerald-50/40 border border-emerald-200/60', 'text-emerald-700', 'Completed', CheckCircle2, 'text-emerald-500', m.completed, `${Math.round(m.completed / m.total * 100)}% finished`, 'text-emerald-600/80')}
          {kpi('bg-blue-50/40 border border-blue-200/60', 'text-blue-700', 'In Progress', Clock, 'text-blue-500', m.inProgress, 'Active work streams', 'text-blue-600/80')}
          {kpi('bg-amber-50/40 border border-amber-200/60', 'text-amber-700', 'Overdue', AlertCircle, 'text-amber-500', m.overdue, m.overdue === 0 ? 'On schedule' : 'Needs attention', 'text-amber-600/80')}
          <div className="col-span-2 sm:col-span-1 bg-slate-50/70 border border-slate-200/70 rounded-lg p-2.5"><div className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider flex items-center justify-between"><span>Overall Progress</span><span className="font-bold text-slate-800">{m.avgPct}%</span></div>
            <div className="w-full bg-slate-200 h-2 rounded-full overflow-hidden mt-2"><div className="bg-blue-600 h-full rounded-full" style={{ width: `${m.avgPct}%` }} /></div><div className="text-[11px] text-slate-400 mt-1">Average across all tasks</div></div>
        </div></div></div>

      <div className="w-full px-6 pt-4 pb-3"><div className="flex flex-col lg:flex-row items-stretch lg:items-center justify-between gap-3 bg-white p-3 rounded-xl border border-slate-200 shadow-xs">
        <div className="flex flex-wrap items-center gap-3 flex-1 min-w-[280px]">
          <div className="flex items-center p-1 bg-slate-100/90 rounded-lg border border-slate-200/80">
            {[['Timeline', Calendar], ['Table', TableIcon]].map(([v, I]) => <button key={v} onClick={() => setActiveView(v)} className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-md ${activeView === v ? 'bg-white text-blue-700 shadow-xs' : 'text-slate-600'}`}><I className="w-3.5 h-3.5" /><span>{v}</span></button>)}
          </div>
          {activeView === 'Timeline' && <div className="flex items-center gap-2 border-l border-slate-200 pl-3"><span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Zoom:</span>
            <div className="flex items-center bg-slate-100 p-0.5 rounded-md border border-slate-200">{['Week', 'Month'].map((z) => <button key={z} onClick={() => setZoom(z)} className={`px-2.5 py-1 text-xs rounded ${zoom === z ? 'bg-white text-slate-900 font-bold shadow-2xs' : 'text-slate-500 font-medium'}`}>{z}</button>)}</div>
            {inRange && <button className="px-2.5 py-1 text-xs font-semibold text-blue-600 bg-blue-50 border border-blue-200/80 rounded-md flex items-center gap-1"><Clock className="w-3.5 h-3.5 text-blue-500" /><span>Jump to Today</span></button>}</div>}
          <div className="relative flex-1 min-w-[180px]"><Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" /><input placeholder="Search by task, owner, or phase..." className="w-full pl-9 pr-8 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-lg placeholder:text-slate-400" /></div>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <div className="flex items-center gap-1.5 text-xs"><span className="text-slate-400 font-medium">Status:</span><select className={sel}><option>All ({tasks.length})</option></select></div>
          <div className="flex items-center gap-1.5 text-xs"><span className="text-slate-400 font-medium">Phase:</span><select className={sel}><option>All Phases</option></select></div>
          <div className="flex items-center gap-1.5 text-xs"><span className="text-slate-400 font-medium">Owner:</span><select className={sel}><option>All Owners</option></select></div>
          {activeView === 'Table' && <button className="px-2.5 py-1 text-xs font-semibold rounded-md border flex items-center gap-1.5 bg-blue-50 text-blue-700 border-blue-200"><Layers className="w-3.5 h-3.5" /><span>Group Phase</span></button>}
        </div></div></div>

      <div className="w-full px-6 pb-12 flex-1 flex flex-col">
        {activeView === 'Timeline' ? (
          <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden flex flex-col flex-1">
            <div ref={ref} className="overflow-x-auto relative flex-1"><div className="flex flex-col min-w-full" style={{ width: `${280 + gridW}px` }}>
              <div className="flex border-b border-slate-200 sticky top-0 z-30 bg-white select-none">
                <div className="w-[280px] min-w-[280px] sticky left-0 z-40 bg-slate-50/95 border-r border-slate-200 p-3 flex items-center justify-between"><span className="font-bold text-xs uppercase tracking-wider text-slate-700">Tasks & Phases</span><span className="text-[11px] text-slate-400 font-medium">{tasks.length} items</span></div>
                <div className="relative flex flex-col bg-slate-50/80" style={{ width: `${gridW}px` }}>
                  <div className="h-7 border-b border-slate-200/80 relative text-[11px]">{Array.from({ length: totalDays }).map((_, i) => { const d = new Date(minD.getFullYear(), minD.getMonth(), minD.getDate() + i); if (!(d.getDate() === 1 || i === 0)) return null;
                    return <div key={i} className="absolute top-0 bottom-0 pl-2 flex items-center border-l border-slate-300 font-bold text-slate-800 tracking-tight" style={{ left: `${i * ppd}px` }}>{d.toLocaleDateString('en-US', { month: 'short', year: 'numeric' })}</div>; })}</div>
                  <div className="h-7 relative text-[10px]">{Array.from({ length: totalDays }).map((_, i) => { if (!(zoom === 'Week' ? i % 7 === 0 : i % 14 === 0)) return null; const d = new Date(minD.getFullYear(), minD.getMonth(), minD.getDate() + i);
                    return <div key={i} className="absolute top-0 bottom-0 pl-1.5 flex items-center border-l border-slate-200 text-slate-600 font-mono" style={{ left: `${i * ppd}px` }}>{d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}</div>; })}</div>
                  {inRange && <div className="absolute top-0 bottom-0 pointer-events-none z-30" style={{ left: `${todayX}px` }}><div className="bg-red-600 text-white text-[9px] font-bold px-1.5 py-0.5 rounded shadow-xs uppercase tracking-wider -translate-x-1/2">Today</div></div>}
                </div></div>
              <div className="relative divide-y divide-slate-100 flex-1">
                <div className="absolute top-0 bottom-0 pointer-events-none z-0" style={{ left: '280px', width: `${gridW}px` }}>
                  {Array.from({ length: totalDays }).map((_, i) => (zoom === 'Week' ? i % 7 === 0 : i % 14 === 0) ? <div key={i} className="absolute top-0 bottom-0 border-l border-slate-100" style={{ left: `${i * ppd}px` }} /> : null)}
                  {inRange && <div className="absolute top-0 bottom-0 border-l-2 border-red-500 z-20" style={{ left: `${todayX}px` }} />}
                </div>
                {Object.entries(groups).map(([ph, pts]) => { const st = PHASE_COLORS[ph] || PHASE_COLORS.Execution; const done = pts.filter((t) => t.status === 'Completed').length; const avg = Math.round(pts.reduce((a, t) => a + t.percentComplete, 0) / pts.length * 100);
                  return (<div key={ph} className="flex flex-col">
                    <div className="flex bg-slate-100/75 border-y border-slate-200/80 select-none">
                      <div className="w-[280px] min-w-[280px] sticky left-0 bg-slate-100/95 border-r border-slate-200/80 p-2.5 flex items-center justify-between">
                        <button className="flex items-center gap-2"><ChevronDown className="w-4 h-4 text-slate-500" /><span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-xs border ${st.bg}`}><span className={`w-1.5 h-1.5 rounded-full ${st.dot}`} /><span className="font-bold">{ph}</span></span></button>
                        <span className="text-[11px] text-slate-500 font-medium">{done}/{pts.length} ({avg}%)</span></div>
                      <div className="relative h-10 flex items-center px-4" style={{ width: `${gridW}px` }}><div className="w-32 bg-slate-200/80 h-1.5 rounded-full overflow-hidden opacity-60"><div className={`h-full ${st.bar}`} style={{ width: `${avg}%` }} /></div></div>
                    </div>
                    {!collapsed[ph] && pts.map((t) => { const od = t.endDate && t.endDate < todayRef && t.status !== 'Completed';
                      const s = Math.max(0, Math.round((t.startDate - minD) / DAY)), e = Math.min(totalDays - 1, Math.round((t.endDate - minD) / DAY)); const left = s * ppd, w = Math.max(20, (e - s + 1) * ppd);
                      return (<div key={t.id} className="flex items-center hover:bg-slate-50/70 group relative border-b border-slate-100">
                        <div className="w-[280px] min-w-[280px] sticky left-0 z-10 bg-white border-r border-slate-200 p-2.5 flex items-center justify-between gap-2 shadow-2xs">
                          <div className="flex items-center gap-2 truncate flex-1"><div className="w-5 h-5 rounded-full bg-slate-100 text-slate-700 font-bold text-[9px] flex items-center justify-center border border-slate-200 shrink-0">{getInitials(t.owner)}</div>
                            <button onClick={() => openEdit(t)} className="font-semibold text-xs text-slate-800 truncate text-left">{t.taskName}</button></div>
                          <div className="flex items-center gap-1 shrink-0">{t.duration != null && <span className="text-[10px] font-mono text-slate-500 bg-slate-100 px-1.5 py-0.5 rounded border border-slate-200">{t.duration}d</span>}
                            <span className={`text-[10px] font-semibold px-1.5 py-0.5 rounded-full border ${badge(t.status)}`}>{t.status === 'Completed' ? 'Done' : t.status}</span></div></div>
                        <div className="relative h-12 flex items-center" style={{ width: `${gridW}px` }}>
                          <div onClick={() => openEdit(t)} style={{ left: `${left}px`, width: `${w}px` }} className={`absolute top-2 h-8 rounded-md border text-xs cursor-pointer overflow-hidden flex items-center select-none ${od ? 'border-rose-500 ring-2 ring-rose-500/80 bg-rose-50' : st.barBg}`}>
                            <div style={{ width: `${Math.round(t.percentComplete * 100)}%` }} className={`absolute top-0 bottom-0 left-0 rounded-l-sm ${od ? 'bg-rose-500' : st.bar}`} />
                            <div className="relative z-10 px-2 flex items-center justify-between w-full text-[11px] font-semibold text-slate-900 truncate"><span className="truncate">{t.taskName}</span><span className="text-[10px] ml-1 shrink-0 font-mono opacity-80">{Math.round(t.percentComplete * 100)}%</span></div>
                          </div></div></div>); })}
                  </div>); })}
              </div></div></div>
            <div className="px-4 py-2.5 bg-slate-50/90 border-t border-slate-200 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 gap-2">
              <div className="flex items-center gap-2"><span>Showing timeline from <strong className="text-slate-700">{formatDateISO(minD)}</strong> to <strong className="text-slate-700">{formatDateISO(maxD)}</strong></span><span className="text-slate-300">•</span><span>Click any bar to edit details</span></div>
              <div className="flex items-center gap-3 text-[11px]"><div className="flex items-center gap-1"><div className="w-3 h-3 rounded-xs border-2 border-rose-500 bg-rose-50" /><span>Red outline: Overdue</span></div><div className="flex items-center gap-1"><div className="w-3 h-0.5 bg-red-500" /><span>Red line: Today</span></div></div>
            </div></div>
        ) : (
          <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden flex flex-col flex-1">
            <div className="overflow-x-auto flex-1"><table className="w-full text-left border-collapse text-xs">
              <thead><tr className="bg-slate-50/80 border-b border-slate-200 text-slate-600 font-semibold uppercase tracking-wider text-[11px]">
                <th className="py-3 px-3 w-10 text-center text-slate-400 font-medium">#</th>
                {['Task Name', 'Owner', 'Start Date', 'End Date', 'Duration', '% Complete', 'Status'].map((h) => <th key={h} className="py-3 px-4"><div className="flex items-center gap-1.5"><span>{h}</span><ArrowUpDown className="w-3 h-3 text-slate-300" /></div></th>)}
                <th className="py-3 px-4 text-right pr-6 w-32">Actions</th></tr></thead>
              <tbody className="divide-y divide-slate-100">
                {Object.entries(groups).map(([ph, pts]) => { const st = PHASE_COLORS[ph] || PHASE_COLORS.Execution; const done = pts.filter((t) => t.status === 'Completed').length; const avg = Math.round(pts.reduce((a, t) => a + t.percentComplete, 0) / pts.length * 100);
                  return (<React.Fragment key={ph}>
                    <tr className="bg-slate-100/70 border-y border-slate-200/80 font-semibold text-slate-800"><td colSpan={10} className="py-2.5 px-3"><div className="flex items-center justify-between">
                      <span className="flex items-center gap-2"><ChevronDown className="w-4 h-4 text-slate-500" /><span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-xs border ${st.bg}`}><span className={`w-1.5 h-1.5 rounded-full ${st.dot}`} /><span className="font-bold">{ph}</span></span><span className="text-xs text-slate-500 font-normal">({pts.length} tasks)</span></span>
                      <div className="flex items-center gap-4 text-xs font-normal text-slate-500 pr-2"><span>Done: <strong className="text-slate-700">{done}/{pts.length}</strong></span><div className="flex items-center gap-2"><div className="w-20 bg-slate-200 h-1.5 rounded-full overflow-hidden"><div className="bg-blue-600 h-full rounded-full" style={{ width: `${avg}%` }} /></div><span className="font-semibold text-slate-700 text-[11px] w-8 text-right">{avg}%</span></div></div>
                    </div></td></tr>
                    {pts.map((t, i) => { const od = t.endDate && t.endDate < new Date() && t.status !== 'Completed'; const p = Math.round(t.percentComplete * 100);
                      return (<tr key={t.id} className="hover:bg-slate-50/90 group">
                        <td className="py-2.5 px-3 text-center text-slate-400 font-mono text-[11px]">{i + 1}</td>
                        <td className="py-2.5 px-4"><button className="font-semibold text-slate-900 text-left">{t.taskName}</button></td>
                        <td className="py-2.5 px-4"><div className="flex items-center gap-2"><div className="w-6 h-6 rounded-full bg-blue-100 text-blue-700 font-bold text-[10px] flex items-center justify-center border border-blue-200 shrink-0">{getInitials(t.owner)}</div><span className="text-slate-700 truncate max-w-[130px]">{t.owner}</span></div></td>
                        <td className="py-2.5 px-4 font-mono text-slate-600 text-[11px] whitespace-nowrap">{t.startDateStr}</td>
                        <td className="py-2.5 px-4 font-mono text-[11px] whitespace-nowrap"><span className={od ? 'text-rose-600 font-bold' : 'text-slate-600'}>{t.endDateStr}</span></td>
                        <td className="py-2.5 px-4 whitespace-nowrap"><span className="inline-flex items-center gap-1 font-mono text-slate-700 bg-slate-100 px-2 py-0.5 rounded text-[11px] border border-slate-200">{t.duration} d</span></td>
                        <td className="py-2.5 px-4"><div className="flex items-center gap-2"><div className="w-16 bg-slate-200 h-2 rounded-full overflow-hidden shrink-0"><div className={`h-full rounded-full ${p === 100 ? 'bg-emerald-500' : 'bg-blue-600'}`} style={{ width: `${p}%` }} /></div><span className="font-mono text-slate-700 text-[11px] w-8 text-right font-medium">{p}%</span></div></td>
                        <td className="py-2.5 px-4"><select value={t.status} onChange={() => {}} className={`text-[11px] font-semibold px-2 py-0.5 rounded-full border ${badge(t.status)}`}><option>Not Started</option><option>In Progress</option><option>Completed</option><option>Blocked</option></select></td>
                        <td className="py-2.5 px-4 text-right pr-6"><div className="flex items-center justify-end gap-1 opacity-70">{[MoveUp, MoveDown, Edit2, Trash2].map((I, k) => <button key={k} className="p-1 rounded text-slate-400"><I className="w-3.5 h-3.5" /></button>)}</div></td>
                      </tr>); })}
                  </React.Fragment>); })}
              </tbody></table></div>
            <div className="px-4 py-3 bg-slate-50/80 border-t border-slate-200 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 gap-2"><div>Showing <span className="font-semibold text-slate-700">{tasks.length}</span> of <span className="font-semibold text-slate-700">{tasks.length}</span> total tasks</div>
              <div className="flex items-center gap-2 text-[11px] text-slate-400"><Info className="w-3.5 h-3.5 text-slate-400" /><span>Duration is calculated as End Date - Start Date + 1 days</span></div></div>
          </div>)}
      </div>

      {modal && (<div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4">
        <div className="bg-white rounded-xl shadow-xl max-w-lg w-full border border-slate-200 overflow-hidden">
          <div className="px-5 py-4 border-b border-slate-100 flex items-center justify-between bg-slate-50/70"><div className="flex items-center gap-2"><div className="p-1.5 rounded-md bg-blue-50 text-blue-600">{modal.mode === 'create' ? <Plus className="w-4 h-4" /> : <Edit2 className="w-4 h-4" />}</div><h3 className="font-bold text-sm text-slate-900">{modal.mode === 'create' ? 'Create New Task' : 'Edit Task Details'}</h3></div><button onClick={() => setModal(null)} className="text-slate-400 p-1"><X className="w-4 h-4" /></button></div>
          <form className="p-5 space-y-4">
            <div><label className="block text-xs font-semibold text-slate-700 mb-1">Task Name <span className="text-rose-500">*</span></label><input defaultValue={modal.v.taskName} className={inp} /></div>
            <div className="grid grid-cols-2 gap-3"><div><label className="block text-xs font-semibold text-slate-700 mb-1">Phase <span className="text-rose-500">*</span></label><input defaultValue={modal.v.phase} className={inp} /></div><div><label className="block text-xs font-semibold text-slate-700 mb-1">Owner</label><input defaultValue={modal.v.owner} className={inp} /></div></div>
            <div className="grid grid-cols-2 gap-3"><div><label className="block text-xs font-semibold text-slate-700 mb-1">Start Date</label><input type="date" defaultValue={modal.v.startDate} className={inp} /></div><div><label className="block text-xs font-semibold text-slate-700 mb-1">End Date</label><input type="date" defaultValue={modal.v.endDate} className={inp} /></div></div>
            <div className="grid grid-cols-2 gap-3 items-center"><div><label className="block text-xs font-semibold text-slate-700 mb-1">Status</label><select defaultValue={modal.v.status} className={inp + ' bg-white'}><option>Not Started</option><option>In Progress</option><option>Completed</option><option>Blocked</option></select></div>
              <div><div className="flex items-center justify-between mb-1"><label className="text-xs font-semibold text-slate-700">Completion</label><span className="text-xs font-bold text-blue-600">{modal.v.pct}%</span></div><input type="range" min="0" max="100" step="5" defaultValue={modal.v.pct} className="w-full accent-blue-600" /></div></div>
            <div className="bg-slate-50 border border-slate-200 rounded-lg p-3 text-[11px] text-slate-500 flex items-start gap-2"><Info className="w-4 h-4 text-slate-400 shrink-0 mt-0.5" /><span>The <strong>Duration</strong> field is formula-driven in the spreadsheet (<code className="bg-slate-200/70 px-1 py-0.5 rounded text-[10px] text-slate-700">=End - Start + 1</code>). Google Sheets will compute this value automatically.</span></div>
            <div className="pt-2 flex items-center justify-end gap-2 border-t border-slate-100"><button type="button" onClick={() => setModal(null)} className="px-3.5 py-2 border border-slate-300 rounded-lg text-xs font-medium text-slate-700">Cancel</button><button type="button" className="px-4 py-2 bg-blue-600 text-white rounded-lg text-xs font-semibold shadow-xs">{modal.mode === 'create' ? 'Create Task' : 'Save Changes'}</button></div>
          </form></div></div>)}
    </div>
  );
}
