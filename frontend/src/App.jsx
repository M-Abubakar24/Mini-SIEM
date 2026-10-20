
import { useEffect, useState } from "react";
import axios from "axios";
import {
  ShieldCheck,
  Activity,
  AlertTriangle,
  RefreshCw,
  LogIn,
  Search,
  LockKeyhole,
} from "lucide-react";
import "./App.css";

const API = "http://127.0.0.1:8000/api";

function App() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [token, setToken] = useState("");
  const [alerts, setAlerts] = useState([]);
  const [events, setEvents] = useState([]);
  const [search, setSearch] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function login(e) {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const response = await axios.post(`${API}/token/`, {
        username,
        password,
      });
      setToken(response.data.access);
    } catch {
      setError("Login failed. Check your Django username and password.");
    } finally {
      setLoading(false);
    }
  }

  async function loadDashboard(accessToken) {
    setLoading(true);
    setError("");

    try {
      const config = {
        headers: { Authorization: `Bearer ${accessToken}` },
      };

      const [alertResponse, eventResponse] = await Promise.all([
        axios.get(`${API}/alerts/`, config),
        axios.get(`${API}/events/`, config),
      ]);

      setAlerts(alertResponse.data);
      setEvents(eventResponse.data);
    } catch {
      setError("Could not load data. Check that Django is running and the token is valid.");
    } finally {
      setLoading(false);
    }
  }
async function updateAlertStatus(alertId, status) {
  try {
    await axios.patch(
      `${API}/alerts/${alertId}/status/`,
      { status },
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    setAlerts((currentAlerts) =>
      currentAlerts.map((alert) =>
        alert.id === alertId ? { ...alert, status } : alert
      )
    );

    setError("");
  } catch {
    setError("Could not update alert status. Please try again.");
  }
}
  useEffect(() => {
    if (token) {
      loadDashboard(token);
    }
  }, [token]);

  const filteredEvents = events.filter((event) => {
    const query = search.toLowerCase();
    return (
      (event.username || "").toLowerCase().includes(query) ||
      (event.source_ip || "").toLowerCase().includes(query) ||
      (event.event_type || "").toLowerCase().includes(query) ||
      (event.message || "").toLowerCase().includes(query)
    );
  });

  const highAlerts = alerts.filter(
    (alert) => alert.severity === "HIGH" || alert.severity === "CRITICAL"
  ).length;

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon"><ShieldCheck size={24} /></div>
          <div>
            <h2>Mini-SIEM</h2>
            <span>SECURITY OPERATIONS</span>
          </div>
        </div>

        <div className="nav-label">WORKSPACE</div>
        <div className="nav-item active"><Activity size={18} /> Overview</div>
        <div className="nav-item"><AlertTriangle size={18} /> Security Alerts</div>
        <div className="nav-item"><LockKeyhole size={18} /> Event Monitoring</div>

        <div className="sidebar-bottom">
          <span className="status-dot" />
          Local monitoring system
          <small>Portfolio project · Development</small>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div>
            <span className="eyebrow">SECURITY CENTER / OVERVIEW</span>
            <h1>Security Operations Dashboard</h1>
            <p>Monitor security events and investigate suspicious activity.</p>
          </div>
          {token && (
            <button className="refresh-button" onClick={() => loadDashboard(token)}>
              <RefreshCw size={16} /> Refresh
            </button>
          )}
        </header>

        {!token ? (
          <section className="login-card">
            <div className="login-icon"><ShieldCheck size={28} /></div>
            <h2>Sign in to your SIEM</h2>
            <p>Use your Django account to access security monitoring data.</p>
            <form onSubmit={login}>
              <label>Username</label>
              <input value={username} onChange={(e) => setUsername(e.target.value)} required />
              <label>Password</label>
              <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
              <button className="primary-button" type="submit" disabled={loading}>
                <LogIn size={17} /> {loading ? "Signing in..." : "Sign in"}
              </button>
            </form>
            {error && <div className="error-message">{error}</div>}
          </section>
        ) : (
          <>
            {error && <div className="error-message">{error}</div>}

            <section className="stats-grid">
              <article className="stat-card">
                <div className="stat-top"><span>Total Events</span><Activity /></div>
                <strong>{events.length}</strong>
                <small>Recorded security events</small>
              </article>
              <article className="stat-card">
                <div className="stat-top"><span>Total Alerts</span><AlertTriangle /></div>
                <strong>{alerts.length}</strong>
                <small>Generated detections</small>
              </article>
              <article className="stat-card">
                <div className="stat-top"><span>High Priority</span><ShieldCheck /></div>
                <strong>{highAlerts}</strong>
                <small>High and critical alerts</small>
              </article>
              <article className="stat-card">
                <div className="stat-top"><span>Open Alerts</span><LockKeyhole /></div>
                <strong>{alerts.filter((a) => a.status === "OPEN").length}</strong>
                <small>Awaiting investigation</small>
              </article>
            </section>

            <section className="panel">
              <div className="panel-heading">
                <div>
                  <h2>Security Alerts</h2>
                  <p>Review detections generated by the backend.</p>
                </div>
                <span className="count-badge">{alerts.length} alerts</span>
              </div>

              {alerts.length === 0 ? (
                <p className="empty-state">No alerts found. Submit test login failures to trigger detection.</p>
              ) : (
                <div className="table-wrap">
                  <table>
                    <thead>
                      <tr><th>Alert</th><th>Source IP</th><th>Severity</th><th>Status</th><th>Created</th></tr>
                    </thead>
                    <tbody>
                      {alerts.map((alert) => (
                        <tr key={alert.id}>
                          <td><strong>{alert.title}</strong><small>{alert.description}</small></td>
                          <td>{alert.source_ip || "—"}</td>
                          <td><span className={`severity ${alert.severity.toLowerCase()}`}>{alert.severity}</span></td>
                          <td>
  <select
    className="status-select"
    value={alert.status}
    onChange={(e) => updateAlertStatus(alert.id, e.target.value)}
  >
    <option value="OPEN">Open</option>
    <option value="INVESTIGATING">Investigating</option>
    <option value="RESOLVED">Resolved</option>
  </select>
</td>
                          <td>{new Date(alert.created_at).toLocaleString()}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </section>

            <section className="panel">
              <div className="panel-heading">
                <div>
                  <h2>Event Log</h2>
                  <p>Search recorded authentication and suspicious activity events.</p>
                </div>
                <div className="search-box">
                  <Search size={16} />
                  <input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search IP, username, type..." />
                </div>
              </div>

              <div className="table-wrap">
                <table>
                  <thead>
                    <tr><th>Event Type</th><th>Username</th><th>Source IP</th><th>Message</th><th>Timestamp</th></tr>
                  </thead>
                  <tbody>
                    {filteredEvents.map((event) => (
                      <tr key={event.id}>
                        <td>{event.event_type}</td>
                        <td>{event.username || "—"}</td>
                        <td>{event.source_ip}</td>
                        <td>{event.message || "—"}</td>
                        <td>{new Date(event.timestamp).toLocaleString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                {filteredEvents.length === 0 && <p className="empty-state">No matching events found.</p>}
              </div>
            </section>
          </>
        )}
      </main>
    </div>
  );
}

export default App;
