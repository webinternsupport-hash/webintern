/**
 * Mobile App Navigation & Interaction Handler
 * Handles bottom nav, drawer menu, and mobile-specific behaviors
 */

class MobileAppManager {
  constructor() {
    this.isMobile = window.innerWidth <= 768;
    this.navDrawer = document.getElementById('mobile-nav-panel');
    this.hamburgerBtn = document.getElementById('hamburger-toggle-btn');
    this.bottomNav = document.getElementById('bottom-nav');
    this.appView = document.getElementById('app-view');
    
    this.init();
  }

  init() {
    // Only initialize mobile features on mobile devices
    if (!this.isMobile) return;

    this.setupEventListeners();
    this.setupBottomNavigation();
    this.setupMenuTrigger();
    this.preventDefaultBehaviors();
    this.handleViewChanges();
  }

  setupEventListeners() {
    // Hamburger menu toggle
    if (this.hamburgerBtn) {
      this.hamburgerBtn.addEventListener('click', () => this.toggleDrawer());
    }

    // Close drawer when clicking a link
    document.querySelectorAll('.mobile-link').forEach(link => {
      link.addEventListener('click', () => this.closeDrawer());
    });

    // Close drawer when clicking outside
    document.addEventListener('click', (e) => {
      if (
        this.navDrawer &&
        !this.navDrawer.contains(e.target) &&
        !this.hamburgerBtn.contains(e.target) &&
        this.navDrawer.classList.contains('active')
      ) {
        this.closeDrawer();
      }
    });

    // Window resize handler
    window.addEventListener('resize', () => {
      this.isMobile = window.innerWidth <= 768;
      if (!this.isMobile) {
        this.closeDrawer();
      }
    });
  }

  toggleDrawer() {
    if (this.navDrawer) {
      this.navDrawer.classList.toggle('active');
    }
  }

  closeDrawer() {
    if (this.navDrawer) {
      this.navDrawer.classList.remove('active');
    }
  }

  setupBottomNavigation() {
    if (!this.bottomNav) return;

    const bottomNavItems = this.bottomNav.querySelectorAll('.bottom-nav-item');
    
    bottomNavItems.forEach(item => {
      item.addEventListener('click', (e) => {
        if (item.id === 'bottom-nav-menu') {
          e.preventDefault();
          this.toggleDrawer();
          return;
        }

        // Update active state
        bottomNavItems.forEach(nav => nav.classList.remove('active'));
        item.classList.add('active');
      });
    });
  }

  setupMenuTrigger() {
    const menuTrigger = document.getElementById('bottom-nav-menu');
    if (menuTrigger) {
      menuTrigger.addEventListener('click', (e) => {
        e.preventDefault();
        this.toggleMoreMenu();
      });
    }

    // Setup more menu close button
    const moreMenuClose = document.getElementById('more-menu-close');
    if (moreMenuClose) {
      moreMenuClose.addEventListener('click', () => this.closeMoreMenu());
    }

    // Close more menu when clicking overlay
    const moreMenuOverlay = document.getElementById('more-menu-overlay');
    if (moreMenuOverlay) {
      moreMenuOverlay.addEventListener('click', (e) => {
        if (e.target === moreMenuOverlay) {
          this.closeMoreMenu();
        }
      });
    }

    // Setup logout button
    const logoutBtn = document.getElementById('more-menu-logout');
    if (logoutBtn) {
      logoutBtn.addEventListener('click', () => {
        this.handleLogout();
      });
    }
  }

  toggleMoreMenu() {
    const overlay = document.getElementById('more-menu-overlay');
    if (overlay) {
      overlay.classList.toggle('active');
    }
  }

  closeMoreMenu() {
    const overlay = document.getElementById('more-menu-overlay');
    if (overlay) {
      overlay.classList.remove('active');
    }
  }

