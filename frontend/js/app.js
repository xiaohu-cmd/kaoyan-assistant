/**
 * 考研助手 SPA Router and App Shell
 */
window.App = (function() {
  const pages = {};
  const state = {
    token: localStorage.getItem('kaoyan_token') || null,
    user: null,
    currentPage: 'dashboard'
  };

  function showLogin() {
    document.getElementById('app-shell').style.display = 'none';
    document.getElementById('login-overlay').style.display = '';
    document.getElementById('login-error').textContent = '';
    document.getElementById('register-error').textContent = '';
  }

  function showApp() {
    document.getElementById('login-overlay').style.display = 'none';
    document.getElementById('app-shell').style.display = '';
  }

  function registerPage(name, renderFn) {
    pages[name] = renderFn;
  }

  async function navigate(pageName) {
    state.currentPage = pageName;
    window.location.hash = pageName;

    // Update nav active state
    document.querySelectorAll('.nav-link').forEach(link => {
      link.classList.toggle('active', link.dataset.page === pageName);
    });

    const content = document.getElementById('content');
    content.innerHTML = '<div style="text-align:center;padding:40px;color:#64748b;">加载中...</div>';

    try {
      if (pages[pageName]) {
        await pages[pageName](content);
      } else {
        content.innerHTML = '<div class="card"><h3>页面未找到</h3><p>请检查导航链接。</p></div>';
      }
    } catch (err) {
      console.error(`Error rendering page ${pageName}:`, err);
      content.innerHTML = `<div class="card"><h3>错误</h3><p>${err.message}</p></div>`;
    }
  }

  function setupNavigation() {
    // Sidebar clicks
    document.querySelectorAll('.nav-link').forEach(link => {
      link.addEventListener('click', (e) => {
        e.preventDefault();
        navigate(link.dataset.page);
      });
    });

    // Hash change
    window.addEventListener('hashchange', () => {
      const page = window.location.hash.slice(1) || 'dashboard';
      if (page !== state.currentPage) {
        navigate(page);
      }
    });
  }

  function setupLogin() {
    // Tab switching
    document.querySelectorAll('.login-tab').forEach(tab => {
      tab.addEventListener('click', () => {
        document.querySelectorAll('.login-tab').forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        const isLogin = tab.dataset.tab === 'login';
        document.getElementById('login-form').style.display = isLogin ? '' : 'none';
        document.getElementById('register-form').style.display = isLogin ? 'none' : '';
        document.getElementById('login-error').textContent = '';
        document.getElementById('register-error').textContent = '';
      });
    });

    // Login form
    document.getElementById('login-form').addEventListener('submit', async (e) => {
      e.preventDefault();
      const username = document.getElementById('login-username').value.trim();
      const password = document.getElementById('login-password').value;
      const errorEl = document.getElementById('login-error');
      errorEl.textContent = '';
      if (!username || !password) {
        errorEl.textContent = '请输入用户名和密码';
        return;
      }
      try {
        await window.API.login(username, password);
        state.token = localStorage.getItem('kaoyan_token');
        showApp();
        navigate(state.currentPage || 'dashboard');
      } catch (err) {
        errorEl.textContent = err.message;
      }
    });

    // Register form
    document.getElementById('register-form').addEventListener('submit', async (e) => {
      e.preventDefault();
      const username = document.getElementById('reg-username').value.trim();
      const password = document.getElementById('reg-password').value;
      const confirm = document.getElementById('reg-password-confirm').value;
      const errorEl = document.getElementById('register-error');
      errorEl.textContent = '';
      if (password !== confirm) {
        errorEl.textContent = '两次密码不一致';
        return;
      }
      if (username.length < 2 || password.length < 4) {
        errorEl.textContent = '用户名至少2字符，密码至少4字符';
        return;
      }
      try {
        await window.API.register(username, password);
        const loginData = await window.API.login(username, password);
        state.token = localStorage.getItem('kaoyan_token');
        showApp();
        navigate('dashboard');
      } catch (err) {
        errorEl.textContent = err.message;
      }
    });
  }

  function setupLogout() {
    document.getElementById('logout-btn').addEventListener('click', () => {
      window.API.logout();
      state.token = null;
      showLogin();
    });
  }

  function init() {
    setupLogin();
    setupLogout();
    setupNavigation();

    if (state.token) {
      showApp();
      const page = window.location.hash.slice(1) || 'dashboard';
      navigate(page);
    } else {
      showLogin();
    }
  }

  return {
    init,
    navigate,
    showLogin,
    showApp,
    registerPage,
    get state() { return state; },
    getPages: function() { return Object.keys(pages); },
    hasPage: function(name) { return name in pages; }
  };
})();

document.addEventListener('DOMContentLoaded', () => {
  window.App.init();
});
