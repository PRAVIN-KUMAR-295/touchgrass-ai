import React, { useEffect, useState } from 'react';
import { api } from './api/client';
import MissionSetup from './components/MissionSetup';
import MissionCard from './components/MissionCard';
import OutdoorActiveMode from './components/OutdoorActiveMode';
import CompletionScreen from './components/CompletionScreen';
import HistoryList from './components/HistoryList';
import StatsWidget from './components/StatsWidget';

export default function App() {
  const [apiHealth, setApiHealth] = useState(null);
  const [currentView, setCurrentView] = useState('home'); // 'home' | 'setup' | 'mission' | 'active' | 'completed' | 'history' | 'stats'
  const [currentMission, setCurrentMission] = useState(null);
  const [actionError, setActionError] = useState(null);

  useEffect(() => {
    api.getHealth()
      .then((data) => setApiHealth(data))
      .catch(() => setApiHealth({ status: 'offline' }));
  }, []);

  const handleStartSetup = () => {
    setActionError(null);
    setCurrentView('setup');
  };

  const handleMissionGenerated = (missionPlan) => {
    setActionError(null);
    setCurrentMission(missionPlan);
    setCurrentView('mission');
  };

  const handleStartMission = async (missionId) => {
    setActionError(null);
    try {
      const updated = await api.startMission(missionId);
      setCurrentMission((prev) => ({ ...prev, ...updated }));
      setCurrentView('active');
    } catch (err) {
      setActionError(err.message || 'Could not start mission. Please try again.');
    }
  };

  const handleCompleteMission = async (missionId) => {
    setActionError(null);
    try {
      const completedRecord = await api.completeMission(missionId);
      setCurrentMission((prev) => ({ ...prev, ...completedRecord }));
      setCurrentView('completed');
    } catch (err) {
      setActionError(err.message || 'Could not record completion. Please try again.');
    }
  };

  const handleResetToHome = () => {
    setActionError(null);
    setCurrentMission(null);
    setCurrentView('home');
  };

  return (
    <div className="app-container">
      {/* Navigation Bar */}
      <nav className="navbar" aria-label="Main Navigation">
        <button
          type="button"
          className="brand brand-btn"
          onClick={handleResetToHome}
          aria-label="TouchGrass AI Home"
        >
          <span className="brand-icon" aria-hidden="true">🌱</span>
          <span>TouchGrass AI</span>
        </button>

        {/* Global Navigation Links */}
        <div className="nav-links" role="menubar">
          <button
            type="button"
            role="menuitem"
            className={`nav-btn ${currentView === 'home' ? 'active' : ''}`}
            onClick={handleResetToHome}
            aria-current={currentView === 'home' ? 'page' : undefined}
          >
            Home
          </button>
          <button
            type="button"
            role="menuitem"
            className={`nav-btn ${currentView === 'setup' ? 'active' : ''}`}
            onClick={handleStartSetup}
            aria-current={currentView === 'setup' ? 'page' : undefined}
          >
            Plan
          </button>
          <button
            type="button"
            role="menuitem"
            className={`nav-btn ${currentView === 'history' ? 'active' : ''}`}
            onClick={() => { setActionError(null); setCurrentView('history'); }}
            aria-current={currentView === 'history' ? 'page' : undefined}
          >
            History
          </button>
          <button
            type="button"
            role="menuitem"
            className={`nav-btn ${currentView === 'stats' ? 'active' : ''}`}
            onClick={() => { setActionError(null); setCurrentView('stats'); }}
            aria-current={currentView === 'stats' ? 'page' : undefined}
          >
            Stats
          </button>
        </div>

        <div className="nav-status" aria-label={`System status: ${apiHealth?.status === 'healthy' ? 'online' : 'offline'}`}>
          <span
            className="status-dot"
            aria-hidden="true"
            style={{
              backgroundColor: apiHealth?.status === 'healthy' ? '#2d6a4f' : '#cf222e',
            }}
          />
          <span className="status-text">{apiHealth?.status === 'healthy' ? 'Online' : 'Offline'}</span>
        </div>
      </nav>

      {/* Main Content View Switcher */}
      <main className="main-content" id="main-content">
        {actionError && (
          <div className="alert-error" role="alert" aria-live="assertive">
            <strong>Notice:</strong> {actionError}
          </div>
        )}

        {currentView === 'home' && (
          <>
            <section className="hero">
              <div className="hero-tag">Hacktoberfest 2026 • Open-Source AI</div>
              <h1 className="hero-title">Step outside. Disconnect. Touch Grass.</h1>
              <p className="hero-subtitle">
                An open-source AI outdoor mission planner that gets you off your screen and out into the real world.
              </p>

              <div className="cta-group">
                <button
                  className="btn-primary"
                  onClick={handleStartSetup}
                  aria-label="Create a new outdoor mission"
                >
                  <span aria-hidden="true">✨</span>
                  <span>Create Mission</span>
                </button>
                <button
                  className="btn-secondary"
                  onClick={() => setCurrentView('stats')}
                  aria-label="View outdoor statistics"
                >
                  <span aria-hidden="true">📊</span>
                  <span>View Stats</span>
                </button>
              </div>
            </section>

            {/* Anti-Screen Banner */}
            <div className="anti-screen-banner" role="region" aria-label="Philosophy">
              <h4>📵 Screen-Minimal By Design</h4>
              <p>
                TouchGrass AI is built to give you a quick, actionable outdoor objective — then instruct you to put your phone away.
              </p>
            </div>

            {/* Feature Highlights */}
            <section className="features-grid" aria-label="Key Features">
              <div className="feature-card">
                <div className="feature-icon" aria-hidden="true">⏱️</div>
                <h3>Micro-Missions</h3>
                <p>15, 30, or 60 minute targeted prompts that fit effortlessly into your day.</p>
              </div>

              <div className="feature-card">
                <div className="feature-icon" aria-hidden="true">🌿</div>
                <h3>Nature & Exploration</h3>
                <p>Engage your senses with mindful walks, outdoor photography, and nature scavenger steps.</p>
              </div>

              <div className="feature-card">
                <div className="feature-icon" aria-hidden="true">🤖</div>
                <h3>Open-Weight Gemma AI</h3>
                <p>Powered by Google&apos;s open-weight Gemma model with reliable safety and deterministic fallbacks.</p>
              </div>
            </section>
          </>
        )}

        {currentView === 'setup' && (
          <MissionSetup
            onBack={handleResetToHome}
            onMissionGenerated={handleMissionGenerated}
          />
        )}

        {currentView === 'mission' && (
          <MissionCard
            mission={currentMission}
            onStart={handleStartMission}
            onPlanAnother={handleStartSetup}
          />
        )}

        {currentView === 'active' && (
          <OutdoorActiveMode
            mission={currentMission}
            onComplete={handleCompleteMission}
            onAbandon={handleResetToHome}
          />
        )}

        {currentView === 'completed' && (
          <CompletionScreen
            mission={currentMission}
            onPlanAnother={handleStartSetup}
            onViewHistory={() => setCurrentView('history')}
          />
        )}

        {currentView === 'history' && (
          <HistoryList onPlanMission={handleStartSetup} />
        )}

        {currentView === 'stats' && (
          <StatsWidget onPlanMission={handleStartSetup} />
        )}
      </main>

      {/* Footer */}
      <footer className="footer" role="contentinfo">
        <p>TouchGrass AI — Open-source outdoor companion. Zero doomscrolling guaranteed.</p>
      </footer>
    </div>
  );
}
