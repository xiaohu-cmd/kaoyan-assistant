/**
 * Plan page: 备考计划
 * Task list with CRUD, filters, pomodoro timer, calendar, review alerts.
 */
(function() {
  window.App.registerPage('plan', async function(container) {
    var tasks = [];
    var filterPhase = '';
    var filterSubject = '';
    var pomodoroInterval = null;
    var pomodoroSeconds = 25 * 60;
    var pomodoroRunning = false;
    var currentSessionId = null;
    var pomodoroSettings = { focus: 25, short_break: 5, long_break: 15 };
    var currentPomodoroType = 'focus';
    var calendarYear, calendarMonth;
    var calendarTasks = {};

    var subjectColors = { 1: 'politics', 2: 'english', 3: 'math', 4: 'statistics' };

    // --- Data loading ---
    async function loadTasks() {
      var url = '/tasks?';
      if (filterPhase) url += 'phase=' + encodeURIComponent(filterPhase) + '&';
      if (filterSubject) url += 'subject_id=' + filterSubject + '&';
      try {
        tasks = await window.API.get(url);
        renderTaskList();
      } catch (err) {
        console.error('Load tasks error:', err);
      }
    }

    async function loadCalendar(year, month) {
      try {
        var startDate = year + '-' + String(month).padStart(2, '0') + '-01';
        var lastDay = new Date(year, month, 0).getDate();
        var endDate = year + '-' + String(month).padStart(2, '0') + '-' + String(lastDay).padStart(2, '0');
        var data = await window.API.get('/tasks/calendar?start=' + startDate + '&end=' + endDate);
        calendarTasks = {};
        if (data && data.length > 0) {
          data.forEach(function(t) {
            var d = t.due_date;
            if (!calendarTasks[d]) calendarTasks[d] = [];
            calendarTasks[d].push(t);
          });
        }
        renderCalendar();
      } catch (err) {
        console.error('Load calendar error:', err);
      }
    }

    async function loadReviewAlerts() {
      try {
        var due = await window.API.get('/tasks/review-due');
        var el = document.getElementById('review-alerts');
        if (!el) return;
        if (!due || due.length === 0) {
          el.innerHTML = '<p style="color:var(--text-secondary);font-size:13px">暂无到期复习任务，继续保持!</p>';
        } else {
          var html = '';
          due.forEach(function(t) {
            var isToday = t.due_date === new Date().toISOString().slice(0, 10);
            var badgeColor = isToday ? 'style="color:var(--danger);font-weight:600"' : 'style="color:var(--warning);font-weight:600"';
            var label = isToday ? '今天到期' : '即将到期';
            html += '<div style="padding:4px 0;display:flex;align-items:center;gap:8px;font-size:13px">' +
              '<span ' + badgeColor + '>' + label + '</span>' +
              '<span class="subj-badge ' + (subjectColors[t.subject_id] || '') + '">' + (t.subject_name || '-') + '</span>' +
              '<span>' + t.title + '</span>' +
              '</div>';
          });
          el.innerHTML = html;
        }
      } catch (err) {
        var el2 = document.getElementById('review-alerts');
        if (el2) el2.textContent = '加载复习提醒失败';
      }
    }

    // --- Task list rendering ---
    var selectedIds = [];

    function updateBatchBar() {
      var bar = document.getElementById('batch-bar');
      var countEl = document.getElementById('batch-count');
      if (!bar) return;
      if (selectedIds.length > 0) {
        bar.classList.add('active');
        countEl.textContent = selectedIds.length;
      } else {
        bar.classList.remove('active');
      }
    }

    function batchDelete() {
      if (!confirm('确定删除选中的 ' + selectedIds.length + ' 个任务？')) return;
      window.API.post('/tasks/batch-delete', { ids: selectedIds.slice() }).then(function() {
        selectedIds = [];
        loadTasks();
      }).catch(function(err) { alert('删除失败: ' + err.message); });
    }

    function batchSetDone() {
      window.API.post('/tasks/batch-status', { ids: selectedIds.slice(), status: 'done' }).then(function() {
        selectedIds = [];
        loadTasks();
      }).catch(function(err) { alert('操作失败: ' + err.message); });
    }

    function toggleSelectAll(checked) {
      document.querySelectorAll('.batch-sel').forEach(function(cb) { cb.checked = checked; });
      selectedIds = [];
      if (checked) tasks.forEach(function(t) { selectedIds.push(t.id); });
      updateBatchBar();
    }

    function renderTaskList() {
      var listEl = document.getElementById('task-list');
      if (!listEl) return;
      if (tasks.length === 0) {
        listEl.innerHTML = '<p style="color:var(--text-secondary);font-size:13px;padding:12px">暂无任务，点击"+ 添加任务"开始。</p>';
        return;
      }
      var html = '<div class="batch-bar" id="batch-bar"><span>已选 <span class="selected-count" id="batch-count">0</span> 项</span>' +
        '<button class="btn-delete" id="batch-delete-btn">批量删除</button>' +
        '<button class="btn-done" id="batch-done-btn" style="background:#dcfce7;color:#16a34a;padding:4px 12px;border-radius:4px;border:none;cursor:pointer;font-size:12px">标记完成</button>' +
        '<button class="btn-cancel" id="batch-cancel-btn">取消选择</button></div>';
      html += '<div class="select-all-row"><input type="checkbox" class="batch-checkbox" id="select-all"> <label for="select-all" style="cursor:pointer">全选</label></div>';
      tasks.forEach(function(t, idx) {
        var checked = t.status === 'done' ? 'checked' : '';
        var textStyle = t.status === 'done' ? 'text-decoration:line-through;color:var(--text-secondary)' : '';
        var statusLabel = t.status === 'done' ? '已完成' : (t.status === 'in_progress' ? '进行中' : '待办');
        // Due date warning
        var today = new Date().toISOString().slice(0, 10);
        var isTodayTask = t.added_to_today === today;
        var dueWarning = '';
        if (t.due_date && t.status !== 'done') {
          if (t.due_date < today) dueWarning = '<span title="已过期!" style="color:#dc2626;font-weight:700;font-size:18px">⚠️</span>';
          else if (t.due_date === today) dueWarning = '<span title="今日截止!" style="color:#d97706;font-weight:700;font-size:18px">🔔</span>';
        }
        html += '<div class="task-item" data-task-id="' + t.id + '" style="padding:10px;border-bottom:1px solid var(--border);display:flex;align-items:center;gap:8px;font-size:13px">' +
          '<input type="checkbox" class="batch-checkbox batch-sel" data-id="' + t.id + '">' +
          '<input type="checkbox" ' + checked + ' data-id="' + t.id + '" class="task-checkbox" style="cursor:pointer" title="切换状态">' +
          '<span class="subj-badge ' + (subjectColors[t.subject_id] || '') + '">' + (t.subject_name || '-') + '</span>' +
          '<span style="flex:1;' + textStyle + '">' + t.title + '</span>' +
          dueWarning +
          '<span style="font-size:10px;color:var(--text-secondary)">' + (t.due_date || '') + '</span>' +
          '<span style="font-size:11px;color:var(--text-secondary)">' + (t.phase || '') + ' | ' + (t.estimated_minutes || 0) + 'min</span>' +
          '<span style="font-size:11px;color:var(--info)">' + statusLabel + '</span>' +
          (t.status !== 'done'
            ? '<button class="btn-sm task-add-today" data-id="' + t.id + '" style="font-size:11px;' + (isTodayTask ? 'background:#dbeafe;color:#2563eb' : '') + '" title="' + (isTodayTask ? '已加入今日' : '加入今日待办') + '">' + (isTodayTask ? '✅ 今日' : '📌 加至今日') + '</button>'
            : '') +
          '<button class="btn-sm task-edit" data-id="' + t.id + '">编辑</button>' +
          '<button class="btn-sm task-move-up" data-id="' + t.id + '" ' + (idx === 0 ? 'disabled' : '') + '>&#9650;</button>' +
          '<button class="btn-sm task-move-down" data-id="' + t.id + '" ' + (idx === tasks.length - 1 ? 'disabled' : '') + '>&#9660;</button>' +
          '<button class="btn-sm task-delete" data-id="' + t.id + '" style="color:var(--danger)">删除</button>' +
          '</div>';
      });
      listEl.innerHTML = html;

      // Batch selection handlers
      document.getElementById('select-all').addEventListener('change', function() { toggleSelectAll(this.checked); });
      document.getElementById('batch-delete-btn').addEventListener('click', batchDelete);
      document.getElementById('batch-done-btn').addEventListener('click', batchSetDone);
      document.getElementById('batch-cancel-btn').addEventListener('click', function() {
        document.querySelectorAll('.batch-sel').forEach(function(cb) { cb.checked = false; });
        document.getElementById('select-all').checked = false;
        selectedIds = [];
        updateBatchBar();
      });
      document.querySelectorAll('.batch-sel').forEach(function(cb) {
        cb.addEventListener('change', function() {
          var id = parseInt(cb.dataset.id);
          if (cb.checked) { if (selectedIds.indexOf(id) < 0) selectedIds.push(id); }
          else { selectedIds = selectedIds.filter(function(x) { return x !== id; }); }
          updateBatchBar();
        });
      });

      // Checkbox: toggle status
      document.querySelectorAll('.task-checkbox').forEach(function(cb) {
        cb.addEventListener('change', function() {
          var id = cb.dataset.id;
          var newStatus = cb.checked ? 'done' : 'todo';
          window.API.patch('/tasks/' + id + '/status', { status: newStatus }).then(function() {
            loadTasks();
          }).catch(function(err) {
            cb.checked = !cb.checked;
            console.error(err);
          });
        });
      });

      // Edit buttons
      // Add to today
      document.querySelectorAll('.task-add-today').forEach(function(btn) {
        btn.addEventListener('click', function(e) {
          e.stopPropagation();
          var id = btn.dataset.id;
          var task = tasks.find(function(t) { return t.id == id; });
          if (!task) return;
          var today = new Date().toISOString().slice(0, 10);
          var isToday = task.added_to_today === today;
          var url = isToday ? '/tasks/' + id + '/remove-today' : '/tasks/' + id + '/add-today';
          window.API.patch(url).then(function() {
            loadTasks();
          }).catch(function(err) { alert(err.message); });
        });
      });

      document.querySelectorAll('.task-edit').forEach(function(btn) {
        btn.addEventListener('click', function() {
          var task = tasks.find(function(t) { return t.id == btn.dataset.id; });
          if (task) showTaskModal(task);
        });
      });

      // Delete buttons
      document.querySelectorAll('.task-delete').forEach(function(btn) {
        btn.addEventListener('click', function() {
          if (confirm('确认删除此任务?')) {
            window.API.delete('/tasks/' + btn.dataset.id).then(function() { loadTasks(); }).catch(function(err) { alert(err.message); });
          }
        });
      });

      // Move up
      document.querySelectorAll('.task-move-up').forEach(function(btn) {
        btn.addEventListener('click', function() {
          reorderTask(parseInt(btn.dataset.id), 'up');
        });
      });

      // Move down
      document.querySelectorAll('.task-move-down').forEach(function(btn) {
        btn.addEventListener('click', function() {
          reorderTask(parseInt(btn.dataset.id), 'down');
        });
      });
    }

    function reorderTask(id, direction) {
      var idx = tasks.findIndex(function(t) { return t.id === id; });
      if (idx < 0) return;
      var swapIdx = direction === 'up' ? idx - 1 : idx + 1;
      if (swapIdx < 0 || swapIdx >= tasks.length) return;
      var newOrder = tasks.map(function(t) { return t.id; });
      var tmp = newOrder[idx];
      newOrder[idx] = newOrder[swapIdx];
      newOrder[swapIdx] = tmp;
      var items = newOrder.map(function(id, i) { return {id: id, sort_order: i}; });
      window.API.patch('/tasks/reorder', items).then(function() {
        loadTasks();
      }).catch(function(err) {
        console.error('Reorder failed:', err);
      });
    }

    // --- Task modal (add/edit) ---
    function showTaskModal(task) {
      var isEdit = !!task;
      // Remove any existing modal first
      var existing = document.getElementById('task-modal-overlay');
      if (existing) existing.remove();

      var phases = [
        { value: 'foundation', label: '基础阶段' },
        { value: 'intensive', label: '强化阶段' },
        { value: 'sprint', label: '冲刺阶段' }
      ];
      var subjects = [
        { value: '', label: '不区分' },
        { value: '1', label: '政治' },
        { value: '2', label: '英语' },
        { value: '3', label: '数学' },
        { value: '4', label: '432统计学' }
      ];
      var statuses = [
        { value: 'todo', label: '待办' },
        { value: 'in_progress', label: '进行中' },
        { value: 'done', label: '已完成' }
      ];

      var phaseOpts = phases.map(function(p) {
        return '<option value="' + p.value + '"' + (task && task.phase === p.value ? ' selected' : '') + '>' + p.label + '</option>';
      }).join('');
      var subjOpts = subjects.map(function(s) {
        var sel = task ? (String(task.subject_id) === s.value ? ' selected' : '') : '';
        return '<option value="' + s.value + '"' + sel + '>' + s.label + '</option>';
      }).join('');
      var statusOpts = statuses.map(function(s) {
        var sel = task && task.status === s.value ? ' selected' : '';
        return '<option value="' + s.value + '"' + sel + '>' + s.label + '</option>';
      }).join('');
      var priorityVal = task ? (task.priority || 0) : 0;

      var html = '<div class="modal-overlay" id="task-modal-overlay">' +
        '<div class="modal">' +
        '<h3>' + (isEdit ? '编辑任务' : '添加任务') + '</h3>' +
        '<div class="form-group"><label>标题</label><input id="task-title" value="' + (task ? escapeHtml(task.title) : '') + '"></div>' +
        '<div class="form-group"><label>描述</label><textarea id="task-desc">' + (task ? escapeHtml(task.description || '') : '') + '</textarea></div>' +
        '<div class="form-group"><label>科目</label><select id="task-subject">' + subjOpts + '</select></div>' +
        '<div class="form-group"><label>阶段</label><select id="task-phase">' + phaseOpts + '</select></div>' +
        '<div class="form-group"><label>状态</label><select id="task-status">' + statusOpts + '</select></div>' +
        '<div class="form-group"><label>优先级</label><select id="task-priority">' +
          '<option value="0"' + (priorityVal === 0 ? ' selected' : '') + '>普通</option>' +
          '<option value="1"' + (priorityVal === 1 ? ' selected' : '') + '>重要</option>' +
          '<option value="2"' + (priorityVal >= 2 ? ' selected' : '') + '>紧急</option>' +
        '</select></div>' +
        '<div class="form-group"><label>截止日期</label><input type="date" id="task-due" value="' + (task ? (task.due_date || '') : '') + '"></div>' +
        '<div class="form-group"><label>预计时长 (分钟)</label><input type="number" id="task-estimated" value="' + (task ? (task.estimated_minutes || 0) : 0) + '" min="0"></div>' +
        '<div class="modal-actions">' +
          '<button class="btn" id="task-modal-cancel">取消</button>' +
          '<button class="btn-primary-sm" id="task-modal-save">' + (isEdit ? '保存' : '添加') + '</button>' +
        '</div>' +
        '</div></div>';

      document.body.insertAdjacentHTML('beforeend', html);

      document.getElementById('task-modal-cancel').addEventListener('click', function() {
        document.getElementById('task-modal-overlay').remove();
      });
      document.getElementById('task-modal-overlay').addEventListener('click', function(e) {
        if (e.target === e.currentTarget) e.currentTarget.remove();
      });
      document.getElementById('task-modal-save').addEventListener('click', function() {
        var data = {
          title: document.getElementById('task-title').value.trim(),
          description: document.getElementById('task-desc').value.trim(),
          subject_id: parseInt(document.getElementById('task-subject').value) || null,
          phase: document.getElementById('task-phase').value,
          status: document.getElementById('task-status').value,
          priority: parseInt(document.getElementById('task-priority').value),
          due_date: document.getElementById('task-due').value || null,
          estimated_minutes: parseInt(document.getElementById('task-estimated').value) || 0
        };
        if (!data.title) { alert('请输入标题'); return; }
        var promise = isEdit ? window.API.put('/tasks/' + task.id, data) : window.API.post('/tasks', data);
        promise.then(function() {
          document.getElementById('task-modal-overlay').remove();
          loadTasks();
          loadCalendar(calendarYear, calendarMonth);
        }).catch(function(err) {
          alert(err.message);
        });
      });
    }

    function escapeHtml(str) {
      return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    }

    // --- Pomodoro ---
    function renderPomodoro() {
      var m = Math.floor(pomodoroSeconds / 60);
      var s = pomodoroSeconds % 60;
      var display = document.getElementById('pomodoro-display');
      if (display) {
        display.textContent = String(m).padStart(2, '0') + ':' + String(s).padStart(2, '0');
      }
      var typeLabel = document.getElementById('pomodoro-type-label');
      if (typeLabel) {
        typeLabel.textContent = currentPomodoroType === 'focus' ? '专注' : (currentPomodoroType === 'short_break' ? '短休息' : '长休息');
      }
    }

    function startPomodoro() {
      if (pomodoroRunning) return;
      pomodoroRunning = true;
      document.getElementById('pomodoro-start').style.display = 'none';
      document.getElementById('pomodoro-pause').style.display = '';
      window.API.post('/pomodoro/start', { subject_id: filterSubject || null, type: currentPomodoroType }).then(function(resp) {
        currentSessionId = resp.id;
      }).catch(function() {});
      pomodoroInterval = setInterval(function() {
        pomodoroSeconds--;
        renderPomodoro();
        if (pomodoroSeconds <= 0) {
          stopPomodoro(true);
        }
      }, 1000);
    }

    function pausePomodoro() {
      pomodoroRunning = false;
      clearInterval(pomodoroInterval);
      document.getElementById('pomodoro-start').style.display = '';
      document.getElementById('pomodoro-pause').style.display = 'none';
    }

    function stopPomodoro(completed) {
      pomodoroRunning = false;
      clearInterval(pomodoroInterval);
      if (currentSessionId) {
        var totalSeconds = pomodoroSettings[currentPomodoroType] * 60;
        var elapsed = totalSeconds - pomodoroSeconds;
        window.API.post('/pomodoro/stop', {
          id: currentSessionId,
          duration_seconds: elapsed,
          completed: !!completed
        }).catch(function() {});
        currentSessionId = null;
      }
      pomodoroSeconds = pomodoroSettings[currentPomodoroType] * 60;
      renderPomodoro();
      document.getElementById('pomodoro-start').style.display = '';
      document.getElementById('pomodoro-pause').style.display = 'none';
    }

    function resetPomodoro() {
      if (pomodoroRunning) {
        clearInterval(pomodoroInterval);
        pomodoroRunning = false;
        document.getElementById('pomodoro-start').style.display = '';
        document.getElementById('pomodoro-pause').style.display = 'none';
        if (currentSessionId) {
          window.API.post('/pomodoro/stop', { id: currentSessionId, duration_seconds: 0, completed: false }).catch(function() {});
          currentSessionId = null;
        }
      }
      pomodoroSeconds = pomodoroSettings[currentPomodoroType] * 60;
      renderPomodoro();
    }

    function switchPomodoroType(type) {
      if (pomodoroRunning) {
        if (!confirm('切换类型会重置当前计时，确定吗?')) return;
        clearInterval(pomodoroInterval);
        pomodoroRunning = false;
        document.getElementById('pomodoro-start').style.display = '';
        document.getElementById('pomodoro-pause').style.display = 'none';
        if (currentSessionId) {
          window.API.post('/pomodoro/stop', { id: currentSessionId, duration_seconds: 0, completed: false }).catch(function() {});
          currentSessionId = null;
        }
      }
      currentPomodoroType = type;
      pomodoroSeconds = pomodoroSettings[type] * 60;
      renderPomodoro();
      document.querySelectorAll('.pomodoro-type-btn').forEach(function(b) {
        b.classList.toggle('active', b.dataset.ptype === type);
      });
    }

    // --- Calendar ---
    function goToPrevMonth() {
      calendarMonth--;
      if (calendarMonth < 1) { calendarMonth = 12; calendarYear--; }
      loadCalendar(calendarYear, calendarMonth);
    }

    function goToNextMonth() {
      calendarMonth++;
      if (calendarMonth > 12) { calendarMonth = 1; calendarYear++; }
      loadCalendar(calendarYear, calendarMonth);
    }

    function renderCalendar() {
      var el = document.getElementById('calendar-container');
      if (!el) return;

      var today = new Date();
      var firstDay = new Date(calendarYear, calendarMonth - 1, 1);
      var lastDay = new Date(calendarYear, calendarMonth, 0);
      var startDow = firstDay.getDay(); // 0=Sun
      var daysInMonth = lastDay.getDate();
      var headers = ['日', '一', '二', '三', '四', '五', '六'];

      var html = '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">' +
        '<button class="btn-sm" id="cal-prev">&lt;</button>' +
        '<strong>' + calendarYear + '年 ' + calendarMonth + '月</strong>' +
        '<button class="btn-sm" id="cal-next">&gt;</button>' +
        '</div>';

      html += '<div class="calendar-grid">';
      headers.forEach(function(h) {
        html += '<div class="calendar-day-header">' + h + '</div>';
      });
      for (var i = 0; i < startDow; i++) {
        html += '<div class="calendar-day" style="opacity:0.3"></div>';
      }
      for (var d = 1; d <= daysInMonth; d++) {
        var dateStr = calendarYear + '-' + String(calendarMonth).padStart(2, '0') + '-' + String(d).padStart(2, '0');
        var hasTask = calendarTasks[dateStr] && calendarTasks[dateStr].length > 0;
        var isToday = (d === today.getDate() && calendarMonth === (today.getMonth() + 1) && calendarYear === today.getFullYear());
        var cls = 'calendar-day' + (isToday ? ' today' : '') + (hasTask ? ' has-task' : '');
        var dots = '';
        if (hasTask) {
          var maxDots = Math.min(calendarTasks[dateStr].length, 3);
          for (var j = 0; j < maxDots; j++) {
            dots += '<span style="display:inline-block;width:4px;height:4px;border-radius:50%;background:var(--info);margin:0 1px"></span>';
          }
        }
        html += '<div class="calendar-day ' + cls.trim() + '" data-date="' + dateStr + '" style="position:relative">' +
          '<div>' + d + '</div>' +
          '<div style="margin-top:2px">' + dots + '</div>' +
          '</div>';
      }
      html += '</div>';

      // Day detail panel
      html += '<div id="calendar-day-detail" style="margin-top:10px;padding:10px;background:var(--bg);border-radius:var(--radius-sm);font-size:12px;display:none"></div>';

      el.innerHTML = html;

      document.getElementById('cal-prev').addEventListener('click', goToPrevMonth);
      document.getElementById('cal-next').addEventListener('click', goToNextMonth);

      document.querySelectorAll('.calendar-day[data-date]').forEach(function(cell) {
        cell.addEventListener('click', function() {
          var date = cell.dataset.date;
          var detail = document.getElementById('calendar-day-detail');
          var dayTasks = calendarTasks[date] || [];
          if (dayTasks.length === 0) {
            detail.style.display = 'block';
            detail.innerHTML = '<strong>' + date + '</strong>: 暂无任务';
          } else {
            var taskHtml = '<strong>' + date + ' 任务:</strong><ul style="list-style:none;margin-top:4px">';
            dayTasks.forEach(function(t) {
              taskHtml += '<li style="padding:2px 0">' +
                '<span class="subj-badge ' + (subjectColors[t.subject_id] || '') + '">' + (t.subject_name || '-') + '</span> ' +
                t.title + ' (' + (t.status === 'done' ? '已完成' : t.status === 'in_progress' ? '进行中' : '待办') + ')' +
                '</li>';
            });
            taskHtml += '</ul>';
            detail.style.display = 'block';
            detail.innerHTML = taskHtml;
          }
        });
      });
    }

    // --- Build page HTML ---
    var html = '';

    // Phase filter tabs
    html += '<div class="card"><div class="card-header"><h3>任务筛选</h3></div>';
    html += '<div class="tag-filters" id="phase-filters">';
    [{ value: '', label: '全部' }, { value: 'foundation', label: '基础' }, { value: 'intensive', label: '强化' }, { value: 'sprint', label: '冲刺' }].forEach(function(p) {
      html += '<button class="tag-filter' + (filterPhase === p.value ? ' active' : '') + '" data-phase="' + p.value + '">' + p.label + '</button>';
    });
    html += '</div>';
    html += '<div class="tag-filters" id="subject-filters">';
    [{ id: '', name: '全部' }, { id: 1, name: '政治' }, { id: 2, name: '英语' }, { id: 3, name: '数学' }, { id: 4, name: '统计' }].forEach(function(s) {
      html += '<button class="tag-filter' + (filterSubject === '' + s.id ? ' active' : '') + '" data-subject="' + s.id + '">' + s.name + '</button>';
    });
    html += '</div>';
    html += '<button class="btn-primary-sm" id="add-task-btn" style="margin-bottom:12px">+ 添加任务</button>';
    html += '<div id="task-list"></div></div>';

    // Pomodoro timer
    html += '<div class="card"><div class="card-header"><h3>番茄计时器</h3><span id="pomodoro-type-label" style="font-size:12px;color:var(--text-secondary)">专注</span></div>';
    html += '<div style="display:flex;gap:6px;justify-content:center;margin-bottom:12px">' +
      '<button class="tag-filter pomodoro-type-btn active" data-ptype="focus">专注</button>' +
      '<button class="tag-filter pomodoro-type-btn" data-ptype="short_break">短休息</button>' +
      '<button class="tag-filter pomodoro-type-btn" data-ptype="long_break">长休息</button>' +
      '</div>';
    html += '<div class="pomodoro-display" id="pomodoro-display">25:00</div>';
    html += '<div class="pomodoro-actions">' +
      '<button class="btn-primary-sm" id="pomodoro-start" style="min-width:80px">开始</button>' +
      '<button class="btn" id="pomodoro-pause" style="display:none;min-width:80px">暂停</button>' +
      '<button class="btn" id="pomodoro-stop" style="min-width:80px">结束</button>' +
      '<button class="btn" id="pomodoro-reset" style="min-width:80px">重置</button>' +
      '</div>';

    // Pomodoro settings
    html += '<div style="display:flex;gap:12px;margin-top:16px;flex-wrap:wrap;justify-content:center;font-size:12px;color:var(--text-secondary)">' +
      '<label>专注: <input type="number" id="pomo-focus" value="' + pomodoroSettings.focus + '" min="1" max="120" style="width:50px;padding:2px 4px;font-size:12px"> 分钟</label>' +
      '<label>短休息: <input type="number" id="pomo-short-break" value="' + pomodoroSettings.short_break + '" min="1" max="30" style="width:50px;padding:2px 4px;font-size:12px"> 分钟</label>' +
      '<label>长休息: <input type="number" id="pomo-long-break" value="' + pomodoroSettings.long_break + '" min="1" max="60" style="width:50px;padding:2px 4px;font-size:12px"> 分钟</label>' +
      '</div>';
    html += '</div>';

    // Calendar
    html += '<div class="card"><div class="card-header"><h3>任务日历</h3></div>';
    html += '<div id="calendar-container" style="margin-top:12px">加载中...</div></div>';

    // Review alerts
    html += '<div class="card"><div class="card-header"><h3>复习提醒</h3></div>';
    html += '<div id="review-alerts" style="color:var(--text-secondary);font-size:13px">加载中...</div></div>';

    container.innerHTML = html;

    // --- Event bindings ---
    document.querySelectorAll('#phase-filters .tag-filter').forEach(function(btn) {
      btn.addEventListener('click', function() {
        filterPhase = btn.dataset.phase;
        document.querySelectorAll('#phase-filters .tag-filter').forEach(function(b) { b.classList.toggle('active', b.dataset.phase === filterPhase); });
        loadTasks();
      });
    });
    document.querySelectorAll('#subject-filters .tag-filter').forEach(function(btn) {
      btn.addEventListener('click', function() {
        filterSubject = btn.dataset.subject;
        document.querySelectorAll('#subject-filters .tag-filter').forEach(function(b) { b.classList.toggle('active', b.dataset.subject === filterSubject); });
        loadTasks();
      });
    });
    document.getElementById('add-task-btn').addEventListener('click', function() { showTaskModal(null); });

    document.getElementById('pomodoro-start').addEventListener('click', startPomodoro);
    document.getElementById('pomodoro-pause').addEventListener('click', pausePomodoro);
    document.getElementById('pomodoro-stop').addEventListener('click', function() { stopPomodoro(false); });
    document.getElementById('pomodoro-reset').addEventListener('click', resetPomodoro);

    document.querySelectorAll('.pomodoro-type-btn').forEach(function(btn) {
      btn.addEventListener('click', function() { switchPomodoroType(btn.dataset.ptype); });
    });

    // Pomodoro settings change
    ['focus', 'short_break', 'long_break'].forEach(function(type) {
      var inputId = type === 'focus' ? 'pomo-focus' : (type === 'short_break' ? 'pomo-short-break' : 'pomo-long-break');
      var el = document.getElementById(inputId);
      if (el) {
        el.addEventListener('change', function() {
          var val = parseInt(el.value) || pomodoroSettings[type];
          if (val < 1) val = 1;
          pomodoroSettings[type] = val;
          if (currentPomodoroType === type && !pomodoroRunning) {
            pomodoroSeconds = val * 60;
            renderPomodoro();
          }
        });
      }
    });

    // Initialize data
    var now = new Date();
    calendarYear = now.getFullYear();
    calendarMonth = now.getMonth() + 1;

    loadTasks();
    loadCalendar(calendarYear, calendarMonth);
    loadReviewAlerts();
  });
})();
