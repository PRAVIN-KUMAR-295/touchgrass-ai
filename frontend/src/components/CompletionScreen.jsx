import React from 'react';

export default function CompletionScreen({ mission, onPlanAnother, onViewHistory }) {
  return (
    <div className="completion-card">
      <div className="completion-icon">🌱</div>
      <h2 className="completion-title">Mission Complete.</h2>
      <p className="completion-subtitle">
        You spent time outside in the real world. Nice work disconnecting.
      </p>

      {mission && (
        <div className="completion-summary-box">
          <div className="summary-field">
            <span>Mission:</span>
            <strong>{mission.title || 'Outdoor Mission'}</strong>
          </div>
          <div className="summary-field">
            <span>Outdoor Time:</span>
            <strong>{mission.duration_minutes} Minutes</strong>
          </div>
          <div className="summary-field">
            <span>Activity:</span>
            <strong style={{ textTransform: 'capitalize' }}>{mission.activity_type}</strong>
          </div>
        </div>
      )}

      <div className="anti-engagement-prompt">
        <p>
          Now, keep your momentum going: carry on with your day and enjoy your refreshed headspace.
        </p>
      </div>

      <div className="completion-actions">
        <button type="button" className="btn-primary" onClick={onPlanAnother}>
          Create Another Mission
        </button>
        <button type="button" className="btn-secondary" onClick={onViewHistory}>
          View History & Stats
        </button>
      </div>
    </div>
  );
}
