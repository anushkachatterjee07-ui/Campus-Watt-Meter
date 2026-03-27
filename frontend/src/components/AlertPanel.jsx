function AlertPanel({ alerts }) {
  const getTimeAgo = (timestamp) => {
    const diff = Date.now() - new Date(timestamp).getTime();
    const seconds = Math.floor(diff / 1000);
    if (seconds < 60) return `${seconds}s ago`;
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes}m ago`;
    return `${Math.floor(minutes / 60)}h ago`;
  };

  return (
    <div className="alert-panel" id="alert-panel">
      <div className="alert-panel-header">
        <h3>
          <span className="alert-icon">⚡</span>
          Energy Waste Alerts
        </h3>
        {alerts.length > 0 && (
          <span className="alert-count">{alerts.length}</span>
        )}
      </div>
      <div className="alert-list">
        {alerts.length === 0 ? (
          <div className="no-alerts">
            <span className="no-alerts-icon">✅</span>
            <p>No energy wastage detected</p>
            <span className="no-alerts-sub">All systems operating efficiently</span>
          </div>
        ) : (
          alerts.map((alert) => (
            <div key={alert.id} className="alert-item" id={`alert-${alert.room_id}`}>
              <div className="alert-pulse"></div>
              <div className="alert-info">
                <span className="alert-room">{alert.room_id}</span>
                <span className="alert-message">{alert.message}</span>
              </div>
              <span className="alert-time">{getTimeAgo(alert.timestamp)}</span>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default AlertPanel;
