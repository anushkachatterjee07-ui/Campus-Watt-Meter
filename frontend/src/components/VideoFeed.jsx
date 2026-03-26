function VideoFeed({ cvStatus, onStart, onStop }) {
  const isRunning = cvStatus?.running;

  return (
    <div className="video-feed-panel" id="video-feed-panel">
      <div className="video-feed-header">
        <h3>
          <span className="video-icon">📷</span>
          Live Camera Feed
        </h3>
        <div className="video-controls">
          {isRunning ? (
            <button className="cv-btn stop" onClick={onStop} id="cv-stop-btn">
              <span className="cv-btn-dot stop-dot"></span>
              Stop
            </button>
          ) : (
            <button className="cv-btn start" onClick={onStart} id="cv-start-btn">
              <span className="cv-btn-dot start-dot"></span>
              Start Camera
            </button>
          )}
        </div>
      </div>

      <div className="video-container">
        {isRunning ? (
          <>
            <img
              src="http://localhost:8000/video-feed"
              alt="Live camera feed with detection overlays"
              className="video-stream"
            />
            <div className="video-overlay-info">
              <span className="video-live-badge">
                <span className="video-live-pulse"></span>
                LIVE
              </span>
              <span className="video-room-label">Room {cvStatus.room_id}</span>
            </div>
            <div className="video-stats-bar">
              <span>Status: <strong>{cvStatus.current_state?.toUpperCase()}</strong></span>
              <span>Persons: <strong>{cvStatus.person_count}</strong></span>
              <span>Confidence: <strong>{cvStatus.confidence > 0 ? `${(cvStatus.confidence * 100).toFixed(0)}%` : '—'}</strong></span>
            </div>
          </>
        ) : (
          <div className="video-offline">
            <div className="offline-icon">📷</div>
            <p className="offline-title">Camera Offline</p>
            <p className="offline-sub">
              {cvStatus?.yolo_available
                ? 'Click "Start Camera" to begin detection'
                : '⚠ ultralytics not installed — run: pip install ultralytics'}
            </p>
            <button className="seed-btn primary" onClick={onStart}>
              Start Camera
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default VideoFeed;
