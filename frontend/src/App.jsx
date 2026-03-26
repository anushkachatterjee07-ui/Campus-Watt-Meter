import { useState, useEffect, useCallback } from 'react';
import Header from './components/Header';
import StatsBar from './components/StatsBar';
import RoomCard from './components/RoomCard';
import AlertPanel from './components/AlertPanel';
import EnergyChart from './components/EnergyChart';
import VideoFeed from './components/VideoFeed';
import './App.css';

const API_URL = 'http://localhost:8000';

function App() {
  const [rooms, setRooms] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [cvStatus, setCvStatus] = useState(null);

  const fetchData = useCallback(async () => {
    try {
      const [statusRes, alertsRes, statsRes, cvRes] = await Promise.all([
        fetch(`${API_URL}/status`),
        fetch(`${API_URL}/alerts`),
        fetch(`${API_URL}/stats`),
        fetch(`${API_URL}/cv/status`),
      ]);

      if (!statusRes.ok || !alertsRes.ok || !statsRes.ok) {
        throw new Error('Backend returned an error');
      }

      const [statusData, alertsData, statsData] = await Promise.all([
        statusRes.json(),
        alertsRes.json(),
        statsRes.json(),
      ]);

      setRooms(statusData);
      setAlerts(alertsData);
      setStats(statsData);
      setLastUpdate(new Date());
      setLoading(false);
      setError(null);

      if (cvRes.ok) {
        setCvStatus(await cvRes.json());
      }
    } catch (err) {
      setError('Unable to connect to the backend. Make sure the server is running on port 8000.');
      setLoading(false);
    }
  }, []);

  const seedData = async () => {
    try {
      await fetch(`${API_URL}/seed`, { method: 'POST' });
      await fetchData();
    } catch (err) {
      setError('Failed to seed demo data');
    }
  };

  const toggleLight = async (roomId) => {
    try {
      await fetch(`${API_URL}/toggle-light/${roomId}`, { method: 'PATCH' });
      await fetchData();
    } catch (err) {
      console.error('Failed to toggle light:', err);
    }
  };

  const startCV = async () => {
    try {
      await fetch(`${API_URL}/cv/start`, { method: 'POST' });
      await fetchData();
    } catch (err) {
      console.error('Failed to start CV:', err);
    }
  };

  const stopCV = async () => {
    try {
      await fetch(`${API_URL}/cv/stop`, { method: 'POST' });
      await fetchData();
    } catch (err) {
      console.error('Failed to stop CV:', err);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, [fetchData]);

  return (
    <div className="app">
      <Header lastUpdate={lastUpdate} />

      <main className="main-content">
        {error && (
          <div className="error-banner" id="error-banner">
            <span className="error-icon">⚠️</span>
            <span>{error}</span>
            <button className="retry-btn" onClick={fetchData}>Retry</button>
          </div>
        )}

        <StatsBar stats={stats} loading={loading} />

        <VideoFeed cvStatus={cvStatus} onStart={startCV} onStop={stopCV} />

        <div className="content-layout">
          <section className="rooms-section">
            <div className="section-header">
              <h2>Room Monitoring</h2>
              <div className="section-actions">
                <button className="seed-btn" id="seed-btn" onClick={seedData}>
                  🔄 Load Demo Data
                </button>
              </div>
            </div>

            {loading ? (
              <div className="loading-state">
                <div className="spinner"></div>
                <p>Connecting to monitoring system...</p>
              </div>
            ) : rooms.length === 0 ? (
              <div className="empty-state">
                <div className="empty-icon">📡</div>
                <h3>No Rooms Monitored</h3>
                <p>Start the camera or load demo data to begin monitoring.</p>
                <button className="seed-btn primary" onClick={startCV}>
                  Start Camera
                </button>
                <button className="seed-btn" onClick={seedData} style={{marginLeft: '10px'}}>
                  Load Demo Data
                </button>
              </div>
            ) : (
              <div className="room-grid" id="room-grid">
                {rooms.map((room, index) => (
                  <RoomCard
                    key={room.room_id}
                    room={room}
                    index={index}
                    onToggleLight={toggleLight}
                  />
                ))}
              </div>
            )}
          </section>

          <aside className="sidebar">
            <AlertPanel alerts={alerts} />
            {stats && stats.total_rooms > 0 && (
              <EnergyChart stats={stats} rooms={rooms} />
            )}
          </aside>
        </div>
      </main>
    </div>
  );
}

export default App;
