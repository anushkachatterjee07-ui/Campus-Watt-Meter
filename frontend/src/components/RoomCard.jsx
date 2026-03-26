function RoomCard({ room, index, onToggleLight }) {
  const getStatusClass = () => {
    if (room.wastage) return 'wastage';
    if (room.occupancy === 'occupied') return 'occupied';
    return 'empty';
  };

  const getStatusLabel = () => {
    if (room.wastage) return '⚡ Energy Wastage';
    if (room.occupancy === 'occupied') return '🟢 Occupied';
    return '⚪ Empty';
  };

  const getTimeAgo = (timestamp) => {
    const diff = Date.now() - new Date(timestamp).getTime();
    const seconds = Math.floor(diff / 1000);
    if (seconds < 60) return `${seconds}s ago`;
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes}m ago`;
    return `${Math.floor(minutes / 60)}h ago`;
  };

  return (
    <div
      className={`room-card ${getStatusClass()}`}
      style={{ animationDelay: `${index * 0.06}s` }}
      id={`room-${room.room_id}`}
    >
      <div className="room-card-header">
        <h3 className="room-id">{room.room_id}</h3>
        <span className={`status-badge ${getStatusClass()}`}>
          {getStatusLabel()}
        </span>
      </div>

      <div className="room-card-body">
        <div className="room-metric">
          <span className="metric-label">Persons</span>
          <span className="metric-value">{room.person_count}</span>
        </div>
        <div className="room-metric">
          <span className="metric-label">Confidence</span>
          <span className="metric-value">
            {room.confidence > 0 ? `${(room.confidence * 100).toFixed(0)}%` : '—'}
          </span>
        </div>
        <div className="room-metric">
          <span className="metric-label">Light</span>
          <button
            className={`light-toggle ${room.light_status}`}
            onClick={() => onToggleLight(room.room_id)}
            title="Toggle light status"
            id={`light-toggle-${room.room_id}`}
          >
            {room.light_status === 'on' ? '💡' : '🌑'}
            <span>{room.light_status.toUpperCase()}</span>
          </button>
        </div>
      </div>

      <div className="room-card-footer">
        <span className="update-time">Updated {getTimeAgo(room.last_updated)}</span>
      </div>
    </div>
  );
}

export default RoomCard;
