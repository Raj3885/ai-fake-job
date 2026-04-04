import React from 'react';
import { motion } from 'framer-motion';

const getBarConfig = (score) => {
  if (score > 60) return {
    color: '#ef4444',
    track: 'rgba(239,68,68,0.12)',
    glow: '0 0 20px rgba(239,68,68,0.4)',
    gradient: 'linear-gradient(90deg, #f97316, #ef4444, #f43f5e)',
  };
  if (score > 30) return {
    color: '#f97316',
    track: 'rgba(249,115,22,0.12)',
    glow: '0 0 20px rgba(249,115,22,0.35)',
    gradient: 'linear-gradient(90deg, #eab308, #f97316)',
  };
  return {
    color: '#22c55e',
    track: 'rgba(34,197,94,0.12)',
    glow: '0 0 20px rgba(34,197,94,0.3)',
    gradient: 'linear-gradient(90deg, #06b6d4, #22c55e)',
  };
};

const RiskGauge = ({ risk_score, risk_category }) => {
  if (risk_score === undefined || risk_score === null) return null;
  const cfg = getBarConfig(risk_score);

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0  }}
      transition={{ delay: 0.15, duration: 0.45 }}
      className="glass-card"
      style={{ padding: '24px' }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '18px' }}>
        <h3 style={{ fontFamily: 'Inter, sans-serif', fontSize: '13px', fontWeight: 600, color: '#475569', textTransform: 'uppercase', letterSpacing: '1px', margin: 0 }}>
          Risk Score
        </h3>
        <motion.span
          initial={{ scale: 0.6, opacity: 0 }}
          animate={{ scale: 1,   opacity: 1 }}
          transition={{ delay: 0.4, type: 'spring', stiffness: 300 }}
          style={{
            fontSize: '28px', fontWeight: 900, fontFamily: 'Inter, sans-serif',
            color: cfg.color, textShadow: cfg.glow,
          }}
        >
          {risk_score}%
        </motion.span>
      </div>

      {/* Track */}
      <div style={{
        width: '100%', height: '10px', borderRadius: '6px',
        background: cfg.track, marginBottom: '14px', overflow: 'hidden',
      }}>
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${risk_score}%` }}
          transition={{ duration: 1.2, ease: [0.16, 1, 0.3, 1], delay: 0.2 }}
          style={{
            height: '100%', borderRadius: '6px',
            background: cfg.gradient,
            boxShadow: cfg.glow,
          }}
        />
      </div>

      {/* Category badge */}
      <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
        <span style={{
          fontFamily: 'Inter, sans-serif', fontSize: '13px', fontWeight: 700,
          color: cfg.color,
          background: cfg.track,
          border: `1px solid ${cfg.color}44`,
          padding: '4px 14px', borderRadius: '20px',
        }}>
          {risk_category}
        </span>
      </div>
    </motion.div>
  );
};

export default RiskGauge;
