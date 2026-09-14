/**
 * Mobile View Fixes
 * Addresses checkbox interactivity, offer letter, certificates, and navigation issues
 */

class MobileViewFixer {
  constructor() {
    this.init();
  }

  init() {
    this.fixCheckboxes();
    this.fixOfferLetterButton();
    this.fixCertificateButton();
    this.fixProfilePageLayout();
    this.fixFormInputs();
    this.fixBottomNavigation();
    this.fixViewDetailsButtons();
    this.fixContentScrolling();
    this.fixAuthenticationFlow();
    this.observePageChanges();
  }

  /**
   * Fix checkbox interactivity and touch targets
   */
  fixCheckboxes() {
    const observer = new MutationObserver(() => {
      document.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
        // Remove old event listeners
        checkbox.removeEventListener('change', this.handleCheckboxChange);
        
        // Add improved event listener
        checkbox.addEventListener('change', (e) => {
          this.handleCheckboxChange.call(this, e);
        }, { passive: false });

        // Ensure label is clickable
        const label = checkbox.closest('label');
        if (label) {
          label.style.minHeight = '44px';
          label.style.padding = '10px 4px';
          label.style.touchAction = 'manipulation';
          
          // Make entire label clickable
          label.addEventListener('click', (e) => {
            if (e.target !== checkbox) {
              checkbox.checked = !checkbox.checked;
              checkbox.dispatchEvent(new Event('change', { bubbles: true }));
            }
          });
        }
      });
    });

    observer.observe(document.body, { childList: true, subtree: true });
  }

  handleCheckboxChange(e) {
    const checkbox = e.target;
    const label = checkbox.closest('label');
    
    if (checkbox.checked) {
      checkbox.setAttribute('checked', 'checked');
      if (label) label.classList.add('checked');
    } else {
      checkbox.removeAttribute('checked');
      if (label) label.classList.remove('checked');
    }
  }

  /**
   * Fix offer letter button visibility and functionality
   */
  fixOfferLetterButton() {
    const observer = new MutationObserver(() => {
      // Find and fix offer letter buttons
      document.querySelectorAll('[class*="offer"], button:contains("Offer")').forEach(btn => {
        if (!btn.classList.contains('mobile-fixed')) {
          btn.classList.add('mobile-fixed');
          btn.style.minHeight = '44px';
          btn.style.padding = '12px 16px';
          btn.style.fontSize = '16px';
          btn.style.display = 'flex';
          btn.style.alignItems = 'center';
          btn.style.justifyContent = 'center';
          btn.style.gap = '8px';
          btn.style.cursor = 'pointer';
          btn.style.touchAction = 'manipulation';
          
          // Add click handler
          btn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            this.handleOfferLetterClick(btn);
          }, { passive: false });
        }
      });

      // Also check for text content
      document.querySelectorAll('button').forEach(btn => {
        if ((btn.textContent.includes('Offer') || btn.textContent.includes('offer')) && 
            !btn.classList.contains('mobile-fixed')) {
          btn.classList.add('mobile-fixed');
          btn.style.minHeight = '44px';
          btn.style.padding = '12px 16px';
          btn.style.fontSize = '16px';
          btn.style.display = 'flex';
          btn.style.alignItems = 'center';
          btn.style.justifyContent = 'center';
          btn.style.gap = '8px';
        }
      });
    });

    observer.observe(document.body, { childList: true, subtree: true });
  }

  handleOfferLetterClick(btn) {
    try {
      // Get the application ID or enrollment ID
      const card = btn.closest('[class*="card"], [class*="item"], article');
      const applicationId = card ? card.getAttribute('data-application-id') || card.getAttribute('data-id') : null;
      
      if (applicationId) {
        // Trigger offer letter download/view
        window.location.hash = `#/offer/${applicationId}`;
      } else {
        console.warn('Cannot find application ID for offer letter');
      }
    } catch (error) {
      console.error('Error handling offer letter click:', error);
    }
  }

  /**
   * Fix certificate button visibility and functionality
   */
  fixCertificateButton() {
    const observer = new MutationObserver(() => {
      document.querySelectorAll('[class*="cert"], button:contains("Cert")').forEach(btn => {
        if (!btn.classList.contains('mobile-fixed')) {
          btn.classList.add('mobile-fixed');
          btn.style.minHeight = '44px';
          btn.style.padding = '12px 16px';
          btn.style.fontSize = '16px';
          btn.style.display = 'flex';
          btn.style.alignItems = 'center';
          btn.style.justifyContent = 'center';
          btn.style.gap = '8px';
          btn.style.cursor = 'pointer';
          btn.style.touchAction = 'manipulation';
          
          btn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            this.handleCertificateClick(btn);
          }, { passive: false });
        }
      });

      // Check text content for cert buttons
      document.querySelectorAll('button').forEach(btn => {
        if ((btn.textContent.includes('Cert') || btn.textContent.includes('cert')) && 
            !btn.classList.contains('mobile-fixed')) {
          btn.classList.add('mobile-fixed');
          btn.style.minHeight = '44px';
          btn.style.padding = '12px 16px';
          btn.style.fontSize = '16px';
          btn.style.display = 'flex';
          btn.style.alignItems = 'center';
          btn.style.justifyContent = 'center';
        }
      });
    });

    observer.observe(document.body, { childList: true, subtree: true });
  }

  handleCertificateClick(btn) {
    try {
      const card = btn.closest('[class*="card"], [class*="item"], article');
      const certificateId = card ? card.getAttribute('data-certificate-id') || card.getAttribute('data-id') : null;
      
      if (certificateId) {
        window.location.hash = `#/certificate/${certificateId}`;
      } else {
        console.warn('Cannot find certificate ID');
      }
    } catch (error) {
      console.error('Error handling certificate click:', error);
    }
  }

  /**
   * Fix profile page layout for mobile
   */
  fixProfilePageLayout() {
    const observer = new MutationObserver(() => {
      // Fix profile container
      const profileContainer = document.querySelector('.profile-container, [id*="profile"]');
      if (profileContainer && !profileContainer.classList.contains('mobile-layout-fixed')) {
        profileContainer.classList.add('mobile-layout-fixed');
        profileContainer.style.padding = '16px';
        profileContainer.style.maxWidth = '100%';
        profileContainer.style.width = '100%';
        profileContainer.style.boxSizing = 'border-box';
      }

      // Fix all buttons on profile
      document.querySelectorAll('[id*="profile"] button, [class*="profile"] button').forEach(btn => {
        btn.style.width = '100%';
        btn.style.minHeight = '44px';
        btn.style.margin = '8px 0';
        btn.style.fontSize = '16px';
      });

      // Fix enrollment items
      document.querySelectorAll('.enrollment-item, .internship-item, .application-card').forEach(item => {
        item.style.display = 'flex';
        item.style.flexDirection = 'column';
        item.style.gap = '12px';
        item.style.padding = '16px';
        item.style.borderRadius = '8px';
        item.style.border = '1px solid #E0E0E0';
        item.style.marginBottom = '12px';
      });

      // Fix date displays
      document.querySelectorAll('[class*="date"], .start-date, .end-date').forEach(el => {
        el.style.wordBreak = 'break-word';
        el.style.overflowWrap = 'break-word';
      });
    });

    observer.observe(document.body, { childList: true, subtree: true });
  }

  /**
   * Fix form inputs for mobile
   */
  fixFormInputs() {
    const observer = new MutationObserver(() => {
      document.querySelectorAll('input[type="text"], input[type="email"], input[type="password"], textarea, select').forEach(input => {
        if (!input.classList.contains('mobile-input-fixed')) {
          input.classList.add('mobile-input-fixed');
          input.style.fontSize = '16px';
          input.style.padding = '12px';
          input.style.borderRadius = '6px';
          input.style.border = '1px solid #E0E0E0';
          input.style.width = '100%';
          input.style.boxSizing = 'border-box';
          input.style.fontFamily = 'inherit';
          
          input.addEventListener('focus', function() {
            this.style.borderColor = '#0B3D91';
            this.style.boxShadow = '0 0 0 3px rgba(11, 61, 145, 0.1)';
          });

          input.addEventListener('blur', function() {
            this.style.borderColor = '#E0E0E0';
            this.style.boxShadow = 'none';
          });
        }
      });
    });

    observer.observe(document.body, { childList: true, subtree: true });
  }

  /**
   * Fix bottom navigation functionality
   */
  fixBottomNavigation() {
    const bottomNav = document.getElementById('bottom-nav');
    if (bottomNav) {
      const items = bottomNav.querySelectorAll('.bottom-nav-item');
      items.forEach(item => {
        item.style.minHeight = '60px';
        item.style.display = 'flex';
        item.style.flexDirection = 'column';
        item.style.alignItems = 'center';
        item.style.justifyContent = 'center';
        item.style.gap = '4px';
        item.style.cursor = 'pointer';
        item.style.flex = '1';
        item.style.touchAction = 'manipulation';

        item.addEventListener('click', (e) => {
          e.preventDefault();
          const href = item.getAttribute('href');
          const dataRoute = item.getAttribute('data-route');
          
          if (href) {
            window.location.hash = href;
          } else if (dataRoute) {
            switch(dataRoute) {
              case 'home':
                window.location.hash = '#/';
                break;
              case 'explore':
              case 'internships':
                window.location.hash = '#/internships';
                break;
              case 'dashboard':
              case 'applications':
                window.location.hash = '#/dashboard';
                break;
              case 'profile':
                window.location.hash = '#/profile';
                break;
            }
          }

          // Update active state
          items.forEach(i => i.classList.remove('active'));
          item.classList.add('active');
        });
      });
    }
  }

  /**
   * Fix card view details button click handlers
   */
  fixViewDetailsButtons() {
    const observer = new MutationObserver(() => {
      // Find all View Details buttons and links
      document.querySelectorAll('a[href*="/internship/"], .btn-outline:contains("View Details")').forEach(btn => {
        if (!btn.classList.contains('view-details-fixed')) {
          btn.classList.add('view-details-fixed');
          btn.style.cursor = 'pointer';
          btn.style.touchAction = 'manipulation';
          btn.style.pointerEvents = 'auto';
          btn.style.zIndex = '10';
          
          // Ensure link is clickable
          btn.addEventListener('click', (e) => {
            const href = btn.getAttribute('href');
            if (href && href.startsWith('#')) {
              e.preventDefault();
              e.stopPropagation();
              window.location.hash = href;
            }
          }, { passive: false });
        }
      });

      // Also check for text content
      document.querySelectorAll('button, a').forEach(el => {
        if (el.textContent.includes('View Details') && !el.classList.contains('view-details-fixed')) {
          el.classList.add('view-details-fixed');
          el.style.cursor = 'pointer';
          el.style.touchAction = 'manipulation';
          el.style.pointerEvents = 'auto';
          
          el.addEventListener('click', (e) => {
            const href = el.getAttribute('href');
            if (href && href.startsWith('#')) {
              e.preventDefault();
              e.stopPropagation();
              window.location.hash = href;
            }
          }, { passive: false });
        }
      });

      // Also handle inline onclick handlers for internship cards
      document.querySelectorAll('[onclick*="DetailView"]').forEach(el => {
        el.style.cursor = 'pointer';
        el.style.touchAction = 'manipulation';
        el.style.pointerEvents = 'auto';
      });
    });

    observer.observe(document.body, { childList: true, subtree: true });
  }

  /**
   * Fix content scrolling and padding
   */
  fixContentScrolling() {
    const mainView = document.getElementById('app-view');
    if (mainView) {
      mainView.style.paddingBottom = '80px';
      mainView.style.minHeight = '100vh';
      mainView.style.width = '100%';
      mainView.style.boxSizing = 'border-box';
      mainView.style.overflowX = 'hidden';
    }

    // Fix body overflow
    document.body.style.overflowX = 'hidden';
    document.documentElement.style.overflowX = 'hidden';
  }

  /**
   * Fix authentication flow for cross-device login
   */
  fixAuthenticationFlow() {
    // Monitor login/registration
    const observer = new MutationObserver(() => {
      // Find login form
      const loginForm = document.querySelector('form[id*="login"], form[id*="auth"], .auth-form');
      if (loginForm && !loginForm.classList.contains('auth-form-fixed')) {
        loginForm.classList.add('auth-form-fixed');
        
        // Find submit button
        const submitBtn = loginForm.querySelector('button[type="submit"]');
        if (submitBtn) {
          submitBtn.style.width = '100%';
          submitBtn.style.minHeight = '44px';
          submitBtn.style.fontSize = '16px';
          submitBtn.style.margin = '16px 0';
        }
      }

      // Ensure token is properly stored
      const token = localStorage.getItem('access_token');
      if (token) {
        // Verify token is accessible
        try {
          const decoded = JSON.parse(atob(token.split('.')[1]));
          if (decoded && decoded.exp) {
            const expiresAt = new Date(decoded.exp * 1000);
            if (expiresAt > new Date()) {
              // Token is valid
              sessionStorage.setItem('auth_verified', 'true');
            }
          }
        } catch (e) {
          console.warn('Could not verify token:', e);
        }
      }
    });

    observer.observe(document.body, { childList: true, subtree: true });
  }

  /**
   * Observe page changes and reapply fixes
   */
  observePageChanges() {
    // Monitor hash changes
    window.addEventListener('hashchange', () => {
      setTimeout(() => {
        this.fixCheckboxes();
        this.fixOfferLetterButton();
        this.fixCertificateButton();
        this.fixProfilePageLayout();
        this.fixFormInputs();
        this.fixBottomNavigation();
        this.fixViewDetailsButtons();
        this.fixContentScrolling();
      }, 100);
    });

    // Monitor view changes
    const appView = document.getElementById('app-view');
    if (appView) {
      const observer = new MutationObserver(() => {
        setTimeout(() => {
          this.fixCheckboxes();
          this.fixOfferLetterButton();
          this.fixCertificateButton();
          this.fixProfilePageLayout();
          this.fixFormInputs();
          this.fixBottomNavigation();
          this.fixViewDetailsButtons();
          this.fixContentScrolling();
        }, 50);
      });

      observer.observe(appView, { childList: true, subtree: true });
    }
  }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    window.mobileViewFixer = new MobileViewFixer();
  });
} else {
  window.mobileViewFixer = new MobileViewFixer();
}
