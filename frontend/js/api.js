/**
 * API client for 考研助手 backend.
 * All requests except login/register include Bearer token.
 */
window.API = (function() {
  const BASE = '/api';

  function getToken() {
    return localStorage.getItem('kaoyan_token');
  }

  function headers() {
    const h = { 'Content-Type': 'application/json' };
    const token = getToken();
    if (token) h['Authorization'] = 'Bearer ' + token;
    return h;
  }

  async function request(method, url, data) {
    const opts = { method, headers: headers() };
    if (data && method !== 'GET') {
      opts.body = JSON.stringify(data);
    }
    const fullUrl = url.startsWith('http') ? url : BASE + url;
    const resp = await fetch(fullUrl, opts);
    if (resp.status === 401) {
      localStorage.removeItem('kaoyan_token');
      if (window.App) window.App.showLogin();
      throw new Error('Unauthorized');
    }
    if (!resp.ok) {
      const errBody = await resp.json().catch(() => ({ detail: resp.statusText }));
      throw new Error(errBody.detail || `HTTP ${resp.status}`);
    }
    return resp.json();
  }

  return {
    get: (url) => request('GET', url),
    post: (url, data) => request('POST', url, data),
    put: (url, data) => request('PUT', url, data),
    patch: (url, data) => request('PATCH', url, data),
    delete: (url) => request('DELETE', url),
    login: async (username, password) => {
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);
      const resp = await fetch(BASE + '/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData
      });
      if (!resp.ok) {
        const err = await resp.json().catch(() => ({ detail: 'Login failed' }));
        throw new Error(err.detail || 'Login failed');
      }
      const data = await resp.json();
      localStorage.setItem('kaoyan_token', data.access_token);
      return data;
    },
    register: (username, password) => request('POST', '/auth/register', { username, password }),
    logout: () => { localStorage.removeItem('kaoyan_token'); }
  };
})();
