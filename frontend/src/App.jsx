
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
import {
  ResponsiveContainer,
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts";
import "./App.css";

const API = "http://127.0.0.1:8000/api";

const CHART_COLORS = ["#65e6c4", "#ff8a65", "#a78bfa", "#facc15"];

const tooltipStyle = {
  backgroundColor: "#111927",
  border: "1px solid #2b384c",
  borderRadius: 8,
  color: "#e5e7eb",
};

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
      setError(
        "Could not load data. Check that Django is running and the token is valid."
      );
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
    (alert) =>
      alert.severity === "HIGH" || alert.severity === "CRITICAL"
  ).length;

  // Chart 1: Events grouped by type.
  const eventTypeData = [
    {
      name: "Login Success",
      count: events.filter(
        (event) => event.event_type === "LOGIN_SUCCESS"
      ).length,
    },
    {
      name: "Login Failure",
      count: events.filter(
        (event) => event.event_type === "LOGIN_FAILURE"
      ).length,
    },
    {
      name: "Suspicious Activity",
      count: events.filter(
        (event) => event.event_type === "SUSPICIOUS_ACTIVITY"
      ).length,
    },
  ];

  // Chart 2: Alerts grouped by severity.
  const severityData = ["LOW", "MEDIUM", "HIGH", "CRITICAL"].map(
    (severity) => ({
      name: severity,
      count: alerts.filter((alert) => alert.severity === severity).length,
    })
  );

  // Chart 3: Events per day over the last seven calendar days.
  const timelineData = (() => {
    const days = [];

    for (let i = 6; i >= 0; i--) {
      const date = new Date();
      date.setHours(0, 0, 0, 0);
      date.setDate(date.getDate() - i);

      const key = [
        date.getFullYear(),
        String(date.getMonth() + 1).padStart(2, "0"),
        String(date.getDate()).padStart(2, "0"),
      ].join("-");

      days.push({
        key,
        date: date.toLocaleDateString("en-US", {
          month: "short",
          day: "numeric",
        }),
        count: 0,
      });
    }

    events.forEach((event) => {
      const timestamp = new Date(event.timestamp);

      if (Number.isNaN(timestamp.getTime())) return;

      const key = [
        timestamp.getFullYear(),
        String(timestamp.getMonth() + 1).padStart(2, "0"),
        String(timestamp.getDate()).padStart(2, "0"),
      ].join("-");

      const day = days.find((item) => item.key === key);

      if (day) {
        day.count += 1;
      }
    });

    return days;
  })();

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">
            <ShieldCheck size={24} />
          </div>
          <div>
            <h2>Mini-SIEM</h2>
            <span>SECURITY OPERATIONS</span>
          </div>
        </div>

        <div className="nav-label">WORKSPACE</div>
        <div className="nav-item active">
          <Activity size={18} /> Overview
        </div>
        <div className="nav-item">
          <AlertTriangle size={18} /> Security Alerts
        </div>
        <div className="nav-item">
          <LockKeyhole size={18} /> Event Monitoring
        </div>

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
            <p>
              Monitor security events and investigate suspicious activity.
            </p>
          </div>

          {token && (
            <button
              className="refresh-button"
              onClick={() => loadDashboard(token)}
              disabled={loading}
            >
              <RefreshCw size={16} />
              {loading ? "Refreshing..." : "Refresh"}
            </button>
          )}
        </header>

        {!token ? (
          <section className="login-card">
            <div className="login-icon">
              <ShieldCheck size={28} />
            </div>
            <h2>Sign in to your SIEM</h2>
            <p>Use your Django account to access security monitoring data.</p>

            <form onSubmit={login}>
              <label>Username</label>
              <input
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
              />

              <label>Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />

              <button
                className="primary-button"
                type="submit"
                disabled={loading}
              >
                <LogIn size={17} />
                {loading ? "Signing in..." : "Sign in"}
              </button>
            </form>

            {error && <div className="error-message">{error}</div>}
          </section>
        ) : (
          <>
            {error && <div className="error-message">{error}</div>}

            <section className="stats-grid">
              <article className="stat-card">
                <div className="stat-top">
                  <span>Total Events</span>
                  <Activity />
                </div>
                <strong>{events.length}</strong>
                <small>Recorded security events</small>
              </article>

              <article className="stat-card">
                <div className="stat-top">
                  <span>Total Alerts</span>
                  <AlertTriangle />
                </div>
                <strong>{alerts.length}</strong>
                <small>Generated detections</small>
              </article>

              <article className="stat-card">
                <div className="stat-top">
                  <span>High Priority</span>
                  <ShieldCheck />
                </div>
                <strong>{highAlerts}</strong>
                <small>High and critical alerts</small>
              </article>

              <article className="stat-card">
                <div className="stat-top">
                  <span>Open Alerts</span>
                  <LockKeyhole />
                </div>
                <strong>
                  {alerts.filter((alert) => alert.status === "OPEN").length}
                </strong>
                <small>Awaiting investigation</small>
              </article>
            </section>

            {/* Security analytics charts */}
            <section className="charts-grid">
              <article className="panel chart-panel">
                <div className="panel-heading">
                  <div>
                    <h2>Security Events</h2>
                    <p>Event activity over the last seven days</p>
                  </div>
                </div>

                <div className="chart-container">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={timelineData}>
                      <CartesianGrid
                        strokeDasharray="3 3"
                        stroke="#263246"
                      />
                      <XAxis dataKey="date" stroke="#8291a5" />
                      <YAxis
                        allowDecimals={false}
                        stroke="#8291a5"
                      />
                      <Tooltip contentStyle={tooltipStyle} />
                      <Line
                        type="monotone"
                        dataKey="count"
                        name="Events"
                        stroke="#65e6c4"
                        strokeWidth={3}
                        dot={{ r: 4, fill: "#65e6c4" }}
                        activeDot={{ r: 6 }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </article>

              <article className="panel chart-panel">
                <div className="panel-heading">
                  <div>
                    <h2>Alerts by Severity</h2>
                    <p>Distribution of detected alerts</p>
                  </div>
                </div>

                <div className="chart-container">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={severityData}>
                      <CartesianGrid
                        strokeDasharray="3 3"
                        stroke="#263246"
                      />
                      <XAxis dataKey="name" stroke="#8291a5" />
                      <YAxis
                        allowDecimals={false}
                        stroke="#8291a5"
                      />
                      <Tooltip contentStyle={tooltipStyle} />
                      <Bar
                        dataKey="count"
                        name="Alerts"
                        fill="#65e6c4"
                        radius={[5, 5, 0, 0]}
                      />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </article>

              <article className="panel chart-panel event-type-panel">
                <div className="panel-heading">
                  <div>
                    <h2>Events by Type</h2>
                    <p>Breakdown of recorded security events</p>
                  </div>
                </div>

                <div className="chart-container">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={eventTypeData}
                        dataKey="count"
                        nameKey="name"
                        cx="50%"
                        cy="50%"
                        outerRadius={85}
                        paddingAngle={3}
                        label
                      >
                        {eventTypeData.map((entry, index) => (
                          <Cell
                            key={entry.name}
                            fill={CHART_COLORS[index]}
                          />
                        ))}
                      </Pie>
                      <Tooltip contentStyle={tooltipStyle} />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
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
                <p className="empty-state">
                  No alerts found. Submit test login failures to trigger
                  detection.
                </p>
              ) : (
                <div className="table-wrap">
                  <table>
                    <thead>
                      <tr>
                        <th>Alert</th>
                        <th>Source IP</th>
                        <th>Severity</th>
                        <th>Status</th>
                        <th>Created</th>
                      </tr>
                    </thead>
                    <tbody>
                      {alerts.map((alert) => (
                        <tr key={alert.id}>
                          <td>
                            <strong>{alert.title}</strong>
                            <small>{alert.description}</small>
                          </td>
                          <td>{alert.source_ip || "—"}</td>
                          <td>
                            <span
                              className={`severity ${alert.severity.toLowerCase()}`}
                            >
                              {alert.severity}
                            </span>
                          </td>
                          <td>
                            <select
                              className="status-select"
                              value={alert.status}
                              onChange={(e) =>
                                updateAlertStatus(
                                  alert.id,
                                  e.target.value
                                )
                              }
                            >
                              <option value="OPEN">Open</option>
                              <option value="INVESTIGATING">
                                Investigating
                              </option>
                              <option value="RESOLVED">Resolved</option>
                            </select>
                          </td>
                          <td>
                            {new Date(alert.created_at).toLocaleString()}
                          </td>
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
                  <p>
                    Search recorded authentication and suspicious activity
                    events.
                  </p>
                </div>

                <div className="search-box">
                  <Search size={16} />
                  <input
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    placeholder="Search IP, username, type..."
                  />
                </div>
              </div>

              <div className="table-wrap">
                <table>
                  <thead>
                    <tr>
                      <th>Event Type</th>
                      <th>Username</th>
                      <th>Source IP</th>
                      <th>Message</th>
                      <th>Timestamp</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredEvents.map((event) => (
                      <tr key={event.id}>
                        <td>{event.event_type}</td>
                        <td>{event.username || "—"}</td>
                        <td>{event.source_ip}</td>
                        <td>{event.message || "—"}</td>
                        <td>
                          {new Date(event.timestamp).toLocaleString()}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>

                {filteredEvents.length === 0 && (
                  <p className="empty-state">No matching events found.</p>
                )}
              </div>
            </section>
          </>
        )}
      </main>
    </div>
  );
}

export default App;
