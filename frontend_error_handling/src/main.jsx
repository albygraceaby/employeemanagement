import React, { useState } from "react";
import { createRoot } from "react-dom/client";
import "./style.css";

const API_BASE = "http://localhost:5000/api";

function getFriendlyMessage(status, rawMessage = "") {
  if (!navigator.onLine) return "You are offline. Please check your internet connection.";
  if (status === 400) return "The request could not be processed. Please check your details.";
  if (status === 401) return "Your session has expired. Please log in again.";
  if (status === 403) return "You do not have permission to perform this action.";
  if (status === 404) return "The requested resource was not found.";
  if (status === 409) return "This action conflicts with existing data. Please review and try again.";
  if (status === 429) return "Too many requests. Please wait a moment and try again.";
  if (status >= 500) return "Something went wrong on the server. Please try again later.";
  return rawMessage || "Something went wrong. Please try again.";
}

async function apiRequest(url, options = {}) {
  try {
    const response = await fetch(url, {
      ...options,
      headers: { "Content-Type": "application/json", ...(options.headers || {}) }
    });

    let data = {};
    try { data = await response.json(); } catch {}

    if (!response.ok) {
      const error = new Error(getFriendlyMessage(response.status, data.message));
      error.status = response.status;
      error.serverMessage = data.message || "";
      throw error;
    }
    return data;
  } catch (error) {
    if (error instanceof TypeError) {
      const e = new Error("Unable to connect to the backend. Please check that the server is running.");
      e.status = 0;
      throw e;
    }
    throw error;
  }
}

function ErrorAlert({ message, onClose }) {
  if (!message) return null;
  return (
    <div className="alert" role="alert">
      <span>⚠️ {message}</span>
      <button onClick={onClose} aria-label="Close error">×</button>
    </div>
  );
}

function App() {
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [jobs, setJobs] = useState([]);

  async function loadJobs() {
    setLoading(true);
    setMessage("");
    try {
      const data = await apiRequest(`${API_BASE}/jobs`);
      setJobs(data.jobs || []);
    } catch (error) {
      setMessage(error.message);
    } finally {
      setLoading(false);
    }
  }

  async function simulate(status) {
    setLoading(true);
    setMessage("");
    try {
      await apiRequest(`${API_BASE}/simulate/${status}`);
    } catch (error) {
      setMessage(error.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="container">
      <section className="card">
        <h1>Job Recommendation Portal</h1>
        <p className="subtitle">Inndhu – Frontend Error Handling Module</p>

        <ErrorAlert message={message} onClose={() => setMessage("")} />

        <div className="actions">
          <button className="primary" onClick={loadJobs} disabled={loading}>
            {loading ? "Loading..." : "Load Job Recommendations"}
          </button>
        </div>

        <div className="demo">
          <h2>Backend Error Demo</h2>
          <p>Test how the frontend converts API errors into user-friendly messages.</p>
          <div className="grid">
            {[400, 401, 403, 404, 429, 500].map((status) => (
              <button key={status} onClick={() => simulate(status)} disabled={loading}>
                Test HTTP {status}
              </button>
            ))}
          </div>
        </div>

        <div className="results">
          <h2>Recommendations</h2>
          {jobs.length === 0 ? (
            <p className="muted">No recommendations loaded yet.</p>
          ) : (
            jobs.map((job) => (
              <article className="job" key={job.id}>
                <div>
                  <h3>{job.title}</h3>
                  <p>{job.company} · {job.location}</p>
                </div>
                <span className="tag">{job.match}% match</span>
              </article>
            ))
          )}
        </div>

        <footer>
          <span>✓ API errors handled</span>
          <span>✓ User-friendly messages</span>
          <span>✓ Loading state</span>
          <span>✓ Network error handling</span>
        </footer>
      </section>
    </main>
  );
}

createRoot(document.getElementById("root")).render(<App />);
