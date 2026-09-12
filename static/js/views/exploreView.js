// Explore Internships & Sectors View Renderer
const ExploreView = {
  activeSectorSlug: null,
  searchQuery: '',
  currentPage: 1,
  perPage: 12,
  searchTimeout: null,

  async renderInternships(sectorSlug = null) {
    this.activeSectorSlug = sectorSlug;
    this.currentPage = 1;
    this.searchQuery = '';

    const container = document.getElementById('app-view');
    if (!container) return;

    container.innerHTML = `
      <section class="section-padding" style="background-color: var(--color-gray-bg); min-height: calc(100vh - 130px);">
        <div class="container">
          <div style="text-align: center; max-width: 700px; margin: 0 auto 24px auto;">
            <h1 style="font-size: 28px; color: var(--color-blue-dark); margin-bottom: 8px; line-height: 1.3;">Browse Internships</h1>
            <p style="color: var(--color-gray-text); font-size: 14px;">Explore sector-based 4-week internship programs and earn verified credentials.</p>
          </div>

          <!-- Filter & Search Controls -->
          <div class="explore-filter-bar">
            <div class="explore-search-box">
              <i data-feather="search" style="color: var(--color-gray-text); width: 18px; height: 18px; flex-shrink: 0;"></i>
              <input type="text" id="explore-search-input" placeholder="Search internships by title or keyword..." value="${this.searchQuery}" style="width:100%; border:none; background:transparent; outline:none; font-size: 14px;" />
              <button id="clear-search-btn" style="display:none; background:none; border:none; cursor:pointer; color:var(--color-gray-text); padding:0 4px; font-weight: bold;" title="Clear search">✕</button>
            </div>

            <div id="results-count-summary" style="font-size: 13px; color: var(--color-gray-text); font-weight: 500; margin-top: 8px;">
              Loading internship listings...
            </div>

            <!-- Sector Filter Tabs -->
            <div class="explore-sector-tabs" id="sector-filter-tabs">
              <button class="btn btn-sm btn-primary">Loading Sectors...</button>
            </div>
          </div>

          <!-- Cards Grid -->
          <div class="cards-grid" id="explore-internships-grid">
            ${this.getSkeletonCardsHTML()}
          </div>

          <!-- Pagination Bar -->
          <div id="explore-pagination" style="margin-top: 20px; display: flex; justify-content: center; align-items: center; gap: 6px; flex-wrap: wrap;"></div>
        </div>
      </section>
    `;

    if (window.feather) feather.replace();

    // Bind Search Input with 300ms Debounce
    const searchInput = document.getElementById('explore-search-input');
    const clearBtn = document.getElementById('clear-search-btn');

    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        const val = e.target.value;
        if (clearBtn) clearBtn.style.display = val ? 'block' : 'none';

        if (this.searchTimeout) clearTimeout(this.searchTimeout);
        this.searchTimeout = setTimeout(() => {
          this.searchQuery = val.trim();
          this.currentPage = 1;
          this.fetchInternships(this.activeSectorSlug, 1, this.searchQuery);
        }, 300);
      });
    }

    if (clearBtn) {
      clearBtn.addEventListener('click', () => {
        if (searchInput) searchInput.value = '';
        clearBtn.style.display = 'none';
        this.searchQuery = '';
        this.currentPage = 1;
        this.fetchInternships(this.activeSectorSlug, 1, '');
      });
    }

    // Parallel execution of Filters and Internships
    await Promise.all([
      this.loadFilters(sectorSlug),
      this.fetchInternships(sectorSlug, 1, '')
    ]);
  },

  getSkeletonCardsHTML() {
    let skeletons = '';
    for (let i = 0; i < 6; i++) {
      skeletons += `
        <div class="card" style="opacity: 0.7; pointer-events: none;">
          <div class="card-header" style="height: 24px; background: #E2E8F0; border-radius: 4px; width: 40%; margin-bottom: 12px;"></div>
          <div style="height: 22px; background: #CBD5E1; border-radius: 4px; width: 85%; margin-bottom: 12px;"></div>
          <div style="height: 14px; background: #E2E8F0; border-radius: 4px; width: 100%; margin-bottom: 8px;"></div>
          <div style="height: 14px; background: #E2E8F0; border-radius: 4px; width: 70%; margin-bottom: 20px;"></div>
          <div class="card-footer" style="padding-top: 12px; border-top: 1px solid var(--color-border);">
            <div style="height: 18px; background: #E2E8F0; border-radius: 4px; width: 30%;"></div>
            <div style="height: 32px; background: #CBD5E1; border-radius: 6px; width: 35%;"></div>
          </div>
        </div>
      `;
    }
    return skeletons;
  },

  async loadFilters(activeSectorSlug) {
    try {
      const res = await API.request('/api/sectors');
      const tabs = document.getElementById('sector-filter-tabs');
      if (res.sectors && tabs) {
        let html = `<button class="btn btn-sm ${!activeSectorSlug ? 'btn-primary' : 'btn-outline'}" onclick="window.location.hash='#/internships'">All Tracks</button>`;
        html += res.sectors.map(sec => `
          <button class="btn btn-sm ${activeSectorSlug === sec.slug ? 'btn-primary' : 'btn-outline'}" onclick="window.location.hash='#/sector/${sec.slug}'">${sec.name}</button>
        `).join('');
        tabs.innerHTML = html;
      }
    } catch (e) {
      console.warn("Filters load warning:", e);
      const tabs = document.getElementById('sector-filter-tabs');
      if (tabs) {
        tabs.innerHTML = `<button class="btn btn-sm btn-primary" onclick="window.location.hash='#/internships'">All Tracks</button>`;
      }
    }
  },

  async fetchInternships(sectorSlug = null, page = 1, searchQuery = '') {
    this.activeSectorSlug = sectorSlug;
    this.currentPage = page;

    const grid = document.getElementById('explore-internships-grid');
    const summary = document.getElementById('results-count-summary');
    const pagination = document.getElementById('explore-pagination');

    if (grid) {
      grid.innerHTML = this.getSkeletonCardsHTML();
    }

    try {
      let url = `/api/internships?page=${page}&per_page=${this.perPage}`;
      if (sectorSlug) url += `&sector=${encodeURIComponent(sectorSlug)}`;
      if (searchQuery) url += `&search=${encodeURIComponent(searchQuery)}`;

      const res = await API.request(url);

      if (!res.internships) {
        throw new Error("Invalid response format from server.");
      }

      if (!grid) return;

      const total = res.total !== undefined ? res.total : res.internships.length;
      const totalPages = res.total_pages || Math.ceil(total / this.perPage) || 1;

      if (summary) {
        if (total === 0) {
          summary.innerText = "0 internships found";
        } else {
          const start = (page - 1) * this.perPage + 1;
          const end = Math.min(page * this.perPage, total);
          summary.innerText = `Showing ${start}–${end} of ${total} virtual internships`;
        }
      }

      if (res.internships.length === 0) {
        grid.innerHTML = `
          <div style="grid-column: 1/-1; text-align: center; padding: 60px 20px; background: var(--color-white); border-radius: var(--radius-lg); border: 1px solid var(--color-border);">
            <div style="font-size: 48px; margin-bottom: 12px;">🔍</div>
            <h3 style="font-size: 22px; color: var(--color-blue-dark); margin-bottom: 8px;">No Internships Match Criteria</h3>
            <p style="color: var(--color-gray-text); margin-bottom: 24px; max-width: 500px; margin-left: auto; margin-right: auto;">
              We couldn't find any virtual internship programs matching your search or sector filter.
            </p>
            <button class="btn btn-primary" onclick="ExploreView.resetFilters()">Clear Filters & View All Programs</button>
          </div>
        `;
        if (pagination) pagination.innerHTML = '';
        return;
      }

      grid.innerHTML = res.internships.map(item => `
        <div class="card">
          <div class="card-header">
            <span class="badge-sector">${item.sector_name || 'Virtual Track'}</span>
            <span class="badge-mode">${item.mode || 'Virtual'}</span>
          </div>
          <h3 class="card-title">${item.title}</h3>
          <p class="card-desc">${item.short_description}</p>
          <div class="card-footer">
            <span class="duration-info">
              <i data-feather="clock" style="width: 14px;"></i>
              ${item.duration_weeks} Weeks
            </span>
            <a href="#/internship/${item.slug}" class="btn btn-outline btn-sm">View Details</a>
          </div>
        </div>
      `).join('');

      if (window.feather) feather.replace();

      // Render Pagination
      this.renderPagination(pagination, page, totalPages, total);

    } catch (err) {
      console.error("Fetch internships error:", err);
      if (grid) {
        grid.innerHTML = `
          <div style="grid-column: 1/-1; text-align: center; padding: 60px 20px; background: #FEF2F2; border-radius: var(--radius-lg); border: 1px solid #FCA5A5;">
            <div style="font-size: 44px; margin-bottom: 12px; color: #EF4444;">⚠️</div>
            <h3 style="font-size: 22px; color: #991B1B; margin-bottom: 8px;">Unable to Load Internships</h3>
            <p style="color: #B91C1C; margin-bottom: 24px; max-width: 500px; margin-left: auto; margin-right: auto;">
              ${err.message || 'There was a problem connecting to the platform database. Please try again.'}
            </p>
            <button class="btn btn-primary" onclick="ExploreView.fetchInternships('${sectorSlug || ''}', ${page}, '${searchQuery}')">
              🔄 Try Reloading
            </button>
          </div>
        `;
      }
      if (summary) summary.innerText = "Error loading internships";
      if (pagination) pagination.innerHTML = '';
    }
  },

  renderPagination(container, currentPage, totalPages, totalItems) {
    if (!container || totalPages <= 1) {
      if (container) container.innerHTML = '';
      return;
    }

    let html = `
      <button class="btn btn-sm btn-outline" ${currentPage === 1 ? 'disabled style="opacity:0.5; cursor:not-allowed;"' : ''} onclick="ExploreView.goToPage(${currentPage - 1})">
        ← Previous
      </button>
    `;

    const maxVisible = 5;
    let startPage = Math.max(1, currentPage - 2);
    let endPage = Math.min(totalPages, startPage + maxVisible - 1);
    if (endPage - startPage < maxVisible - 1) {
      startPage = Math.max(1, endPage - maxVisible + 1);
    }

    for (let p = startPage; p <= endPage; p++) {
      html += `
        <button class="btn btn-sm ${p === currentPage ? 'btn-primary' : 'btn-outline'}" onclick="ExploreView.goToPage(${p})">
          ${p}
        </button>
      `;
    }

    html += `
      <button class="btn btn-sm btn-outline" ${currentPage === totalPages ? 'disabled style="opacity:0.5; cursor:not-allowed;"' : ''} onclick="ExploreView.goToPage(${currentPage + 1})">
        Next →
      </button>
    `;

    container.innerHTML = html;
  },

  goToPage(page) {
    this.currentPage = page;
    window.scrollTo({ top: 200, behavior: 'smooth' });
    this.fetchInternships(this.activeSectorSlug, page, this.searchQuery);
  },

  resetFilters() {
    this.searchQuery = '';
    this.activeSectorSlug = null;
    this.currentPage = 1;
    window.location.hash = '#/internships';
  },

  async renderSectors() {
    const container = document.getElementById('app-view');
    if (!container) return;

    container.innerHTML = `
      <section class="section-padding" style="background-color: var(--color-gray-bg); min-height: 80vh;">
        <div class="container">
          <div style="text-align: center; max-width: 600px; margin: 0 auto 48px auto;">
            <h1 style="font-size: 38px; color: var(--color-blue-dark); margin-bottom: 12px;">All Sector Tracks</h1>
            <p style="color: var(--color-gray-text);">Choose a sector domain to view all virtual internship programs available.</p>
          </div>

          <div class="cards-grid" id="all-sectors-grid">
            ${this.getSkeletonCardsHTML()}
          </div>
        </div>
      </section>
    `;

    try {
      const res = await API.request('/api/sectors');
      const grid = document.getElementById('all-sectors-grid');
      if (res.sectors && grid) {
        grid.innerHTML = res.sectors.map(sec => `
          <div class="card">
            <div style="width: 56px; height: 56px; border-radius: 14px; background: var(--color-blue-light); color: var(--color-primary-blue); display:flex; align-items:center; justify-content:center; margin-bottom: 16px;">
              <i data-feather="${sec.icon_url || 'grid'}" style="width: 28px; height: 28px;"></i>
            </div>
            <h3 class="card-title">${sec.name}</h3>
            <p class="card-desc">${sec.description}</p>
            <div class="card-footer">
              <span class="duration-info">${sec.internships_count || 1} Program(s)</span>
              <a href="#/sector/${sec.slug}" class="btn btn-outline btn-sm">Explore Sector →</a>
            </div>
          </div>
        `).join('');
        if (window.feather) feather.replace();
      }
    } catch (e) {
      console.error("All sectors load error:", e);
      const grid = document.getElementById('all-sectors-grid');
      if (grid) {
        grid.innerHTML = `
          <div style="grid-column: 1/-1; text-align: center; padding: 60px 20px; background: #FEF2F2; border-radius: var(--radius-lg); border: 1px solid #FCA5A5;">
            <div style="font-size: 44px; margin-bottom: 12px; color: #EF4444;">⚠️</div>
            <h3 style="font-size: 22px; color: #991B1B; margin-bottom: 8px;">Failed to Load Sectors</h3>
            <p style="color: #B91C1C; margin-bottom: 24px;">${e.message || 'Error connecting to database.'}</p>
            <button class="btn btn-primary" onclick="ExploreView.renderSectors()">🔄 Retry</button>
          </div>
        `;
      }
    }
  }
};