  handleLogout() {
    if (confirm('Are you sure you want to logout?')) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user_profile');
      this.closeMoreMenu();
      window.location.hash = '#/';
      window.location.reload();
    }
  }

  handleViewChanges() {
    // Monitor route changes and update bottom nav
    if (window.app && window.app.router) {
      const originalNavigate = window.app.router.navigate.bind(window.app.router);
      window.app.router.navigate = (route) => {
        this.updateBottomNav(route);
        return originalNavigate(route);
      };
    }
  }

  updateBottomNav(route) {
    const bottomNavItems = this.bottomNav?.querySelectorAll('.bottom-nav-item');
    if (!bottomNavItems) return;

    bottomNavItems.forEach(item => {
      item.classList.remove('active');
      const itemRoute = item.getAttribute('data-route');
      
      if (
        (itemRoute === 'home' && (route === '/' || route === '')) ||
        (itemRoute === 'internships' && route.includes('internships')) ||
        (itemRoute === 'dashboard' && route.includes('dashboard'))
      ) {
        item.classList.add('active');
      }
    });
  }

  preventDefaultBehaviors() {
    // Prevent pull-to-refresh on iOS
    document.body.addEventListener('touchmove', (e) => {
      if (e.touches.length > 1) {
        e.preventDefault();
      }
    }, { passive: false });

    // Prevent text selection on buttons (mobile)
    document.querySelectorAll('.btn, .bottom-nav-item, .mobile-link').forEach(el => {
      el.addEventListener('selectstart', (e) => e.preventDefault());
    });
  }

  // Utility: Scroll to top with animation
  scrollToTop() {
    const mainView = document.getElementById('app-view');
    if (mainView) {
      mainView.scrollTo({ top: 0, behavior: 'smooth' });
    }
  }

  // Utility: Check if currently mobile
  static isMobileDevice() {
    return window.innerWidth <= 768;
  }

  // Utility: Get safe area insets (for notch devices)
  static getSafeAreaInsets() {
    return {
      top: parseInt(getComputedStyle(document.documentElement).getPropertyValue('env(safe-area-inset-top)')) || 0,
      bottom: parseInt(getComputedStyle(document.documentElement).getPropertyValue('env(safe-area-inset-bottom)')) || 0,
      left: parseInt(getComputedStyle(document.documentElement).getPropertyValue('env(safe-area-inset-left)')) || 0,
      right: parseInt(getComputedStyle(document.documentElement).getPropertyValue('env(safe-area-inset-right)')) || 0,
    };
  }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    window.mobileAppManager = new MobileAppManager();
  });
} else {
  window.mobileAppManager = new MobileAppManager();
}

/**
 * Mobile App Gesture Handlers
 * Add swipe gestures for better mobile UX
 */

class GestureHandler {
  constructor() {
    this.touchStartX = 0;
    this.touchEndX = 0;
    this.init();
  }

  init() {
    document.addEventListener('touchstart', (e) => this.handleTouchStart(e), false);
    document.addEventListener('touchend', (e) => this.handleTouchEnd(e), false);
  }

  handleTouchStart(e) {
    this.touchStartX = e.changedTouches[0].screenX;
  }

  handleTouchEnd(e) {
    this.touchEndX = e.changedTouches[0].screenX;
    this.handleSwipe();
  }

  handleSwipe() {
    const diff = this.touchStartX - this.touchEndX;
    const drawer = document.getElementById('mobile-nav-panel');
    
    if (!drawer) return;

    // Swipe right to open drawer
    if (diff < -50) {
      drawer.classList.add('active');
    }
    // Swipe left to close drawer
    else if (diff > 50) {
      drawer.classList.remove('active');
    }
  }
}

// Initialize gesture handler on mobile
if (window.innerWidth <= 768) {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      window.gestureHandler = new GestureHandler();
    });
  } else {
    window.gestureHandler = new GestureHandler();
  }
}

/**
 * Prevent iOS zoom on input focus
 * Ensures font-size 16px is set (iOS won't zoom if >= 16px)
 */

document.addEventListener('focus', (e) => {
  if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
    // Temporary zoom correction
    const viewport = document.querySelector('meta[name="viewport"]');
    if (viewport) {
      viewport.setAttribute('content', 'width=device-width, initial-scale=1.0, user-scalable=0');
    }
  }
}, true);

document.addEventListener('blur', (e) => {
  if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
    // Restore zoom capability
    const viewport = document.querySelector('meta[name="viewport"]');
    if (viewport) {
      viewport.setAttribute('content', 'width=device-width, initial-scale=1.0, user-scalable=yes');
    }
  }
}, true);

/**
 * Fullscreen Request Fallback
 * Allow entering fullscreen app mode on supported browsers
 */

window.requestAppFullscreen = () => {
  const elem = document.documentElement;
  const requestFullscreen = elem.requestFullscreen ||
                           elem.webkitRequestFullscreen ||
                           elem.mozRequestFullScreen ||
                           elem.msRequestFullscreen;
  
  if (requestFullscreen) {
    requestFullscreen.call(elem).catch(err => {
      console.log('Fullscreen request denied:', err);
    });
  }
};

/**
 * Orientation Change Handling
 * Adjust layout when device orientation changes
 */

window.addEventListener('orientationchange', () => {
  // Close drawer on orientation change
  const drawer = document.getElementById('mobile-nav-panel');
  if (drawer) {
    drawer.classList.remove('active');
  }

  // Trigger app reflow
  setTimeout(() => {
    window.dispatchEvent(new Event('resize'));
  }, 100);
});
