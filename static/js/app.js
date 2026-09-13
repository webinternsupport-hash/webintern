// Main Web Intern Single-Page App Router
document.addEventListener('DOMContentLoaded', () => {
  HeaderComponent.init();
  setupScrollToTop();
  handleRouting();

  window.addEventListener('hashchange', handleRouting);
});

function handleRouting() {
  const hash = window.location.hash || '#/';
  const route = hash.split('?')[0];

  // Highlight active nav links
  document.querySelectorAll('.nav-link, .mobile-link').forEach(link => {
    if (link.getAttribute('href') === route) {
      link.classList.add('active');
    } else {
      link.classList.remove('active');
    }
  });

  // Scroll to top on page change
  window.scrollTo({ top: 0, behavior: 'smooth' });

  // Route Dispatcher
  if (route === '#/' || route === '') {
    HomeView.render();
  } else if (route === '#/internships') {
    ExploreView.renderInternships();
  } else if (route === '#/sectors') {
    ExploreView.renderSectors();
  } else if (route.startsWith('#/sector/')) {
    const slug = route.replace('#/sector/', '');
    ExploreView.renderInternships(slug);
  } else if (route.startsWith('#/internship/')) {
    const slug = route.replace('#/internship/', '');
    DetailView.render(slug);
  } else if (route.startsWith('#/login')) {
    AuthViews.renderLogin();
  } else if (route.startsWith('#/register')) {
    AuthViews.renderRegister();
  } else if (route.startsWith('#/dashboard')) {
    DashboardView.render();
  } else if (route.startsWith('#/admin')) {
    AdminView.render();
  } else if (route === '#/about-us') {
    StaticViews.renderAbout();
  } else if (route === '#/contact-us') {
    StaticViews.renderContact();
  } else if (route === '#/privacy-policy') {
    StaticViews.renderPrivacy();
  } else {
    HomeView.render();
  }
}

function setupScrollToTop() {
  const btn = document.getElementById('scroll-top-btn');
  if (!btn) return;

  window.addEventListener('scroll', () => {
    if (window.scrollY > 300) {
      btn.classList.add('visible');
    } else {
      btn.classList.remove('visible');
    }
  });

  btn.addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
}
