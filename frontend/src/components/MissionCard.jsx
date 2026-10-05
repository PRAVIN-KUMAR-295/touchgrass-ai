import React from 'react';

export default function MissionCard({ mission, onStart, onPlanAnother }) {
  if (!mission) return null;

  return (
    <div className="mission-card-view" role="article" aria-label="Generated Outdoor Mission">
      {/* Header Banner & Metadata */}
      <div className="mission-card-header">
        <div className="mission-tags" aria-label="Mission Attributes">
          <span className="badge-duration">⏱️ {mission.duration_minutes} Mins</span>
          <span className="badge-activity" style={{ textTransform: 'capitalize' }}>
            🌿 {mission.activity_type}
          </span>
          <span className="badge-difficulty" style={{ textTransform: 'capitalize' }}>
            🎯 {mission.difficulty}
          </span>
          <span className="badge-mode" style={{ textTransform: 'capitalize' }}>
            {mission.mode === 'friends' ? '👫 With Friends' : '🧘 Solo'}
          </span>
        </div>
        <h2 className="mission-card-title">{mission.title}</h2>
      </div>

      {/* Screen Disconnect Banner */}
      <div className="put-phone-away-banner">
        <span className="banner-icon" aria-hidden="true">📵</span>
        <div>
          <h4>Put your phone away and go.</h4>
          <p>Read your steps below, keep your device in your pocket, and immerse yourself in the outdoors.</p>
        </div>
      </div>

      {/* Mission Steps */}
      <div className="mission-steps-section">
        <h3 className="section-title">Outdoor Mission Steps</h3>
        <ol className="steps-list" aria-label="Steps list">
          {mission.steps?.map((step, idx) => (
            <li key={idx} className="step-item">
              <span className="step-number" aria-hidden="true">{idx + 1}</span>
              <span className="step-text">{step}</span>
            </li>
          ))}
        </ol>
      </div>

      {/* Safety Reminder */}
      {mission.safety_note && (
        <div className="safety-note-box" role="note" aria-label="Safety guidance">
          <span className="safety-icon" aria-hidden="true">🛡️</span>
          <div>
            <strong>Safety Guidance:</strong>
            <p>{mission.safety_note}</p>
          </div>
        </div>
      )}

      {/* Subtle Fallback Notice */}
      {mission.is_fallback && (
        <div className="subtle-fallback-notice" role="status">
          ℹ️ Using a ready-made mission while AI is unavailable.
        </div>
      )}

      {/* Action Footer */}
      <div className="mission-card-actions">
        <button
          type="button"
          className="btn-primary btn-start-mission"
          onClick={() => onStart && onStart(mission.id)}
          aria-label="Start this mission now"
        >
          🚀 Start Mission
        </button>
        <button
          type="button"
          className="btn-secondary"
          onClick={onPlanAnother}
          aria-label="Plan a different mission"
        >
          ← Plan Another Mission
        </button>
      </div>
    </div>
  );
}
