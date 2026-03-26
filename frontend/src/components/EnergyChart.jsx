import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';

function EnergyChart({ stats, rooms }) {
  const wastageEmpty = stats.wastage_count;
  const efficientEmpty = stats.empty - stats.wastage_count;

  const data = [
    { name: 'Occupied', value: stats.occupied, color: '#10b981' },
    { name: 'Efficient (Empty)', value: efficientEmpty, color: '#64748b' },
    { name: 'Wastage', value: wastageEmpty, color: '#ef4444' },
  ].filter((d) => d.value > 0);

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div className="chart-tooltip">
          <p className="tooltip-label">{payload[0].name}</p>
          <p className="tooltip-value">
            {payload[0].value} room{payload[0].value !== 1 ? 's' : ''}
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="energy-chart" id="energy-chart">
      <div className="chart-header">
        <h3>
          <span className="chart-icon">📊</span>
          Room Distribution
        </h3>
      </div>
      <div className="chart-container">
        <ResponsiveContainer width="100%" height={200}>
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={55}
              outerRadius={80}
              paddingAngle={4}
              dataKey="value"
              stroke="none"
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
          </PieChart>
        </ResponsiveContainer>
        <div className="chart-center-label">
          <span className="efficiency-value">{stats.efficiency_rate}%</span>
          <span className="efficiency-label">Efficient</span>
        </div>
      </div>
      <div className="chart-legend">
        {data.map((item) => (
          <div key={item.name} className="legend-item">
            <span className="legend-dot" style={{ background: item.color }}></span>
            <span className="legend-text">{item.name}</span>
            <span className="legend-value">{item.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default EnergyChart;
