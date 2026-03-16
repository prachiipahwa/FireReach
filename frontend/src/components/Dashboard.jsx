import React, { useState } from 'react';
import { runFireReachAgent } from '../api';
import { Play, CheckCircle2, AlertCircle, Activity, FileText, Send } from 'lucide-react';

const Dashboard = () => {
  const [formData, setFormData] = useState({
    icp: 'B2B SaaS companies focused on AI-driven sales enablement tools needing scalable infrastructure.',
    companyName: 'Acme Corp',
    targetEmail: 'founder@acmecorp.example.com',
  });
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await runFireReachAgent(
        formData.icp,
        formData.companyName,
        formData.targetEmail
      );
      setResult(data);
    } catch (err) {
      setError(err.detail || err.message || 'An error occurred while running the agent.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <header className="header">
        <Activity size={32} color="#f24e1e" />
        <h1>FireReach <span style={{ color: "var(--text-muted)", fontWeight: "400" }}>| Agentic Outreach</span></h1>
      </header>

      <div className="dashboard-grid">
        {/* Input Form Panel */}
        <section className="glass-panel" style={{ padding: '1.5rem', height: 'fit-content' }}>
          <h2 className="section-header" style={{ marginBottom: '1.5rem' }}>
            <Play size={20} className="section-icon" /> Campaign Target
          </h2>
          
          <form onSubmit={handleSubmit}>
            <div className="input-group">
              <label>Target Company</label>
              <input
                type="text"
                name="companyName"
                value={formData.companyName}
                onChange={handleInputChange}
                className="input-field"
                placeholder="e.g. Acme Corp"
                required
              />
            </div>
            
            <div className="input-group">
              <label>Target Email</label>
              <input
                type="email"
                name="targetEmail"
                value={formData.targetEmail}
                onChange={handleInputChange}
                className="input-field"
                placeholder="e.g. contact@company.com"
                required
              />
            </div>

            <div className="input-group">
              <label>Ideal Customer Profile (ICP)</label>
              <textarea
                name="icp"
                value={formData.icp}
                onChange={handleInputChange}
                className="input-field"
                placeholder="Describe your target audience..."
                required
              />
            </div>

            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? (
                <><div className="spinner"></div> Running Agent...</>
              ) : (
                <><Play size={18} fill="currentColor" /> Initialize Workflow</>
              )}
            </button>
          </form>

          {error && (
            <div style={{ marginTop: '1rem', padding: '1rem', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', borderRadius: '8px', color: '#ef4444', fontSize: '0.85rem', display: 'flex', gap: '8px' }}>
              <AlertCircle size={16} style={{ flexShrink: 0 }} />
              <span>{error}</span>
            </div>
          )}
        </section>

        {/* Output Panel */}
        <section className="glass-panel" style={{ display: 'flex', flexDirection: 'column' }}>
          {!result && !loading ? (
            <div className="empty-state">
              <Activity size={48} />
              <h3>Awaiting Target Data</h3>
              <p style={{ marginTop: '0.5rem', maxWidth: '300px' }}>Enter a company and execute the agent to harvest signals and generate outreach.</p>
            </div>
          ) : (
            <div className="output-container">
              {/* Agent Trace */}
              {(result?.trace || loading) && (
                <div className="output-section" style={{ borderBottom: '1px solid var(--border-color)', background: 'rgba(0,0,0,0.2)' }}>
                  <h3 className="section-header" style={{ fontSize: '0.95rem' }}>
                    <Activity size={16} className="section-icon" /> Agent Reasoning Loop
                  </h3>
                  <div className="trace-log">
                    {result ? (
                      result.trace.map((step, i) => (
                        <div key={i} className="trace-item">
                          <CheckCircle2 size={14} /> {step}
                        </div>
                      ))
                    ) : (
                      <div className="trace-item"><div className="spinner" style={{ width: '12px', height: '12px', borderWidth: '2px' }}/> Connecting to LangGraph workflow...</div>
                    )}
                  </div>
                </div>
              )}

              {result && (
                <>
                  {/* Harvested Signals */}
                  <div className="output-section">
                    <h3 className="section-header">
                      <Activity size={20} className="section-icon" /> Harvested Signals
                    </h3>
                    <ul className="signals-list">
                      {(() => {
                        try {
                          const data = JSON.parse(result.signals);
                          return (data.signals || []).map((sig, idx) => <li key={idx}>{sig}</li>);
                        } catch {
                          return <li>{result.signals}</li>;
                        }
                      })()}
                    </ul>
                  </div>

                  {/* Account Brief */}
                  <div className="output-section" style={{ background: 'rgba(255, 255, 255, 0.02)' }}>
                    <h3 className="section-header">
                      <FileText size={20} className="section-icon" /> Strategic Account Brief
                    </h3>
                    <div className="text-content">
                      {result.account_brief}
                    </div>
                  </div>

                  {/* Generated Email */}
                  <div className="output-section">
                    <h3 className="section-header">
                      <Send size={20} className="section-icon" /> Autonomous Outreach Draft
                    </h3>
                    <div className="email-preview">
                      {result.email_content}
                    </div>
                    
                    <div style={{ marginTop: '1rem' }}>
                      <span className="status-badge">
                        <CheckCircle2 size={16} /> {result.delivery_status}
                      </span>
                    </div>
                  </div>
                </>
              )}
            </div>
          )}
        </section>
      </div>
    </>
  );
};

export default Dashboard;
