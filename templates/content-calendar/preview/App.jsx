import React, { useState, useMemo } from 'react';
import ReactDOM from 'react-dom';
import * as dndKit from '@dnd-kit/core';
import {
  Calendar as CalendarIcon, Kanban as KanbanIcon, Table as TableIcon, BarChart3, Plus, Search, Filter, Trash2, Edit3,
  ExternalLink, ChevronLeft, ChevronRight, CheckCircle2, Clock, FileText, User, Check, X, AlertTriangle, TrendingUp,
  Tag, Layers, ArrowUpDown, Sparkles, GripVertical
} from 'lucide-react';

const STATUS_CONFIG = {
  Published: { bg: 'bg-emerald-50', text: 'text-emerald-700', border: 'border-emerald-200', dot: 'bg-emerald-500', bar: 'bg-emerald-500', headerBg: 'bg-emerald-100/70', label: 'Published' },
  Scheduled: { bg: 'bg-indigo-50', text: 'text-indigo-700', border: 'border-indigo-200', dot: 'bg-indigo-500', bar: 'bg-indigo-500', headerBg: 'bg-indigo-100/70', label: 'Scheduled' },
  'In Progress': { bg: 'bg-amber-50', text: 'text-amber-800', border: 'border-amber-200', dot: 'bg-amber-500', bar: 'bg-amber-500', headerBg: 'bg-amber-100/70', label: 'In Progress' },
  Review: { bg: 'bg-purple-50', text: 'text-purple-700', border: 'border-purple-200', dot: 'bg-purple-500', bar: 'bg-purple-500', headerBg: 'bg-purple-100/70', label: 'Review' },
  Draft: { bg: 'bg-slate-100', text: 'text-slate-700', border: 'border-slate-200', dot: 'bg-slate-400', bar: 'bg-slate-400', headerBg: 'bg-slate-200/70', label: 'Draft' }
};
const CHANNEL_CONFIG = {
  Blog: { bg: 'bg-blue-50', text: 'text-blue-700', border: 'border-blue-200' },
  LinkedIn: { bg: 'bg-sky-50', text: 'text-sky-700', border: 'border-sky-200' },
  YouTube: { bg: 'bg-rose-50', text: 'text-rose-700', border: 'border-rose-200' },
  'Email Newsletter': { bg: 'bg-violet-50', text: 'text-violet-700', border: 'border-violet-200' },
  Instagram: { bg: 'bg-pink-50', text: 'text-pink-700', border: 'border-pink-200' }
};
const PILLAR_CONFIG = {
  'Thought Leadership': { bg: 'bg-indigo-50', text: 'text-indigo-700', border: 'border-indigo-200' },
  'Product Education': { bg: 'bg-cyan-50', text: 'text-cyan-800', border: 'border-cyan-200' },
  'Customer Stories': { bg: 'bg-emerald-50', text: 'text-emerald-800', border: 'border-emerald-200' },
  'Industry Trends': { bg: 'bg-orange-50', text: 'text-orange-800', border: 'border-orange-200' },
  'Brand Awareness': { bg: 'bg-fuchsia-50', text: 'text-fuchsia-800', border: 'border-fuchsia-200' }
};

function parseYMD(dateStr) {
  if (!dateStr || typeof dateStr !== 'string') return null;
  const parts = dateStr.trim().split('-');
  if (parts.length === 3) {
    const y = parseInt(parts[0], 10), m = parseInt(parts[1], 10), d = parseInt(parts[2], 10);
    if (!isNaN(y) && !isNaN(m) && !isNaN(d)) return new Date(y, m - 1, d);
  }
  return null;
}
function formatDisplayDate(dateStr) {
  const d = parseYMD(dateStr);
  if (!d) return dateStr || '—';
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}
function renderKpiValue(val, isPercentage = false) {
  if (val === null || val === undefined) return '—';
  if (typeof val === 'string') {
    if (val.startsWith('#') || val.toLowerCase().includes('error') || val.toLowerCase().includes('n/a')) return <span className="text-red-500 font-medium text-base">{val}</span>;
    const num = parseFloat(val);
    if (!isNaN(num)) return isPercentage ? `${(num * 100).toFixed(1)}%` : num.toLocaleString();
    return val;
  }
  if (typeof val === 'number') {
    if (isNaN(val)) return '—';
    return isPercentage ? `${(val * 100).toFixed(1)}%` : val.toLocaleString();
  }
  return String(val);
}

function KanbanDroppableColumn({ status, count, onAddStatus, children }) {
  const { setNodeRef, isOver } = dndKit.useDroppable({ id: `column-${status}` });
  const conf = STATUS_CONFIG[status] || STATUS_CONFIG.Draft;
  return (
    <div ref={setNodeRef} className={`flex flex-col bg-slate-50/80 rounded-xl border flex-1 min-w-[260px] transition-all p-3 ${isOver ? 'border-indigo-400 bg-indigo-50/50 ring-2 ring-indigo-200 shadow-sm' : 'border-slate-200'}`}>
      <div className="flex items-center justify-between pb-3 border-b border-slate-200/80 mb-3">
        <div className="flex items-center gap-2">
          <span className={`w-2.5 h-2.5 rounded-full ${conf.dot}`} />
          <h4 className="font-semibold text-sm text-slate-800 tracking-tight">{status}</h4>
          <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-slate-200/70 text-slate-700">{count}</span>
        </div>
        <button type="button" onClick={() => onAddStatus(status)} className="text-slate-400 hover:text-indigo-600 hover:bg-white rounded-md p-1 transition-colors" title={`Add item to ${status}`}>
          <Plus className="w-4 h-4" />
        </button>
      </div>
      <div className="flex flex-col gap-2.5 flex-1 min-h-[140px] overflow-y-auto">
        {children}
        {count === 0 && (
          <div className="flex flex-col items-center justify-center flex-1 border-2 border-dashed border-slate-200 rounded-lg p-6 text-slate-400 text-xs">
            <span>No content in {status}</span>
            <span className="text-[11px] text-slate-400 mt-1">Drag cards here</span>
          </div>
        )}
      </div>
    </div>
  );
}

