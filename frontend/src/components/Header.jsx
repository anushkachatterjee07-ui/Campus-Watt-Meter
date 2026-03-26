import { useState, useEffect } from 'react';

function Header({ lastUpdate }) {
  const [time, setTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <header className="header" id="header">
      <div className="header-left">
        <div className="logo">
          <span className="logo-icon">🛡️</span>
          <div className="logo-text">
            <h1>GreenGuard</h1>
            <span className="logo-subtitle">AI Energy Monitor</span>
          </div>
        </div>
      </div>
      <div className="header-right">
        <div className="live-indicator" id="live-indicator">
          <span className="live-dot"></span>
          <span>LIVE</span>
        </div>
        <div className="header-time">
          <span className="time-value">{time.toLocaleTimeString()}</span>
          <span className="time-date">
            {time.toLocaleDateString('en-US', {
              weekday: 'short',
              month: 'short',
              day: 'numeric',
            })}
          </span>
        </div>
      </div>
    </header>
  );
}

export default Header;
