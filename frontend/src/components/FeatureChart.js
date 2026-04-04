import React from 'react';
import { motion } from 'framer-motion';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Cell
} from 'recharts';

const COLORS = ['#6366f1', '#8b5cf6', '#06b6d4', '#3b82f6', '#a78bfa'];

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{
      background: 'rgba(15,23,42,0.95)',
      border: '1px solid rgba(99,102,241,0.4)',
      borderRadius: '10px',
      padding: '12px 16px',
      fontFamily: 'Inter, sans-serif',
      backdropFilter: 'blur(12px)',
    }}>
      <div style={{ color: '#94a3b8', fontSize: '12px', marginBottom: '4px' }}>{label}</div>
      <div style={{ color: '#6366f1', fontWeight: 700, fontSize: '15px' }}>
        {payload[0].value.toFixed(4)}
      </div>
    </div>
  );
};

const FeatureChart = ({ top_features }) => {
  let data = [];
  if (top_features && typeof top_features === 'object') {
    data = Object.entries(top_features)
      .map(([name, value]) => ({ name, value }))
      .sort((a, b) => b.value - a.value)
      .slice(0, 5);
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0  }}
      transition={{ delay: 0.25, duration: 0.45 }}
      className="glass-card"
      style={{ padding: '24px' }}
    >
      <h3 style={{
        fontFamily: 'Inter, sans-serif', fontSize: '13px', fontWeight: 600,
        color: '#475569', textTransform: 'uppercase', letterSpacing: '1px', margin: '0 0 22px 0',
      }}>
        📊 Top Influencing Features
      </h3>

      {data.length > 0 ? (
        <div style={{ width: '100%', height: 240 }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart layout="vertical" data={data} margin={{ top: 0, right: 20, left: 80, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" horizontal={false} />
              <XAxis
                type="number" tick={{ fill: '#475569', fontSize: 11, fontFamily: 'Inter, sans-serif' }}
                axisLine={{ stroke: 'rgba(255,255,255,0.06)' }} tickLine={false}
              />
              <YAxis
                type="category" dataKey="name" width={100}
                tick={{ fill: '#94a3b8', fontSize: 12, fontFamily: 'Inter, sans-serif' }}
                axisLine={false} tickLine={false}
              />
              <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(99,102,241,0.05)' }} />
              <Bar dataKey="value" radius={[0, 6, 6, 0]} barSize={22} animationDuration={1000}>
                {data.map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]}
                    style={{ filter: `drop-shadow(0 0 6px ${COLORS[i % COLORS.length]}88)` }}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      ) : (
        <div style={{ color: '#475569', fontFamily: 'Inter, sans-serif', fontSize: '14px', padding: '12px 0' }}>
          No feature data available.
        </div>
      )}
    </motion.div>
  );
};

export default FeatureChart;
