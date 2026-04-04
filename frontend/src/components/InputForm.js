import React, { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const TYPES = [
  { value: 'job',    label: '💼  Job Fraud Detection',    desc: 'Analyze job postings for fraudulent patterns' },
  { value: 'review', label: '⭐  Fake Review Detection',  desc: 'Detect deceptive product reviews' },
];

const InputForm = ({ onSubmit, loading }) => {
  const [text, setText] = useState('');
  const [type, setType] = useState('job');
  const [focused, setFocused] = useState(false);
  const textareaRef = useRef(null);

  const wordCount = text.trim() ? text.trim().split(/\s+/).length : 0;
  const isEmpty   = !text.trim();
  const isDisabled = isEmpty || loading;

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!isEmpty && !loading) onSubmit(text, type);
  };

  return (
    <form onSubmit={handleSubmit} style={{ width: '100%' }}>

      {/* Type Selector */}
      <div style={{ display: 'flex', gap: '12px', marginBottom: '20px' }}>
        {TYPES.map(t => (
          <button
            key={t.value}
            type="button"
            onClick={() => setType(t.value)}
            style={{
              flex: 1,
              padding: '14px 16px',
              borderRadius: '12px',
              border: `1.5px solid ${type === t.value ? 'rgba(99,102,241,0.7)' : 'rgba(255,255,255,0.06)'}`,
              background: type === t.value
                ? 'linear-gradient(135deg, rgba(99,102,241,0.18), rgba(139,92,246,0.12))'
                : 'rgba(255,255,255,0.03)',
              color: type === t.value ? '#e0e7ff' : '#94a3b8',
              cursor: 'pointer',
              textAlign: 'left',
              transition: 'all 0.25s ease',
              boxShadow: type === t.value ? '0 0 20px rgba(99,102,241,0.15)' : 'none',
            }}
          >
            <div style={{ fontSize: '14px', fontWeight: 600, marginBottom: '3px', fontFamily: 'Inter, sans-serif' }}>
              {t.label}
            </div>
            <div style={{ fontSize: '11px', opacity: 0.65, fontFamily: 'Inter, sans-serif' }}>{t.desc}</div>
          </button>
        ))}
      </div>

      {/* Textarea */}
      <div style={{ position: 'relative', marginBottom: '20px' }}>
        <textarea
          ref={textareaRef}
          value={text}
          onChange={e => setText(e.target.value)}
          onFocus={() => setFocused(true)}
          onBlur={() => setFocused(false)}
          placeholder="Paste job description, email, or review text here…"
          rows={6}
          style={{
            width: '100%',
            padding: '18px 20px',
            borderRadius: '14px',
            border: `1.5px solid ${focused ? 'rgba(99,102,241,0.6)' : 'rgba(255,255,255,0.07)'}`,
            background: 'rgba(255,255,255,0.03)',
            color: '#e2e8f0',
            fontSize: '15px',
            fontFamily: 'Inter, sans-serif',
            lineHeight: 1.7,
            resize: 'vertical',
            outline: 'none',
            transition: 'border-color 0.3s ease, box-shadow 0.3s ease',
            boxShadow: focused ? '0 0 0 4px rgba(99,102,241,0.1), 0 0 30px rgba(99,102,241,0.08)' : 'none',
            boxSizing: 'border-box',
            minHeight: '140px',
          }}
        />
        {/* Character counter */}
        {text && (
          <div style={{
            position: 'absolute', bottom: '12px', right: '16px',
            fontSize: '11px', color: '#475569', fontFamily: 'Inter, sans-serif',
            pointerEvents: 'none',
          }}>
            {wordCount} words
          </div>
        )}
      </div>

      {/* Analyze button */}
      <motion.button
        type="submit"
        disabled={isDisabled}
        whileHover={!isDisabled ? { scale: 1.015, y: -1 } : {}}
        whileTap={!isDisabled   ? { scale: 0.975 }        : {}}
        style={{
          width: '100%',
          padding: '17px',
          borderRadius: '14px',
          border: 'none',
          fontSize: '16px',
          fontWeight: 700,
          fontFamily: 'Inter, sans-serif',
          letterSpacing: '0.3px',
          cursor: isDisabled ? 'not-allowed' : 'pointer',
          background: isDisabled
            ? 'rgba(99,102,241,0.2)'
            : 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #06b6d4 100%)',
          color: isDisabled ? 'rgba(255,255,255,0.3)' : '#fff',
          boxShadow: isDisabled ? 'none' : '0 8px 32px rgba(99,102,241,0.35), 0 0 60px rgba(139,92,246,0.15)',
          transition: 'background 0.3s ease, box-shadow 0.3s ease, opacity 0.3s ease',
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        {/* Shimmer sweep on hover */}
        {!isDisabled && (
          <span style={{
            position: 'absolute', inset: 0,
            background: 'linear-gradient(105deg, transparent 40%, rgba(255,255,255,0.12) 50%, transparent 60%)',
            backgroundSize: '200% 100%',
            animation: 'shimmer 2.5s ease infinite',
            pointerEvents: 'none',
          }} />
        )}
        {loading ? 'Analyzing…' : 'Analyze'}
      </motion.button>
    </form>
  );
};

export default InputForm;
