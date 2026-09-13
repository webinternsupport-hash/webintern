// Global Modal & Razorpay Checkout Controller
const Modals = {
  init() {
    const overlay = document.getElementById('global-modal-overlay');
    if (overlay) {
      overlay.addEventListener('click', (e) => {
        if (e.target === overlay) {
          this.close();
        }
      });
    }

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        this.close();
      }
    });
  },

  open(htmlContent) {
    this.init();
    const overlay = document.getElementById('global-modal-overlay');
    const content = document.getElementById('global-modal-content');
    if (!overlay || !content) return;

    content.innerHTML = `
      <button class="modal-close-btn" onclick="Modals.close()" title="Close Modal">&times;</button>
      ${htmlContent}
    `;
    overlay.classList.add('open');
    if (window.feather) feather.replace();
  },

  close() {
    const overlay = document.getElementById('global-modal-overlay');
    if (overlay) {
      overlay.classList.remove('open');
    }
  },

  async openRazorpayCheckout(applicationIdOrCertificateId) {
    try {
      Toast.show('Generating secure Razorpay payment gateway order (₹199 Fee)...', 'info');
      const orderRes = await API.request('/api/payments/certificate/create-order', {
        method: 'POST',
        body: {
          enrollment_id: applicationIdOrCertificateId,
          application_id: applicationIdOrCertificateId,
          certificate_id: applicationIdOrCertificateId
        }
      });

      if (orderRes.already_paid) {
        Toast.show('You have already paid the ₹199 certificate fee!', 'success');
        if (window.DashboardView) DashboardView.render();
        return;
      }

      const options = {
        key: orderRes.key_id,
        amount: orderRes.amount,
        currency: orderRes.currency,
        name: "WEBINTERN Platform",
        description: "₹199 Internship Completion Certificate Fee",
        order_id: orderRes.order_id,
        handler: async function (response) {
          Toast.show('Verifying transaction signature...', 'info');
          try {
            const verifyRes = await API.request('/api/payments/certificate/verify', {
              method: 'POST',
              body: {
                razorpay_order_id: response.razorpay_order_id,
                razorpay_payment_id: response.razorpay_payment_id,
                razorpay_signature: response.razorpay_signature,
                enrollment_id: applicationIdOrCertificateId,
                application_id: applicationIdOrCertificateId
              }
            });
            Toast.show(verifyRes.message || 'Payment Verified Successfully!', 'success');
            if (window.DashboardView) {
              DashboardView.render();
            } else {
              window.location.hash = '#/dashboard';
            }
          } catch (e) {
            Toast.show('Payment verification failed: ' + (e.message || e), 'error');
          }
        },
        prefill: {
          name: API.getCurrentUser()?.name || "",
          email: API.getCurrentUser()?.email || ""
        },
        theme: {
          color: "#0B3D91"
        }
      };

      if (window.Razorpay) {
        const rzp = new Razorpay(options);
        rzp.open();
      } else {
        Toast.show('Razorpay SDK loading... Retry in a moment.', 'error');
      }
    } catch (err) {
      Toast.show(err.message || 'Payment initiation failed.', 'error');
    }
  },

  openPaymentInfoModal(appId, title) {
    const html = `
      <div style="padding: 10px 4px; text-align: left;">
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 16px;">
          <div style="background: #EAF1FB; border-radius: 50%; padding: 12px; color: #0B3D91; display: flex; align-items: center; justify-content: center;">
            <i data-feather="award" style="width:28px; height:28px;"></i>
          </div>
          <div>
            <h2 style="font-size: 20px; color: #0B3D91; margin: 0;">Official Certificate Verification Fee</h2>
            <p style="font-size: 13px; color: #64748B; margin-top: 2px;">${title || 'Internship Completion Certificate'}</p>
          </div>
        </div>

        <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 12px; padding: 20px; margin-bottom: 20px;">
          <h4 style="font-size: 15px; color: #1E293B; margin-top: 0; margin-bottom: 12px; font-weight: 700;">Why is the ₹199 Verification Fee Required?</h4>
          <ul style="padding-left: 20px; margin: 0; font-size: 14px; color: #475569; line-height: 1.8;">
            <li><strong>MSME Recognized Framework:</strong> Includes government-aligned virtual internship certification credentials.</li>
            <li><strong>Permanent QR Verification:</strong> Generates a lifetime verifiable QR code and record link for employers.</li>
            <li><strong>Authenticated Digital Seal & Signatures:</strong> Features founding board signatures and authenticated hologram seal.</li>
            <li><strong>LinkedIn & Resume Badge:</strong> Official credential token for your professional profile & academic submission.</li>
          </ul>
        </div>

        <div style="display: flex; gap: 12px; justify-content: flex-end;">
          <button onclick="Modals.close()" class="btn btn-outline" style="padding: 10px 20px;">Cancel</button>
          <button onclick="Modals.close(); Modals.openRazorpayCheckout('${appId}')" class="btn btn-primary" style="padding: 10px 24px; font-weight: 700;">
            Proceed to Pay ₹199 via Razorpay →
          </button>
        </div>
      </div>
    `;
    this.open(html);
  },

  openAssignmentPendingModal(appId, title, completedWeeks, durationWeeks) {
    const html = `
      <div style="padding: 10px 4px; text-align: left;">
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 16px;">
          <div style="background: #FEF3C7; border-radius: 50%; padding: 12px; color: #D97706; display: flex; align-items: center; justify-content: center;">
            <i data-feather="clock" style="width:28px; height:28px;"></i>
          </div>
          <div>
            <h2 style="font-size: 20px; color: #0B3D91; margin: 0;">Payment Verified — Assignments Pending</h2>
            <p style="font-size: 13px; color: #64748B; margin-top: 2px;">${title || 'Internship Completion Certificate'}</p>
          </div>
        </div>

        <div style="background: #FFFBEB; border: 1px solid #FCD34D; border-radius: 12px; padding: 20px; margin-bottom: 20px;">
          <p style="font-size: 14px; color: #92400E; margin: 0; line-height: 1.6;">
            <strong>Thank you! Your payment of ₹199 has been successfully verified.</strong>
          </p>
          <p style="font-size: 14px; color: #475569; line-height: 1.6; margin-top: 10px; margin-bottom: 0;">
            To maintain academic & industry standards, your official Internship Completion Certificate will be automatically issued and emailed to your registered email address as soon as you finish all <strong>4 weeks of internship assignments & project tasks</strong>.
          </p>
        </div>

        <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 14px 18px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center;">
          <span style="font-size: 14px; color: #334155; font-weight: 600;">Current Assignment Progress:</span>
          <span style="font-size: 14px; font-weight: 700; color: #0B3D91;">Week ${completedWeeks || 0} of ${durationWeeks || 4} Completed</span>
        </div>

        <div style="display: flex; gap: 12px; justify-content: flex-end;">
          <button onclick="Modals.close()" class="btn btn-outline" style="padding: 10px 20px;">Close</button>
          <button onclick="Modals.close(); DashboardView.openWorkspace('${appId}')" class="btn btn-primary" style="padding: 10px 24px; font-weight: 700;">
            Go to Task Workspace & Submit Tasks →
          </button>
        </div>
      </div>
    `;
    this.open(html);
  }
};

document.addEventListener('DOMContentLoaded', () => {
  Modals.init();
});
