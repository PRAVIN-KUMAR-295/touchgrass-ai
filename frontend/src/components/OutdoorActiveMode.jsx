import React, { useEffect, useState } from 'react';

export default function OutdoorActiveMode({ mission, onComplete, onAbandon }) {
  const [secondsElapsed, setSecondsElapsed] = useState(0);
  const [submitting, setSubmitting] = useState(false);
  const [checkedSteps, setCheckedSteps] = useState({});

  const totalDurationSeconds = (mission.duration_minutes || 30) * 60;

  useEffect(() => {
    const timerInterval = setInterval(() => {
      setSecondsElapsed((prev) => prev + 1);
    }, 1000);

    return () => clearInterval(timerInterval);
  }, []);

  const formatTime = (totalSeconds) => {
    const mins = Math.floor(totalSeconds / 60);
    const secs = totalSeconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const toggleStep = (idx) => {
    setCheckedSteps((prev) => ({
      ...prev,
      [idx]: !prev[idx],
    }));
  };

  const handleCompleteClick = async () => {
    setSubmitting(true);
    try {
      await onComplete(mission.id);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="active-mode-card" role="region" aria-label="Outdoor Active Mission Mode">
      {/* Phone Away Notice */}
      <div className="active-phone-banner">
        <span className="active-phone-icon" aria-hidden="true">📵</span>
        <div>
          <h3>Put your phone away and go</h3>
          <p>Read your steps once, pocket your device, and immerse yourself in the outdoors.</p>
        </div>
      </div>

      {/* Header Info */}
      <div className="active-mission-header">
        <h2 className="active-title">{mission.title}</h2>
        <div className="active-meta-tags" aria-label="Mission Details">
          <span className="badge-duration">⏱️ Goal: {mission.duration_minutes} Mins</span>
          <span className="badge-activity" style={{ textTransform: 'capitalize' }}>🌿 {mission.activity_type}</span>
          <span className="badge-difficulty" style={{ textTransform: 'capitalize' }}>🎯 {mission.difficulty}</span>
          <span className="badge-mode" style={{ textTransform: 'capitalize' }}>{mission.mode}</span>
        </div>
      </div>

      {/* Outdoor Timer Widget */}
      <div className="outdoor-timer-display" role="timer" aria-label="Outdoor Session Timer">
        <div className="timer-block">
          <span className="timer-label">Time Outdoors</span>
          <span className="timer-value" aria-live="off">{formatTime(secondsElapsed)}</span>
        </div>
        <div className="timer-divider" aria-hidden="true">/</div>
        <div className="timer-block">
          <span className="timer-label">Target Duration</span>
          <span className="timer-value">{formatTime(totalDurationSeconds)}</span>
        </div>
      </div>

      {/* Mission Steps Checklist */}
      <div className="active-checklist-section">
        <h4 className="checklist-heading" id="steps-checklist-heading">Actionable Steps Checklist</h4>
        <div className="checklist-items" role="group" aria-labelledby="steps-checklist-heading">
          {mission.steps?.map((step, idx) => {
            const isChecked = !!checkedSteps[idx];
            return (
              <label
                key={idx}
                className={`checklist-item ${isChecked ? 'completed' : ''}`}
                tabIndex="0"
                onKeyDown={(e) => {
                  if (e.key === ' ' || e.key === 'Enter') {
                    e.preventDefault();
                    toggleStep(idx);
                  }
                }}
              >
                <input
                  type="checkbox"
                  checked={isChecked}
                  onChange={() => toggleStep(idx)}
                  aria-label={`Step ${idx + 1}: ${step}`}
                />
                <span className="checkmark-box" aria-hidden="true">{isChecked ? '✓' : ''}</span>
                <span className="step-label">{step}</span>
              </label>
            );
          })}
        </div>
      </div>

      {/* Safety Notice */}
      {mission.safety_note && (
        <div className="active-safety-reminder" role="note" aria-label="Safety Guidance">
          <strong>🛡️ Safety Guidance:</strong> {mission.safety_note}
        </div>
      )}

      {/* Action Buttons */}
      <div className="active-actions-group">
        <button
          type="button"
          className="btn-primary btn-complete"
          onClick={handleCompleteClick}
          disabled={submitting}
          aria-label="Complete Outdoor Mission"
        >
          {submitting ? 'Recording Completion...' : '✓ Complete Mission'}
        </button>

        <button
          type="button"
          className="btn-abandon"
          onClick={onAbandon}
          disabled={submitting}
          aria-label="Cancel mission and return to home"
        >
          Cancel / Return Home
        </button>
      </div>
    </div>
  );
}
