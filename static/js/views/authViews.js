// Auth Views Renderer (Create Account & Login with Email/Password and Full Student Credentials)


const AuthViews = {
  renderRegister() {
    const container = document.getElementById('app-view');
    if (!container) return;

    container.innerHTML = `
      <section class="section-padding" style="background-color: var(--color-gray-bg); min-height: calc(100vh - 72px); display: flex; align-items: center; justify-content: center;">
        <div class="container" style="max-width: 500px;">
          <div style="background: var(--color-white); border-radius: var(--radius-lg); padding: 40px 32px; border: 1px solid var(--color-border); box-shadow: var(--shadow-xl);">
            
            <div style="text-align: center; margin-bottom: 24px;">
              <img src="/assets/logo.svg" alt="Web Intern" height="36" style="margin: 0 auto 16px auto;" />
              <h1 style="font-size: 26px; color: var(--color-blue-dark); margin-bottom: 6px;">Create your account</h1>
              <p style="color: var(--color-gray-text); font-size: 14px;">Register to start your virtual internship program.</p>
            </div>

            <!-- Direct Account Registration Form -->
            <form id="register-form">
              <div class="form-group">
                <label class="form-label">Full Name *</label>
                <div style="position: relative;">
                  <i data-feather="user" style="position: absolute; left: 14px; top: 50%; transform: translateY(-50%); color: var(--color-gray-text); width: 18px;"></i>
                  <input type="text" id="reg-name" class="form-input" style="padding-left: 42px;" placeholder="John Doe" required />
                </div>
              </div>

              <div class="form-group">
                <label class="form-label">Email Address *</label>
                <div style="position: relative;">
                  <i data-feather="mail" style="position: absolute; left: 14px; top: 50%; transform: translateY(-50%); color: var(--color-gray-text); width: 18px;"></i>
                  <input type="email" id="reg-email" class="form-input" style="padding-left: 42px;" placeholder="you@example.com" required />
                </div>
              </div>

              <div class="form-group">
                <label class="form-label">Mobile Number</label>
                <div style="display: flex; gap: 8px;">
                  <select id="reg-country-code" class="form-input" style="width: 110px; padding: 12px 8px; font-size: 13px;">
                    <option value="+91">+91 — IN</option>
                    <option value="+1">+1 — US</option>
                    <option value="+44">+44 — UK</option>
                    <option value="+61">+61 — AU</option>
                    <option value="+971">+971 — AE</option>
                  </select>
                  <div style="position: relative; flex-grow: 1;">
                    <i data-feather="phone" style="position: absolute; left: 14px; top: 50%; transform: translateY(-50%); color: var(--color-gray-text); width: 18px;"></i>
                    <input type="tel" id="reg-phone" class="form-input" style="padding-left: 42px;" placeholder="9876543210" />
                  </div>
                </div>
              </div>

              <div class="form-group">
                <label class="form-label">College / University Name *</label>
                <div style="position: relative;">
                  <i data-feather="book" style="position: absolute; left: 14px; top: 50%; transform: translateY(-50%); color: var(--color-gray-text); width: 18px;"></i>
                  <input type="text" id="reg-college" class="form-input" style="padding-left: 42px;" placeholder="e.g. Saveetha Dental College / Anna University" required />
                </div>
              </div>

              <div class="form-group">
                <label class="form-label">Department / Specialization *</label>
                <div style="position: relative;">
                  <i data-feather="award" style="position: absolute; left: 14px; top: 50%; transform: translateY(-50%); color: var(--color-gray-text); width: 18px;"></i>
                  <input type="text" id="reg-department" class="form-input" style="padding-left: 42px;" placeholder="e.g. Dental Surgery (BDS) / Computer Science" required />
                </div>
              </div>

              <div class="form-group">
                <label class="form-label">Password *</label>
                <div style="position: relative;">
                  <i data-feather="lock" style="position: absolute; left: 14px; top: 50%; transform: translateY(-50%); color: var(--color-gray-text); width: 18px;"></i>
                  <input type="password" id="reg-password" class="form-input" style="padding-left: 42px;" placeholder="Minimum 6 characters" minlength="6" required />
                </div>
              </div>

              <div class="form-group">
                <label class="form-label">Confirm Password *</label>
                <div style="position: relative;">
                  <i data-feather="lock" style="position: absolute; left: 14px; top: 50%; transform: translateY(-50%); color: var(--color-gray-text); width: 18px;"></i>
                  <input type="password" id="reg-confirm-password" class="form-input" style="padding-left: 42px;" placeholder="Re-enter password" minlength="6" required />
                </div>
              </div>

              <div style="margin-bottom: 24px; display: flex; flex-direction: column; gap: 14px;">
                <label class="checkbox-label" for="reg-terms" style="display: flex; align-items: flex-start; gap: 12px; font-size: 14px; color: var(--color-blue-dark); cursor: pointer; padding: 6px 0; touch-action: manipulation;">
                  <input type="checkbox" id="reg-terms" style="width: 22px; height: 22px; min-width: 22px; min-height: 22px; flex-shrink: 0; margin-top: 1px; cursor: pointer; accent-color: #0B3D91;" required />
                  <span style="font-size: 13.5px; line-height: 1.4;">I agree to the <a href="#/privacy-policy" target="_blank" style="color: var(--color-accent-blue); text-decoration: underline; font-weight: 600;" onclick="event.stopPropagation();">Terms & Conditions</a> and <a href="#/privacy-policy" target="_blank" style="color: var(--color-accent-blue); text-decoration: underline; font-weight: 600;" onclick="event.stopPropagation();">Privacy Policy</a> *</span>
                </label>

                <label class="checkbox-label" for="reg-marketing" style="display: flex; align-items: flex-start; gap: 12px; font-size: 14px; color: var(--color-blue-dark); cursor: pointer; padding: 6px 0; touch-action: manipulation;">
                  <input type="checkbox" id="reg-marketing" style="width: 22px; height: 22px; min-width: 22px; min-height: 22px; flex-shrink: 0; margin-top: 1px; cursor: pointer; accent-color: #0B3D91;" />
                  <span style="font-size: 13.5px; line-height: 1.4;">Send me updates, offers and marketing emails</span>
                </label>
              </div>

              <button type="submit" id="reg-submit-btn" class="btn btn-primary btn-full btn-lg" style="border-radius: 9999px;">
                Create Account
              </button>
            </form>

            <div style="text-align: center; margin-top: 24px; padding-top: 16px; border-top: 1px solid var(--color-border);">
              <span style="font-size: 14px; color: var(--color-gray-text);">Already have an account? </span>
              <a href="#/login" style="font-weight: 600; color: var(--color-accent-blue);">Sign In</a>
            </div>

          </div>
        </div>
      </section>
    `;

    if (window.feather) feather.replace();
    this.bindRegisterEvents();
  },

  bindRegisterEvents() {
    const form = document.getElementById('register-form');

    form?.addEventListener('submit', async (e) => {
      e.preventDefault();
      const name = document.getElementById('reg-name').value.trim();
      const email = document.getElementById('reg-email').value.trim();
      const phone = document.getElementById('reg-phone').value.trim();
      const countryCode = document.getElementById('reg-country-code').value;
      const college = document.getElementById('reg-college')?.value.trim() || '';
      const department = document.getElementById('reg-department')?.value.trim() || '';
      const password = document.getElementById('reg-password').value;
      const confirmPassword = document.getElementById('reg-confirm-password').value;
      const terms = document.getElementById('reg-terms').checked;
      const marketing = document.getElementById('reg-marketing').checked;

      if (password !== confirmPassword) {
        Toast.show('Passwords do not match.', 'error');
        return;
      }

      if (!terms) {
        Toast.show('You must agree to the Terms & Conditions.', 'error');
        return;
      }

      const submitBtn = document.getElementById('reg-submit-btn');
      try {
        submitBtn.disabled = true;
        submitBtn.innerText = 'Creating account...';

        const res = await API.request('/api/auth/register', {
          method: 'POST',
          body: {
            full_name: name,
            email,
            phone,
            phone_country_code: countryCode,
            college,
            department,
            password,
            confirm_password: confirmPassword,
            terms_accepted: terms,
            marketing_opt_in: marketing
          }
        });

        API.setAuthToken(res.token);
        API.setCurrentUser(res.user);
        HeaderComponent.updateAuthState();

        Toast.show('Account created successfully! Welcome to WebIntern.', 'success');
        window.location.hash = '#/dashboard';
      } catch (err) {
        Toast.show(err.message, 'error');
      } finally {
        submitBtn.disabled = false;
        submitBtn.innerText = 'Create Account';
      }
    });
  },

  renderLogin() {
    const container = document.getElementById('app-view');
    if (!container) return;

    container.innerHTML = `
      <section class="section-padding" style="background-color: var(--color-gray-bg); min-height: calc(100vh - 72px); display: flex; align-items: center; justify-content: center;">
        <div class="container" style="max-width: 440px;">
          <div style="background: var(--color-white); border-radius: var(--radius-lg); padding: 40px 32px; border: 1px solid var(--color-border); box-shadow: var(--shadow-xl);">
            
            <div style="text-align: center; margin-bottom: 28px;">
              <img src="/assets/logo.svg" alt="Web Intern" height="36" style="margin: 0 auto 16px auto;" />
              <h1 style="font-size: 26px; color: var(--color-blue-dark); margin-bottom: 6px;">Welcome back</h1>
              <p style="color: var(--color-gray-text); font-size: 14px;">Sign in to access your WebIntern dashboard.</p>
            </div>

            <!-- Email & Password Login Form -->
            <form id="login-form">
              <div class="form-group">
                <label class="form-label">Email Address</label>
                <div style="position: relative;">
                  <i data-feather="mail" style="position: absolute; left: 14px; top: 50%; transform: translateY(-50%); color: var(--color-gray-text); width: 18px;"></i>
                  <input type="email" id="login-email" class="form-input" style="padding-left: 42px;" placeholder="you@example.com" required />
                </div>
              </div>

              <div class="form-group">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                  <label class="form-label" style="margin-bottom: 0;">Password</label>
                  <a href="javascript:void(0)" onclick="AuthViews.handleForgotPassword()" style="font-size: 13px; color: var(--color-accent-blue); font-weight: 500;">Forgot password?</a>
                </div>
                <div style="position: relative;">
                  <i data-feather="lock" style="position: absolute; left: 14px; top: 50%; transform: translateY(-50%); color: var(--color-gray-text); width: 18px;"></i>
                  <input type="password" id="login-password" class="form-input" style="padding-left: 42px;" placeholder="Enter your password" required />
                </div>
              </div>

              <button type="submit" id="login-submit-btn" class="btn btn-primary btn-full btn-lg" style="border-radius: 9999px;">
                Sign In
              </button>
            </form>

            <div style="text-align: center; margin-top: 24px; padding-top: 16px; border-top: 1px solid var(--color-border);">
              <span style="font-size: 14px; color: var(--color-gray-text);">New to Web Intern? </span>
              <a href="#/register" style="font-weight: 600; color: var(--color-accent-blue);">Create an account</a>
            </div>

          </div>
        </div>
      </section>
    `;

    if (window.feather) feather.replace();
    this.bindLoginEvents();
  },

  bindLoginEvents() {
    const form = document.getElementById('login-form');

    form?.addEventListener('submit', async (e) => {
      e.preventDefault();
      const email = document.getElementById('login-email').value.trim();
      const password = document.getElementById('login-password').value;
      const submitBtn = document.getElementById('login-submit-btn');

      try {
        submitBtn.disabled = true;
        submitBtn.innerText = 'Signing in...';

        const res = await API.request('/api/auth/login', {
          method: 'POST',
          body: { email, password }
        });

        API.setAuthToken(res.token);
        API.setCurrentUser(res.user);
        HeaderComponent.updateAuthState();

        // Restore user's persistent account data from IndexedDB
        if (Storage && res.user && res.user.id) {
          try {
            const accountData = await Storage.restoreUserAccount(res.user.id);
            console.log('[Auth] Account data restored:', accountData);
          } catch (err) {
            console.warn('[Auth] Failed to restore account data:', err);
          }
        }

        Toast.show('Login successful!', 'success');

        const params = new URLSearchParams(window.location.hash.split('?')[1] || '');
        const redirect = params.get('redirect');
        window.location.hash = redirect ? decodeURIComponent(redirect) : '#/dashboard';
      } catch (err) {
        Toast.show(err.message, 'error');
      } finally {
        submitBtn.disabled = false;
        submitBtn.innerText = 'Sign In';
      }
    });
  },

  async handleForgotPassword() {
    const email = prompt('Enter your registered email address to receive a password reset link:');
    if (!email || !email.trim()) return;

    try {
      Toast.show('Sending password reset email via Resend...', 'info');
      const res = await API.request('/api/auth/forgot-password', {
        method: 'POST',
        body: { email: email.trim() }
      });
      Toast.show(res.message, 'success');
    } catch (err) {
      Toast.show(err.message, 'error');
    }
  }
};
