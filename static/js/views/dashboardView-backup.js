// Dashboard View Controller
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
              <p style="margin-top: 6px; opacity: 0.9; font-size: 14px; line-height: 1.5;">${user.name || user.email}</p>
              <p style="margin-top: 6px; opacity: 0.85; font-size: 13px; line-height: 1.4;">Track your internships, submit assignments, and download certificates.</p>
            </div>
            <div class="tab-buttons" style="margin-top: 12px;">
              <button onclick="DashboardView.switchTab('apps')" id="tab-btn-apps" class="tab-button" style="background: #FFFFFF; color: #082B66; border: none; box-shadow: 0 2px 8px rgba(0,0,0,0.15);">My Internships</button>
              <button onclick="DashboardView.switchTab('docs')" id="tab-btn-docs" class="tab-button" style="background: rgba(255,255,255,0.2); color: #FFFFFF; border: 1px solid rgba(255,255,255,0.3);">Documents</button>
            </div>
          </div>

          <!-- Applications Tab Content -->
          <div id="tab-content-apps">
            <div id="dashboard-apps-list">
              <div style="padding: 40px; text-align: center; color: var(--color-gray-text);">Loading your internship workspace...</div>
            </div>
          </div>

          <!-- Documents Tab Content -->
          <div id="tab-content-docs" style="display: none;">
            <div id="dashboard-docs-list">
              <div style="padding: 40px; text-align: center; color: var(--color-gray-text);">Loading document records...</div>
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
        btnApps.style.border = '2px solid #FFFFFF';
        btnApps.style.fontWeight = '700';
        btnApps.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
      }
      if (btnDocs) {
        btnDocs.style.background = 'rgba(255,255,255,0.15)';
        btnDocs.style.color = '#FFFFFF';
        btnDocs.style.border = '2px solid rgba(255,255,255,0.8)';
        btnDocs.style.fontWeight = '600';
        btnDocs.style.boxShadow = 'none';
      }
    } else {
      contentApps.style.display = 'none';
      contentDocs.style.display = 'block';
      if (btnDocs) {
        btnDocs.style.background = '#FFFFFF';
        btnDocs.style.color = '#082B66';
        btnDocs.style.border = '2px solid #FFFFFF';
        btnDocs.style.fontWeight = '700';
        btnDocs.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
      }
      if (btnApps) {
        btnApps.style.background = 'rgba(255,255,255,0.15)';
        btnApps.style.color = '#FFFFFF';
        btnApps.style.border = '2px solid rgba(255,255,255,0.8)';
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
          <div style="background: white; border-radius: var(--radius-lg); padding: 48px; text-align: center; border: 1px solid var(--color-border);">
            <i data-feather="book-open" style="width: 48px; height: 48px; color: var(--color-accent-blue); margin-bottom: 16px;"></i>
            <h3 style="font-size: 22px; color: var(--color-blue-dark); margin-bottom: 8px;">No Active Internships Found</h3>
            <p style="color: var(--color-gray-text); margin-bottom: 24px;">You haven't enrolled in any virtual internship program yet.</p>
            <a href="#/internships" class="btn btn-primary">Browse Available Internships →</a>
          </div>
        `;
        if (window.feather) feather.replace();
        return;
      }

      container.innerHTML = res.applications.map(app => {
        const isCompleted = app.status === 'completed' || app.completion_status === 'completed';
        const isPaid = Boolean(app.is_verified_paid == 1 || app.is_verified_paid === true || app.paid);

        return `
          <div style="background: var(--color-white); border-radius: var(--radius-lg); border: 1px solid var(--color-border); padding: 32px; margin-bottom: 24px; box-shadow: var(--shadow-sm);">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; flex-wrap: wrap; gap: 12px;">
              <div>
                <span class="badge-sector">${app.sector_name}</span>
                <h2 style="font-size: 24px; color: var(--color-blue-dark); margin-top: 6px;">${app.internship_title}</h2>
                <p style="font-size: 13px; color: var(--color-gray-text); margin-top: 2px;">
                  Start Date: <strong>${app.start_date || 'N/A'}</strong> | Target End Date: <strong>${app.end_date || 'N/A'}</strong>
                </p>
              </div>
              <div style="display: flex; gap: 10px; flex-wrap: wrap; align-items: center;">
                <a href="/api/applications/${app.id}/offer-letter.pdf" target="_blank" class="btn btn-outline btn-sm">
                  <i data-feather="file-text" style="width:14px;"></i> View Offer Letter PDF
                </a>

                ${isPaid && isCompleted && app.certificate_id ? `
                  <a href="/api/certificates/${app.certificate_id}/pdf" target="_blank" class="btn btn-primary btn-sm">
                    <i data-feather="award" style="width:14px;"></i> View / Download Certificate
                  </a>
                ` : `
                  <button onclick="DashboardView.handleCertificateClick('${app.id}')" class="btn btn-primary btn-sm">
                    <i data-feather="award" style="width:14px;"></i> View / Download Certificate
                  </button>
                `}
              </div>
            </div>

            <!-- Progress Bar -->
            <div style="margin-bottom: 24px;">
              <div style="display: flex; justify-content: space-between; font-size: 14px; font-weight: 600; margin-bottom: 8px;">
                <span style="color: var(--color-blue-dark);">Module Progress: Week ${app.completed_weeks} of ${app.duration_weeks} Completed</span>
                <span style="color: var(--color-accent-blue);">${app.progress_percent}%</span>
              </div>
              <div class="progress-bar-track">
                <div class="progress-bar-fill" style="width: ${app.progress_percent}%;"></div>
              </div>
            </div>

            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
              <span style="font-size: 13px; color: var(--color-gray-text);">
                Status: <strong style="color: #0B3D91; text-transform: uppercase;">${app.status || 'ACTIVE'}</strong>
              </span>
              <button onclick="DashboardView.openWorkspace('${app.id}')" class="btn btn-primary">
                Open Task Workspace & Submit Assignments →
              </button>
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
        container.innerHTML = `<div style="background: white; border-radius: var(--radius-lg); padding: 40px; text-align: center;">No document records found.</div>`;
        return;
      }

      container.innerHTML = `
        <div style="background: var(--color-white); border-radius: var(--radius-lg); border: 1px solid var(--color-border); padding: 32px;">
          <h2 style="font-size: 22px; color: var(--color-blue-dark); margin-bottom: 20px;">My Official Documents</h2>
          
          <div style="display: flex; flex-direction: column; gap: 20px;">
            ${res.applications.map(app => {
              const isCompleted = app.status === 'completed' || app.completion_status === 'completed';
              const isPaid = Boolean(app.is_verified_paid == 1 || app.is_verified_paid === true || app.paid);

              return `
                <!-- Offer Letter Box -->
                <div style="border: 1px solid var(--color-border); border-radius: var(--radius-md); padding: 20px; background: #F8FAFC;">
                  <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
                    <div>
                      <h3 style="font-size: 18px; color: var(--color-blue-dark); margin: 0;">Internship Offer Letter</h3>
                      <p style="font-size: 14px; color: var(--color-gray-text); margin-top: 4px;">Program: <strong>${app.internship_title}</strong></p>
                      <span style="font-size: 12px; font-weight: 700; color: #10B981; background: #D1FAE5; padding: 4px 10px; border-radius: 99px;">STATUS: ISSUED</span>
                    </div>
                    <div style="display: flex; gap: 10px;">
                      <a href="/api/applications/${app.id}/offer-letter.pdf" target="_blank" class="btn btn-outline btn-sm">
                        [View]
                      </a>
                      <a href="/api/applications/${app.id}/offer-letter.pdf" download class="btn btn-primary btn-sm">
                        [Download]
                      </a>
                    </div>
                  </div>
                </div>

                <!-- Certificate Box -->
                <div style="border: 1px solid var(--color-border); border-radius: var(--radius-md); padding: 20px; background: #F8FAFC;">
                  <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
                    <div>
                      <h3 style="font-size: 18px; color: var(--color-blue-dark); margin: 0;">Internship Completion Certificate</h3>
                      <p style="font-size: 14px; color: var(--color-gray-text); margin-top: 4px;">Program: <strong>${app.internship_title}</strong></p>
                      ${isPaid && isCompleted && app.certificate_id ? `
                        <span style="font-size: 12px; font-weight: 700; color: #0B3D91; background: #EAF1FB; padding: 4px 10px; border-radius: 99px;">
                          STATUS: ISSUED & PAID (ID: ${app.certificate_id})
                        </span>
                      ` : isPaid ? `
                        <span style="font-size: 12px; font-weight: 700; color: #D97706; background: #FEF3C7; padding: 4px 10px; border-radius: 99px;">
                          STATUS: PAID — ASSIGNMENTS PENDING
                        </span>
                      ` : `
                        <span style="font-size: 12px; font-weight: 700; color: #475569; background: #E2E8F0; padding: 4px 10px; border-radius: 99px;">
                          STATUS: CERTIFICATE PENDING
                        </span>
                      `}
                    </div>
                    <div style="display: flex; gap: 10px;">
                      ${isPaid && isCompleted && app.certificate_id ? `
                        <a href="/api/certificates/${app.certificate_id}/pdf" target="_blank" class="btn btn-outline btn-sm">
                          [View]
                        </a>
                        <a href="/api/certificates/${app.certificate_id}/pdf" download class="btn btn-primary btn-sm">
                          [Download]
                        </a>
                      ` : `
                        <button onclick="DashboardView.handleCertificateClick('${app.id}')" class="btn btn-primary btn-sm">
                          View / Download Certificate
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

      let html = `
        <div style="max-width: 680px; font-family: inherit;">
          <!-- Sticky Top Header Bar -->
          <div style="position: sticky; top: -28px; background: #FFFFFF; z-index: 10; margin: -28px -28px 20px -28px; padding: 16px 24px; border-bottom: 1px solid var(--color-border); display: flex; align-items: center; justify-content: space-between; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
            <button onclick="Modals.close()" class="btn btn-outline btn-sm" style="display: inline-flex; align-items: center; gap: 6px; font-weight: 700;">
              ← Back to Dashboard
            </button>
            <span style="font-size: 13px; font-weight: 700; color: var(--color-blue-dark);">
              ${app.internship_title}
            </span>
          </div>

          <div style="margin-bottom: 20px;">
            <h2 style="font-size: 24px; color: var(--color-blue-dark); margin-bottom: 6px;">Task Workspace & Deliverables</h2>
            <p style="color: var(--color-gray-text); font-size: 14px; margin: 0;">
              Upload your weekly PDF assignment deliverables (Max 10MB per module) for mentor review and grading.
            </p>
          </div>

          <div style="display: flex; flex-direction: column; gap: 20px; margin-bottom: 24px;">
            ${app.tasks.map(t => {
              const sub = t.submission;
              const subStatus = sub ? sub.status : 'NOT_SUBMITTED';
              let badgeColor = '#9CA3AF';
              if (['graded', 'approved'].includes(subStatus.toLowerCase())) badgeColor = '#10B981';
              if (subStatus.toLowerCase() === 'submitted' || subStatus.toLowerCase() === 'pending') badgeColor = '#3B82F6';
              if (['revise', 'rejected', 'late'].includes(subStatus.toLowerCase())) badgeColor = '#EF4444';

              return `
                <div style="border: 1px solid var(--color-border); border-radius: var(--radius-md); padding: 20px; background: #FFFFFF; box-shadow: var(--shadow-sm);">
                  <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; flex-wrap: wrap; gap: 8px;">
                    <strong style="color: var(--color-blue-dark); font-size: 16px;">Week ${t.week_number}: ${t.title}</strong>
                    <div style="display: flex; align-items: center; gap: 10px;">
                      ${sub && sub.file_url ? `
                        <a href="${sub.file_url}" target="_blank" class="btn btn-outline btn-sm" style="font-size: 11px; padding: 4px 8px;">
                          📄 View Uploaded PDF
                        </a>
                      ` : ''}
                      <span style="font-size: 11px; font-weight: 700; color: white; background: ${badgeColor}; padding: 4px 10px; border-radius: 99px; text-transform: uppercase;">
                        ${subStatus.replace('_', ' ')}
                      </span>
                    </div>
                  </div>
                  <p style="font-size: 13px; color: var(--color-gray-text); margin-bottom: 12px; line-height: 1.5;">
                    <strong>Deliverables Required:</strong> ${t.deliverables}
                  </p>

                  <!-- Marks & Feedback Display -->
                  ${sub && sub.marks !== null && sub.marks !== undefined ? `
                    <div style="font-size: 13px; background: #ECFDF5; border-left: 4px solid #10B981; padding: 12px; margin: 12px 0; color: #065F46; border-radius: 4px; line-height: 1.6;">
                      <div style="font-weight: 700; font-size: 14px; margin-bottom: 6px; color: #047857;">
                        🏆 Marks Obtained: ${sub.marks} / ${sub.max_marks || 10}
                      </div>
                      <div style="white-space: pre-line;">
                        ${(sub.feedback || 'Assignment successfully evaluated.').replace(/\n/g, '<br/>')}
                      </div>
                    </div>
                  ` : ''}

                  <form onsubmit="DashboardView.submitPdfFile(event, '${app.id}', ${t.week_number})" style="margin-top: 14px; background: #F8FAFC; padding: 14px; border-radius: var(--radius-sm); border: 1px dashed var(--color-border);">
                    <div style="display: flex; gap: 10px; align-items: center; flex-wrap: wrap;">
                      <input type="file" id="pdf-file-${t.week_number}" accept=".pdf,application/pdf" class="form-input" style="font-size: 12px; padding: 8px; flex: 1; min-width: 220px;" />
                      <button type="submit" class="btn btn-primary btn-sm" style="white-space: nowrap; padding: 8px 16px;">
                        ${sub ? 'Re-upload PDF' : 'Upload & Submit PDF'}
                      </button>
                    </div>
                    <span style="font-size: 11px; color: #64748B; margin-top: 6px; display: block;">
                      Supported format: PDF documents only (Max size 10MB).
                    </span>
                  </form>
                </div>
              `;
            }).join('')}
          </div>

          <div style="display: flex; justify-content: space-between; align-items: center; padding-top: 16px; border-top: 1px solid var(--color-border);">
            <button onclick="Modals.close()" class="btn btn-outline">
              ← Close & Return to Dashboard
            </button>
            <button onclick="Modals.openRazorpayCheckout('${app.id}')" class="btn btn-primary btn-sm" style="background-color: #D97706; border-color: #B45309; color: white;">
              💳 Pay ₹199 Certificate Fee
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
