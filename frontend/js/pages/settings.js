/**
 * Settings page: 设置
 */
(function() {
  window.App.registerPage('settings', async function(container) {
    var settings = {};
    try {
      settings = await window.API.get('/settings');
    } catch (err) {
      container.innerHTML = '<div class="card"><p style="color:var(--danger)">加载失败: ' + err.message + '</p></div>';
      return;
    }

    var html = '';

    // User section
    html += '<div class="card">' +
      '<div class="card-header"><h3>用户信息</h3></div>' +
      '<div class="form-group"><label>用户名</label><input id="set-username" value="' + (settings.username || '') + '"></div>' +
    '</div>';

    // Password change section
    html += '<div class="card">' +
      '<div class="card-header"><h3>修改密码</h3></div>' +
      '<div class="form-group"><label>当前密码</label><input type="password" id="set-old-password" placeholder="输入当前密码"></div>' +
      '<div class="form-group"><label>新密码</label><input type="password" id="set-new-password" placeholder="输入新密码 (至少4字符)"></div>' +
      '<div class="form-group"><label>确认新密码</label><input type="password" id="set-new-password-confirm" placeholder="再次输入新密码"></div>' +
      '<button class="btn-primary-sm" id="change-password-btn">修改密码</button>' +
      '<p id="password-msg" style="margin-top:8px;font-size:12px"></p>' +
    '</div>';

    // Target & Exam
    html += '<div class="card">' +
      '<div class="card-header"><h3>考研设置</h3></div>' +
      '<div class="two-col">' +
        '<div class="form-group"><label>目标院校</label><input id="set-school" value="' + (settings.target_school || '') + '" placeholder="如: 厦门大学经济学院"></div>' +
        '<div class="form-group"><label>考试日期</label><input type="date" id="set-exam-date" value="' + (settings.exam_date || '2027-12-25') + '"></div>' +
      '</div>' +
    '</div>';

    // Phase dates
    html += '<div class="card">' +
      '<div class="card-header"><h3>阶段规划</h3></div>' +
      '<div class="two-col">' +
        '<div class="form-group"><label>基础阶段开始</label><input type="date" id="set-f-start" value="' + (settings.foundation_start || '') + '"></div>' +
        '<div class="form-group"><label>基础阶段结束</label><input type="date" id="set-f-end" value="' + (settings.foundation_end || '') + '"></div>' +
        '<div class="form-group"><label>强化阶段开始</label><input type="date" id="set-i-start" value="' + (settings.intensive_start || '') + '"></div>' +
        '<div class="form-group"><label>强化阶段结束</label><input type="date" id="set-i-end" value="' + (settings.intensive_end || '') + '"></div>' +
        '<div class="form-group"><label>冲刺阶段开始</label><input type="date" id="set-s-start" value="' + (settings.sprint_start || '') + '"></div>' +
        '<div class="form-group"><label>冲刺阶段结束</label><input type="date" id="set-s-end" value="' + (settings.sprint_end || '') + '"></div>' +
      '</div>' +
    '</div>';

    // Daily vocab target
    html += '<div class="card">' +
      '<div class="card-header"><h3>每日目标</h3></div>' +
      '<div class="form-group"><label>每日词汇学习数量</label><input type="number" id="set-vocab-target" value="' + (settings.daily_new_words || '30') + '" min="1" max="500"></div>' +
    '</div>';

    // Pomodoro
    html += '<div class="card">' +
      '<div class="card-header"><h3>番茄计时设置</h3></div>' +
      '<div class="two-col">' +
        '<div class="form-group"><label>专注时长 (分钟)</label><input type="number" id="set-focus" value="' + (settings.pomodoro_focus_minutes || '25') + '" min="5" max="120"></div>' +
        '<div class="form-group"><label>短休时长 (分钟)</label><input type="number" id="set-short" value="' + (settings.pomodoro_short_break_minutes || '5') + '" min="1" max="30"></div>' +
        '<div class="form-group"><label>长休时长 (分钟)</label><input type="number" id="set-long" value="' + (settings.pomodoro_long_break_minutes || '15') + '" min="5" max="60"></div>' +
        '<div class="form-group"><label>长休间隔 (轮次)</label><input type="number" id="set-interval" value="' + (settings.pomodoro_sessions_before_long_break || '4') + '" min="1" max="10"></div>' +
      '</div>' +
    '</div>';

    // AI settings
    html += '<div class="card">' +
      '<div class="card-header"><h3>AI批改设置</h3></div>' +
      '<div class="form-group"><label>API Key</label><input id="set-api-key" value="' + (settings.ai_api_key || '') + '" type="password" placeholder="OpenAI兼容API密钥"></div>' +
      '<div class="form-group"><label>API Base URL</label><input id="set-api-base" value="' + (settings.ai_api_base || 'https://api.openai.com/v1') + '"></div>' +
      '<div class="form-group"><label>模型</label><input id="set-model" value="' + (settings.ai_model || 'gpt-3.5-turbo') + '"></div>' +
    '</div>';

    // Data management
    html += '<div class="card">' +
      '<div class="card-header"><h3>数据管理</h3></div>' +
      '<div style="display:flex;gap:12px;flex-wrap:wrap">' +
        '<button class="btn-primary-sm" id="export-data">导出数据 (JSON)</button>' +
        '<button class="btn" id="import-data">导入数据 (JSON)</button>' +
        '<input type="file" id="import-file" accept=".json" style="display:none">' +
      '</div>' +
      '<p id="data-msg" style="margin-top:8px;font-size:12px"></p>' +
    '</div>';

    // Save button
    html += '<button class="btn-primary-sm" id="save-settings" style="margin-bottom:40px;width:100%">保存设置</button>';

    container.innerHTML = html;

    // Save settings
    document.getElementById('save-settings').addEventListener('click', async function() {
      try {
        var data = {
          username: document.getElementById('set-username').value,
          target_school: document.getElementById('set-school').value,
          exam_date: document.getElementById('set-exam-date').value,
          foundation_start: document.getElementById('set-f-start').value,
          foundation_end: document.getElementById('set-f-end').value,
          intensive_start: document.getElementById('set-i-start').value,
          intensive_end: document.getElementById('set-i-end').value,
          sprint_start: document.getElementById('set-s-start').value,
          sprint_end: document.getElementById('set-s-end').value,
          daily_new_words: parseInt(document.getElementById('set-vocab-target').value) || 30,
          pomodoro_focus_minutes: parseInt(document.getElementById('set-focus').value) || 25,
          pomodoro_short_break_minutes: parseInt(document.getElementById('set-short').value) || 5,
          pomodoro_long_break_minutes: parseInt(document.getElementById('set-long').value) || 15,
          pomodoro_sessions_before_long_break: parseInt(document.getElementById('set-interval').value) || 4,
          ai_api_key: document.getElementById('set-api-key').value,
          ai_api_base: document.getElementById('set-api-base').value,
          ai_model: document.getElementById('set-model').value
        };
        await window.API.put('/settings', data);
        alert('设置已保存!');
      } catch (err) {
        alert('保存失败: ' + err.message);
      }
    });

    // Change password
    document.getElementById('change-password-btn').addEventListener('click', async function() {
      var oldPw = document.getElementById('set-old-password').value;
      var newPw = document.getElementById('set-new-password').value;
      var confirmPw = document.getElementById('set-new-password-confirm').value;
      var msgEl = document.getElementById('password-msg');

      if (!oldPw || !newPw) {
        msgEl.style.color = 'var(--danger)';
        msgEl.textContent = '请填写当前密码和新密码';
        return;
      }
      if (newPw !== confirmPw) {
        msgEl.style.color = 'var(--danger)';
        msgEl.textContent = '两次新密码不一致';
        return;
      }
      if (newPw.length < 4) {
        msgEl.style.color = 'var(--danger)';
        msgEl.textContent = '新密码至少4个字符';
        return;
      }
      try {
        await window.API.put('/auth/password', {
          old_password: oldPw,
          new_password: newPw
        });
        msgEl.style.color = 'var(--success)';
        msgEl.textContent = '密码修改成功!';
        document.getElementById('set-old-password').value = '';
        document.getElementById('set-new-password').value = '';
        document.getElementById('set-new-password-confirm').value = '';
      } catch (err) {
        msgEl.style.color = 'var(--danger)';
        msgEl.textContent = '修改失败: ' + err.message;
      }
    });

    // Export data
    document.getElementById('export-data').addEventListener('click', async function() {
      var msgEl = document.getElementById('data-msg');
      try {
        var data = await window.API.post('/settings/data/export');
        var blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        var url = URL.createObjectURL(blob);
        var a = document.createElement('a');
        a.href = url;
        a.download = 'kaoyan-backup-' + new Date().toISOString().slice(0, 10) + '.json';
        a.click();
        URL.revokeObjectURL(url);
        msgEl.style.color = 'var(--success)';
        msgEl.textContent = '导出成功!';
      } catch (err) {
        msgEl.style.color = 'var(--danger)';
        msgEl.textContent = err.message;
      }
    });

    // Import data
    document.getElementById('import-data').addEventListener('click', function() {
      document.getElementById('import-file').click();
    });

    document.getElementById('import-file').addEventListener('change', async function(e) {
      var file = e.target.files[0];
      if (!file) return;
      var msgEl = document.getElementById('data-msg');
      try {
        var text = await file.text();
        var data = JSON.parse(text);
        await window.API.post('/settings/data/import', data);
        msgEl.style.color = 'var(--success)';
        msgEl.textContent = '导入成功! 正在刷新设置...';
        setTimeout(function() { window.App.navigate('settings'); }, 500);
      } catch (err) {
        msgEl.style.color = 'var(--danger)';
        msgEl.textContent = '导入失败: ' + err.message;
      }
      // Reset file input
      e.target.value = '';
    });
  });
})();
