function StatsBar({ stats, loading }) {
  const statItems = [
    { label: 'Total Rooms', value: stats?.total_rooms ?? '—', icon: '🏢', color: 'blue' },
    { label: 'Occupied', value: stats?.occupied ?? '—', icon: '👥', color: 'green' },
    { label: 'Empty', value: stats?.empty ?? '—', icon: '🚪', color: 'slate' },
    { label: 'Wastage Alerts', value: stats?.wastage_count ?? '—', icon: '⚡', color: 'red' },
  ];

  return (
    <div className="stats-bar" id="stats-bar">
      {statItems.map((item) => (
        <div
          key={item.label}
          className={`stat-card stat-${item.color} ${loading ? 'loading' : ''}`}
          id={`stat-${item.color}`}
        >
          <div className="stat-icon">{item.icon}</div>
          <div className="stat-info">
            <span className="stat-value">
              {loading ? '' : item.value}
            </span>
            <span className="stat-label">{item.label}</span>
          </div>
        </div>
      ))}
    </div>
  );
}

export default StatsBar;
