import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import InputForm from '../components/InputForm';
import ResultCard from '../components/ResultCard';
import RiskGauge from '../components/RiskGauge';
import KeywordList from '../components/KeywordList';
import FeatureChart from '../components/FeatureChart';
import ExplanationBox from '../components/ExplanationBox';
import { predictFraud } from '../api/predict';

/* ──────────────────────────────────────────────────
   Full-screen loading overlay with dual-ring spinner
   ────────────────────────────────────────────────── */
const LoadingOverlay = () => (
  <motion.div
    className="loading-overlay"
    initial={{ opacity: 0 }}
    animate={{ opacity: 1 }}
    exit={{ opacity: 0 }}
    transition={{ duration: 0.3 }}
  >
    <div className="loader-ring" />
    <div className="loader-dots">
      <span /><span /><span />
    </div>
    <p className="loader-text">Running fraud detection models…</p>
  </motion.div>
);

/* ──────────────────────────────────────────────────
   Floating particle orbs (decorative, CSS-animated)
   ────────────────────────────────────────────────── */
const Orb = ({ style }) => (
  <div style={{
    position: 'fixed', borderRadius: '50%',
    filter: 'blur(80px)', pointerEvents: 'none', zIndex: 0,
    ...style,
  }} />
);

/* ────────────────── Home Page ───────────────────── */
const Home = () => {
  const [result,  setResult]  = useState(null);
  const [loading, setLoading] = useState(false);
  const [error,   setError]   = useState(null);

  const handleAnalyze = async (text, type) => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await predictFraud(text, type);
      setResult(data);
    } catch (err) {
      setError('⚠️ Could not connect to the prediction API. Make sure the backend is running on port 8000.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {/* Ambient orbs */}
      <Orb style={{ top: '-10%', left: '-5%',  width: 500, height: 500, background: 'rgba(99,102,241,0.18)' }} />
      <Orb style={{ bottom: '5%',  right: '-8%', width: 420, height: 420, background: 'rgba(139,92,246,0.14)' }} />
      <Orb style={{ top: '45%',  left: '60%',  width: 300, height: 300, background: 'rgba(6,182,212,0.08)'  }} />

      {/* Full-screen loading */}
      <AnimatePresence>{loading && <LoadingOverlay />}</AnimatePresence>

      {/* Page scroll container */}
      <div style={{ minHeight: '100vh', padding: '0 16px 80px', position: 'relative', zIndex: 1 }}>
        <div style={{ maxWidth: 720, margin: '0 auto' }}>

          {/* ── Hero Header ── */}
          <motion.div
            initial={{ opacity: 0, y: -24 }}
            animate={{ opacity: 1,  y: 0   }}
            transition={{ duration: 0.7, ease: [0.16,1,0.3,1] }}
            style={{ textAlign: 'center', padding: '72px 0 48px' }}
          >
            {/* Icon badge */}
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: 'spring', stiffness: 220, damping: 18, delay: 0.1 }}
              style={{
                display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
                width: 72, height: 72, borderRadius: '22px',
                background: 'linear-gradient(135deg, rgba(99,102,241,0.3), rgba(139,92,246,0.2))',
                border: '1px solid rgba(99,102,241,0.35)',
                fontSize: '32px', marginBottom: '28px',
                boxShadow: '0 8px 32px rgba(99,102,241,0.25), inset 0 1px 0 rgba(255,255,255,0.08)',
              }}
            >
              🛡️
            </motion.div>

            <h1 className="gradient-text" style={{
              fontFamily: 'Inter, sans-serif',
              fontSize: 'clamp(28px, 5vw, 48px)',
              fontWeight: 900, lineHeight: 1.15,
              letterSpacing: '-1px', marginBottom: '16px',
            }}>
              AI Fraud Detection
            </h1>

            <p style={{
              fontFamily: 'Inter, sans-serif',
              fontSize: '17px', color: '#64748b',
              lineHeight: 1.6, maxWidth: 480, margin: '0 auto 10px',
            }}>
              Detect fraudulent job postings and fake reviews using explainable machine learning — in seconds.
            </p>

            {/* Status pills */}
            <div style={{ display: 'flex', gap: 10, justifyContent: 'center', marginTop: 22, flexWrap: 'wrap' }}>
              {['XGBoost Model', 'TF-IDF + Sentiment', 'Real-time Inference'].map(t => (
                <span key={t} style={{
                  fontFamily: 'Inter, sans-serif', fontSize: '12px', fontWeight: 600,
                  padding: '5px 13px', borderRadius: '20px',
                  background: 'rgba(99,102,241,0.1)',
                  border: '1px solid rgba(99,102,241,0.2)',
                  color: '#a5b4fc',
                }}>
                  {t}
                </span>
              ))}
            </div>
          </motion.div>

          {/* ── Input Card ── */}
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1,  y: 0  }}
            transition={{ delay: 0.2, duration: 0.6, ease: [0.16,1,0.3,1] }}
            className="glass-card"
            style={{ padding: '28px', marginBottom: '28px' }}
          >
            <InputForm onSubmit={handleAnalyze} loading={loading} />
          </motion.div>

          {/* Error State */}
          <AnimatePresence>
            {error && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                style={{
                  background: 'rgba(239,68,68,0.08)',
                  border: '1px solid rgba(239,68,68,0.3)',
                  borderRadius: '12px',
                  padding: '16px 20px',
                  color: '#fca5a5',
                  fontFamily: 'Inter, sans-serif',
                  fontSize: '14px',
                  marginBottom: '24px',
                  textAlign: 'center',
                }}
              >
                {error}
              </motion.div>
            )}
          </AnimatePresence>

          {/* ── Results Stack ── */}
          <AnimatePresence>
            {result && !loading && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}
              >
                {/* Divider */}
                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                  <div style={{ flex: 1, height: 1, background: 'rgba(255,255,255,0.06)' }} />
                  <span style={{ fontFamily: 'Inter, sans-serif', fontSize: '12px', color: '#334155', fontWeight: 600, letterSpacing: '0.8px' }}>
                    ANALYSIS COMPLETE
                  </span>
                  <div style={{ flex: 1, height: 1, background: 'rgba(255,255,255,0.06)' }} />
                </div>

                <ResultCard   result={result} />
                <RiskGauge    risk_score={result.risk_score}    risk_category={result.risk_category} />
                <KeywordList  matched_keywords={result.matched_keywords} />
                <FeatureChart top_features={result.top_features} />
                <ExplanationBox
                  fraud_probability_explanation={result.fraud_probability_explanation}
                  explanation={result.explanation}
                />
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </>
  );
};

export default Home;
