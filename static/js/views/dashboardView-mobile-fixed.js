// Dashboard View Controller - Mobile Optimized
const DashboardView = {
  render() {
    const user = API.getCurrentUser();
    if (!user) {
      window.location.hash = '#/login';
      return;
    }

    const appEl = document.getElementById('app-view') || document.getElementById('app');
    if (!appEl) return;
    appEl.innerHTML = `
      <section class="section" style="padding: 16px 0; background-color: var(--color-gray-bg); min-height: calc(100vh - 130px);">
        <div class="container">
          <!-- Welcome Banner -->
          <div class="welcome-banner">
            <div>
              <h1 style="font-size: 22px; margin: 0; color: white; line-height: 1.3;">Welcome back! 👋</h1>
              <p style="margin-top: 6px; opacity: 0.9; font-size: 14px; line-height: 1.5; color: white;">${user.name || user.email}</p>
              <p style="margin-top: 6px; opacity: 0.85; font-size: 13px; line-height: 1.4; color: white;">Track your internships, submit assignments, and download certificates.</p>
            </div>
            <div class="tab-buttons" style="margin-top: 12px;">
              <button onclick="DashboardView.switchTab('apps')" id="tab-btn-apps" class="tab-button" style="background: #FFFFFF; color: #082B66; border: none; box-shadow: 0 2px 8px rgba(0,0,0,0.15);">My Internships</button>
              <button onclick="DashboardView.switchTab('docs')" id="tab-btn-docs" class="tab-button" style="background: rgba(255,255,255,0.2); color: #FFFFFF; border: 1px solid rgba(255,255,255,0.3);">Documents</button>
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
      const res = await API.request('/api/applications/me');
      const container = document.getElementById('dashboard-apps-list');
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

        return `
          <div class="application-card">
            <div style="display: flex; align-items: flex-start; justify-content: space-between; gap: 10px; flex-wrap: wrap; margin-bottom: 12px;">
              <div>
                <span class="badge-sector">${app.sector_name}</span>
                <h2 style="font-size: 18px; color: var(--color-blue-dark); margin: 8px 0 4px 0; line-height: 1.3;">${app.internship_title}</h2>
                <p style="font-size: 12px; color: var(--color-gray-text); margin: 2px 0; line-height: 1.4;">
                  Start: <strong>${app.start_date || 'N/A'}</strong> • End: <strong>${app.end_date || 'N/A'}</strong>
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

            <!-- Status & Actions -->
            <div style="margin-top: 12px;">
              <p style="font-size: 12px; color: var(--color-gray-text); margin-bottom: 10px;">
                Status: <strong style="color: #0B3D91;">${app.status || 'ACTIVE'}</strong>
              </p>
              <div class="application-actions">
                <a href="/api/applications/${app.id}/offer-letter.pdf" target="_blank" class="btn btn-outline btn-sm" style="flex: 1; text-align: center; font-size: 12px;">
                  📄 Offer
                </a>
                ${isPaid && isCompleted && app.certificate_id ? `
                  <a href="/api/certificates/${app.certificate_id}/pdf" target="_blank" class="btn btn-primary btn-sm" style="flex: 1; text-align: center; background: #2E7DFF !important; color: white !important; font-size: 12px;">
                    🏆 Cert
                  </a>
                ` : `
                  <button onclick="DashboardView.handleCertificateClick('${app.id}')" class="btn btn-primary btn-sm" style="flex: 1; background: #2E7DFF !important; color: white !important; font-size: 12px;">
                    🏆 Cert
                  </button>
                `}
                <button onclick="DashboardView.openWorkspace('${app.id}')" class="btn btn-primary btn-sm" style="flex: 1; background: #0B3D91 !important; color: white !important; font-size: 12px;">
                  ✏️ Tasks
                </button>
              </div>
            </div>
          </div>
        `;
      }).join('');

      if (window.feather) feather.replace();
    } catch (e) {
      console.error("Load applications error:", e);
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
          <h2 style="font-size: 18px; color: var(--color-blue-dark); margin-bottom: 16px;">My Official Documents</h2>
          
          <div style="display: flex; flex-direction: column; gap: 12px;">
            ${res.applications.map(app => {
              const isCompleted = app.status === 'completed' || app.completion_status === 'completed';
              const isPaid = Boolean(app.is_verified_paid == 1 || app.is_verified_paid === true || app.paid);

              return `
                <div style="border: 1px solid var(--color-border); border-radius: 10px; padding: 12px; background: #F8FAFC;">
                  <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 8px; flex-wrap: wrap;">
                    <div style="flex: 1;">
                      <h3 style="font-size: 14px; color: var(--color-blue-dark); margin: 0 0 4px 0;">Internship Offer Letter</h3>
                      <p style="font-size: 12px; color: var(--color-gray-text); margin: 0;">${app.internship_title}</p>
                      <span style="font-size: 10px; font-weight: 700; color: #10B981; background: #D1FAE5; padding: 3px 8px; border-radius: 4px; display: inline-block; margin-top: 6px;">ISSUED</span>
                    </div>
                    <div style="display: flex; gap: 6px; flex-wrap: wrap; justify-content: flex-end;">
                      <a href="/api/applications/${app.id}/offer-letter.pdf" target="_blank" class="btn btn-outline btn-sm" style="font-size: 11px; padding: 6px 10px; min-height: 32px;">View</a>
                      <a href="/api/applications/${app.id}/offer-letter.pdf" download class="btn btn-primary btn-sm" style="font-size: 11px; padding: 6px 10px; min-height: 32px; background: #2E7DFF !important;">Download</a>
                    </div>
                  </div>
                </div>

                <div style="border: 1px solid var(--color-border); border-radius: 10px; padding: 12px; background: #F8FAFC;">
                  <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 8px; flex-wrap: wrap;">
                    <div style="flex: 1;">
                      <h3 style="font-size: 14px; color: var(--color-blue-dark); margin: 0 0 4px 0;">Certificate</h3>
                      <p style="font-size: 12px; color: var(--color-gray-text); margin: 0;">${app.internship_title}</p>
                      ${isPaid && isCompleted && app.certificate_id ? `
                        <span style="font-size: 10px; font-weight: 700; color: #0B3D91; background: #EAF1FB; padding: 3px 8px; border-radius: 4px; display: inline-block; margin-top: 6px;">ISSUED & PAID</span>
                      ` : isPaid ? `
                        <span style="font-size: 10px; font-weight: 700; color: #D97706; background: #FEF3C7; padding: 3px 8px; border-radius: 4px; display: inline-block; margin-top: 6px;">PAID - PENDING</span>
                      ` : `
                        <span style="font-size: 10px; font-weight: 700; color: #475569; background: #E2E8F0; padding: 3px 8px; border-radius: 4px; display: inline-block; margin-top: 6px;">PENDING</span>
                      `}
                    </div>
                    <div style="display: flex; gap: 6px; flex-wrap: wrap; justify-content: flex-end;">
                      ${isPaid && isCompleted && app.certificate_id ? `
                        <a href="/api/certificates/${app.certificate_id}/pdf" target="_blank" class="btn btn-outline btn-sm" style="font-size: 11px; padding: 6px 10px; min-height: 32px;">View</a>
                        <a href="/api/certificates/${app.certificate_id}/pdf" download class="btn btn-primary btn-sm" style="font-size: 11px; padding: 6px 10px; min-height: 32px; background: #2E7DFF !important;">Download</a>
                      ` : `
                        <button onclick="DashboardView.handleCertificateClick('${app.id}')" class="btn btn-primary btn-sm" style="font-size: 11px; padding: 6px 10px; min-height: 32px; background: #2E7DFF !important;">Get Certificate</button>
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
            <h2 style="font-size: 18px; color: var(--color-blue-dark); margin-bottom: 6px;">Task Workspace</h2>
            <p style="color: var(--color-gray-text); font-size: 13px; margin: 0; line-height: 1.4;">
              Upload your weekly PDF assignment deliverables (Max 10MB per module) for mentor review and grading.
            </p>
          </div>

          <div style="display: flex; flex-direction: column; gap: 12px; margin-bottom: 16px;">
            ${app.tasks.map(t => {
              const sub = t.submission;
              const subStatus = sub ? sub.status : 'NOT_SUBMITTED';
              let badgeColor = '#9CA3AF';
              if (['graded', 'approved'].includes(subStatus.toLowerCase())) badgeColor = '#10B981';
              if (subStatus.toLowerCase() === 'submitted' || subStatus.toLowerCase() === 'pending') badgeColor = '#3B82F6';
              if (['revise', 'rejected', 'late'].includes(subStatus.toLowerCase())) badgeColor = '#EF4444';

              return `
                <div class="task-card">
                  <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 8px; flex-wrap: wrap; margin-bottom: 8px;">
                    <strong style="font-size: 14px; color: var(--color-blue-dark);">Week ${t.week_number}: ${t.title}</strong>
                    ${sub && sub.file_url ? `
                      <a href="${sub.file_url}" target="_blank" style="font-size: 11px; color: #2E7DFF; text-decoration: underline;">📄 PDF</a>
                    ` : ''}
                    <span style="font-size: 10px; font-weight: 700; color: white; background: ${badgeColor}; padding: 3px 8px; border-radius: 4px; text-transform: uppercase;">
                      ${subStatus.replace('_', ' ')}
                    </span>
                  </div>
                  <p style="font-size: 12px; color: var(--color-gray-text); margin-bottom: 10px; line-height: 1.4;">
                    <strong>Deliverables:</strong> ${t.deliverables}
                  </p>

                  ${sub && sub.marks !== null && sub.marks !== undefined ? `
                    <div style="font-size: 12px; background: #ECFDF5; border-left: 4px solid #10B981; padding: 10px; margin: 10px 0; color: #065F46; border-radius: 4px; line-height: 1.5;">
                      <div style="font-weight: 700; margin-bottom: 4px;">🏆 Marks: ${sub.marks} / ${sub.max_marks || 10}</div>
                      <div style="white-space: pre-wrap; font-size: 11px;">${(sub.feedback || 'Assignment successfully evaluated.').substring(0, 150)}</div>
                    </div>
                  ` : ''}

                  <form onsubmit="DashboardView.submitPdfFile(event, '${app.id}', ${t.week_number})" style="margin-top: 10px; background: #F8FAFC; padding: 10px; border-radius: 6px; border: 1px dashed var(--color-border);">
                    <div style="display: flex; gap: 8px; align-items: center; flex-wrap: wrap;">
                      <input type="file" id="pdf-file-${t.week_number}" accept=".pdf,application/pdf" class="form-input" style="font-size: 12px; padding: 8px; flex: 1; min-width: 150px;" />
                      <button type="submit" class="btn btn-primary btn-sm" style="white-space: nowrap; padding: 6px 12px; font-size: 11px; min-height: 36px;">
                        Upload
                      </button>
                    </div>
                    <span style="font-size: 10px; color: #64748B; margin-top: 4px; display: block;">
                      PDF only, max 10MB
                    </span>
                  </form>
                </div>
              `;
            }).join('')}
          </div>

          <div style="display: flex; justify-content: space-between; align-items: center; gap: 8px; padding-top: 12px; border-top: 1px solid var(--color-border); flex-wrap: wrap;">
            <button onclick="Modals.close()" class="btn btn-outline btn-sm" style="flex: 1; font-size: 12px;">
              Close
            </button>
            <button onclick="Modals.openRazorpayCheckout('${app.id}')" class="btn btn-primary btn-sm" style="flex: 1; background-color: #D97706 !important; border-color: #B45309 !important; color: white !important; font-size: 12px;">
              💳 Pay ₹199
            </button>
          </div>
        </div>
      `;

      Modals.open(html);
    } catch (e) {
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
      Toast.show('Only PDF files (.pdf) are allowed.', 'error');
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      Toast.show('File size exceeds 10MB limit.', 'error');
      return;
    }

    const formData = new FormData();
    formData.append('application_id', appId);
    formData.append('week_number', weekNumber);
    formData.append('file', file);

    try {
      Toast.show(`Uploading Week ${weekNumber} assignment PDF...`, 'info');
      const token = localStorage.getItem('access_token');
      const res = await fetch('/api/submissions/upload', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: formData
      });
      const data = await res.json();
      if (res.ok) {
        Toast.show(data.message || 'Assignment PDF uploaded successfully!', 'success');
        Modals.close();
        this.loadApplications();
      } else {
        Toast.show(data.error || 'PDF upload failed.', 'error');
      }
    } catch (e) {
      Toast.show(e.message || 'Task upload failed.', 'error');
    }
  }
};
