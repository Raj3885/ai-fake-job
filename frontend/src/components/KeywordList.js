import React from 'react';
import { motion } from 'framer-motion';

const KeywordList = ({ matched_keywords }) => {
  const keywords = Array.isArray(matched_keywords) ? matched_keywords.slice(0, 10) : [];

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0  }}
      transition={{ delay: 0.2, duration: 0.45 }}
      className="glass-card"
      style={{ padding: '24px' }}
    >
      <h3 style={{
        fontFamily: 'Inter, sans-serif', fontSize: '13px', fontWeight: 600,
        color: '#475569', textTransform: 'uppercase', letterSpacing: '1px', margin: '0 0 18px 0',
      }}>
        🔍 Matched Risk Keywords
      </h3>

      {keywords.length > 0 ? (
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px' }}>
          {keywords.map((kw, i) => (
            <motion.span
              key={i}
              initial={{ opacity: 0, scale: 0.8, y: 8 }}
              animate={{ opacity: 1, scale: 1,   y: 0 }}
              transition={{ delay: i * 0.06, type: 'spring', stiffness: 300, damping: 22 }}
              style={{
                fontFamily: 'Inter, sans-serif',
                fontSize: '13px', fontWeight: 600,
                padding: '6px 14px',
                borderRadius: '20px',
                background: 'linear-gradient(135deg, rgba(244,63,94,0.15), rgba(239,68,68,0.1))',
                border: '1px solid rgba(244,63,94,0.3)',
                color: '#fda4af',
                letterSpacing: '0.2px',
                cursor: 'default',
                transition: 'all 0.2s ease',
              }}
              onMouseEnter={e => {
                e.currentTarget.style.background = 'linear-gradient(135deg, rgba(244,63,94,0.25), rgba(239,68,68,0.2))';
                e.currentTarget.style.borderColor = 'rgba(244,63,94,0.55)';
              }}
              onMouseLeave={e => {
                e.currentTarget.style.background = 'linear-gradient(135deg, rgba(244,63,94,0.15), rgba(239,68,68,0.1))';
                e.currentTarget.style.borderColor = 'rgba(244,63,94,0.3)';
              }}
            >
              {kw}
            </motion.span>
          ))}
        </div>
      ) : (
        <div style={{
          display: 'flex', alignItems: 'center', gap: '10px',
          color: '#475569', fontFamily: 'Inter, sans-serif', fontSize: '14px',
          padding: '12px 0',
        }}>
          <span style={{ fontSize: '20px' }}>✅</span>
          No suspicious keywords detected
        </div>
      )}
    </motion.div>
  );
};

export default KeywordList;
