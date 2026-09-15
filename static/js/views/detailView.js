// Internship Detailed Overview & Apply View
const DetailView = {
  async render(slug) {
    const container = document.getElementById('app-view');
    if (!container) return;

    container.innerHTML = `
      <section style="background: linear-gradient(135deg, var(--color-blue-dark) 0%, var(--color-primary-blue) 100%); color: var(--color-white); padding: 48px 0;">
        <div class="container">
          <div style="height: 16px; background: rgba(255,255,255,0.2); width: 25%; border-radius: 4px; margin-bottom: 16px;"></div>
          <div style="height: 36px; background: rgba(255,255,255,0.3); width: 60%; border-radius: 6px; margin-bottom: 16px;"></div>
          <div style="height: 20px; background: rgba(255,255,255,0.2); width: 80%; border-radius: 4px;"></div>
        </div>
      </section>
      <div class="container section-padding" style="text-align:center; color: var(--color-gray-text);">Loading internship program details...</div>
    `;

    try {
      const res = await API.request(`/api/internships/${slug}`);
      if (!res || !res.internship) {
        throw new Error("Internship program data not found.");
      }
      const item = res.internship;

      container.innerHTML = `
        <!-- Header Banner -->
        <section style="background: linear-gradient(135deg, var(--color-blue-dark) 0%, var(--color-primary-blue) 100%); color: var(--color-white); padding: 48px 0;">
          <div class="container">
            <div style="font-size: 13px; color: var(--color-blue-light); margin-bottom: 16px;">
              <a href="#/" style="color: var(--color-blue-light);">Home</a> / 
              <a href="#/sectors" style="color: var(--color-blue-light);">Sectors</a> / 
              <a href="#/sector/${item.sector_slug}" style="color: var(--color-blue-light);">${item.sector_name}</a> / 
              <span style="color: var(--color-white);">${item.title}</span>
            </div>

            <div style="display: flex; gap: 12px; margin-bottom: 16px; flex-wrap: wrap;">
              <span class="badge-sector" style="background: var(--color-accent-blue); color: #fff;">${item.sector_name}</span>
              <span class="badge-mode" style="background: rgba(255,255,255,0.2); color: #fff;">${item.mode || 'Virtual'}</span>
            </div>

            <h1 style="font-size: 40px; color: var(--color-white); margin-bottom: 16px;">${item.title}</h1>
            <p style="font-size: 18px; color: #DCE6F5; max-width: 800px; line-height: 1.6; margin-bottom: 28px;">${item.short_description}</p>

            <div style="display: flex; gap: 24px; align-items: center; flex-wrap: wrap;">
              <div style="display: flex; align-items: center; gap: 8px; font-weight: 600; font-size: 15px;">
                <i data-feather="clock" style="color: var(--color-accent-blue);"></i>
                Duration: ${item.duration_weeks} Weeks
              </div>
              <div style="display: flex; align-items: center; gap: 8px; font-weight: 600; font-size: 15px;">
                <i data-feather="dollar-sign" style="color: var(--color-accent-blue);"></i>
                Fee: 100% Free
              </div>

              <button onclick="DetailView.apply('${item.id}')" class="btn btn-primary btn-lg" style="background: var(--color-accent-blue); border-color: var(--color-accent-blue);">
                Apply for Internship Now →
              </button>
            </div>
          </div>
        </section>

        <!-- Main Detail Grid -->
        <section class="section-padding" style="background: var(--color-gray-bg);">
          <div class="container">
            <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 40px;">
              <div>
                <!-- About Description -->
                <div style="background: var(--color-white); border-radius: var(--radius-lg); padding: 32px; border: 1px solid var(--color-border); margin-bottom: 32px;">
                  <h2 style="font-size: 24px; color: var(--color-blue-dark); margin-bottom: 16px;">About this Internship Program</h2>
                  <p style="font-size: 15px; color: var(--color-gray-text); line-height: 1.7; white-space: pre-line;">${item.full_description || item.short_description}</p>
                </div>

                <!-- Tasks & Duties Accordion -->
                <div style="background: var(--color-white); border-radius: var(--radius-lg); padding: 32px; border: 1px solid var(--color-border); margin-bottom: 32px;">
                  <h2 style="font-size: 24px; color: var(--color-blue-dark); margin-bottom: 8px;">Tasks and Weekly Duties</h2>
                  <p style="color: var(--color-gray-text); margin-bottom: 24px;">Complete the following structured modules to earn your certificate of completion.</p>

                  <div class="accordion" id="tasks-accordion">
                    ${item.tasks && item.tasks.length > 0 ? item.tasks.map((task, idx) => `
                      <div class="accordion-item ${idx === 0 ? 'active' : ''}">
                        <div class="accordion-header" onclick="this.parentElement.classList.toggle('active')">
                          <span>Module Week ${task.week_number}: ${task.title}</span>
                          <i data-feather="chevron-down"></i>
                        </div>
                        <div class="accordion-body">
                          <div style="margin-bottom: 16px;">
                            <strong style="color: var(--color-blue-dark);">Objective:</strong>
                            <p style="color: var(--color-gray-text); font-size: 14px; margin-top: 4px;">${task.objective || 'N/A'}</p>
                          </div>
                          <div style="margin-bottom: 16px;">
                            <strong style="color: var(--color-blue-dark);">Expected Deliverable:</strong>
                            <p style="color: var(--color-gray-text); font-size: 14px; margin-top: 4px;">${task.deliverables || 'N/A'}</p>
                          </div>
                          <div style="margin-bottom: 16px;">
                            <strong style="color: var(--color-blue-dark);">Key Execution Steps:</strong>
                            <p style="color: var(--color-gray-text); font-size: 14px; margin-top: 4px; white-space: pre-line;">${task.key_steps || 'N/A'}</p>
                          </div>
                          <div>
                            <strong style="color: var(--color-blue-dark);">Evaluation Criteria:</strong>
                            <p style="color: var(--color-gray-text); font-size: 14px; margin-top: 4px;">${task.evaluation_criteria || 'N/A'}</p>
                          </div>
                        </div>
                      </div>
                    `).join('') : '<p>No tasks configured for this internship.</p>'}
                  </div>
                </div>
              </div>

              <!-- Sidebar Card -->
              <div>
                <div style="background: var(--color-white); border-radius: var(--radius-lg); padding: 28px; border: 1px solid var(--color-border); position: sticky; top: 96px;">
                  <h3 style="font-size: 20px; color: var(--color-blue-dark); margin-bottom: 16px;">Program Summary</h3>
                  
                  <ul style="list-style: none; display: flex; flex-direction: column; gap: 14px; margin-bottom: 24px; font-size: 14px;">
                    <li style="display:flex; justify-content:space-between; border-bottom: 1px solid var(--color-border); padding-bottom: 8px;">
                      <span style="color: var(--color-gray-text);">Duration:</span>
                      <strong style="color: var(--color-blue-dark);">${item.duration_weeks} Weeks</strong>
                    </li>
                    <li style="display:flex; justify-content:space-between; border-bottom: 1px solid var(--color-border); padding-bottom: 8px;">
                      <span style="color: var(--color-gray-text);">Learning Mode:</span>
                      <strong style="color: var(--color-blue-dark);">${item.mode || 'Virtual'}</strong>
                    </li>
                    <li style="display:flex; justify-content:space-between; border-bottom: 1px solid var(--color-border); padding-bottom: 8px;">
                      <span style="color: var(--color-gray-text);">Offer Letter:</span>
                      <strong style="color: #10B981;">Instant Automated</strong>
                    </li>
                    <li style="display:flex; justify-content:space-between; border-bottom: 1px solid var(--color-border); padding-bottom: 8px;">
                      <span style="color: var(--color-gray-text);">Certificate:</span>
                      <strong style="color: var(--color-primary-blue);">Included</strong>
                    </li>
                  </ul>

                  <button onclick="DetailView.apply('${item.id}')" class="btn btn-primary btn-full btn-lg">
                    Apply Now
                  </button>
                </div>
              </div>
            </div>
          </div>
        </section>
      `;

      if (window.feather) feather.replace();
    } catch (e) {
      container.innerHTML = `
        <div class="container section-padding" style="text-align:center; max-width: 600px; margin: 40px auto;">
          <div style="background: #FEF2F2; border-radius: var(--radius-lg); border: 1px solid #FCA5A5; padding: 40px 20px;">
            <div style="font-size: 44px; margin-bottom: 12px; color: #EF4444;">⚠️</div>
            <h3 style="font-size: 22px; color: #991B1B; margin-bottom: 8px;">Program Not Found</h3>
            <p style="color: #B91C1C; margin-bottom: 24px;">${e.message || 'Unable to retrieve details for this internship program.'}</p>
            <a href="#/internships" class="btn btn-primary">Browse All Internships</a>
          </div>
        </div>
      `;
    }
  },

  async apply(internshipId) {
    const user = API.getCurrentUser();
    if (!user) {
      Toast.show('Please sign in or create an account to apply.', 'info');
      window.location.hash = `#/login?redirect=${encodeURIComponent(window.location.hash)}`;
      return;
    }

    // ========== PRE-FLIGHT AUTH CHECK ==========
    // Catch expired/invalid token BEFORE the apply request to avoid 500 spinner.
    try {
      await API.request('/api/auth/me');
    } catch (authErr) {
      const msg = authErr.message || 'Session expired';
      console.warn('[Apply Pre-Auth] Invalid/expired session:', msg);
      if (msg.toLowerCase().includes('session') || msg.toLowerCase().includes('token') || msg.toLowerCase().includes('expired') || msg.toLowerCase().includes('login')) {
        API.setAuthToken(null);
        API.setCurrentUser(null);
        Toast.show('Your session has expired. Please login again to apply.', 'error');
        setTimeout(() => {
          window.location.hash = `#/login?redirect=${encodeURIComponent(window.location.hash)}`;
        }, 600);
      } else {
        Toast.show(msg, 'error');
      }
      return;
    }

    try {
      Toast.show('Submitting application & issuing offer letter...', 'info');
      const res = await API.request('/api/applications', {
        method: 'POST',
        body: { internship_id: internshipId }
      });

      // Cache server confirmed enrollment to IndexedDB for offline access
      if (Storage && res.application) {
        try {
          const app = res.application;
          const finalEnrollment = {
            id: app.id,
            userId: user.id,
            internshipId: internshipId,
            internshipTitle: app.internship_title || '',
            companyName: app.company_name || '',
            sectorName: app.sector_name || '',
            status: app.status || 'active',
            progress: 0,
            enrolledAt: app.applied_at ? new Date(app.applied_at).toISOString() : new Date().toISOString(),
            startDate: app.start_date,
            endDate: app.end_date,
            serverData: app,
            pendingSync: false,
            offerLetterId: res.offer_letter_id,
            offer_download_url: res.offer_download_url
          };
          await Storage.saveEnrollment(finalEnrollment);

          if (app.id) {
            const offerLetter = {
              userId: user.id,
              enrollmentId: app.id,
              internshipId: internshipId,
              internshipTitle: finalEnrollment.internshipTitle,
              candidateName: user.name || user.full_name || user.email,
              status: 'issued',
              issueDate: new Date().toISOString(),
              downloadUrl: res.offer_download_url || null,
              offerId: res.offer_letter_id || null
            };
            await Storage.saveOfferLetter(offerLetter);
          }
        } catch (err) {
          console.warn('[Storage] Failed to cache confirmed enrollment:', err);
        }
      }

      // ========== SHOW WARNINGS FROM BACKEND AS INFO TOASTS ==========
      if (Array.isArray(res.warnings) && res.warnings.length) {
        res.warnings.slice(0, 3).forEach(w => {
          setTimeout(() => Toast.show(w, 'info'), 400);
        });
      }

      if (res.offer_download_url) {
        Toast.show((res.message || 'Enrollment successful!') + ' You can also download the offer letter from the dashboard.', 'success', 5000);
      } else {
        Toast.show(res.message || 'Enrollment successful!', 'success');
      }
      window.location.hash = '#/dashboard';
    } catch (err) {
      const errMsg = (err && err.message) ? err.message : 'Could not complete application. Please try again.';
      const sessionRelated = /session|token|expired|login/i.test(errMsg);
      if (sessionRelated) {
        API.setAuthToken(null);
        API.setCurrentUser(null);
        Toast.show('Session expired. Please login and try applying again.', 'error');
        setTimeout(() => {
          window.location.hash = `#/login?redirect=${encodeURIComponent(window.location.hash)}`;
        }, 800);
      } else {
        Toast.show(errMsg, 'error', 6000);
      }
    }
  }
  }
};
