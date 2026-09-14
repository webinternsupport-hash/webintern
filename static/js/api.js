// Web Intern REST API Client Wrapper & Supabase Client Init
// Integrated with IndexedDB storage for persistent account data
const API = {
  supabaseClient: null,

  async getSupabase() {
    if (this.supabaseClient) return this.supabaseClient;
    try {
      const config = await this.request('/api/auth/config');
      if (window.supabase && config.supabase_url && config.supabase_anon_key) {
        this.supabaseClient = window.supabase.createClient(config.supabase_url, config.supabase_anon_key);
        return this.supabaseClient;
      }
    } catch (e) {
      console.warn('Failed to initialize Supabase client:', e);
    }
    return null;
  },

  getAuthToken() {
    return localStorage.getItem('access_token');
  },

  setAuthToken(token) {
    if (token) {
      localStorage.setItem('access_token', token);
    } else {
      localStorage.removeItem('access_token');
    }
  },

  getCurrentUser() {
    const raw = localStorage.getItem('user_profile');
    try {
      return raw ? JSON.parse(raw) : null;
    } catch (e) {
      return null;
    }
  },

  setCurrentUser(user) {
    if (user) {
      localStorage.setItem('user_profile', JSON.stringify(user));
      
      // Also save to IndexedDB for persistent account data
      // This ties the account to this browser/device
      if (Storage && user.id) {
        Storage.saveUser({
          userId: user.id || `user_${crypto.randomUUID()}`,
          name: user.name || user.full_name || '',
          email: user.email || '',
          phone: user.phone || '',
          college: user.college || '',
          department: user.department || '',
          degree: user.degree || '',
          role: user.role || 'student'
        }).catch(err => console.warn('[Storage] Failed to save user:', err));
      }
    } else {
      localStorage.removeItem('user_profile');
    }
  },

  async request(endpoint, options = {}, retryCount = 0) {
    // CRITICAL FIX #4: Ensure endpoint uses absolute path that works in production
    // Handle both relative paths (/api/...) and full URLs
    let fullUrl = endpoint;
    if (!endpoint.startsWith('http')) {
      // Relative path - use window.location.origin for deployment compatibility
      if (!endpoint.startsWith('/')) {
        fullUrl = '/' + endpoint;
      }
      fullUrl = window.location.origin + fullUrl;
    }
    
    console.log('[API] Request:', endpoint, '→', fullUrl);

    const headers = {
      'Content-Type': 'application/json',
      ...options.headers
    };

    const token = this.getAuthToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const config = {
      method: options.method || 'GET',
      headers,
      credentials: 'include', // Include cookies for CORS requests
      ...options
    };

    if (options.body && typeof options.body === 'object') {
      config.body = JSON.stringify(options.body);
    }

    try {
      const response = await fetch(fullUrl, config);
      const contentType = response.headers.get('content-type') || '';
      let data;

      if (contentType.includes('application/json')) {
        data = await response.json();
      } else {
        const text = await response.text();
        if (!response.ok) {
          throw new Error(`Server Error (${response.status}): ${text.replace(/<[^>]*>?/gm, '').trim().slice(0, 120) || 'Request failed'}`);
        }
        try {
          data = JSON.parse(text);
        } catch (e) {
          data = { message: text };
        }
      }

      // Handle token expiration
      if (response.status === 401 && data?.code === 'INVALID_TOKEN') {
        console.warn('[Token Expired] Clearing auth data');
        this.setAuthToken(null);
        this.setCurrentUser(null);
        
        // Redirect to login
        if (!endpoint.includes('/api/auth/')) {
          window.location.hash = '#/login';
          throw new Error('Session expired. Please login again.');
        }
      }

      if (!response.ok) {
        throw new Error(data.error || data.message || `Request failed with status ${response.status}`);
      }
      return data;
    } catch (err) {
      console.error(`[API Error ${endpoint}]:`, err);
      throw err;
    }
  }
};
