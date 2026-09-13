// Header & Mobile Drawer Controller
const HeaderComponent = {
  init() {
    this.setupMobileDrawer();
    this.updateAuthState();
  },

  updateAuthState() {
    const user = API.getCurrentUser();
    const headerActions = document.getElementById('header-auth-actions');
    const mobileActions = document.getElementById('mobile-auth-actions');

    if (user) {
      const isDashboard = window.location.hash.startsWith('#/dashboard');
      const isAdmin = user.role === 'admin';
      const targetHash = isAdmin ? '#/admin' : '#/dashboard';
      const targetLabel = isAdmin ? 'Admin Panel' : 'Student Dashboard';

      if (headerActions) {
        headerActions.innerHTML = `
          <a href="${targetHash}" class="btn btn-primary btn-sm">
            <i data-feather="${isAdmin ? 'shield' : 'layout'}" style="width:16px; height:16px;"></i>
            ${targetLabel}
          </a>
          <button onclick="HeaderComponent.logout()" class="btn btn-outline btn-sm">Sign Out</button>
        `;
      }

      if (mobileActions) {
        mobileActions.innerHTML = `
          <a href="${targetHash}" class="btn btn-primary btn-full">${targetLabel}</a>
          <button onclick="HeaderComponent.logout()" class="btn btn-outline btn-full">Sign Out</button>
        `;
      }
    } else {
      if (headerActions) {
        headerActions.innerHTML = `
          <a href="#/login" class="btn btn-outline btn-sm">Sign In</a>
          <a href="#/register" class="btn btn-primary btn-sm">Get Started</a>
        `;
      }

      if (mobileActions) {
        mobileActions.innerHTML = `
          <a href="#/register" class="btn btn-primary btn-full">Get Started</a>
          <a href="#/login" class="btn btn-outline btn-full">Log In</a>
        `;
      }
    }

    if (window.feather) {
      feather.replace();
    }
  },

  setupMobileDrawer() {
    const toggleBtn = document.getElementById('hamburger-toggle-btn');
    const panel = document.getElementById('mobile-nav-panel');
    const icon = document.getElementById('hamburger-icon');

    if (!toggleBtn || !panel) return;

    toggleBtn.addEventListener('click', () => {
      const isOpen = panel.classList.contains('open');
      if (isOpen) {
        this.closeMobileDrawer();
      } else {
        panel.classList.add('open');
        panel.setAttribute('aria-hidden', 'false');
        if (icon) {
          icon.setAttribute('data-feather', 'x');
        }
      }
      if (window.feather) feather.replace();
    });

    // Close on link click inside drawer
    panel.addEventListener('click', (e) => {
      if (e.target.tagName === 'A' || e.target.closest('a')) {
        this.closeMobileDrawer();
      }
    });
  },

  closeMobileDrawer() {
    const panel = document.getElementById('mobile-nav-panel');
    const icon = document.getElementById('hamburger-icon');
    if (panel) {
      panel.classList.remove('open');
      panel.setAttribute('aria-hidden', 'true');
    }
    if (icon) {
      icon.setAttribute('data-feather', 'menu');
    }
    if (window.feather) feather.replace();
  },

  logout() {
    // CRITICAL: Only clear session tokens, NOT persistent account data
    // User's enrollments, certificates, and profile data remain in IndexedDB
    API.setAuthToken(null);
    API.setCurrentUser(null);
    Toast.show('You have logged out successfully.', 'info');
    this.updateAuthState();
    window.location.hash = '#/';
  }
};
