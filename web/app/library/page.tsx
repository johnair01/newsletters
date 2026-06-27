'use client';

import { useState } from 'react';
import Link from 'next/link';
import { records, stateFilterMeta, topicNames, SURFACES, type ReviewState } from '@/lib/data';

const mono = "'DM Mono', monospace";
const serif = "'DM Serif Display', serif";

type LibView = 'record' | 'topic';
type Filter = 'all' | ReviewState;

export default function LibraryPage() {
  const [libView, setLibView] = useState<LibView>('record');
  const [filter, setFilter] = useState<Filter>('all');

  const filtered = records.filter((r) => filter === 'all' || r.state === filter);
  const topics = topicNames
    .map((name) => ({ name, records: filtered.filter((r) => r.topic === name) }))
    .filter((t) => t.records.length > 0);
  const activeStateLabel = stateFilterMeta.find((m) => m.key === filter)?.label ?? 'All';
  const hasRecords = filtered.length > 0;

  const seg = (active: boolean) => ({
    background: active ? 'var(--text)' : 'transparent',
    color: active ? 'var(--color-paper)' : 'var(--text)',
  });

  return (
    <div style={{ padding: '36px 28px 70px', maxWidth: 1040, margin: '0 auto' }}>
      <p style={{ fontFamily: mono, fontSize: 11, letterSpacing: '.2em', textTransform: 'uppercase', color: 'var(--text-dim)', margin: '0 0 12px' }}>The index</p>
      <h1 style={{ fontFamily: serif, fontWeight: 400, fontSize: 'clamp(32px,4.5vw,46px)', lineHeight: 1.05, margin: '0 0 10px' }}>Library</h1>
      <p style={{ fontSize: 16, lineHeight: 1.55, color: 'var(--text-dim)', maxWidth: '58ch', margin: '0 0 26px' }}>
        Browse by <strong style={{ color: 'var(--text)' }}>record</strong> or by <strong style={{ color: 'var(--text)' }}>topic</strong>. Review state is a badge and a filter — not the way in. Click a record to open its surfaces.
      </p>

      {/* controls */}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '16px 22px', alignItems: 'center', justifyContent: 'space-between', borderTop: '2px solid var(--text)', borderBottom: '1px solid var(--line)', padding: '13px 0', marginBottom: 28 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <span style={{ fontFamily: mono, fontSize: 10, letterSpacing: '.14em', textTransform: 'uppercase', color: 'var(--text-dim)' }}>Browse</span>
          <div style={{ display: 'flex', border: '1px solid var(--text)' }}>
            <button type="button" data-nav onClick={() => setLibView('record')} style={{ fontFamily: mono, fontSize: 11, letterSpacing: '.08em', textTransform: 'uppercase', border: 0, padding: '8px 15px', ...seg(libView === 'record') }}>By record</button>
            <button type="button" data-nav onClick={() => setLibView('topic')} style={{ fontFamily: mono, fontSize: 11, letterSpacing: '.08em', textTransform: 'uppercase', border: 0, borderLeft: '1px solid var(--text)', padding: '8px 15px', ...seg(libView === 'topic') }}>By topic</button>
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
          <span style={{ fontFamily: mono, fontSize: 10, letterSpacing: '.14em', textTransform: 'uppercase', color: 'var(--text-dim)' }}>Filter state</span>
          {stateFilterMeta.map((m) => {
            const active = filter === m.key;
            const count = m.key === 'all' ? records.length : records.filter((r) => r.state === m.key).length;
            return (
              <button
                key={m.key}
                type="button"
                data-nav
                onClick={() => setFilter(m.key)}
                style={{ display: 'flex', alignItems: 'center', gap: 6, fontFamily: mono, fontSize: 10.5, textTransform: 'uppercase', letterSpacing: '.05em', background: active ? 'var(--text)' : 'transparent', color: active ? 'var(--color-paper)' : 'var(--text)', border: `1px solid ${active ? 'var(--text)' : 'var(--line)'}`, padding: '5px 10px' }}
              >
                <span style={{ width: 8, height: 8, background: m.dot, display: 'inline-block', borderRadius: '50%' }} />
                {m.label}<span style={{ opacity: 0.6 }}>{count}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* empty state */}
      {!hasRecords && (
        <div style={{ border: '1px dashed var(--line)', background: 'var(--color-surface-low)', padding: '48px 24px', textAlign: 'center' }}>
          <p style={{ fontFamily: mono, fontSize: 10, letterSpacing: '.14em', textTransform: 'uppercase', color: 'var(--text-dim)', margin: '0 0 10px' }}>No records · {activeStateLabel}</p>
          <p style={{ fontFamily: serif, fontSize: 24, lineHeight: 1.2, margin: '0 0 8px', color: 'var(--text)' }}>
            {libView === 'record' ? 'Nothing in this state yet.' : 'No topics match this state.'}
          </p>
          <p style={{ fontSize: 14, lineHeight: 1.55, color: 'var(--text-dim)', margin: '0 auto 18px', maxWidth: '42ch' }}>
            {libView === 'record' ? (
              <>No records are currently <strong style={{ color: 'var(--text)' }}>{activeStateLabel}</strong>. Try another state, or clear the filter to see everything.</>
            ) : (
              <>Clear the filter to browse all topics again.</>
            )}
          </p>
          <button type="button" data-nav onClick={() => setFilter('all')} style={{ fontFamily: mono, fontSize: 11, letterSpacing: '.08em', textTransform: 'uppercase', background: 'var(--text)', color: 'var(--color-paper)', border: 0, padding: '11px 18px' }}>Clear filter</button>
        </div>
      )}

      {/* BY RECORD */}
      {hasRecords && libView === 'record' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 1, background: 'var(--line)', border: '1px solid var(--line)' }}>
          {filtered.map((r) => (
            <div key={r.id} style={{ background: 'var(--card)', padding: '22px 20px', display: 'grid', gridTemplateColumns: '1fr auto', gap: 14, alignItems: 'start' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 8, flexWrap: 'wrap' }}>
                  <span style={{ fontFamily: mono, fontSize: 9.5, letterSpacing: '.12em', textTransform: 'uppercase', color: 'var(--text-dim)' }}>Record · {r.topic}</span>
                  <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6, fontFamily: mono, fontSize: 9.5, letterSpacing: '.08em', textTransform: 'uppercase', color: r.stateColor, border: `1px solid ${r.stateColor}`, padding: '2px 8px' }}>
                    <span style={{ width: 7, height: 7, background: r.stateColor, display: 'inline-block', borderRadius: '50%' }} />{r.state}
                  </span>
                </div>
                <Link href={r.href} data-nav style={{ display: 'inline-block', color: 'var(--text)' }}>
                  <span style={{ fontFamily: serif, fontSize: 26, lineHeight: 1.05 }}>{r.title}</span>
                </Link>
                <p style={{ fontSize: 14, lineHeight: 1.55, color: 'var(--text-dim)', margin: '7px 0 14px', maxWidth: '60ch' }}>{r.summary}</p>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
                  <span style={{ fontFamily: mono, fontSize: 9.5, letterSpacing: '.1em', textTransform: 'uppercase', color: 'var(--text-dim)' }}>Read as</span>
                  {r.chips.map((type) => {
                    const s = SURFACES[type];
                    return (
                      <Link key={type} href={s.href} data-nav style={{ fontFamily: mono, fontSize: 10.5, letterSpacing: '.04em', textTransform: 'uppercase', background: 'transparent', border: '1px solid var(--line)', borderLeft: `3px solid ${s.color}`, color: 'var(--text)', padding: '4px 9px' }}>{s.label}</Link>
                    );
                  })}
                </div>
              </div>
              <Link href={r.href} data-nav style={{ alignSelf: 'center', fontFamily: mono, fontSize: 11, letterSpacing: '.08em', textTransform: 'uppercase', background: 'var(--text)', color: 'var(--color-paper)', padding: '11px 16px', whiteSpace: 'nowrap' }}>Open →</Link>
            </div>
          ))}
        </div>
      )}

      {/* BY TOPIC */}
      {hasRecords && libView === 'topic' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 34 }}>
          {topics.map((t) => (
            <div key={t.name}>
              <div style={{ display: 'flex', alignItems: 'baseline', gap: 12, borderBottom: '1px solid var(--line)', paddingBottom: 8, marginBottom: 16 }}>
                <h2 style={{ fontFamily: serif, fontWeight: 400, fontSize: 26, margin: 0 }}>{t.name}</h2>
                <span style={{ fontFamily: mono, fontSize: 10, letterSpacing: '.1em', textTransform: 'uppercase', color: 'var(--text-dim)' }}>{t.records.length} records</span>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill,minmax(240px,1fr))', gap: 1, background: 'var(--line)', border: '1px solid var(--line)' }}>
                {t.records.map((r) => (
                  <Link key={r.id} href={r.href} data-nav style={{ textAlign: 'left', background: 'var(--card)', borderLeft: `3px solid ${r.stateColor}`, padding: '16px 15px', color: 'var(--text)' }}>
                    <span style={{ display: 'inline-flex', alignItems: 'center', gap: 5, fontFamily: mono, fontSize: 9, letterSpacing: '.08em', textTransform: 'uppercase', color: r.stateColor, marginBottom: 9 }}>
                      <span style={{ width: 6, height: 6, background: r.stateColor, display: 'inline-block', borderRadius: '50%' }} />{r.state}
                    </span>
                    <span style={{ fontFamily: serif, fontSize: 20, lineHeight: 1.08, display: 'block', marginBottom: 6 }}>{r.title}</span>
                    <span style={{ fontSize: 12.5, lineHeight: 1.45, color: 'var(--text-dim)', display: 'block' }}>{r.count} surfaces →</span>
                  </Link>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
