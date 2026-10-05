import React from 'react';

export default function MissionPlaceholder({ mission, onReset }) {
  if (!mission) return null;

  return (
    <div className="mission-placeholder-card">
      <div className="placeholder-badge">Phase 3 Validated</div>
      <h2>Mission Created</h2>
      <p className="placeholder-info">
        Mission record has been safely stored in SQLite with validated parameters:
      </p>

      <div className="summary-box">
        <div className="summary-item">
          <span className="summary-label">Duration:</span>
          <strong>{mission.duration_minutes} Minutes</strong>
        </div>
        <div className="summary-item">
          <span className="summary-label">Activity:</span>
          <strong style={{ textTransform: 'capitalize' }}>{mission.activity_type}</strong>
        </div>
        <div className="summary-item">
          <span className="summary-label">Difficulty:</span>
          <strong style={{ textTransform: 'capitalize' }}>{mission.difficulty}</strong>
        </div>
        <div className="summary-item">
          <span className="summary-label">Mode:</span>
          <strong style={{ textTransform: 'capitalize' }}>{mission.mode}</strong>
        </div>
        <div className="summary-item">
          <span className="summary-label">Status:</span>
          <code>{mission.status}</code>
        </div>
        <div className="summary-item">
          <span className="summary-label">ID:</span>
          <code className="text-muted">{mission.id}</code>
        </div>
      </div>

      <div className="notice-banner">
        <span>ℹ️</span>
        <p>{mission.message || 'Mission created. AI generation will be added in the next phase.'}</p>
      </div>

      <button type="button" className="btn-secondary" onClick={onReset}>
        ← Plan Another Mission / Return Home
      </button>
    </div>
  );
}
