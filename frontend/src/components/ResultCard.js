import React from 'react';
import { motion } from 'framer-motion';

const METRICS = (r) => [
  { label: 'Confidence',     value: `${(r.confidence * 100).toFixed(1)}%`,  icon: '🎯' },
  { label: 'Risk Score',     value: `${r.risk_score}%`,                     icon: '⚡' },
  { label: 'Risk Category',  value: r.risk_category,                        icon: '🔺' },
  { label: 'Sentiment',      value: r.sentiment_label,                      icon: '💬' },
  { label: 'Text Length',    value: `${r.text_length} words`,               icon: '📝' },
  { label: 'Keyword Risk',   value: r.keyword_risk_level,                   icon: '🔑' },
];

const riskColor = (score) => {
  if (score > 60) return { color: '#fca5a5', glow: 'rgba(239,68,68,0.3)' };
  if (score > 30) return { color: '#fdba74', glow: 'rgba(249,115,22,0.3)' };
  return { color: '#86efac', glow: 'rgba(34,197,94,0.3)' };
};

const ResultCard = ({ result }) => {
  if (!result) return null;
  const { prediction, risk_score } = result;
  const isFake = prediction === 'Fake';
  const rc = riskColor(risk_score);

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.96, y: 20 }}
      animate={{ opacity: 1, scale: 1,    y: 0   }}
      transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
      className="glass-card"
      style={{ padding: '28px', overflow: 'hidden', position: 'relative' }}
    >
      {/* Background accent glow */}
      <div style={{
        position: 'absolute', top: -60, right: -60, width: 200, height: 200,
        borderRadius: '50%',
        background: isFake
          ? 'radial-gradient(circle, rgba(239,68,68,0.12) 0%, transparent 70%)'
          : 'radial-gradient(circle, rgba(34,197,94,0.12) 0%, transparent 70%)',
        pointerEvents: 'none',
      }} />

      <h2 style={{
        fontFamily: 'Inter, sans-serif', fontSize: '13px', fontWeight: 600,
        color: '#475569', textTransform: 'uppercase', letterSpacing: '1px',
        marginBottom: '20px',
      }}>Analysis Result</h2>

      {/* Prediction Badge */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '28px' }}>
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ type: 'spring', stiffness: 260, damping: 20, delay: 0.2 }}
          className={isFake ? 'badge-fake' : 'badge-real'}
          style={{
            padding: '10px 24px', borderRadius: '50px',
            fontSize: '20px', fontWeight: 800, fontFamily: 'Inter, sans-serif',
            boxShadow: `0 0 24px ${isFake ? 'rgba(239,68,68,0.25)' : 'rgba(34,197,94,0.2)'}`,
          }}
        >
          {isFake ? '⚠️ Fake' : '✅ Real'}
        </motion.div>

        <div style={{
          flex: 1, height: '2px',
          background: `linear-gradient(to right, ${isFake ? 'rgba(239,68,68,0.4)' : 'rgba(34,197,94,0.4)'}, transparent)`,
          borderRadius: '1px',
        }} />
      </div>

      {/* Metrics Grid */}
      <div style={{
        display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px',
      }}>
        {METRICS(result).map((m, i) => (
          <motion.div
            key={m.label}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.15 + i * 0.07 }}
            style={{
              background: 'rgba(255,255,255,0.03)',
              border: '1px solid rgba(255,255,255,0.06)',
              borderRadius: '10px',
              padding: '14px',
            }}
          >
            <div style={{ fontSize: '18px', marginBottom: '6px' }}>{m.icon}</div>
            <div style={{
              fontSize: '11px', fontWeight: 600, color: '#64748b',
              textTransform: 'uppercase', letterSpacing: '0.5px',
              fontFamily: 'Inter, sans-serif', marginBottom: '4px',
            }}>
              {m.label}
            </div>
            <div style={{
              fontSize: '16px', fontWeight: 700, fontFamily: 'Inter, sans-serif',
              color: m.label === 'Risk Score' || m.label === 'Risk Category' ? rc.color : '#e2e8f0',
            }}>
              {m.value}
            </div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
};

export default ResultCard;
