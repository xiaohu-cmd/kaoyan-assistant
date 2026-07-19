/**
 * Schools page: 院校信息 + 提醒中心
 */
(function() {
  window.App.registerPage('schools', async function(container) {
    var schools = [];
    try {
      schools = await window.API.get('/schools');
    } catch (err) {
      container.innerHTML = '<div class="card"><p style="color:var(--danger)">加载失败: ' + err.message + '</p></div>';
      return;
    }

    var today = new Date();
    var todayStr = today.toISOString().slice(0, 10);
    var html = '';

    // ===== ALERT CENTER =====
    html += '<div class="card" style="border-left:4px solid #dc2626;margin-bottom:16px"><div class="card-header"><h3>提醒中心</h3></div><div style="font-size:13px;line-height:2">';

    // Milestones
    var milestones = [
      { date: '2026-07-30', label: '各校招生简章陆续发布', icon: '📋', color: '#d97706' },
      { date: '2026-09-24', label: '预报名开始', icon: '📝', color: '#2563eb' },
      { date: '2026-10-08', label: '正式报名开始', icon: '✍️', color: '#dc2626' },
      { date: '2026-10-25', label: '正式报名截止', icon: '⏰', color: '#dc2626' },
      { date: '2026-11-01', label: '网上确认', icon: '✅', color: '#16a34a' },
      { date: '2026-12-15', label: '打印准考证', icon: '🎫', color: '#2563eb' },
      { date: '2026-12-26', label: '考研初试', icon: '🔥', color: '#dc2626' },
    ];

    milestones.forEach(function(m) {
      var days = Math.ceil((new Date(m.date) - today) / 86400000);
      if (days >= 0 && days <= 60) {
        var urgency = days <= 3 ? 'font-weight:700;color:' + m.color : 'color:' + m.color;
        html += '<div style="' + urgency + '">' + m.icon + ' <strong>' + m.label + '</strong> — ' +
          (days === 0 ? '<span style="color:#dc2626">就是今天!</span>' : '还有 <strong>' + days + '</strong> 天') +
          ' <span style="font-size:11px;color:var(--text-secondary)">(' + m.date + ')</span></div>';
      }
    });

    // 15-day review
    var lastReview = localStorage.getItem('last-review-reminder');
    var shouldRemind = !lastReview || (today - new Date(lastReview)) / 86400000 >= 15;
    if (shouldRemind) {
      html += '<div style="margin-top:8px;padding:8px;background:#fef3c7;border-radius:6px;color:#92400e">' +
        '📊 <strong>15天复习回顾:</strong> 建议回顾近两周复习进度，对比目标院校最新分数线调整计划。<br>' +
        '<button class="btn-sm" id="dismiss-review" style="margin-top:4px">已回顾，15天后再提醒</button></div>';
    }

    // School comparison
    html += '<div style="margin-top:8px;border-top:1px solid var(--border);padding-top:8px">' +
      '<strong>关键差异:</strong> 厦大考<em style="color:#dc2626">英语一</em>(复试线350/统考32人)，' +
      '西交考<em style="color:#16a34a">英语二</em>(复试线345/统考32人)但专业课含<em style="color:#dc2626">计量经济学60分</em>。' +
      '两校学制均为3年。厦大淘汰规则严格(英语<15分即淘汰)。</div>';

    html += '</div></div>';

    // ===== SCHOOL DATA =====
    if (schools.length === 0) {
      html += '<p style="color:var(--text-secondary);font-size:13px">暂无院校数据。</p>';
    } else {
      var grouped = {};
      schools.forEach(function(s) {
        if (!grouped[s.school_name]) grouped[s.school_name] = [];
        grouped[s.school_name].push(s);
      });

      Object.keys(grouped).forEach(function(name) {
        var entries = grouped[name].sort(function(a, b) { return b.year - a.year; });
        // Skip timeline/tips entries
        if (name === '考研日程') return;
        var latest = entries[0];

        html += '<div class="card" style="border-left:4px solid var(--info);margin-bottom:12px;padding:16px">' +
          '<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px">' +
            '<h4>' + name + '</h4>' +
            '<span style="font-size:12px;color:var(--text-secondary)">' + entries.length + ' 年数据</span>' +
          '</div>';

        if (latest.major) html += '<div style="font-size:13px;margin-bottom:4px"><strong>专业:</strong> ' + latest.major + '</div>';
        if (latest.exam_subjects) {
          var subjStr = latest.exam_subjects;
          try { var sj = JSON.parse(subjStr); if (Array.isArray(sj)) subjStr = sj.join(', '); } catch(e) {}
          html += '<div style="font-size:13px;margin-bottom:4px"><strong>科目:</strong> ' + subjStr + '</div>';
        }
        if (latest.reference_books) {
          var bookStr = latest.reference_books;
          try { var bj = JSON.parse(bookStr); if (Array.isArray(bj)) bookStr = bj.join('; '); } catch(e) {}
          html += '<div style="font-size:13px;margin-bottom:4px"><strong>参考书:</strong> ' + bookStr + '</div>';
        }
        if (latest.admission_line > 0) {
          html += '<div style="font-size:13px;margin-bottom:4px">' +
            '<strong>最新复试线(' + latest.year + '):</strong> ' + latest.admission_line +
            ' | 招生' + (latest.enrollment_count || '-') + '人 | 报考' + (latest.applicant_count || '-') + '人</div>';
        }
        if (latest.notes) {
          html += '<div style="font-size:12px;color:var(--text-secondary);margin-top:4px;padding:8px;background:#f8fafc;border-radius:6px">' + latest.notes + '</div>';
        }

        // Average scores section
        var scoreEntry = entries.find(function(e) { return e.major && e.major.indexOf('录取分数') >= 0; });
        if (scoreEntry && scoreEntry.reference_books) {
          try {
            var scores = JSON.parse(scoreEntry.reference_books);
            if (Array.isArray(scores) && scores.length > 0) {
              html += '<div style="margin-top:8px;padding:8px;background:#f0fdf4;border-radius:6px;font-size:13px">' +
                '<strong>录取均分(' + scoreEntry.year + '):</strong> ';
              html += scores.join(' | ') + '</div>';
            }
          } catch(e) {}
        }
        if (scoreEntry && scoreEntry.exam_subjects) {
          html += '<div style="font-size:12px;color:var(--text-secondary);margin-top:2px">' + scoreEntry.exam_subjects + '</div>';
        }

        // History table
        var dataRows = entries.filter(function(e) { return e.admission_line > 0; });
        if (dataRows.length > 0) {
          html += '<div style="margin-top:8px"><table class="table" style="font-size:12px"><thead><tr><th>年份</th><th>复试线</th><th>招生</th><th>报考</th></tr></thead><tbody>';
          dataRows.forEach(function(e) {
            html += '<tr><td>' + e.year + '</td><td>' + (e.admission_line || '-') + '</td><td>' + (e.enrollment_count || '-') + '</td><td>' + (e.applicant_count || '-') + '</td></tr>';
          });
          html += '</tbody></table></div>';
        }

        html += '<div style="margin-top:8px;display:flex;gap:6px">' +
          '<button class="btn-sm school-edit" data-id="' + latest.id + '" data-name="' + name + '">编辑</button>' +
          '<button class="btn-sm school-delete" data-id="' + latest.id + '" style="color:var(--danger)">删除</button>' +
        '</div></div>';
      });

      // Charts
      html += '<div class="card"><div class="card-header"><h3>复试线趋势</h3></div><div style="height:260px"><canvas id="admission-chart"></canvas></div></div>';
      html += '<div class="card"><div class="card-header"><h3>招生/报考人数</h3></div><div style="height:260px"><canvas id="enrollment-chart"></canvas></div></div>';
    }

    container.innerHTML = html;

    // Dismiss review reminder
    var dismissBtn = document.getElementById('dismiss-review');
    if (dismissBtn) dismissBtn.addEventListener('click', function() {
      localStorage.setItem('last-review-reminder', today.toISOString());
      dismissBtn.parentElement.style.display = 'none';
    });

    // Add school button
    // (school page has data already, hide add button since data is pre-loaded)
    // Edit/delete handlers
    document.querySelectorAll('.school-edit').forEach(function(btn) {
      btn.addEventListener('click', function() {
        var entry = schools.find(function(s) { return s.id === parseInt(btn.dataset.id); });
        if (entry) showSchoolModal(entry);
      });
    });
    document.querySelectorAll('.school-delete').forEach(function(btn) {
      btn.addEventListener('click', async function() {
        if (confirm('确认删除?')) {
          try { await window.API.delete('/schools/' + btn.dataset.id); } catch (err) { alert(err.message); return; }
          window.App.navigate('schools');
        }
      });
    });

    function showSchoolModal(existing) {
      var isEdit = !!existing;
      var overlay = document.createElement('div');
      overlay.className = 'modal-overlay';
      overlay.innerHTML = '<div class="modal" style="min-width:480px">' +
        '<h3>' + (isEdit ? '编辑' : '添加') + '</h3>' +
        '<div class="form-group"><label>院校名称</label><input id="sm-name" value="' + (isEdit ? existing.school_name || '' : '') + '"></div>' +
        '<div style="display:flex;gap:8px"><div class="form-group" style="flex:1"><label>年份</label><input type="number" id="sm-year" value="' + (isEdit ? existing.year || '' : '2026') + '"></div>' +
        '<div class="form-group" style="flex:1"><label>复试线</label><input type="number" id="sm-line" value="' + (isEdit ? existing.admission_line || '' : '') + '"></div></div>' +
        '<div style="display:flex;gap:8px"><div class="form-group" style="flex:1"><label>招生人数</label><input type="number" id="sm-enroll" value="' + (isEdit ? existing.enrollment_count || '' : '') + '"></div>' +
        '<div class="form-group" style="flex:1"><label>报考人数</label><input type="number" id="sm-app" value="' + (isEdit ? existing.applicant_count || '' : '') + '"></div></div>' +
        '<div class="form-group"><label>考试科目</label><input id="sm-subjects" value="' + (isEdit ? existing.exam_subjects || '' : '') + '"></div>' +
        '<div class="form-group"><label>参考书目</label><input id="sm-books" value="' + (isEdit ? existing.reference_books || '' : '') + '"></div>' +
        '<div class="modal-actions"><button class="btn" id="sm-cancel">取消</button><button class="btn-primary-sm" id="sm-save">保存</button></div></div>';
      document.body.appendChild(overlay);
      overlay.querySelector('#sm-cancel').addEventListener('click', function() { overlay.remove(); });
      overlay.addEventListener('click', function(e) { if (e.target === overlay) overlay.remove(); });
      overlay.querySelector('#sm-save').addEventListener('click', async function() {
        var nameVal = overlay.querySelector('#sm-name').value.trim();
        if (!nameVal) { alert('请输入院校名称'); return; }
        var data = {
          school_name: nameVal, year: parseInt(overlay.querySelector('#sm-year').value) || 2026,
          major: '应用统计专硕',
          admission_line: parseFloat(overlay.querySelector('#sm-line').value) || 0,
          enrollment_count: parseInt(overlay.querySelector('#sm-enroll').value) || 0,
          applicant_count: parseInt(overlay.querySelector('#sm-app').value) || 0,
          exam_subjects: overlay.querySelector('#sm-subjects').value,
          reference_books: overlay.querySelector('#sm-books').value, is_pinned: 1
        };
        try {
          if (isEdit) await window.API.put('/schools/' + existing.id, data);
          else await window.API.post('/schools', data);
        } catch (err) { alert(err.message); return; }
        overlay.remove(); window.App.navigate('schools');
      });
    }

    // Charts
    if (schools.length > 0) {
      var sorted = schools.slice().sort(function(a, b) { return a.year - b.year; });
      var years = []; sorted.forEach(function(s) { if (years.indexOf(s.year) === -1) years.push(s.year); });
      var names = []; sorted.forEach(function(s) { if (names.indexOf(s.school_name) === -1) names.push(s.school_name); });
      var colors = ['#3b82f6', '#22c55e', '#ef4444', '#f59e0b'];

      var admCtx = document.getElementById('admission-chart');
      if (admCtx) {
        new Chart(admCtx, { type: 'line', data: { labels: years, datasets: names.map(function(name, i) { return { label: name, data: years.map(function(y) { var e = sorted.find(function(s) { return s.school_name === name && s.year === y && s.admission_line > 0; }); return e ? e.admission_line : null; }), borderColor: colors[i], backgroundColor: 'transparent', tension: 0.3, spanGaps: true }; }) }, options: { responsive: true, maintainAspectRatio: false, scales: { y: { beginAtZero: false } } } });
      }
      var enrCtx = document.getElementById('enrollment-chart');
      if (enrCtx) {
        var ds = [];
        names.forEach(function(name, i) {
          ds.push({ label: name + '招生', data: years.map(function(y) { var e = sorted.find(function(s) { return s.school_name === name && s.year === y && s.enrollment_count > 0; }); return e ? e.enrollment_count : null; }), borderColor: colors[i], backgroundColor: colors[i] + '30', tension: 0.3, spanGaps: true });
          ds.push({ label: name + '报考', data: years.map(function(y) { var e = sorted.find(function(s) { return s.school_name === name && s.year === y && s.applicant_count > 0; }); return e ? e.applicant_count : null; }), borderColor: colors[i], borderDash: [5,5], backgroundColor: 'transparent', tension: 0.3, spanGaps: true });
        });
        new Chart(enrCtx, { type: 'line', data: { labels: years, datasets: ds }, options: { responsive: true, maintainAspectRatio: false, scales: { y: { beginAtZero: false } } } });
      }
    }
  });
})();
