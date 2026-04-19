import React, { useState, useEffect } from 'react';
import { startWorkflow, resumeWorkflow } from '../api';
import { Play, CheckCircle2, AlertCircle, Activity, FileText, Send, CheckSquare, Square, ThumbsUp } from 'lucide-react';

const Dashboard = () => {
  const [formData, setFormData] = useState({
    icp: 'healthcare and medical software seeking enterprise upgrades',
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const [threadId, setThreadId] = useState(null);
  const [workflowState, setWorkflowState] = useState('input'); // input, picking_companies, approving_drafts, completed

  const [selectedCompanies, setSelectedCompanies] = useState({});
  const [approvedDrafts, setApprovedDrafts] = useState({});

  const [showSenderModal, setShowSenderModal] = useState(false);
  const [senderInfo, setSenderInfo] = useState({ name: '', designation: '', contact: '' });

  const [newCompanyInput, setNewCompanyInput] = useState('');

  const [displayedTrace, setDisplayedTrace] = useState([]);

  useEffect(() => {
    if (result?.trace) {
      setDisplayedTrace([]);
      let currentIndex = 0;

      const intervalId = setInterval(() => {
        if (currentIndex < result.trace.length) {
          setDisplayedTrace(prev => [...prev, result.trace[currentIndex]]);
          currentIndex++;
        } else {
          clearInterval(intervalId);
        }
      }, 300); // Faster tracing for hitl

      return () => clearInterval(intervalId);
    } else {
      setDisplayedTrace([]);
    }
  }, [result?.trace]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleStart = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    setDisplayedTrace([]);

    try {
      const data = await startWorkflow(formData.icp);
      setResult(data);
      setThreadId(data.thread_id);

      if (data.state === 'paused_at_companies') {
        setWorkflowState('picking_companies');
        const initialSelects = {};
        data.company_list?.forEach(c => initialSelects[c] = false);
        setSelectedCompanies(initialSelects);
      } else {
        setWorkflowState('completed');
      }
    } catch (err) {
      setError(err?.detail || err?.message || 'An error occurred starting agent.');
    } finally {
      setLoading(false);
    }
  };

  const handleResumeCompanies = async () => {
    setLoading(true);
    setError(null);

    const chosen = Object.keys(selectedCompanies).filter(c => selectedCompanies[c]);
    if (chosen.length === 0) {
      setError("Please select at least one company to proceed.");
      setLoading(false);
      return;
    }

    try {
      const data = await resumeWorkflow(threadId, { company_list: chosen });
      setResult(data);

      if (data.state === 'paused_at_approval') {
        setWorkflowState('approving_drafts');
        const draftSelects = {};
        data.results?.forEach(r => draftSelects[r.email] = false);
        setApprovedDrafts(draftSelects);
      } else {
        setWorkflowState('completed');
      }
    } catch (err) {
      setError(err?.detail || err?.message || 'An error occurred handling companies.');
    } finally {
      setLoading(false);
    }
  };

  const handleResumeDrafts = async (e) => {
    if (e) e.preventDefault();
    setShowSenderModal(false);
    setLoading(true);
    setError(null);

    const updatedResults = (result.results || []).map(r => {
      let content = r.email_content;
      if (approvedDrafts[r.email]) {
        // Replace common signature hooks from Groq model
        content = content.replace(/\[Your Name\]/gi, senderInfo.name || '[Your Name]');
        content = content.replace(/\[Designation\]/gi, senderInfo.designation || '[Designation]');
        content = content.replace(/\[Title\]/gi, senderInfo.designation || '[Title]');
        content = content.replace(/\[Contact\]/gi, senderInfo.contact || '[Contact]');
      }
      return {
        ...r,
        approved: approvedDrafts[r.email] || false,
        email_content: content
      };
    });

    try {
      const data = await resumeWorkflow(threadId, { results: updatedResults });
      setResult(data);
      setWorkflowState('completed');
    } catch (err) {
      setError(err?.detail || err?.message || 'An error occurred sending emails.');
    } finally {
      setLoading(false);
    }
  };

  const toggleCompany = (comp) => {
    setSelectedCompanies(prev => ({ ...prev, [comp]: !prev[comp] }));
  };

  const toggleDraft = (email) => {
    setApprovedDrafts(prev => ({ ...prev, [email]: !prev[email] }));
  };

  const handleAddCustomCompany = () => {
    if (newCompanyInput.trim()) {
      const comp = newCompanyInput.trim();
      if (!selectedCompanies[comp]) {
        setSelectedCompanies(prev => ({ ...prev, [comp]: true }));
      }
      setNewCompanyInput('');
    }
  };

  const getAnalytics = () => {
    if (!result?.results) return { total: 0, approved: 0, delivered: 0, bounced: 0 };
    const res = result.results;
    return {
      total: res.length,
      approved: res.filter(r => r.approved).length,
      delivered: res.filter(r => r.approved && r.delivery_status && !r.delivery_status.includes("Failed") && !r.delivery_status.includes("Error") && !r.delivery_status.includes("Bounced")).length,
      bounced: res.filter(r => r.approved && (r.delivery_status?.includes("Bounced") || r.delivery_status?.includes("Failed") || r.delivery_status?.includes("Error"))).length
    };
  };

  return (
    <>
      <header className="header">
        <Activity size={32} color="#f24e1e" />
        <h1>FireReach <span style={{ color: "var(--text-muted)", fontWeight: "400" }}>| HITL Outreach</span></h1>
      </header>

      <div className="dashboard-grid">
        {/* State / Control Panel */}
        <section className="glass-panel" style={{ padding: '1.5rem', height: 'fit-content' }}>

          {/* STEP 1: INPUT */}
          {workflowState === 'input' && (
            <>
              <h2 className="section-header" style={{ marginBottom: '1.5rem' }}>
                <Play size={20} className="section-icon" /> Initialize Campaign
              </h2>
              <form onSubmit={handleStart}>
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
                  {loading ? <><div className="spinner"></div> Running Agent...</> : <><Play size={18} fill="currentColor" /> Generate Targets</>}
                </button>
              </form>
            </>
          )}

          {/* STEP 2: PICK COMPANIES */}
          {workflowState === 'picking_companies' && (
            <>
              <h2 className="section-header" style={{ marginBottom: '1.5rem' }}>
                <CheckSquare size={20} className="section-icon" /> Select Targets
              </h2>
              <p style={{ marginBottom: '1rem', fontSize: '0.9rem', color: "var(--text-muted)" }}>
                The agent found these companies. Select which ones to draft outreach for:
              </p>

              <div style={{ display: 'flex', gap: '10px', marginBottom: '1.5rem' }}>
                <input
                  type="text"
                  value={newCompanyInput}
                  onChange={(e) => setNewCompanyInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault();
                      handleAddCustomCompany();
                    }
                  }}
                  className="input-field"
                  style={{ flex: 1, padding: '8px 12px', fontSize: '0.9rem' }}
                  placeholder="Or add a custom company name..."
                />
                <button
                  type="button"
                  onClick={handleAddCustomCompany}
                  className="btn-primary"
                  style={{ padding: '8px 16px', background: 'rgba(255,255,255,0.1)', border: '1px solid var(--border-color)', color: '#fff', width: 'auto' }}>
                  + Add
                </button>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', marginBottom: '1.5rem', maxHeight: '300px', overflowY: 'auto' }}>
                {Object.keys(selectedCompanies).map((comp, idx) => (
                  <div
                    key={idx}
                    onClick={() => toggleCompany(comp)}
                    style={{ display: 'flex', alignItems: 'center', gap: '10px', background: 'rgba(255,255,255,0.05)', padding: '10px', borderRadius: '5px', cursor: 'pointer' }}>
                    {selectedCompanies[comp] ? <CheckSquare size={20} color="#10b981" /> : <Square size={20} />}
                    <span>{comp}</span>
                  </div>
                ))}
              </div>

              <button onClick={handleResumeCompanies} className="btn-primary" disabled={loading}>
                {loading ? <><div className="spinner"></div> Processing...</> : <><Play size={18} fill="currentColor" /> Confirm Targets & Draft</>}
              </button>
            </>
          )}

          {/* STEP 3: APPROVE DRAFTS */}
          {workflowState === 'approving_drafts' && (
            <>
              <h2 className="section-header" style={{ marginBottom: '1.5rem' }}>
                <ThumbsUp size={20} className="section-icon" /> Approve Drafts
              </h2>
              <p style={{ marginBottom: '1rem', fontSize: '0.9rem', color: "var(--text-muted)" }}>
                Review the agent's personalized outreach drafts below. Check the ones you approve for Sending.
              </p>

              <button onClick={() => setShowSenderModal(true)} className="btn-primary" disabled={loading} style={{ background: '#10b981', borderColor: '#059669' }}>
                {loading ? <><div className="spinner"></div> Dispatching...</> : <><Send size={18} fill="currentColor" /> Send Approved Emails</>}
              </button>
            </>
          )}

          {/* SENDER INFO MODAL */}
          {showSenderModal && (
            <div style={{ position: 'fixed', top: 0, left: 0, width: '100%', height: '100%', background: 'rgba(0,0,0,0.8)', zIndex: 100, display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
              <div style={{ background: '#1e1e1e', padding: '2rem', borderRadius: '12px', width: '400px', border: '1px solid var(--border-color)', boxShadow: '0 10px 30px rgba(0,0,0,0.5)' }}>
                <h3 style={{ marginBottom: '1rem', color: '#fff', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Send size={20} color="#10b981" /> Finalize Signatures
                </h3>
                <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)', marginBottom: '1.5rem' }}>
                  Please enter your details to replace the placeholder fields ([Your Name], etc) in the approved emails before broadcasting.
                </p>
                <form onSubmit={handleResumeDrafts}>
                  <div className="input-group">
                    <label>Your Name</label>
                    <input type="text" value={senderInfo.name} onChange={(e) => setSenderInfo(p => ({ ...p, name: e.target.value }))} className="input-field" placeholder="e.g. John Doe" required />
                  </div>
                  <div className="input-group">
                    <label>Designation / Title</label>
                    <input type="text" value={senderInfo.designation} onChange={(e) => setSenderInfo(p => ({ ...p, designation: e.target.value }))} className="input-field" placeholder="e.g. Founder & CEO" required />
                  </div>
                  <div className="input-group">
                    <label>Contact Info</label>
                    <input type="text" value={senderInfo.contact} onChange={(e) => setSenderInfo(p => ({ ...p, contact: e.target.value }))} className="input-field" placeholder="e.g. john@company.com" />
                  </div>

                  <div style={{ display: 'flex', gap: '10px', marginTop: '1.5rem' }}>
                    <button type="button" onClick={() => setShowSenderModal(false)} className="btn-primary" style={{ background: 'transparent', border: '1px solid var(--border-color)', flex: 1 }}>Cancel</button>
                    <button type="submit" className="btn-primary" style={{ background: '#10b981', borderColor: '#059669', flex: 1 }}>Finalize & Send</button>
                  </div>
                </form>
              </div>
            </div>
          )}

          {/* STEP 4: COMPLETED */}
          {workflowState === 'completed' && (() => {
            const stats = getAnalytics();
            return (
              <div style={{ textAlign: 'center', padding: '1rem' }}>
                <CheckCircle2 size={48} color="#10b981" style={{ margin: '0 auto 1rem' }} />
                <h3>Campaign Completed!</h3>
                <p style={{ marginTop: '0.5rem', color: 'var(--text-muted)', fontSize: '0.9rem' }}>Review your delivery metrics below.</p>

                {/* KPI Analytics Block */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '10px', marginTop: '1.5rem', marginBottom: '1.5rem' }}>
                  <div className="glass-panel" style={{ padding: '15px 5px', textAlign: 'center', background: 'rgba(255,255,255,0.03)' }}>
                    <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>{stats.total}</div>
                    <div style={{ fontSize: '0.75rem', color: "var(--text-muted)", marginTop: '4px' }}>Total Leads</div>
                  </div>
                  <div className="glass-panel" style={{ padding: '15px 5px', textAlign: 'center', background: 'rgba(59, 130, 246, 0.1)', border: '1px solid rgba(59, 130, 246, 0.2)' }}>
                    <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#3b82f6' }}>{stats.approved}</div>
                    <div style={{ fontSize: '0.75rem', color: "var(--text-muted)", marginTop: '4px' }}>Approved</div>
                  </div>
                  <div className="glass-panel" style={{ padding: '15px 5px', textAlign: 'center', background: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.2)' }}>
                    <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#10b981' }}>{stats.delivered}</div>
                    <div style={{ fontSize: '0.75rem', color: "var(--text-muted)", marginTop: '4px' }}>Delivered</div>
                  </div>
                  <div className="glass-panel" style={{ padding: '15px 5px', textAlign: 'center', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.2)' }}>
                    <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#ef4444' }}>{stats.bounced}</div>
                    <div style={{ fontSize: '0.75rem', color: "var(--text-muted)", marginTop: '4px' }}>Failed</div>
                  </div>
                </div>



                <button onClick={() => { setWorkflowState('input'); setResult(null); }} className="btn-primary" style={{ marginTop: '1.5rem' }}>Start New Campaign</button>
              </div>
            )
          })()}

          {error && (
            <div style={{ marginTop: '1rem', padding: '1rem', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', borderRadius: '8px', color: '#ef4444', fontSize: '0.85rem', display: 'flex', gap: '8px' }}>
              <AlertCircle size={16} style={{ flexShrink: 0 }} />
              <span>{error}</span>
            </div>
          )}
        </section>

        {/* Output Panel / Trace */}
        <section className="glass-panel" style={{ display: 'flex', flexDirection: 'column' }}>
          {!result && !loading ? (
            <div className="empty-state">
              <Activity size={48} />
              <h3>Awaiting Input</h3>
              <p style={{ marginTop: '0.5rem', maxWidth: '300px' }}>Provide an ICP pattern and let the agent prospect and write outreach.</p>
            </div>
          ) : (
            <div className="output-container">
              {/* Agent Trace Log (Hidden when fully completed to save space) */}
              {workflowState !== 'completed' && (result?.trace || loading) && (
                <div className="output-section" style={{ borderBottom: '1px solid var(--border-color)', background: 'rgba(0,0,0,0.2)' }}>
                  <h3 className="section-header" style={{ fontSize: '0.95rem' }}>
                    <Activity size={16} className="section-icon" /> Agent Reasoning Trace
                  </h3>
                  <div className="trace-log" style={{ maxHeight: '180px', overflowY: 'auto' }}>
                    {result ? (
                      displayedTrace.map((step, i) => (
                        <div key={i} className="trace-item">
                          <CheckCircle2 size={14} /> {step}
                        </div>
                      ))
                    ) : (
                      <div className="trace-item"><div className="spinner" style={{ width: '12px', height: '12px', borderWidth: '2px' }} /> Connecting to LangGraph...</div>
                    )}
                    {/* Show a thinking indicator if trace is still populating or graph is active */}
                    {loading && (
                      <div className="trace-item" style={{ opacity: 0.7 }}>
                        <div className="spinner" style={{ width: '12px', height: '12px', borderWidth: '2px' }} /> Executing Node...
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* DRAFTS VIEW FOR APPROVAL / COMPLETED STUFF */}
              {(workflowState === 'approving_drafts' || workflowState === 'completed') && result?.results && result.results.length > 0 && (
                <div className="output-section">
                  <h3 className="section-header">
                    <FileText size={20} className="section-icon" /> Generated Emails
                  </h3>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                    {result.results.map((lead, idx) => (
                      <div key={idx} style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid var(--border-color)', borderRadius: '8px', padding: '1rem' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '10px' }}>
                          <h4>{lead.company_name} ({lead.email})</h4>

                          {/* Only show checkbox if in approval state */}
                          {workflowState === 'approving_drafts' && (
                            <div
                              onClick={() => toggleDraft(lead.email)}
                              style={{ display: 'flex', alignItems: 'center', gap: '5px', cursor: 'pointer', background: approvedDrafts[lead.email] ? 'rgba(16, 185, 129, 0.2)' : 'rgba(255,255,255,0.1)', padding: '5px 10px', borderRadius: '4px' }}>
                              {approvedDrafts[lead.email] ? <CheckSquare size={16} color="#10b981" /> : <Square size={16} />}
                              <span style={{ fontSize: '0.85rem' }}>Approve Delivery</span>
                            </div>
                          )}
                        </div>

                        {/* Brief View Mode */}
                        <details style={{ marginBottom: '10px', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                          <summary style={{ cursor: 'pointer', color: '#f24e1e' }}>View Strategic Brief</summary>
                          <div style={{ marginTop: '10px', padding: '10px', background: 'rgba(0,0,0,0.2)', borderRadius: '4px' }}>
                            {lead.account_brief}
                          </div>
                        </details>

                        {/* Email Subject / Content */}
                        <div className="email-preview" style={{ whiteSpace: 'pre-wrap', marginTop: '10px' }}>
                          {lead.email_content}
                        </div>

                        {/* Final Status Render */}
                        {workflowState === 'completed' && (
                          <div style={{ marginTop: '1rem' }}>
                            <span className="status-badge" style={{ background: lead.delivery_status?.includes("Skipped") || lead.delivery_status?.includes("Error") || lead.delivery_status?.includes("Failed") ? 'rgba(239, 68, 68, 0.2)' : 'rgba(16, 185, 129, 0.2)' }}>
                              <CheckCircle2 size={16} /> {lead.delivery_status}
                            </span>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </section>
      </div>
    </>
  );
};

export default Dashboard;
