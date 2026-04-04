import React from 'react';
import { motion } from 'framer-motion';

const ExplanationBox = ({ fraud_probability_explanation, explanation }) => {
  const isEmpty = !fraud_probability_explanation && !explanation;

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0  }}
      transition={{ delay: 0.3, duration: 0.45 }}
      className="glass-card"
      style={{ padding: '24px' }}
    >
      <h3 style={{
        fontFamily: 'Inter, sans-serif', fontSize: '13px', fontWeight: 600,
        color: '#475569', textTransform: 'uppercase', letterSpacing: '1px', margin: '0 0 18px 0',
      }}>
        🤖 AI Explanation
      </h3>

      {isEmpty ? (
        <p style={{ color: '#475569', fontFamily: 'Inter, sans-serif', fontSize: '14px', fontStyle: 'italic', margin: 0 }}>
          No explanation available.
        </p>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          {fraud_probability_explanation && (
            <div style={{
              background: 'rgba(99,102,241,0.06)',
              border: '1px solid rgba(99,102,241,0.15)',
              borderLeft: '3px solid #6366f1',
              borderRadius: '10px',
              padding: '14px 16px',
              color: '#c7d2fe',
              fontFamily: 'Inter, sans-serif',
              fontSize: '14px',
              lineHeight: 1.7,
            }}>
              {fraud_probability_explanation}
            </div>
          )}
          {explanation && (
            <div style={{
              background: 'rgba(255,255,255,0.02)',
              border: '1px solid rgba(255,255,255,0.06)',
              borderLeft: '3px solid rgba(139,92,246,0.6)',
              borderRadius: '10px',
              padding: '14px 16px',
              color: '#94a3b8',
              fontFamily: 'Inter, sans-serif',
              fontSize: '14px',
              lineHeight: 1.7,
            }}>
              {explanation}
            </div>
          )}
        </div>
      )}
    </motion.div>
  );
};

export default ExplanationBox;
