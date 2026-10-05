import React, { useState } from 'react';
import { api } from '../api/client';

const DURATION_OPTIONS = [
  { value: 15, label: '15 Min', desc: 'Quick micro-break' },
  { value: 30, label: '30 Min', desc: 'Mindful excursion' },
  { value: 60, label: '60 Min', desc: 'Deep outdoor recharge' },
];

const ACTIVITY_OPTIONS = [
  { id: 'walking', label: 'Walking', icon: '🚶', desc: 'Brisk walk or stroll' },
  { id: 'nature', label: 'Nature', icon: '🌿', desc: 'Plants, trees, and earth' },
  { id: 'photography', label: 'Photography', icon: '📷', desc: 'Outdoor sights & light' },
  { id: 'exercise', label: 'Exercise', icon: '🏃', desc: 'Stretching & movement' },
  { id: 'social', label: 'Social', icon: '👥', desc: 'Outdoors with others' },
];

const DIFFICULTY_OPTIONS = [
  { id: 'easy', label: 'Easy', desc: 'Gentle & relaxing' },
  { id: 'medium', label: 'Medium', desc: 'Active & engaging' },
  { id: 'hard', label: 'Hard', desc: 'High energy' },
];

const MODE_OPTIONS = [
  { id: 'solo', label: 'Solo', icon: '🧘', desc: 'Quiet personal time' },
  { id: 'friends', label: 'With Friends', icon: '👫', desc: 'Shared activity' },
];

export default function MissionSetup({ onBack, onMissionGenerated }) {
  const [duration, setDuration] = useState(30);
  const [activity, setActivity] = useState('nature');
  const [difficulty, setDifficulty] = useState('easy');
  const [mode, setMode] = useState('solo');

  const [loading, setLoading] = useState(false);
  const [loadingStatus, setLoadingStatus] = useState('');
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    // Validation
    if (![15, 30, 60].includes(duration)) {
      setError('Please choose a valid duration (15, 30, or 60 minutes).');
      return;
    }
    if (!['walking', 'nature', 'photography', 'exercise', 'social'].includes(activity)) {
      setError('Please select an outdoor activity.');
      return;
    }
    if (!['easy', 'medium', 'hard'].includes(difficulty)) {
      setError('Please select a valid difficulty level.');
      return;
    }
    if (!['solo', 'friends'].includes(mode)) {
      setError('Please select a mode.');
      return;
    }

    setLoading(true);
    setLoadingStatus('Creating mission record...');

    try {
      const payload = {
        duration_minutes: duration,
        activity_type: activity,
        difficulty: difficulty,
        mode: mode,
      };
      const createdRecord = await api.createMission(payload);

      setLoadingStatus('Creating your outdoor mission...');
      const generatedPlan = await api.generateMission(createdRecord.id);

      onMissionGenerated(generatedPlan);
    } catch (err) {
      setError(err.message || 'Unable to generate mission. Please check your connection and try again.');
    } finally {
      setLoading(false);
      setLoadingStatus('');
    }
  };

  return (
    <div className="setup-container">
      <div className="setup-header">
        <button
          type="button"
          className="btn-back"
          onClick={onBack}
          aria-label="Return to home page"
        >
          ← Back to Home
        </button>
        <h2 className="setup-title" id="setup-heading">Plan Your Outdoor Mission</h2>
        <p className="setup-subtitle">
          Configure your outdoor break. Put your phone away once you start.
        </p>
      </div>

      {error && (
        <div className="alert-error" role="alert" aria-live="assertive">
          <strong>Notice:</strong> {error}
        </div>
      )}

      {loading ? (
        <div className="loading-state-box" role="status" aria-live="polite">
          <div className="spinner" aria-hidden="true">🌱</div>
          <h3>{loadingStatus}</h3>
          <p>Preparing practical outdoor steps with safety verification...</p>
        </div>
      ) : (
        <form
          onSubmit={handleSubmit}
          className="setup-form"
          aria-labelledby="setup-heading"
        >
          {/* Available Time */}
          <fieldset className="form-group">
            <legend className="group-label">1. Available Time</legend>
            <div className="pill-grid" role="radiogroup" aria-label="Available Time">
              {DURATION_OPTIONS.map((item) => {
                const isSelected = duration === item.value;
                return (
                  <button
                    type="button"
                    key={item.value}
                    role="radio"
                    aria-checked={isSelected}
                    className={`choice-card ${isSelected ? 'selected' : ''}`}
                    onClick={() => setDuration(item.value)}
                  >
                    <div className="choice-title">{item.label}</div>
                    <div className="choice-desc">{item.desc}</div>
                  </button>
                );
              })}
            </div>
          </fieldset>

          {/* Activity Type */}
          <fieldset className="form-group">
            <legend className="group-label">2. Activity Type</legend>
            <div className="pill-grid" role="radiogroup" aria-label="Activity Type">
              {ACTIVITY_OPTIONS.map((item) => {
                const isSelected = activity === item.id;
                return (
                  <button
                    type="button"
                    key={item.id}
                    role="radio"
                    aria-checked={isSelected}
                    className={`choice-card ${isSelected ? 'selected' : ''}`}
                    onClick={() => setActivity(item.id)}
                  >
                    <div className="choice-title">
                      <span aria-hidden="true">{item.icon}</span> {item.label}
                    </div>
                    <div className="choice-desc">{item.desc}</div>
                  </button>
                );
              })}
            </div>
          </fieldset>

          {/* Difficulty */}
          <fieldset className="form-group">
            <legend className="group-label">3. Difficulty</legend>
            <div className="pill-grid" role="radiogroup" aria-label="Difficulty">
              {DIFFICULTY_OPTIONS.map((item) => {
                const isSelected = difficulty === item.id;
                return (
                  <button
                    type="button"
                    key={item.id}
                    role="radio"
                    aria-checked={isSelected}
                    className={`choice-card ${isSelected ? 'selected' : ''}`}
                    onClick={() => setDifficulty(item.id)}
                  >
                    <div className="choice-title">{item.label}</div>
                    <div className="choice-desc">{item.desc}</div>
                  </button>
                );
              })}
            </div>
          </fieldset>

          {/* Mode */}
          <fieldset className="form-group">
            <legend className="group-label">4. Mode</legend>
            <div className="pill-grid" role="radiogroup" aria-label="Mode">
              {MODE_OPTIONS.map((item) => {
                const isSelected = mode === item.id;
                return (
                  <button
                    type="button"
                    key={item.id}
                    role="radio"
                    aria-checked={isSelected}
                    className={`choice-card ${isSelected ? 'selected' : ''}`}
                    onClick={() => setMode(item.id)}
                  >
                    <div className="choice-title">
                      <span aria-hidden="true">{item.icon}</span> {item.label}
                    </div>
                    <div className="choice-desc">{item.desc}</div>
                  </button>
                );
              })}
            </div>
          </fieldset>

          {/* Action Button */}
          <div className="submit-section">
            <button
              type="submit"
              className="btn-primary btn-block"
              disabled={loading}
              aria-label="Generate Outdoor Mission"
            >
              Generate Mission
            </button>
          </div>
        </form>
      )}
    </div>
  );
}