function KanbanCardInner({ item, colMap, onEdit, onDelete, onStatusChange, followLink, isOverlay = false }) {
  const row = item.row;
  const title = row[colMap.title] || 'Untitled';
  const pillar = row[colMap.pillar];
  const channel = row[colMap.channel];
  const date = row[colMap.date];
  const status = row[colMap.status] || 'Draft';
  const owner = row[colMap.owner];
  const reviewer = row[colMap.reviewer];
  const link = row[colMap.link];
  const notes = row[colMap.notes];
  const statusConf = STATUS_CONFIG[status] || STATUS_CONFIG.Draft;
  const channelConf = CHANNEL_CONFIG[channel] || { bg: 'bg-slate-50', text: 'text-slate-700', border: 'border-slate-200' };
  const pillarConf = PILLAR_CONFIG[pillar] || { bg: 'bg-slate-50', text: 'text-slate-700', border: 'border-slate-200' };
  return (
    <div className={`bg-white rounded-lg border border-slate-200/90 p-3.5 shadow-sm transition-all group ${isOverlay ? 'shadow-2xl border-indigo-400 ring-2 ring-indigo-300' : 'hover:shadow-md'}`}>
      <div className="flex items-start justify-between gap-2 mb-2">
        <div className="flex flex-wrap items-center gap-1.5">
          {pillar && <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${pillarConf.bg} ${pillarConf.text} ${pillarConf.border}`}>{pillar}</span>}
          {channel && <span className={`text-[10px] font-medium px-2 py-0.5 rounded-full border ${channelConf.bg} ${channelConf.text} ${channelConf.border}`}>{channel}</span>}
        </div>
        <div className="flex items-center gap-1">
          <div className="cursor-grab active:cursor-grabbing text-slate-400 hover:text-slate-600 p-0.5" title="Drag card between columns"><GripVertical className="w-3.5 h-3.5" /></div>
          {!isOverlay && onEdit && (
            <button type="button" onPointerDown={(e) => e.stopPropagation()} onClick={(e) => { e.stopPropagation(); onEdit(item); }} className="text-slate-400 hover:text-indigo-600 p-1 rounded hover:bg-slate-50 transition-colors" title="Edit item"><Edit3 className="w-3.5 h-3.5" /></button>
          )}
          {!isOverlay && onDelete && (
            <button type="button" onPointerDown={(e) => e.stopPropagation()} onClick={(e) => { e.stopPropagation(); onDelete(item); }} className="text-slate-400 hover:text-rose-600 p-1 rounded hover:bg-slate-50 transition-colors" title="Delete item"><Trash2 className="w-3.5 h-3.5" /></button>
          )}
        </div>
      </div>
      <h5 className="font-medium text-sm text-slate-900 leading-snug mb-1.5">{title}</h5>
      {notes && <p className="text-xs text-slate-500 line-clamp-2 mb-2.5 leading-relaxed">{notes}</p>}
      <div className="flex items-center justify-between pt-2 border-t border-slate-100 text-xs text-slate-600">
        <div className="flex items-center gap-1 text-[11px] text-slate-500 font-medium"><Clock className="w-3.5 h-3.5 text-slate-400" /><span>{formatDisplayDate(date)}</span></div>
        <div className="flex items-center gap-1.5">
          {owner && <span className="w-5 h-5 rounded-full bg-slate-100 text-slate-700 text-[10px] font-bold flex items-center justify-center border border-slate-200" title={`Owner: ${owner}${reviewer ? ` | Reviewer: ${reviewer}` : ''}`}>{owner.charAt(0)}</span>}
          {link && link !== '[link removed]' && (
            <button type="button" onPointerDown={(e) => e.stopPropagation()} onClick={(e) => { e.stopPropagation(); followLink(link); }} className="text-indigo-600 hover:text-indigo-800 p-0.5 rounded" title="Open asset link"><ExternalLink className="w-3.5 h-3.5" /></button>
          )}
          {!isOverlay ? (
            <select value={status} onPointerDown={(e) => e.stopPropagation()} onChange={(e) => onStatusChange(item.index_, e.target.value)} className={`text-[10px] font-semibold rounded px-1.5 py-0.5 border cursor-pointer ${statusConf.bg} ${statusConf.text} ${statusConf.border} focus:outline-none`}>
              <option value="Draft">Draft</option><option value="In Progress">In Progress</option><option value="Review">Review</option><option value="Scheduled">Scheduled</option><option value="Published">Published</option>
            </select>
          ) : (
            <span className={`text-[10px] font-semibold rounded px-1.5 py-0.5 border ${statusConf.bg} ${statusConf.text} ${statusConf.border}`}>{status}</span>
          )}
        </div>
      </div>
    </div>
  );
}

function KanbanDraggableCard({ item, colMap, onEdit, onDelete, onStatusChange, followLink }) {
  const { attributes, listeners, setNodeRef, isDragging } = dndKit.useDraggable({ id: item.index_ });
  return (
    <div ref={setNodeRef} {...attributes} {...listeners} className={`touch-none cursor-grab active:cursor-grabbing transition-opacity ${isDragging ? 'opacity-30' : ''}`}>
      <KanbanCardInner item={item} colMap={colMap} onEdit={onEdit} onDelete={onDelete} onStatusChange={onStatusChange} followLink={followLink} />
    </div>
  );
}

export default function App({ data, updateItem, deleteItem, insertItem, moveItem, followLink }) {
  const sheetData = data?.[0]?.data || [];
  const titleText = sheetData[0]?.row?.[0] || 'Marketing Content Calendar';
  const subtitleText = sheetData[1]?.row?.[0] || 'Multi-Channel Editorial Roadmap & Campaign Publication Schedule';
  const kpiHeaderItem = useMemo(() => sheetData.find((item) => Array.isArray(item.row) && item.row.some((c) => typeof c === 'string' && c.includes('TOTAL CONTENT'))), [sheetData]);
  const kpiValueItem = useMemo(() => (kpiHeaderItem ? sheetData.find((item) => item.index_ === kpiHeaderItem.index_ + 1) : null), [sheetData, kpiHeaderItem]);
  const headerRowObj = useMemo(() => sheetData.find((item) => Array.isArray(item.row) && item.row.includes('Content Title')) || sheetData[5], [sheetData]);
  const headerRowIndex = headerRowObj?.index_ ?? 5;
  const headers = headerRowObj?.row || [];
  const colMap = useMemo(() => {
    const findCol = (name, fallback) => { const idx = headers.indexOf(name); return idx !== -1 ? idx : fallback; };
    return { title: findCol('Content Title', 0), pillar: findCol('Content Pillar', 1), channel: findCol('Channel', 2), format: findCol('Format', 3), date: findCol('Target Date', 4), audience: findCol('Target Audience', 5), status: findCol('Status', 6), owner: findCol('Owner', 7), reviewer: findCol('Reviewer', 8), link: findCol('Asset Link', 9), notes: findCol('Notes', 10) };
  }, [headers]);
  const contentRows = useMemo(() => sheetData.filter((item) => item.index_ > headerRowIndex && Array.isArray(item.row) && item.row.some((cell) => cell !== null && cell !== undefined && cell !== '')), [sheetData, headerRowIndex]);

  const [activeTab, setActiveTab] = useState('kanban');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedPillar, setSelectedPillar] = useState('ALL');
  const [selectedChannel, setSelectedChannel] = useState('ALL');
  const [selectedStatus, setSelectedStatus] = useState('ALL');
  const [selectedOwner, setSelectedOwner] = useState('ALL');
  const [sortCol, setSortCol] = useState('date');
  const [sortAsc, setSortAsc] = useState(true);
  const [currentYear, setCurrentYear] = useState(2026);
  const [currentMonth, setCurrentMonth] = useState(10);
  const [modalMode, setModalMode] = useState(null);
  const [editingItem, setEditingItem] = useState(null);
  const [deletingItem, setDeletingItem] = useState(null);
  const [formData, setFormData] = useState({ title: '', pillar: 'Thought Leadership', channel: 'Blog', format: 'Long-form Guide', date: '2026-11-15', audience: '', status: 'Draft', owner: '', reviewer: '', link: '', notes: '' });

  const uniq = (key) => { const s = new Set(); contentRows.forEach((r) => { if (r.row[colMap[key]]) s.add(r.row[colMap[key]]); }); return Array.from(s); };
  const uniquePillars = useMemo(() => uniq('pillar'), [contentRows, colMap]);
  const uniqueChannels = useMemo(() => uniq('channel'), [contentRows, colMap]);
  const uniqueOwners = useMemo(() => uniq('owner'), [contentRows, colMap]);

  const filteredRows = useMemo(() => contentRows.filter((item) => {
    const row = item.row;
    const title = String(row[colMap.title] || '').toLowerCase(), notes = String(row[colMap.notes] || '').toLowerCase(), audience = String(row[colMap.audience] || '').toLowerCase(), owner = String(row[colMap.owner] || '').toLowerCase(), reviewer = String(row[colMap.reviewer] || '').toLowerCase();
    const pillar = row[colMap.pillar] || '', channel = row[colMap.channel] || '', status = row[colMap.status] || '';
    if (searchQuery.trim()) { const q = searchQuery.toLowerCase().trim(); if (!(title.includes(q) || notes.includes(q) || audience.includes(q) || owner.includes(q) || reviewer.includes(q))) return false; }
    if (selectedPillar !== 'ALL' && pillar !== selectedPillar) return false;
    if (selectedChannel !== 'ALL' && channel !== selectedChannel) return false;
    if (selectedStatus !== 'ALL' && status !== selectedStatus) return false;
    if (selectedOwner !== 'ALL' && owner !== selectedOwner.toLowerCase()) return false;
    return true;
  }), [contentRows, colMap, searchQuery, selectedPillar, selectedChannel, selectedStatus, selectedOwner]);

  const sortedTableRows = useMemo(() => {
    const list = [...filteredRows];
    list.sort((a, b) => {
      let valA = a.row[colMap[sortCol]] || '', valB = b.row[colMap[sortCol]] || '';
      if (sortCol === 'date') { const da = parseYMD(valA)?.getTime() || 0, db = parseYMD(valB)?.getTime() || 0; return sortAsc ? da - db : db - da; }
      if (typeof valA === 'string') valA = valA.toLowerCase(); if (typeof valB === 'string') valB = valB.toLowerCase();
      if (valA < valB) return sortAsc ? -1 : 1; if (valA > valB) return sortAsc ? 1 : -1; return 0;
    });
    return list;
  }, [filteredRows, colMap, sortCol, sortAsc]);

  const [activeDragId, setActiveDragId] = useState(null);
  const activeDragItem = useMemo(() => (activeDragId === null || activeDragId === undefined ? null : contentRows.find((r) => r.index_ === activeDragId) || null), [activeDragId, contentRows]);
  const sensors = dndKit.useSensors(dndKit.useSensor(dndKit.PointerSensor, { activationConstraint: { distance: 5 } }));
  const collisionDetectionStrategy = (args) => { const p = dndKit.pointerWithin(args); return p && p.length > 0 ? p : dndKit.rectIntersection(args); };
  const handleDragStart = (event) => setActiveDragId(event.active.id);
  const handleDragEnd = (event) => {
    const { active, over } = event; setActiveDragId(null); if (!over) return;
    let targetStatus = null;
    if (typeof over.id === 'string' && over.id.startsWith('column-')) targetStatus = over.id.replace('column-', '');
    if (targetStatus) { const a = contentRows.find((r) => r.index_ === active.id); if (a && (a.row[colMap.status] || 'Draft') !== targetStatus) handleQuickStatusChange(active.id, targetStatus); }
  };
  const handleDragCancel = () => setActiveDragId(null);
  const handleQuickStatusChange = (rowIndex, newStatus) => { const u = Array(11).fill(undefined); u[colMap.status] = newStatus; updateItem(0, rowIndex, u); };
  const openAddModal = (defaultStatus = 'Draft', defaultDate = '') => {
    setFormData({ title: '', pillar: 'Thought Leadership', channel: 'Blog', format: 'Long-form Guide', date: defaultDate || '2026-11-20', audience: '', status: defaultStatus, owner: '', reviewer: '', link: '', notes: '' });
    setModalMode('add'); setEditingItem(null);
  };
  const openEditModal = (item) => {
    const row = item.row;
    setFormData({ title: row[colMap.title] || '', pillar: row[colMap.pillar] || 'Thought Leadership', channel: row[colMap.channel] || 'Blog', format: row[colMap.format] || 'Long-form Guide', date: row[colMap.date] || '', audience: row[colMap.audience] || '', status: row[colMap.status] || 'Draft', owner: row[colMap.owner] || '', reviewer: row[colMap.reviewer] || '', link: row[colMap.link] || '', notes: row[colMap.notes] || '' });
    setEditingItem(item); setModalMode('edit');
  };
  const handleFormSubmit = (e) => {
    e.preventDefault(); if (!formData.title.trim()) return;
    const p = [formData.title.trim(), formData.pillar, formData.channel, formData.format, formData.date, formData.audience, formData.status, formData.owner, formData.reviewer, formData.link, formData.notes];
    if (modalMode === 'add') insertItem(0, undefined, p); else if (modalMode === 'edit' && editingItem) updateItem(0, editingItem.index_, p);
    setModalMode(null); setEditingItem(null);
  };
  const confirmDelete = () => { if (deletingItem) { deleteItem(0, deletingItem.index_); setDeletingItem(null); } };

  const calendarDays = useMemo(() => {
    const firstDay = new Date(currentYear, currentMonth, 1);
    const startDayOfWeek = firstDay.getDay();
    const daysInMonth = new Date(currentYear, currentMonth + 1, 0).getDate();
    const daysInPrevMonth = new Date(currentYear, currentMonth, 0).getDate();
    const cells = [];
    for (let i = startDayOfWeek - 1; i >= 0; i--) { const d = daysInPrevMonth - i; const mm = String(currentMonth === 0 ? 12 : currentMonth).padStart(2, '0'); const yy = currentMonth === 0 ? currentYear - 1 : currentYear; cells.push({ day: d, isCurrentMonth: false, dateStr: `${yy}-${mm}-${String(d).padStart(2, '0')}` }); }
    for (let d = 1; d <= daysInMonth; d++) { const mm = String(currentMonth + 1).padStart(2, '0'); cells.push({ day: d, isCurrentMonth: true, dateStr: `${currentYear}-${mm}-${String(d).padStart(2, '0')}` }); }
    const remainder = cells.length % 7;
    if (remainder > 0) { for (let d = 1; d <= 7 - remainder; d++) { const mm = String(currentMonth + 2 > 12 ? 1 : currentMonth + 2).padStart(2, '0'); const yy = currentMonth + 1 >= 12 ? currentYear + 1 : currentYear; cells.push({ day: d, isCurrentMonth: false, dateStr: `${yy}-${mm}-${String(d).padStart(2, '0')}` }); } }
    return cells;
  }, [currentYear, currentMonth]);
  const monthNames = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
  const STATUSES = ['Draft', 'In Progress', 'Review', 'Scheduled', 'Published'];
  const tabBtn = (key, Icon, label) => (
    <button type="button" onClick={() => setActiveTab(key)} className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md transition-all ${activeTab === key ? 'bg-white text-indigo-600 shadow-xs font-semibold' : 'text-slate-600 hover:text-slate-900'}`}>
      <Icon className="w-3.5 h-3.5" /><span>{label}</span>
    </button>
  );
  const kpi = (Icon, tint, label, val, pct) => (
    <div className="bg-white border border-slate-200/80 rounded-lg p-2.5 shadow-xs flex items-center gap-3">
      <div className={`w-8 h-8 rounded-lg ${tint} flex items-center justify-center flex-shrink-0`}><Icon className="w-4 h-4" /></div>
      <div><div className="text-[10px] font-bold uppercase tracking-wider text-slate-400">{label}</div><div className="text-lg font-bold text-slate-900 leading-tight">{renderKpiValue(val, pct)}</div></div>
    </div>
  );
  const selectCls = 'bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 text-xs text-slate-700 focus:outline-none focus:ring-1 focus:ring-indigo-500';
  const inputCls = 'w-full px-3 py-2 bg-white border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-indigo-500';

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col font-sans">
      <header className="bg-white border-b border-slate-200/90 sticky top-0 z-30 shadow-xs">
        <div className="w-full px-6 py-3.5 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-600 flex items-center justify-center text-white shadow-sm flex-shrink-0"><CalendarIcon className="w-5 h-5" /></div>
            <div><h1 className="text-xl font-bold tracking-tight text-slate-900 leading-tight">{titleText}</h1><p className="text-xs text-slate-500 font-medium">{subtitleText}</p></div>
          </div>
          <div className="flex items-center gap-3 self-end md:self-auto">
            <div className="inline-flex rounded-lg bg-slate-100 p-1 border border-slate-200/80 text-xs font-medium">
              {tabBtn('kanban', KanbanIcon, 'Kanban')}{tabBtn('calendar', CalendarIcon, 'Calendar')}{tabBtn('table', TableIcon, 'Table')}{tabBtn('insights', BarChart3, 'Insights')}
            </div>
            <button type="button" onClick={() => openAddModal()} className="inline-flex items-center gap-1.5 px-3.5 py-1.5 text-xs font-semibold rounded-lg bg-indigo-600 text-white hover:bg-indigo-700 shadow-xs transition-colors"><Plus className="w-4 h-4" /><span>New Content</span></button>
          </div>
        </div>
        {kpiValueItem && (
          <div className="bg-slate-50/70 border-t border-slate-200/80 px-6 py-2.5">
            <div className="w-full grid grid-cols-2 sm:grid-cols-4 gap-3">
              {kpi(FileText, 'bg-blue-50 text-blue-600', 'TOTAL CONTENT', kpiValueItem.row[0])}
              {kpi(Clock, 'bg-amber-50 text-amber-600', 'IN PROGRESS', kpiValueItem.row[2])}
              {kpi(CheckCircle2, 'bg-emerald-50 text-emerald-600', 'SCHEDULED / PUBLISHED', kpiValueItem.row[4])}
              {kpi(TrendingUp, 'bg-purple-50 text-purple-600', 'READY RATE', kpiValueItem.row[6], true)}
            </div>
          </div>
        )}
      </header>

      <div className="w-full px-6 pt-4 pb-2">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-3 bg-white p-2.5 rounded-xl border border-slate-200/90 shadow-2xs">
          <div className="flex items-center gap-2 flex-1 min-w-[240px]">
            <div className="relative flex-1">
              <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input type="text" value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} placeholder="Search title, notes, audience, owner..." className="w-full pl-9 pr-3 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-xs focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:bg-white transition-all placeholder:text-slate-400" />
              {searchQuery && <button type="button" onClick={() => setSearchQuery('')} className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"><X className="w-3.5 h-3.5" /></button>}
            </div>
          </div>
          <div className="flex flex-wrap items-center gap-2 text-xs">
            <div className="flex items-center gap-1.5 text-slate-400"><Filter className="w-3.5 h-3.5" /><span className="text-[11px] font-medium hidden sm:inline">Filters:</span></div>
            <select value={selectedPillar} onChange={(e) => setSelectedPillar(e.target.value)} className={selectCls}><option value="ALL">All Pillars</option>{uniquePillars.map((p) => <option key={p} value={p}>{p}</option>)}</select>
            <select value={selectedChannel} onChange={(e) => setSelectedChannel(e.target.value)} className={selectCls}><option value="ALL">All Channels</option>{uniqueChannels.map((c) => <option key={c} value={c}>{c}</option>)}</select>
            {activeTab !== 'kanban' && <select value={selectedStatus} onChange={(e) => setSelectedStatus(e.target.value)} className={selectCls}><option value="ALL">All Statuses</option>{Object.keys(STATUS_CONFIG).map((s) => <option key={s} value={s}>{s}</option>)}</select>}
            <select value={selectedOwner} onChange={(e) => setSelectedOwner(e.target.value)} className={selectCls}><option value="ALL">All Owners</option>{uniqueOwners.map((o) => <option key={o} value={o}>{o}</option>)}</select>
          </div>
        </div>
      </div>

      <main className="w-full px-6 py-3 flex-1 flex flex-col">
        {activeTab === 'kanban' && (
          <dndKit.DndContext sensors={sensors} collisionDetection={collisionDetectionStrategy} onDragStart={handleDragStart} onDragEnd={handleDragEnd} onDragCancel={handleDragCancel}>
            <div className="flex gap-4 overflow-x-auto pb-4 pt-1 flex-1 w-full items-start">
              {STATUSES.map((statusKey) => {
                const columnItems = filteredRows.filter((r) => (r.row[colMap.status] || 'Draft') === statusKey);
                return (
                  <KanbanDroppableColumn key={statusKey} status={statusKey} count={columnItems.length} onAddStatus={openAddModal}>
                    {columnItems.map((item) => <KanbanDraggableCard key={item.index_} item={item} colMap={colMap} onEdit={openEditModal} onDelete={(it) => setDeletingItem(it)} onStatusChange={handleQuickStatusChange} followLink={followLink} />)}
                  </KanbanDroppableColumn>
                );
              })}
            </div>
            {typeof document !== 'undefined' && ReactDOM.createPortal(
              <dndKit.DragOverlay dropAnimation={null}>
                {activeDragItem ? <div className="w-[280px] sm:w-[320px] pointer-events-none shadow-2xl rounded-lg rotate-1 opacity-95"><KanbanCardInner item={activeDragItem} colMap={colMap} followLink={followLink} isOverlay /></div> : null}
              </dndKit.DragOverlay>, document.body)}
          </dndKit.DndContext>
        )}

        {activeTab === 'calendar' && (
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm flex flex-col flex-1 p-4">
            <div className="flex items-center justify-between pb-4 border-b border-slate-100">
              <div className="flex items-center gap-3">
                <h3 className="text-base font-bold text-slate-900">{monthNames[currentMonth]} {currentYear}</h3>
                <span className="text-xs text-slate-500 font-medium bg-slate-100 px-2 py-0.5 rounded-full">{filteredRows.filter((r) => { const d = parseYMD(r.row[colMap.date]); return d && d.getFullYear() === currentYear && d.getMonth() === currentMonth; }).length} scheduled</span>
              </div>
              <div className="flex items-center gap-1.5">
                <button type="button" onClick={() => { if (currentMonth === 0) { setCurrentMonth(11); setCurrentYear((y) => y - 1); } else setCurrentMonth((m) => m - 1); }} className="p-1.5 text-slate-500 hover:text-slate-800 hover:bg-slate-100 rounded-lg border border-slate-200"><ChevronLeft className="w-4 h-4" /></button>
                <button type="button" onClick={() => { setCurrentMonth(10); setCurrentYear(2026); }} className="px-2.5 py-1 text-xs font-medium text-slate-600 hover:bg-slate-100 rounded-lg border border-slate-200">November 2026</button>
                <button type="button" onClick={() => { if (currentMonth === 11) { setCurrentMonth(0); setCurrentYear((y) => y + 1); } else setCurrentMonth((m) => m + 1); }} className="p-1.5 text-slate-500 hover:text-slate-800 hover:bg-slate-100 rounded-lg border border-slate-200"><ChevronRight className="w-4 h-4" /></button>
              </div>
            </div>
            <div className="grid grid-cols-7 border-b border-slate-200 text-center py-2 text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
              <div>Sun</div><div>Mon</div><div>Tue</div><div>Wed</div><div>Thu</div><div>Fri</div><div>Sat</div>
            </div>
            <div className="grid grid-cols-7 gap-px bg-slate-200 flex-1 min-h-[500px]">
              {calendarDays.map((cell, idx) => {
                const cellItems = filteredRows.filter((r) => r.row[colMap.date] === cell.dateStr);
                return (
                  <div key={idx} className={`bg-white p-2 flex flex-col min-h-[96px] transition-colors relative group ${!cell.isCurrentMonth ? 'bg-slate-50/50 text-slate-400' : 'text-slate-800'}`}>
                    <div className="flex items-center justify-between mb-1">
                      <span className={`text-xs font-semibold ${cell.isCurrentMonth ? 'text-slate-800' : 'text-slate-400'}`}>{cell.day}</span>
                      <button type="button" onClick={() => openAddModal('Draft', cell.dateStr)} className="opacity-0 group-hover:opacity-100 p-0.5 text-slate-400 hover:text-indigo-600 rounded hover:bg-slate-100 transition-opacity"><Plus className="w-3 h-3" /></button>
                    </div>
                    <div className="flex flex-col gap-1 overflow-y-auto max-h-[90px]">
                      {cellItems.map((item) => {
                        const status = item.row[colMap.status] || 'Draft'; const sc = STATUS_CONFIG[status] || STATUS_CONFIG.Draft; const title = item.row[colMap.title] || 'Untitled';
                        return <div key={item.index_} onClick={() => openEditModal(item)} className={`p-1 rounded border text-[11px] font-medium leading-tight cursor-pointer hover:shadow-xs transition-shadow flex items-center justify-between gap-1 ${sc.bg} ${sc.text} ${sc.border}`}><span className="truncate">{title}</span><span className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${sc.dot}`} /></div>;
                      })}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {activeTab === 'table' && (
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm flex flex-col flex-1 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="bg-slate-50 border-b border-slate-200 text-slate-600 font-semibold select-none">
                    <th className="py-3 px-4"><div className="flex items-center gap-1.5"><span>Content Title</span><ArrowUpDown className="w-3 h-3 text-slate-400" /></div></th>
                    <th className="py-3 px-3">Pillar</th><th className="py-3 px-3">Channel</th><th className="py-3 px-3">Format</th>
                    <th className="py-3 px-3"><div className="flex items-center gap-1.5"><span>Target Date</span><ArrowUpDown className="w-3 h-3 text-slate-400" /></div></th>
                    <th className="py-3 px-3">Audience</th><th className="py-3 px-3">Status</th><th className="py-3 px-3">Owner</th><th className="py-3 px-3">Reviewer</th><th className="py-3 px-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {sortedTableRows.map((item) => {
                    const row = item.row; const status = row[colMap.status] || 'Draft'; const sc = STATUS_CONFIG[status] || STATUS_CONFIG.Draft;
                    const pillar = row[colMap.pillar], channel = row[colMap.channel];
                    const cc = CHANNEL_CONFIG[channel] || { bg: 'bg-slate-50', text: 'text-slate-700', border: 'border-slate-200' };
                    const pc = PILLAR_CONFIG[pillar] || { bg: 'bg-slate-50', text: 'text-slate-700', border: 'border-slate-200' };
                    return (
                      <tr key={item.index_} className="hover:bg-slate-50/80 transition-colors group">
                        <td className="py-3 px-4 max-w-xs"><div className="font-semibold text-slate-900 leading-snug">{row[colMap.title] || '—'}</div>{row[colMap.notes] && <div className="text-[11px] text-slate-400 line-clamp-1 mt-0.5">{row[colMap.notes]}</div>}</td>
                        <td className="py-3 px-3 whitespace-nowrap">{pillar ? <span className={`px-2 py-0.5 rounded-full border text-[10px] font-semibold ${pc.bg} ${pc.text} ${pc.border}`}>{pillar}</span> : '—'}</td>
                        <td className="py-3 px-3 whitespace-nowrap">{channel ? <span className={`px-2 py-0.5 rounded-full border text-[10px] font-medium ${cc.bg} ${cc.text} ${cc.border}`}>{channel}</span> : '—'}</td>
                        <td className="py-3 px-3 whitespace-nowrap text-slate-600">{row[colMap.format] || '—'}</td>
                        <td className="py-3 px-3 whitespace-nowrap font-medium text-slate-700">{formatDisplayDate(row[colMap.date])}</td>
                        <td className="py-3 px-3 text-slate-600 max-w-[160px] truncate">{row[colMap.audience] || '—'}</td>
                        <td className="py-3 px-3 whitespace-nowrap"><select value={status} onChange={(e) => handleQuickStatusChange(item.index_, e.target.value)} className={`text-[11px] font-semibold rounded-lg px-2 py-1 border cursor-pointer ${sc.bg} ${sc.text} ${sc.border} focus:outline-none`}>{STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}</select></td>
                        <td className="py-3 px-3 whitespace-nowrap text-slate-700">{row[colMap.owner] || '—'}</td>
                        <td className="py-3 px-3 whitespace-nowrap text-slate-500">{row[colMap.reviewer] || '—'}</td>
                        <td className="py-3 px-4 text-right whitespace-nowrap"><div className="inline-flex items-center gap-1.5">
                          {row[colMap.link] && <button type="button" className="p-1 text-slate-400 hover:text-indigo-600 rounded hover:bg-slate-100"><ExternalLink className="w-3.5 h-3.5" /></button>}
                          <button type="button" onClick={() => openEditModal(item)} className="p-1 text-slate-400 hover:text-indigo-600 rounded hover:bg-slate-100"><Edit3 className="w-3.5 h-3.5" /></button>
                          <button type="button" onClick={() => setDeletingItem(item)} className="p-1 text-slate-400 hover:text-rose-600 rounded hover:bg-slate-100"><Trash2 className="w-3.5 h-3.5" /></button>
                        </div></td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
            <div className="p-3 bg-slate-50 border-t border-slate-200 text-xs text-slate-500 flex items-center justify-between"><span>Showing {sortedTableRows.length} of {contentRows.length} total entries</span><span className="text-[11px] text-slate-400">All edits sync dynamically with Google Sheets</span></div>
          </div>
        )}

        {activeTab === 'insights' && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 flex-1">
            <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col">
              <h3 className="font-bold text-sm text-slate-900 mb-1 flex items-center gap-2"><Tag className="w-4 h-4 text-indigo-600" /><span>Channel Distribution</span></h3>
              <p className="text-xs text-slate-500 mb-4">Volume of assets across media formats</p>
              <div className="space-y-3 flex-1">{uniqueChannels.map((chan) => { const count = contentRows.filter((r) => r.row[colMap.channel] === chan).length; const pct = contentRows.length ? (count / contentRows.length) * 100 : 0; return (
                <div key={chan} className="space-y-1"><div className="flex justify-between text-xs"><span className="font-medium text-slate-700">{chan}</span><span className="text-slate-500 font-semibold">{count} ({pct.toFixed(0)}%)</span></div><div className="w-full h-2 rounded-full bg-slate-100 overflow-hidden"><div className="h-full bg-indigo-500 rounded-full" style={{ width: `${pct}%` }} /></div></div>); })}</div>
            </div>
            <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col">
              <h3 className="font-bold text-sm text-slate-900 mb-1 flex items-center gap-2"><Layers className="w-4 h-4 text-purple-600" /><span>Content Pillar Distribution</span></h3>
              <p className="text-xs text-slate-500 mb-4">Alignment against core marketing pillars</p>
              <div className="space-y-3 flex-1">{uniquePillars.map((pil) => { const count = contentRows.filter((r) => r.row[colMap.pillar] === pil).length; const pct = contentRows.length ? (count / contentRows.length) * 100 : 0; return (
                <div key={pil} className="space-y-1"><div className="flex justify-between text-xs"><span className="font-medium text-slate-700">{pil}</span><span className="text-slate-500 font-semibold">{count} ({pct.toFixed(0)}%)</span></div><div className="w-full h-2 rounded-full bg-slate-100 overflow-hidden"><div className="h-full bg-purple-500 rounded-full" style={{ width: `${pct}%` }} /></div></div>); })}</div>
            </div>
            <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col">
              <h3 className="font-bold text-sm text-slate-900 mb-1 flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-emerald-600" /><span>Editorial Pipeline Funnel</span></h3>
              <p className="text-xs text-slate-500 mb-4">Lifecycle status breakdown</p>
              <div className="grid grid-cols-5 gap-2 text-center pt-2">{STATUSES.map((st) => { const count = contentRows.filter((r) => (r.row[colMap.status] || 'Draft') === st).length; const conf = STATUS_CONFIG[st]; return (
                <div key={st} className={`p-3 rounded-xl border ${conf.bg} ${conf.border} flex flex-col justify-center items-center`}><span className="text-xl font-bold text-slate-900">{count}</span><span className={`text-[11px] font-semibold mt-1 ${conf.text}`}>{st}</span></div>); })}</div>
            </div>
            <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col">
              <h3 className="font-bold text-sm text-slate-900 mb-1 flex items-center gap-2"><User className="w-4 h-4 text-blue-600" /><span>Content Ownership & Workload</span></h3>
              <p className="text-xs text-slate-500 mb-4">Total pieces assigned per creator</p>
              <div className="space-y-2.5 flex-1">{uniqueOwners.map((o) => { const count = contentRows.filter((r) => r.row[colMap.owner] === o).length; const live = contentRows.filter((r) => r.row[colMap.owner] === o && (r.row[colMap.status] === 'Published' || r.row[colMap.status] === 'Scheduled')).length; return (
                <div key={o} className="flex items-center justify-between p-2 rounded-lg bg-slate-50 border border-slate-200/70 text-xs"><div className="flex items-center gap-2"><span className="w-6 h-6 rounded-full bg-indigo-100 text-indigo-700 font-bold flex items-center justify-center text-[10px]">{o.charAt(0)}</span><span className="font-semibold text-slate-800">{o}</span></div><div className="flex items-center gap-2"><span className="text-emerald-700 font-medium text-[11px]">{live} live/ready</span><span className="text-slate-400">•</span><span className="font-bold text-slate-700">{count} total</span></div></div>); })}</div>
            </div>
          </div>
        )}
      </main>

      {modalMode && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-xl w-full border border-slate-200 shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
            <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center">{modalMode === 'add' ? <Plus className="w-4 h-4" /> : <Edit3 className="w-4 h-4" />}</div>
                <div><h3 className="font-bold text-sm text-slate-900">{modalMode === 'add' ? 'Create New Content Item' : 'Edit Content Details'}</h3><p className="text-[11px] text-slate-400">Saves directly to your live spreadsheet</p></div>
              </div>
              <button type="button" onClick={() => setModalMode(null)} className="text-slate-400 hover:text-slate-600 p-1.5 rounded-lg hover:bg-slate-100"><X className="w-4 h-4" /></button>
            </div>
            <form onSubmit={handleFormSubmit} className="p-6 overflow-y-auto space-y-4 text-xs">
              <div><label className="block font-semibold text-slate-700 mb-1">Content Title <span className="text-rose-500">*</span></label><input type="text" required value={formData.title} onChange={(e) => setFormData({ ...formData, title: e.target.value })} placeholder="e.g. 2027 Marketing Automation Playbook" className={inputCls} /></div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div><label className="block font-semibold text-slate-700 mb-1">Content Pillar</label><select value={formData.pillar} onChange={(e) => setFormData({ ...formData, pillar: e.target.value })} className={inputCls}>{Object.keys(PILLAR_CONFIG).map((p) => <option key={p}>{p}</option>)}</select></div>
                <div><label className="block font-semibold text-slate-700 mb-1">Channel</label><select value={formData.channel} onChange={(e) => setFormData({ ...formData, channel: e.target.value })} className={inputCls}>{Object.keys(CHANNEL_CONFIG).map((c) => <option key={c}>{c}</option>)}</select></div>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div><label className="block font-semibold text-slate-700 mb-1">Format</label><input type="text" value={formData.format} onChange={(e) => setFormData({ ...formData, format: e.target.value })} className={inputCls} /></div>
                <div><label className="block font-semibold text-slate-700 mb-1">Target Date</label><input type="date" value={formData.date} onChange={(e) => setFormData({ ...formData, date: e.target.value })} className={inputCls} /></div>
                <div><label className="block font-semibold text-slate-700 mb-1">Status</label><select value={formData.status} onChange={(e) => setFormData({ ...formData, status: e.target.value })} className={inputCls}>{STATUSES.map((s) => <option key={s}>{s}</option>)}</select></div>
              </div>
              <div><label className="block font-semibold text-slate-700 mb-1">Target Audience</label><input type="text" value={formData.audience} onChange={(e) => setFormData({ ...formData, audience: e.target.value })} placeholder="e.g. Marketing Directors & CMOs" className={inputCls} /></div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div><label className="block font-semibold text-slate-700 mb-1">Owner</label><input type="text" value={formData.owner} onChange={(e) => setFormData({ ...formData, owner: e.target.value })} placeholder="e.g. Sarah Chen" className={inputCls} /></div>
                <div><label className="block font-semibold text-slate-700 mb-1">Reviewer</label><input type="text" value={formData.reviewer} onChange={(e) => setFormData({ ...formData, reviewer: e.target.value })} placeholder="e.g. Michael Heap" className={inputCls} /></div>
              </div>
              <div><label className="block font-semibold text-slate-700 mb-1">Notes & Scope</label><textarea rows={2} value={formData.notes} onChange={(e) => setFormData({ ...formData, notes: e.target.value })} placeholder="Brief context, links, or creative instructions..." className={inputCls} /></div>
              <div className="pt-2 flex items-center justify-end gap-2 border-t border-slate-100">
                <button type="button" onClick={() => setModalMode(null)} className="px-4 py-2 text-slate-600 hover:bg-slate-100 rounded-lg font-medium">Cancel</button>
                <button type="submit" className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-semibold shadow-xs">{modalMode === 'add' ? 'Add Item' : 'Save Changes'}</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
