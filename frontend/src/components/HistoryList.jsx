import React, { useEffect, useState } from 'react';
import { api } from '../api/client';

export default function HistoryList({ onPlanMission }) {
  const [missions, setMissions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getMissions('completed');
      setMissions(data);
    } catch (err) {
      setError(err.message || 'Could not load completed missions.');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Recent';
    const date = new Date(dateString);
    return date.toLocaleDateString(undefined, {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="history-container">
      <div className="history-header">
        <h2 className="section-heading">Outdoor Activity History</h2>
        <p className="section-subheading">Your completed outdoor excursions.</p>
      </div>

      {loading && (
        <div className="loading-state-box">
          <p>Loading your activity log...</p>
        </div>
      )}

      {error && (
        <div className="alert-error" role="alert">
          {error}
        </div>
      )}

      {!loading && !error && missions.length === 0 && (
        <div className="empty-history-box">
          <div className="empty-icon">🍃</div>
          <h3>No completed missions yet.</h3>
          <p>Go touch some grass to start your outdoor log.</p>
          <button type="button" className="btn-primary" onClick={onPlanMission} style={{ marginTop: '1rem' }}>
            Plan a Mission
          </button>
        </div>
      )}

      {!loading && !error && missions.length > 0 && (
        <div className="history-list">
          {missions.map((m) => (
            <div key={m.id} className="history-card">
              <div className="history-card-top">
                <span className="history-title">{m.title || 'Outdoor Mission'}</span>
                <span className="history-date">{formatDate(m.completed_at || m.created_at)}</span>
              </div>
              <div className="history-card-details">
                <span className="badge-duration">⏱️ {m.duration_minutes} Mins</span>
                <span className="badge-activity" style={{ textTransform: 'capitalize' }}>🌿 {m.activity_type}</span>
                <span className="badge-difficulty" style={{ textTransform: 'capitalize' }}>🎯 {m.difficulty}</span>
                <span className="badge-mode" style={{ textTransform: 'capitalize' }}>{m.mode}</span>
                <span className="badge-completed">✓ Completed</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
