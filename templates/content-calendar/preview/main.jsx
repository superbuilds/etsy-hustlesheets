import React, { useState } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.jsx';
const H = ['Content Title','Content Pillar','Channel','Format','Target Date','Target Audience','Status','Owner','Reviewer','Asset Link','Notes'];
const C = [
 ['Holiday Gift Guide for Busy Marketers','Brand Awareness','Instagram','Carousel','2026-11-30','Social followers','Draft','Priya Nair','Sarah Chen','','Outline 8 picks; need product shots from design.'],
 ['Year-End Customer Wins Roundup','Customer Stories','Email Newsletter','Newsletter','2026-12-08','Existing customers','Draft','Maya Rodriguez','Ethan Brooks','','Collect 5 short quotes from CS team.'],
 ['State of B2B Marketing Tech Stack 2026','Industry Trends','LinkedIn','Report','2026-11-24','Marketing Ops leads','In Progress','Sarah Chen','Ethan Brooks','','Data pull complete from survey responses (n=620).'],
 ['Behind the Scenes: Engineering Sprint Culture','Brand Awareness','Instagram','Reel','2026-11-27','Talent & community','In Progress','David Park','Priya Nair','','Filming interview clips with lead architects.'],
 ['Mastering Customer Retention with Email Nurtures','Product Education','Email Newsletter','Email Series','2026-12-01','Lifecycle marketers','In Progress','Maya Rodriguez','Sarah Chen','','Drafting copy for 4-part automated onboarding flow.'],
 ['2027 Budget Allocation Benchmark Framework','Thought Leadership','Blog','Long-form Guide','2026-12-04','CMOs & VPs','Review','Ethan Brooks','Sarah Chen','','Submitted to executive review; waiting on legal sign-off.'],
 ['How Acme SaaS Scaled Inbound Leads 4x','Customer Stories','Blog','Case Study','2026-11-15','Demand gen managers','Scheduled','Ethan Brooks','Maya Rodriguez','https://example.com','Customer sign-off secured; scheduled for Tuesday 9am EST.'],
 ['5 Common Attribution Traps to Avoid','Thought Leadership','LinkedIn','Carousel','2026-11-18','Performance marketers','Scheduled','David Park','Ethan Brooks','','Co-authored with head of analytics; 7 visual slides.'],
 ['Interactive Demo: Building Modern Dashboards','Product Education','YouTube','Video','2026-11-20','Analysts & ops teams','Scheduled','Priya Nair','David Park','https://example.com','Video render finalized; thumbnail A/B test staged.'],
 ['2027 Marketing Automation Playbook','Thought Leadership','Blog','Long-form Guide','2026-11-10','Marketing directors','Published','Sarah Chen','Ethan Brooks','https://example.com','Promoted across paid channels; includes gated PDF download.'],
 ['Q4 Product Feature Launch Recap','Product Education','Email Newsletter','Newsletter','2026-11-12','Existing customers','Published','Maya Rodriguez','David Park','https://example.com','Highlights new reporting filters and workflow automations.'],
 ['Webinar: Content Ops at Scale','Thought Leadership','YouTube','Webinar','2026-11-05','Content leads','Published','David Park','Sarah Chen','https://example.com','212 live attendees; replay posted.'],
];
function initRows() {
  const st = (s) => C.filter(r => r[6] === s).length;
  const ready = st('Scheduled') + st('Published');
  const rows = [['Marketing Content Calendar'], ['Multi-Channel Editorial Roadmap & Campaign Publication Schedule'], [],
    ['TOTAL CONTENT','','IN PROGRESS','','SCHEDULED / PUBLISHED','','READY RATE'],
    [C.length,'',st('In Progress'),'',ready,'',ready / C.length], H, ...C];
  return rows.map((row, i) => ({ index_: i, row }));
}
function Harness() {
  const [rows, setRows] = useState(initRows);
  const updateItem = (_, idx, vals) => setRows(rs => rs.map(r => r.index_ === idx ? { ...r, row: r.row.map((c, i) => vals[i] === undefined ? c : vals[i]) } : r));
  const insertItem = (_, __, vals) => setRows(rs => [...rs, { index_: rs.length, row: vals }]);
  const deleteItem = (_, idx) => setRows(rs => rs.filter(r => r.index_ !== idx));
  return <App data={[{ data: rows }]} updateItem={updateItem} insertItem={insertItem} deleteItem={deleteItem} moveItem={() => {}} followLink={() => {}} />;
}
createRoot(document.getElementById('root')).render(<Harness />);
