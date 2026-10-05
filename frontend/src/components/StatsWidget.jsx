import React, { useEffect, useState } from 'react';
import { api } from '../api/client';

export default function StatsWidget({ onPlanMission }) {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getStats();
      setStats(data);
    } catch (err) {
      setError(err.message || 'Could not load statistics.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="stats-container">
      <div className="stats-header">
        <h2 className="section-heading">Outdoor Statistics</h2>
        <p className="section-subheading">A mindful summary of your time away from screens.</p>
      </div>

      {loading && (
        <div className="loading-state-box">
          <p>Calculating outdoor time...</p>
        </div>
      )}

      {error && (
        <div className="alert-error" role="alert">
          {error}
        </div>
      )}

      {!loading && stats && (
        <div className="stats-grid">
          <div className="stat-card">
            <span className="stat-icon">🌱</span>
            <div className="stat-number">{stats.completed_missions}</div>
            <div className="stat-label">Missions Completed</div>
          </div>

          <div className="stat-card">
            <span className="stat-icon">⏱️</span>
            <div className="stat-number">{stats.total_outdoor_minutes}</div>
            <div className="stat-label">Outdoor Minutes</div>
          </div>

          <div className="stat-card">
            <span className="stat-icon">🔥</span>
            <div className="stat-number">{stats.current_streak}</div>
            <div className="stat-label">Day Streak</div>
          </div>
        </div>
      )}

      <div className="stats-reflection-banner">
        <h4>Mindful Reflection</h4>
        <p>
          Every minute counted here was spent directly in the real world rather than consuming digital feeds.
        </p>
        <button type="button" className="btn-primary" onClick={onPlanMission} style={{ marginTop: '1.25rem' }}>
          Plan Your Next Mission
        </button>
      </div>
    </div>
  );
}
