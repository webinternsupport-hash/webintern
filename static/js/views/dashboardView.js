// Dashboard View Controller - Mobile Optimized
const DashboardView = {
  render() {
    const user = API.getCurrentUser();
    console.log('[Dashboard] Rendering for user:', user ? user.email : 'NOT LOGGED IN');
    
    if (!user) {
      console.warn('[Dashboard] No user found, redirecting to login');
      window.location.hash = '#/login';
      return;
    }

    const appEl = document.getElementById('app-view') || document.getElementById('app');
    if (!appEl) {
      console.error('[Dashboard] App view element not found');
      return;
    }
    appEl.innerHTML = `
      <section class="section" style="padding: 16px 0; background-color: var(--color-gray-bg); min-height: calc(100vh - 130px);">
        <div class="container">
          <!-- Welcome Banner with Gradient -->
          <div class="welcome-banner" style="background: linear-gradient(135deg, var(--color-blue-dark) 0%, var(--color-primary-blue) 100%); padding: 24px 16px; border-radius: 12px; margin-bottom: 20px; box-shadow: 0 4px 12px rgba(8, 43, 102, 0.15);">
            <div>
              <h1 style="font-size: 22px; margin: 0; color: white; line-height: 1.3;">Welcome back! 👋</h1>
              <p style="margin-top: 6px; opacity: 0.95; font-size: 14px; line-height: 1.5; color: white;">${user.name || user.email}</p>
              <p style="margin-top: 6px; opacity: 0.9; font-size: 13px; line-height: 1.4; color: white;">Track your internships, submit assignments, and download certificates.</p>
            </div>
            <div class="tab-buttons" style="margin-top: 12px; display: flex; gap: 10px; flex-wrap: wrap;">
              <button onclick="DashboardView.switchTab('apps')" id="tab-btn-apps" class="tab-button" style="flex: 1; min-width: 140px; padding: 10px 12px; font-size: 13px; font-weight: 700; border-radius: 8px; border: none; background: #FFFFFF; color: var(--color-primary-blue); box-shadow: 0 2px 8px rgba(0,0,0,0.15); cursor: pointer; transition: all 0.2s ease;">My Internships</button>
              <button onclick="DashboardView.switchTab('docs')" id="tab-btn-docs" class="tab-button" style="flex: 1; min-width: 140px; padding: 10px 12px; font-size: 13px; font-weight: 700; border-radius: 8px; border: 1px solid rgba(255,255,255,0.3); background: rgba(255,255,255,0.2); color: #FFFFFF; cursor: pointer; transition: all 0.2s ease;">Documents</button>
            </div>
          </div>

          <!-- Applications Tab Content -->
          <div id="tab-content-apps" style="margin-top: 16px;">
            <div id="dashboard-apps-list">
              <div style="padding: 32px 16px; text-align: center; color: var(--color-gray-text);">Loading your internship workspace...</div>
            </div>
          </div>

          <!-- Documents Tab Content -->
          <div id="tab-content-docs" style="display: none; margin-top: 16px;">
            <div id="dashboard-docs-list">
              <div style="padding: 32px 16px; text-align: center; color: var(--color-gray-text);">Loading document records...</div>
            </div>
          </div>
        </div>
      </section>
    `;

    if (window.feather) feather.replace();
    this.loadApplications();
  },

  switchTab(tab) {
    const btnApps = document.getElementById('tab-btn-apps');
    const btnDocs = document.getElementById('tab-btn-docs');
    const contentApps = document.getElementById('tab-content-apps');
    const contentDocs = document.getElementById('tab-content-docs');

    if (tab === 'apps') {
      contentApps.style.display = 'block';
      contentDocs.style.display = 'none';
      if (btnApps) {
        btnApps.style.background = '#FFFFFF';
        btnApps.style.color = '#082B66';
        btnApps.style.border = 'none';
        btnApps.style.fontWeight = '700';
        btnApps.style.boxShadow = '0 2px 8px rgba(0,0,0,0.15)';
      }
      if (btnDocs) {
        btnDocs.style.background = 'rgba(255,255,255,0.2)';
        btnDocs.style.color = '#FFFFFF';
        btnDocs.style.border = '1px solid rgba(255,255,255,0.3)';
        btnDocs.style.fontWeight = '600';
        btnDocs.style.boxShadow = 'none';
      }
    } else {
      contentApps.style.display = 'none';
      contentDocs.style.display = 'block';
      if (btnDocs) {
        btnDocs.style.background = '#FFFFFF';
        btnDocs.style.color = '#082B66';
        btnDocs.style.border = 'none';
        btnDocs.style.fontWeight = '700';
        btnDocs.style.boxShadow = '0 2px 8px rgba(0,0,0,0.15)';
      }
      if (btnApps) {
        btnApps.style.background = 'rgba(255,255,255,0.2)';
        btnApps.style.color = '#FFFFFF';
        btnApps.style.border = '1px solid rgba(255,255,255,0.3)';
        btnApps.style.fontWeight = '600';
        btnApps.style.boxShadow = 'none';
      }
      this.loadDocuments();
    }
  },

  async loadApplications() {
    try {
      const user = API.getCurrentUser();
      console.log('[Dashboard] Current user:', user ? user.email : 'NO USER');
      
      const container = document.getElementById('dashboard-apps-list');
      if (!container) {
        console.error('[Dashboard] Container not found!');
        return;
      }
      
      // CRITICAL FIX #1: Fetch fresh data from server FIRST
      // This ensures users always see their current persisted account data
      let applicationsToDisplay = [];
      let serverFetchSucceeded = false;
      
      try {
        console.log('[Dashboard] Fetching fresh applications from /api/applications/me');
        const res = await API.request('/api/applications/me');
        applicationsToDisplay = res.applications || [];
        serverFetchSucceeded = true;
        console.log('[Dashboard] Successfully fetched server apps:', applicationsToDisplay.length);
        
        // Save server data to IndexedDB for future offline access
        if (Storage && user && user.id && applicationsToDisplay.length > 0) {
          for (const app of applicationsToDisplay) {
            const enrollment = {
              userId: user.id,
              internshipId: app.internship_id || app.id,
              internshipTitle: app.internship_title,
              companyName: app.company_name || '',
              sectorName: app.sector_name,
              emoji: app.internship_emoji || app.emoji || '💼',
              status: app.status || 'active',
              progress: app.progress_percent || 0,
              enrolledAt: app.applied_at || new Date().toISOString(),
              startDate: app.start_date,
              endDate: app.end_date,
              durationWeeks: app.duration_weeks || 4,
              completedWeeks: app.completed_weeks || 0,
              serverData: app
            };
            try {
              await Storage.saveEnrollment(enrollment);
            } catch (err) {
              console.warn('[Storage] Failed to save enrollment:', err);
            }
          }
        }
      } catch (err) {
        console.error('[Dashboard] Failed to fetch fresh data from server:', err);
        
        // FALLBACK: Only use persisted data if server fetch fails
        if (Storage && user && user.id) {
          try {
            const persistedApps = await Storage.getUserEnrollments(user.id);
            applicationsToDisplay = persistedApps || [];
            console.log('[Dashboard] Using persisted enrollments as fallback:', applicationsToDisplay.length);
          } catch (fallbackErr) {
            console.warn('[Dashboard] Fallback to persisted data also failed:', fallbackErr);
          }
        }
      }
      
      const res = { applications: applicationsToDisplay };
      // Note: container was already retrieved at the start of loadApplications
      if (!container) return;

      if (!res.applications || res.applications.length === 0) {
        container.innerHTML = `
          <div class="no-data-state">
            <i data-feather="book-open" style="width: 48px; height: 48px; color: var(--color-accent-blue); margin-bottom: 16px;"></i>
            <h3 style="font-size: 18px; color: var(--color-blue-dark); margin-bottom: 8px;">No Active Internships</h3>
            <p style="color: var(--color-gray-text); margin-bottom: 16px; font-size: 14px;">You haven't enrolled in any virtual internship program yet.</p>
            <a href="#/internships" class="btn btn-primary">Browse Internships →</a>
          </div>
        `;
        if (window.feather) feather.replace();
        return;
      }

      container.innerHTML = res.applications.map(app => {
        const isCompleted = app.status === 'completed' || app.completion_status === 'completed';
        const isPaid = Boolean(app.is_verified_paid == 1 || app.is_verified_paid === true || app.paid);
        
        // Get emoji (from various possible sources)
        const emoji = app.internship_emoji || app.emoji || '💼';
        
        // Calculate pending days
        const endDate = app.end_date ? new Date(app.end_date) : null;
        const today = new Date();
        let daysRemaining = null;
        if (endDate) {
          const diffTime = endDate.getTime() - today.getTime();
          daysRemaining = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        }
        
        // Determine certificate status message
        let certStatusMsg = '⏳ Pending Tasks';
        let certStatusColor = '#EAB308'; // yellow
        if (isCompleted && !isPaid) {
          certStatusMsg = '💳 Pay ₹199 to Unlock';
          certStatusColor = '#F59E0B'; // orange
        } else if (isCompleted && isPaid) {
          certStatusMsg = '✅ Ready to Download';
          certStatusColor = '#10B981'; // green
        }

        return `
          <div class="application-card" style="background: white; border-radius: 12px; border: 1px solid var(--color-border); padding: 16px; margin-bottom: 16px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04);">
            <div style="display: flex; align-items: flex-start; justify-content: space-between; gap: 10px; flex-wrap: wrap; margin-bottom: 12px;">
              <div style="flex: 1;">
                <!-- Emoji Bubble Display -->
                <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
                  <div style="width: 48px; height: 48px; background: linear-gradient(135deg, var(--color-accent-blue) 0%, var(--color-primary-blue) 100%); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 24px; box-shadow: 0 4px 12px rgba(46, 125, 255, 0.3);">
                    ${emoji}
                  </div>
                  <div style="flex: 1;">
                    <span class="badge-sector" style="font-size: 11px; font-weight: 700; color: var(--color-primary-blue); background: var(--color-blue-light); padding: 2px 8px; border-radius: 4px; display: inline-block;">${app.sector_name}</span>
                    <h2 style="font-size: 16px; color: var(--color-blue-dark); margin: 4px 0 2px 0; line-height: 1.3; font-weight: 700;">${app.internship_title}</h2>
                  </div>
                </div>
                <p style="font-size: 11px; color: var(--color-gray-text); margin: 4px 0; line-height: 1.4;">
                  📅 Start: <strong>${app.start_date || 'N/A'}</strong> • End: <strong>${app.end_date || 'N/A'}</strong>
                </p>
              </div>
            </div>

            <!-- Progress Section -->
            <div class="progress-section">
              <div class="progress-label">
                <span style="font-size: 12px;">Week ${app.completed_weeks} of ${app.duration_weeks}</span>
                <span style="font-size: 12px;">${app.progress_percent}%</span>
              </div>
              <div class="progress-bar-track">
                <div class="progress-bar-fill" style="width: ${app.progress_percent}%;"></div>
              </div>
            </div>

            <!-- Certificate Status Banner -->
            <div style="margin-top: 10px; background: #F9FAFB; border-left: 3px solid ${certStatusColor}; padding: 8px; border-radius: 4px; font-size: 12px; color: var(--color-gray-text);">
              <strong style="color: ${certStatusColor};">${certStatusMsg}</strong>
              ${daysRemaining !== null && daysRemaining > 0 && !isCompleted ? `
                <span style="font-size: 11px; color: var(--color-gray-text); display: block; margin-top: 3px;">
                  📅 ${daysRemaining} day${daysRemaining !== 1 ? 's' : ''} remaining
                </span>
              ` : ''}
            </div>

            <!-- Status & Actions -->
            <div style="margin-top: 12px;">
              <p style="font-size: 12px; color: var(--color-gray-text); margin-bottom: 10px;">
                Status: <strong style="color: var(--color-primary-blue);">${app.status || 'ACTIVE'}</strong>
              </p>
              <div class="application-actions" style="display: flex; gap: 8px; flex-wrap: wrap; align-items: center;">
                <!-- Offer Letter View -->
                <a href="/api/applications/${app.id}/offer-letter.pdf" target="_blank"
                   title="View Offer Letter"
                   style="display: inline-flex; align-items: center; gap: 6px; padding: 8px 14px; min-height: 40px; font-size: 12px; font-weight: 600; border-radius: 8px; border: 1.5px solid #94A3B8; color: #475569; background: #fff; text-decoration: none; cursor: pointer; transition: background 0.2s, color 0.2s; flex: 1; min-width: 100px; justify-content: center;"
                   onmouseover="this.style.background='#F1F5F9';this.style.borderColor='#64748B'"
                   onmouseout="this.style.background='#fff';this.style.borderColor='#94A3B8'">
                  <i data-feather="eye" style="width: 14px; height: 14px; flex-shrink: 0;"></i>
                  View
                </a>

                <!-- Offer Letter Download -->
                <a href="/api/applications/${app.id}/offer-letter.pdf" download="Offer_Letter_${app.id}.pdf"
                   title="Download Offer Letter"
                   style="display: inline-flex; align-items: center; gap: 6px; padding: 8px 14px; min-height: 40px; font-size: 12px; font-weight: 600; border-radius: 8px; border: 1.5px solid var(--color-primary-blue); color: var(--color-primary-blue); background: #EAF1FB; text-decoration: none; cursor: pointer; transition: background 0.2s, color 0.2s; flex: 1; min-width: 100px; justify-content: center;"
                   onmouseover="this.style.background='var(--color-primary-blue)';this.style.color='#fff'"
                   onmouseout="this.style.background='#EAF1FB';this.style.color='var(--color-primary-blue)'">
                  <i data-feather="download" style="width: 14px; height: 14px; flex-shrink: 0;"></i>
                  Download
                </a>

                <!-- Certificate download or status -->
                ${isPaid && isCompleted && app.certificate_id ? `
                  <a href="/api/certificates/${app.certificate_id}/pdf" target="_blank"
                     title="View Certificate"
                     style="display: inline-flex; align-items: center; gap: 6px; padding: 8px 14px; min-height: 40px; font-size: 12px; font-weight: 600; border-radius: 8px; border: 1.5px solid #94A3B8; color: #475569; background: #fff; text-decoration: none; cursor: pointer; transition: background 0.2s, color 0.2s; flex: 1; min-width: 100px; justify-content: center;"
                     onmouseover="this.style.background='#F1F5F9';this.style.borderColor='#64748B'"
                     onmouseout="this.style.background='#fff';this.style.borderColor='#94A3B8'">
                    <i data-feather="eye" style="width: 14px; height: 14px; flex-shrink: 0;"></i>
                    View
                  </a>
                  <a href="/api/certificates/${app.certificate_id}/pdf" download="Certificate_${app.certificate_id}.pdf"
                     title="Download Certificate"
                     style="display: inline-flex; align-items: center; gap: 6px; padding: 8px 14px; min-height: 40px; font-size: 12px; font-weight: 600; border-radius: 8px; border: 1.5px solid #10B981; color: #10B981; background: #D1FAE5; text-decoration: none; cursor: pointer; transition: background 0.2s, color 0.2s; flex: 1; min-width: 100px; justify-content: center;"
                     onmouseover="this.style.background='#10B981';this.style.color='#fff'"
                     onmouseout="this.style.background='#D1FAE5';this.style.color='#10B981'">
                    <i data-feather="download" style="width: 14px; height: 14px; flex-shrink: 0;"></i>
                    Download
                  </a>
                ` : `
                  <button onclick="DashboardView.handleCertificateClick('${app.id}')"
                          title="${certStatusMsg}"
                          style="display: inline-flex; align-items: center; gap: 6px; padding: 8px 14px; min-height: 40px; font-size: 12px; font-weight: 600; border-radius: 8px; border: 1.5px solid ${certStatusColor}; color: ${certStatusColor}; background: #FFFBEB; cursor: pointer; transition: background 0.2s; flex: 1; min-width: 100px; justify-content: center;">
                    <i data-feather="award" style="width: 14px; height: 14px; flex-shrink: 0;"></i>
                    Certificate
                  </button>
                `}

                <!-- Tasks -->
                <button onclick="DashboardView.openWorkspace('${app.id}')"
                        style="display: inline-flex; align-items: center; gap: 6px; padding: 8px 14px; min-height: 40px; font-size: 12px; font-weight: 600; border-radius: 8px; border: none; background: var(--color-primary-blue); color: #fff; cursor: pointer; transition: opacity 0.2s; flex: 1; min-width: 100px; justify-content: center;"
                        onmouseover="this.style.opacity='0.85'"
                        onmouseout="this.style.opacity='1'">
                  <i data-feather="edit-3" style="width: 14px; height: 14px; flex-shrink: 0;"></i>
                  Tasks
                </button>
              </div>
            </div>
          </div>
        `;
      }).join('');

      if (window.feather) feather.replace();
    } catch (e) {
      console.error('[Dashboard] Load applications error:', e);
      const container = document.getElementById('dashboard-apps-list');
      if (container) {
        container.innerHTML = `
          <div class="no-data-state" style="padding: 40px 20px; text-align: center; color: #EF4444;">
            <p style="font-weight: 700; margin-bottom: 8px;">Failed to Load Dashboard</p>
            <p style="font-size: 14px; color: #666; margin-bottom: 16px;">${e.message || 'An error occurred'}</p>
            <button onclick="location.reload()" class="btn btn-primary" style="font-size: 12px;">Reload Page</button>
          </div>
        `;
      }
    }
  },

  async loadDocuments() {
    try {
      const res = await API.request('/api/applications/me');
      const container = document.getElementById('dashboard-docs-list');
      if (!container) return;

      if (!res.applications || res.applications.length === 0) {
        container.innerHTML = `<div class="no-data-state"><p>No document records found.</p></div>`;
        return;
      }

      container.innerHTML = `
        <div style="background: var(--color-white); border-radius: 12px; border: 1px solid var(--color-border); padding: 16px; overflow-x: auto;">
          <h2 style="font-size: 18px; color: var(--color-blue-dark); margin-bottom: 16px;">📋 My Official Documents</h2>
          
          <div style="display: flex; flex-direction: column; gap: 12px;">
            ${res.applications.map(app => {
              const isCompleted = app.status === 'completed' || app.completion_status === 'completed';
              const isPaid = Boolean(app.is_verified_paid == 1 || app.is_verified_paid === true || app.paid);
              
              // Calculate pending days
              const endDate = app.end_date ? new Date(app.end_date) : null;
              const today = new Date();
              let daysRemaining = null;
              if (endDate) {
                const diffTime = endDate.getTime() - today.getTime();
                daysRemaining = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
              }

              return `
                <div style="border: 1px solid var(--color-border); border-radius: 10px; padding: 12px; background: #F8FAFC;">
                  <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 8px; flex-wrap: wrap;">
                    <div style="flex: 1;">
                      <h3 style="font-size: 14px; color: var(--color-blue-dark); margin: 0 0 4px 0;">📄 Internship Offer Letter</h3>
                      <p style="font-size: 12px; color: var(--color-gray-text); margin: 0;">${app.internship_title}</p>
                      <span style="font-size: 10px; font-weight: 700; color: #10B981; background: #D1FAE5; padding: 3px 8px; border-radius: 4px; display: inline-block; margin-top: 6px;">✅ ISSUED</span>
                    </div>
                    <div style="display: flex; gap: 6px; flex-wrap: wrap; justify-content: flex-end; align-items: center;">
                      <a href="/api/applications/${app.id}/offer-letter.pdf" target="_blank"
                         title="View Offer Letter"
                         style="display: inline-flex; align-items: center; gap: 5px; padding: 6px 12px; font-size: 11px; font-weight: 600; border-radius: 7px; border: 1.5px solid #94A3B8; color: #475569; background: #fff; text-decoration: none; min-height: 32px; cursor: pointer;">
                        <i data-feather="eye" style="width: 13px; height: 13px;"></i> View
                      </a>
                      <a href="/api/applications/${app.id}/offer-letter.pdf" download
                         title="Download Offer Letter"
                         style="display: inline-flex; align-items: center; gap: 5px; padding: 6px 12px; font-size: 11px; font-weight: 600; border-radius: 7px; border: 1.5px solid var(--color-primary-blue); color: #fff; background: var(--color-primary-blue); text-decoration: none; min-height: 32px; cursor: pointer;">
                        <i data-feather="download" style="width: 13px; height: 13px;"></i> Download
                      </a>
                    </div>
                  </div>
                </div>

                <div style="border: 1px solid var(--color-border); border-radius: 10px; padding: 12px; background: #F8FAFC;">
                  <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 8px; flex-wrap: wrap;">
                    <div style="flex: 1;">
                      <h3 style="font-size: 14px; color: var(--color-blue-dark); margin: 0 0 4px 0;">🏆 Internship Certificate</h3>
                      <p style="font-size: 12px; color: var(--color-gray-text); margin: 0;">${app.internship_title}</p>
                      ${isPaid && isCompleted && app.certificate_id ? `
                        <span style="font-size: 10px; font-weight: 700; color: #10B981; background: #D1FAE5; padding: 3px 8px; border-radius: 4px; display: inline-block; margin-top: 6px;">✅ ISSUED & PAID</span>
                      ` : isPaid ? `
                        <span style="font-size: 10px; font-weight: 700; color: #D97706; background: #FEF3C7; padding: 3px 8px; border-radius: 4px; display: inline-block; margin-top: 6px;">🟠 PAID - PENDING COMPLETION</span>
                        ${daysRemaining !== null && daysRemaining > 0 ? `
                          <p style="font-size: 10px; color: #92400E; margin: 4px 0 0 0;">⏳ ${daysRemaining} day${daysRemaining !== 1 ? 's' : ''} remaining to complete all tasks</p>
                        ` : ''}
                      ` : `
                        <span style="font-size: 10px; font-weight: 700; color: #475569; background: #E2E8F0; padding: 3px 8px; border-radius: 4px; display: inline-block; margin-top: 6px;">⏳ PENDING</span>
                        ${daysRemaining !== null && daysRemaining > 0 ? `
                          <p style="font-size: 10px; color: #334155; margin: 4px 0 0 0;">📅 Complete internship in ${daysRemaining} day${daysRemaining !== 1 ? 's' : ''}, then pay ₹199</p>
                        ` : ''}
                      `}
                    </div>
                    <div style="display: flex; gap: 6px; flex-wrap: wrap; justify-content: flex-end; align-items: center;">
                      ${isPaid && isCompleted && app.certificate_id ? `
                        <a href="/api/certificates/${app.certificate_id}/pdf" target="_blank"
                           title="View Certificate"
                           style="display: inline-flex; align-items: center; gap: 5px; padding: 6px 12px; font-size: 11px; font-weight: 600; border-radius: 7px; border: 1.5px solid #94A3B8; color: #475569; background: #fff; text-decoration: none; min-height: 32px; cursor: pointer;">
                          <i data-feather="eye" style="width: 13px; height: 13px;"></i> View
                        </a>
                        <a href="/api/certificates/${app.certificate_id}/pdf" download
                           title="Download Certificate"
                           style="display: inline-flex; align-items: center; gap: 5px; padding: 6px 12px; font-size: 11px; font-weight: 600; border-radius: 7px; border: 1.5px solid #10B981; color: #fff; background: #10B981; text-decoration: none; min-height: 32px; cursor: pointer;">
                          <i data-feather="download" style="width: 13px; height: 13px;"></i> Download
                        </a>
                      ` : `
                        <button onclick="DashboardView.handleCertificateClick('${app.id}')"
                                style="display: inline-flex; align-items: center; gap: 5px; padding: 6px 12px; font-size: 11px; font-weight: 600; border-radius: 7px; border: none; background: #D97706; color: #fff; min-height: 32px; cursor: pointer;">
                          💳 Get Certificate
                        </button>
                      `}
                    </div>
                  </div>
                </div>
              `;
            }).join('')}
          </div>
        </div>
      `;
    } catch (e) {
      console.error("Load documents error:", e);
    }
  },

  async handleCertificateClick(appId) {
    try {
      const res = await API.request(`/api/applications/${appId}`);
      if (!res || !res.application) {
        Toast.show('Application record not found.', 'error');
        return;
      }

      const app = res.application;
      const isPaid = Boolean(app.is_verified_paid == 1 || app.is_verified_paid === true);
      const completedWeeks = app.submissions ? app.submissions.filter(s => s.status === 'approved' || s.status === 'graded').length : (app.completed_weeks || 0);
      const isCompleted = app.status === 'completed' || app.completion_status === 'completed' || completedWeeks >= (app.duration_weeks || 4);

      if (!isPaid) {
        Modals.openPaymentInfoModal(appId, app.internship_title);
      } else if (!isCompleted) {
        Modals.openAssignmentPendingModal(appId, app.internship_title, completedWeeks, app.duration_weeks || 4);
      } else {
        const certId = app.certificate_id || app.id;
        window.open(`/api/certificates/${certId}/pdf`, '_blank');
      }
    } catch (e) {
      console.error("handleCertificateClick error:", e);
      Toast.show('Failed to process certificate request.', 'error');
    }
  },

  async openWorkspace(appId) {
    try {
      const res = await API.request(`/api/applications/${appId}`);
      const app = res.application;

      // Ensure tasks exist
      if (!app.tasks || app.tasks.length === 0) {
        Toast.show('No tasks found for this internship. Tasks are being prepared.', 'warning');
        return;
      }

      let html = `
        <div style="max-width: 100%; font-family: inherit;">
          <div style="position: sticky; top: -28px; background: #FFFFFF; z-index: 10; margin: -28px -28px 16px -28px; padding: 12px 16px; border-bottom: 1px solid var(--color-border); display: flex; align-items: center; justify-content: space-between; gap: 10px; flex-wrap: wrap;">
            <button onclick="Modals.close()" class="btn btn-outline btn-sm" style="display: inline-flex; align-items: center; gap: 6px; font-weight: 700; font-size: 12px;">
              ← Back
            </button>
            <span style="font-size: 12px; font-weight: 700; color: var(--color-blue-dark); text-align: center; flex: 1;">
              ${app.internship_title}
            </span>
          </div>

          <div style="margin-bottom: 16px;">
            <h2 style="font-size: 18px; color: var(--color-blue-dark); margin-bottom: 6px;">📝 Task Workspace</h2>
            <p style="color: var(--color-gray-text); font-size: 13px; margin: 0; line-height: 1.4;">
              Upload your weekly PDF assignment deliverables (Max 10MB per module) for mentor review and grading.
            </p>
          </div>

          <div style="display: flex; flex-direction: column; gap: 14px; margin-bottom: 16px;">
            ${app.tasks.map(t => {
              const sub = t.submission;
              const subStatus = sub ? sub.status : 'NOT_SUBMITTED';
              let badgeColor = '#9CA3AF';
              if (['graded', 'approved'].includes(subStatus.toLowerCase())) badgeColor = '#10B981';
              if (subStatus.toLowerCase() === 'submitted' || subStatus.toLowerCase() === 'pending') badgeColor = '#3B82F6';
              if (['revise', 'rejected', 'late'].includes(subStatus.toLowerCase())) badgeColor = '#EF4444';

              return `
                <div class="task-card" style="background: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 8px; padding: 12px; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">
                  <!-- Task Header -->
                  <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 8px; flex-wrap: wrap; margin-bottom: 10px;">
                    <div>
                      <strong style="font-size: 14px; color: var(--color-blue-dark);">📌 Week ${t.week_number}: ${t.title}</strong>
                      <p style="font-size: 11px; color: #6B7280; margin: 4px 0 0 0;">${t.objective || 'Complete assignment'}</p>
                    </div>
                    <span style="font-size: 10px; font-weight: 700; color: white; background: ${badgeColor}; padding: 4px 10px; border-radius: 4px; text-transform: uppercase; white-space: nowrap;">
                      ${subStatus.replace('_', ' ')}
                    </span>
                  </div>

                  <!-- Deliverables Section -->
                  <div style="background: #F3F4F6; padding: 10px; border-radius: 6px; margin-bottom: 10px; font-size: 12px; line-height: 1.5; color: #374151;">
                    <strong style="color: #0B3D91;">✓ Deliverables:</strong> ${t.deliverables}
                  </div>

                  <!-- Key Steps Section -->
                  ${t.key_steps ? `
                    <div style="background: #EFF6FF; border-left: 3px solid #2E7DFF; padding: 10px; border-radius: 4px; margin-bottom: 10px; font-size: 11px; line-height: 1.5; color: #1E3A8A;">
                      <strong>📋 Task Steps:</strong>
                      <pre style="margin: 4px 0 0 0; white-space: pre-wrap; word-wrap: break-word; font-size: 11px; font-family: monospace; color: #374151;">
${t.key_steps.substring(0, 300).trim()}${t.key_steps.length > 300 ? '...' : ''}
                      </pre>
                    </div>
                  ` : ''}

                  <!-- Submitted Work Display -->
                  ${sub && sub.marks !== null && sub.marks !== undefined ? `
                    <div style="font-size: 12px; background: #ECFDF5; border-left: 4px solid #10B981; padding: 10px; margin: 10px 0; color: #065F46; border-radius: 4px; line-height: 1.5;">
                      <div style="font-weight: 700; margin-bottom: 4px;">🏆 Marks: ${sub.marks} / ${sub.max_marks || 10}</div>
                      <div style="white-space: pre-wrap; font-size: 11px;">${(sub.feedback || 'Assignment successfully evaluated.').substring(0, 200)}</div>
                      ${sub.file_url ? `<a href="${sub.file_url}" target="_blank" style="font-size: 10px; color: #059669; text-decoration: underline; display: block; margin-top: 4px;">📄 View Submitted PDF</a>` : ''}
                    </div>
                  ` : sub && sub.file_url ? `
                    <div style="background: #DBEAFE; border-left: 4px solid #3B82F6; padding: 10px; margin: 10px 0; color: #1E40AF; border-radius: 4px; font-size: 11px;">
                      ✅ Submitted (Awaiting review)
                      <a href="${sub.file_url}" target="_blank" style="font-size: 10px; color: #1E40AF; text-decoration: underline; display: block; margin-top: 4px;">📄 View Submitted PDF</a>
                    </div>
                  ` : ''}

                  <!-- Upload Form -->
                  <form onsubmit="DashboardView.submitPdfFile(event, '${app.id}', ${t.week_number})" style="margin-top: 10px; background: #F8FAFC; padding: 12px; border-radius: 6px; border: 2px dashed #BFDBFE;">
                    <div style="display: flex; gap: 8px; align-items: flex-start; flex-direction: column;">
                      <label style="font-size: 12px; font-weight: 600; color: #374151;">📤 Upload PDF Assignment:</label>
                      <input type="file" id="pdf-file-${t.week_number}" accept=".pdf,application/pdf" class="form-input" style="font-size: 12px; padding: 8px; width: 100%; border: 1px solid #D1D5DB; border-radius: 4px; box-sizing: border-box;" required />
                      <div style="display: flex; gap: 8px; width: 100%;">
                        <button type="submit" class="btn btn-primary btn-sm" style="flex: 1; padding: 8px 12px; font-size: 12px; background: #0B3D91 !important; color: white; border: none; border-radius: 4px; cursor: pointer;">
                          📤 Upload & Submit
                        </button>
                        <button type="reset" class="btn btn-outline btn-sm" style="flex: 1; padding: 8px 12px; font-size: 12px; border: 1px solid #D1D5DB; border-radius: 4px; cursor: pointer;">
                          Clear
                        </button>
                      </div>
                      <span style="font-size: 10px; color: #64748B;">PDF files only, max 10MB. Must include all deliverables.</span>
                    </div>
                  </form>
                </div>
              `;
            }).join('')}
          </div>

          <!-- Footer -->
          <div style="display: flex; justify-content: space-between; align-items: center; gap: 8px; padding: 12px; border-top: 1px solid var(--color-border); background: #F9FAFB; border-radius: 6px; margin-top: 16px; flex-wrap: wrap;">
            <button onclick="Modals.close()" class="btn btn-outline btn-sm" style="flex: 1; font-size: 12px; min-width: 100px;">
              ✕ Close
            </button>
            <button onclick="Modals.openRazorpayCheckout('${app.id}')" class="btn btn-primary btn-sm" style="flex: 1; background-color: #D97706 !important; border-color: #B45309 !important; color: white !important; font-size: 12px; min-width: 120px;">
              💳 Pay ₹199 (Certificate)
            </button>
          </div>
        </div>
      `;

      Modals.open(html);
    } catch (e) {
      console.error("openWorkspace error:", e);
      Toast.show(e.message || 'Failed to open workspace.', 'error');
    }
  },

  async submitPdfFile(event, appId, weekNumber) {
    event.preventDefault();
    const fileInput = document.getElementById(`pdf-file-${weekNumber}`);
    
    if (!fileInput || !fileInput.files || fileInput.files.length === 0) {
      Toast.show('Please select a PDF file to upload.', 'error');
      return;
    }

    const file = fileInput.files[0];
    
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      Toast.show('❌ Only PDF files (.pdf) are allowed.', 'error');
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      Toast.show('❌ File size exceeds 10MB limit. Your file: ' + (file.size / (1024 * 1024)).toFixed(2) + 'MB', 'error');
      return;
    }

    if (file.size < 10 * 1024) {
      Toast.show('⚠️ File seems too small (< 10KB). Please ensure you uploaded the correct file.', 'warning');
    }

    const formData = new FormData();
    formData.append('application_id', appId);
    formData.append('week_number', weekNumber);
    formData.append('file', file);

    try {
      Toast.show(`📤 Uploading Week ${weekNumber} assignment PDF...`, 'info');
      const token = localStorage.getItem('access_token');
      const res = await fetch('/api/submissions/upload', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: formData
      });
      const data = await res.json();
      
      if (res.ok) {
        Toast.show('✅ ' + (data.message || 'Assignment PDF uploaded successfully!'), 'success');
        setTimeout(() => {
          Modals.close();
          this.loadApplications();
        }, 1000);
      } else {
        Toast.show('❌ ' + (data.error || 'PDF upload failed. Try again.'), 'error');
      }
    } catch (e) {
      console.error("submitPdfFile error:", e);
      Toast.show('❌ ' + (e.message || 'Network error during upload.'), 'error');
    }
  }
};
