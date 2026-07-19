/**
 * Dashboard page: 学习仪表盘
 * Countdown, streak, today study time, today tasks, subject progress,
 * weekly bar chart, monthly heatmap, and daily review.
 */
(function() {
  window.App.registerPage('dashboard', async function(container) {
    const today = new Date();
    const year = today.getFullYear();
    const month = today.getMonth() + 1;

    var overview, heatmapData, weeklyReport, monthlyReport;
    try {
      [overview, heatmapData, weeklyReport, monthlyReport] = await Promise.all([
        window.API.get('/dashboard/overview'),
        window.API.get('/dashboard/heatmap?year=' + year + '&month=' + month),
        window.API.get('/dashboard/weekly-report?date=' + today.toISOString().slice(0, 10)),
        window.API.get('/dashboard/monthly-report?month=' + year + '-' + String(month).padStart(2, '0'))
      ]);
    } catch (err) {
      container.innerHTML = '<div class="card"><p style="color:var(--danger)">加载失败: ' + err.message + '</p></div>';
      return;
    }

    var subjectColors = { 1: 'politics', 2: 'english', 3: 'math', 4: 'statistics' };

    // Build HTML
    var html = '';

    // --- Stat cards row ---
    html += '<div class="stat-grid">';
    html += '<div class="stat-card"><div class="stat-value">' + (overview.countdown_days || '-') + '</div><div class="stat-label">距考研 (天)</div></div>';
    html += '<div class="stat-card"><div class="stat-value">' + (overview.streak_days || 0) + ' &#128293;</div><div class="stat-label">连续打卡 (天)</div></div>';
    html += '<div class="stat-card"><div class="stat-value">' + (overview.today_minutes || 0) + '</div><div class="stat-label">今日学习 (分钟)</div></div>';
    html += '<div class="stat-card"><div class="stat-value">' + (overview.today_tasks_count || 0) + '</div><div class="stat-label">今日待办</div></div>';
    html += '</div>';

    // --- Quick pomodoro start ---
    html += '<div class="card" style="text-align:center;">';
    html += '<button class="btn-primary-sm" id="quick-pomodoro" style="padding:10px 24px;font-size:15px;">&#9201; 快速开始番茄钟</button>';
    html += '<span id="quick-pomodoro-msg" style="margin-left:12px;font-size:12px;color:var(--text-secondary)"></span>';
    html += '</div>';

    // --- Today's tasks + Subject progress (two-col) ---
    html += '<div class="two-col">';

    // Today's tasks
    html += '<div class="card"><div class="card-header"><h3>今日待办</h3><a href="#plan" style="font-size:12px;color:var(--info)">去添加 →</a></div>';
    if (overview.today_tasks && overview.today_tasks.length > 0) {
      html += '<ul style="list-style:none">';
      overview.today_tasks.forEach(function(t) {
        var checked = t.status === 'done' ? 'checked' : '';
        var style = t.status === 'done' ? 'text-decoration:line-through;color:var(--text-secondary)' : '';
        var dueInfo = t.due_date ? ' 📅' + t.due_date : '';
        html += '<li style="padding:6px 0;display:flex;align-items:center;gap:8px;font-size:13px">' +
          '<input type="checkbox" ' + checked + ' data-task-id="' + t.id + '" class="dash-task-check" style="cursor:pointer">' +
          '<span class="subj-badge ' + (subjectColors[t.subject_id] || '') + '">' + (t.subject_name || '-') + '</span>' +
          '<span style="flex:1;' + style + '">' + t.title + '</span>' +
          '<span style="font-size:10px;color:var(--text-secondary)">' + dueInfo + '</span>' +
          '<span style="font-size:11px;color:var(--text-secondary)">' + (t.phase || '') + '</span>' +
          '<button class="btn-sm dash-remove-today" data-id="' + t.id + '" title="从今日移除" style="font-size:10px;color:var(--text-secondary);cursor:pointer">✕</button>' +
          '</li>';
      });
      html += '</ul>';
    } else {
      html += '<p style="color:var(--text-secondary);font-size:13px;padding:12px;text-align:center">' +
        '还没有今日任务。<br>去 <a href="#plan" style="color:var(--info)">备考计划</a> 点击 <b>📌 加至今日</b> 来添加。</p>';
    }
    html += '</div>';

    // Subject progress
    html += '<div class="card"><div class="card-header"><h3>各科进度</h3></div>';
    if (overview.subject_progress && overview.subject_progress.length > 0) {
      overview.subject_progress.forEach(function(sp) {
        var color = sp.color || 'var(--info)';
        html += '<div style="margin-bottom:14px">' +
          '<div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:4px">' +
            '<span class="subj-badge ' + (subjectColors[sp.subject_id] || '') + '">' + sp.name + '</span>' +
            '<span style="color:var(--text-secondary)">任务 ' + (sp.task_completion_rate || 0) + '% | 学时 ' + (sp.time_achievement_rate || 0) + '%</span>' +
          '</div>' +
          '<div class="progress-bar">' +
            '<div class="progress-fill" style="width:' + (sp.task_completion_rate || 0) + '%;background:' + color + '"></div>' +
          '</div>' +
          '<div style="font-size:11px;color:var(--text-secondary);margin-top:2px">' + (sp.actual_minutes || 0) + ' / ' + (sp.planned_minutes || 0) + ' 分钟</div>' +
          '</div>';
      });
    } else {
      html += '<p style="color:var(--text-secondary);font-size:13px">暂无科目数据。</p>';
    }
    html += '</div>';
    html += '</div>'; // end two-col

    // --- Report tabs (weekly / monthly) ---
    html += '<div class="card">';
    html += '<div class="card-header">';
    html += '<h3>学习报告</h3>';
    html += '<div class="tag-filters" style="margin-bottom:0">' +
      '<button class="tag-filter active" id="tab-weekly">本周</button>' +
      '<button class="tag-filter" id="tab-monthly">本月</button>' +
      '</div>';
    html += '</div>';

    // Weekly chart container
    html += '<div id="report-weekly">';
    html += '<div style="height:220px"><canvas id="weekly-chart"></canvas></div>';
    if (weeklyReport && weeklyReport.total_minutes !== undefined) {
      html += '<div style="display:flex;justify-content:space-around;margin-top:12px;font-size:12px;color:var(--text-secondary)">' +
        '<span>总计: ' + weeklyReport.total_minutes + ' 分钟</span>' +
        '<span>日均: ' + (weeklyReport.avg_daily_minutes || 0) + ' 分钟</span>' +
        '</div>';
    }
    html += '</div>';

    // Monthly chart container (hidden by default)
    html += '<div id="report-monthly" style="display:none">';
    html += '<div style="height:220px"><canvas id="monthly-chart"></canvas></div>';
    if (monthlyReport && monthlyReport.total_minutes !== undefined) {
      html += '<div style="display:flex;justify-content:space-around;margin-top:12px;font-size:12px;color:var(--text-secondary)">' +
        '<span>总计: ' + monthlyReport.total_minutes + ' 分钟</span>' +
        '<span>日均: ' + (monthlyReport.avg_daily_minutes || 0) + ' 分钟</span>' +
        '</div>';
    }
    html += '</div>';
    html += '</div>';

    // --- Monthly heatmap ---
    html += '<div class="card"><div class="card-header"><h3>本月学习热力图</h3></div>';
    html += '<div class="heatmap-grid">';
    if (heatmapData && heatmapData.length > 0) {
      var maxMin = Math.max.apply(null, heatmapData.map(function(h) { return h.minutes || 0; }));
      if (maxMin === 0) maxMin = 1;
      heatmapData.forEach(function(h) {
        var level = (h.minutes || 0) === 0 ? 0 : Math.ceil((h.minutes || 0) / maxMin * 4);
        html += '<div class="heatmap-cell l' + level + '" title="' + h.date + ': ' + (h.minutes || 0) + '分钟"></div>';
      });
    } else {
      html += '<p style="color:var(--text-secondary);font-size:13px">本月暂无学习记录</p>';
    }
    html += '</div></div>';

    // --- Daily review input ---
    html += '<div class="card">';
    html += '<div class="card-header"><h3>每日复盘</h3></div>';
    html += '<div class="form-group"><label>今日总结</label><textarea id="review-text" rows="2" placeholder="今天完成了什么？有什么收获？遇到的困难？"></textarea></div>';
    html += '<div class="form-group"><label>心情</label><select id="review-mood">' +
      '<option value="great">太棒了</option><option value="good">不错</option><option value="neutral" selected>一般</option><option value="tired">有点累</option><option value="bad">不太好</option>' +
      '</select></div>';
    html += '<div class="form-group"><label>明日计划</label><input id="review-plan" placeholder="明天准备做什么？"></div>';
    html += '<button class="btn-primary-sm" id="submit-checkin">提交复盘</button>';
    html += '<p id="checkin-msg" style="margin-top:8px;font-size:12px"></p>';
    html += '<div style="margin-top:12px;border-top:2px solid #2563eb;padding:12px;background:#eff6ff;border-radius:8px;cursor:pointer" id="toggle-past-reviews">' +
      '<div style="display:flex;justify-content:space-between;align-items:center">' +
      '<span style="font-size:15px;font-weight:700;color:#2563eb">📋 查看历史复盘记录</span><span id="toggle-arrow" style="font-size:14px">▼ 展开</span></div>' +
      '<div id="past-reviews-list" style="max-height:400px;overflow-y:auto;margin-top:10px;display:none"></div></div>';
    html += '</div>';

    container.innerHTML = html;

    // --- Initialize weekly bar chart ---
    var weeklyCtx = document.getElementById('weekly-chart');
    if (weeklyCtx && weeklyReport && weeklyReport.daily_breakdown) {
      new Chart(weeklyCtx, {
        type: 'bar',
        data: {
          labels: weeklyReport.daily_breakdown.map(function(d) { return d.date ? d.date.slice(5) : ''; }),
          datasets: [{
            label: '学习分钟',
            data: weeklyReport.daily_breakdown.map(function(d) { return d.minutes || 0; }),
            backgroundColor: '#3b82f6',
            borderRadius: 4
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: { y: { beginAtZero: true, title: { display: true, text: '分钟' } } }
        }
      });
    }

    // --- Report tab switching ---
    var tabWeekly = document.getElementById('tab-weekly');
    var tabMonthly = document.getElementById('tab-monthly');
    var divWeekly = document.getElementById('report-weekly');
    var divMonthly = document.getElementById('report-monthly');
    var monthlyChartInstance = null;

    if (tabWeekly && tabMonthly) {
      tabWeekly.addEventListener('click', function() {
        tabWeekly.classList.add('active');
        tabMonthly.classList.remove('active');
        divWeekly.style.display = '';
        divMonthly.style.display = 'none';
      });
      tabMonthly.addEventListener('click', function() {
        tabMonthly.classList.add('active');
        tabWeekly.classList.remove('active');
        divMonthly.style.display = '';
        divWeekly.style.display = 'none';
        // Render monthly chart on first view
        if (!monthlyChartInstance) {
          var monthlyCtx = document.getElementById('monthly-chart');
          if (monthlyCtx && monthlyReport && monthlyReport.daily_breakdown) {
            monthlyChartInstance = new Chart(monthlyCtx, {
              type: 'bar',
              data: {
                labels: monthlyReport.daily_breakdown.map(function(d) { return d.date ? d.date.slice(5) : ''; }),
                datasets: [{
                  label: '学习分钟',
                  data: monthlyReport.daily_breakdown.map(function(d) { return d.minutes || 0; }),
                  backgroundColor: '#22c55e',
                  borderRadius: 4
                }]
              },
              options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: { y: { beginAtZero: true, title: { display: true, text: '分钟' } } }
              }
            });
          }
        }
      });
    }

    // --- Quick pomodoro ---
    var quickBtn = document.getElementById('quick-pomodoro');
    var quickMsg = document.getElementById('quick-pomodoro-msg');
    if (quickBtn) {
      quickBtn.addEventListener('click', function() {
        quickBtn.disabled = true;
        quickMsg.textContent = '番茄钟已开始...';
        window.API.post('/pomodoro/start', { subject_id: null, type: 'focus' })
          .then(function() {
            quickMsg.textContent = '番茄钟已启动! 25分钟专注时间。';
            setTimeout(function() { quickBtn.disabled = false; quickMsg.textContent = ''; }, 3000);
          })
          .catch(function(err) {
            quickMsg.textContent = '启动失败: ' + err.message;
            quickBtn.disabled = false;
          });
      });
    }

    // --- Task quick check-off ---
    document.querySelectorAll('.dash-task-check').forEach(function(cb) {
      cb.addEventListener('change', function() {
        var id = cb.dataset.taskId;
        var status = cb.checked ? 'done' : 'todo';
        window.API.patch('/tasks/' + id + '/status', { status: status }).catch(function(err) {
          cb.checked = !cb.checked;
          console.error('Task status update failed:', err);
        });
      });
    });

    // Remove from today
    document.querySelectorAll('.dash-remove-today').forEach(function(btn) {
      btn.addEventListener('click', function(e) {
        e.stopPropagation();
        var id = btn.dataset.id;
        window.API.patch('/tasks/' + id + '/remove-today').then(function() {
          // Reload dashboard
          window.App.navigate('dashboard');
        }).catch(function(err) { alert(err.message); });
      });
    });

    // --- Checkin submit ---
    var submitBtn = document.getElementById('submit-checkin');
    var msgEl = document.getElementById('checkin-msg');
    if (submitBtn) {
      submitBtn.addEventListener('click', function() {
        var reviewText = document.getElementById('review-text').value;
        var mood = document.getElementById('review-mood').value;
        var plan = document.getElementById('review-plan').value;
        window.API.post('/checkins', {
          review_text: reviewText,
          mood: mood,
          tomorrow_plan: plan
        }).then(function() {
          msgEl.style.color = 'var(--success)';
          msgEl.textContent = '复盘已保存!';
          document.getElementById('review-text').value = '';
          document.getElementById('review-plan').value = '';
        }).catch(function(err) {
          msgEl.style.color = 'var(--danger)';
          msgEl.textContent = err.message;
        });
      });

      // Toggle past reviews
      var toggleBtn = document.getElementById('toggle-past-reviews');
      var pastList = document.getElementById('past-reviews-list');
      var toggleArrow = document.getElementById('toggle-arrow');
      var reviewsLoaded = false;

      if (toggleBtn && pastList) {
        toggleBtn.addEventListener('click', function(e) {
          if (e.target.closest('#past-reviews-list')) return;
          if (pastList.style.display === 'none') {
            pastList.style.display = 'block';
            toggleArrow.textContent = '▲ 收起';
            if (!reviewsLoaded) {
              pastList.innerHTML = '<p style="color:var(--text-secondary);font-size:12px;padding:8px">加载中...</p>';
              // Load all review records (from 2020 to far future)
              window.API.get('/checkins?start=2020-01-01&end=2099-12-31').then(function(checkins) {
                reviewsLoaded = true;
                if (!checkins || checkins.length === 0) {
                  pastList.innerHTML = '<p style="color:var(--text-secondary);font-size:12px;padding:8px">暂无历史复盘记录。</p>';
                  return;
                }
                var moodLabels = { great: '😄', good: '😊', neutral: '😐', tired: '😫', bad: '😞' };
                // Group by date
                var grouped = {};
                checkins.forEach(function(c) {
                  var d = c.date || '未知';
                  if (!grouped[d]) grouped[d] = [];
                  grouped[d].push(c);
                });
                var dates = Object.keys(grouped).sort().reverse();
                var html = '';
                dates.forEach(function(date) {
                  var items = grouped[date];
                  var latest = items[0];
                  // Show latest as summary, rest expandable
                  html += '<div style="border-bottom:1px solid var(--border);padding:8px 0">' +
                    '<div style="display:flex;justify-content:space-between;align-items:center;cursor:pointer" class="date-toggle" data-date="' + date + '">' +
                    '<div style="flex:1">' +
                    '<strong>' + date + '</strong>' +
                    '<span style="margin-left:8px;font-size:11px">' + (moodLabels[latest.mood] || '😐') + ' · ' + (latest.total_minutes || 0) + '分钟</span>' +
                    (items.length > 1 ? '<span style="margin-left:4px;font-size:10px;color:var(--info)">(' + items.length + '条)</span>' : '') +
                    '</div>' +
                    '<span class="date-arrow" style="font-size:10px;color:var(--text-secondary)">▶</span></div>' +
                    '<div class="date-detail" data-date="' + date + '" style="display:none;margin-top:4px;padding-left:12px">';
                  items.forEach(function(c, idx) {
                    html += '<div style="padding:6px 8px;margin:4px 0;background:#f8fafc;border-radius:4px;font-size:12px" data-checkin-id="' + c.id + '">' +
                      '<div style="display:flex;justify-content:space-between;margin-bottom:2px">' +
                      '<span style="color:var(--text-secondary);font-size:10px">' + (c.checkin_time ? c.checkin_time.slice(11, 16) : '') + ' #' + (idx + 1) + '</span>' +
                      '<span>' +
                      '<button class="btn-sm edit-checkin" data-id="' + c.id + '" style="font-size:10px;padding:2px 6px">✏️</button>' +
                      '<button class="btn-sm delete-checkin" data-id="' + c.id + '" style="font-size:10px;padding:2px 6px;color:var(--danger)">🗑️</button>' +
                      '</span></div>' +
                      (c.review_text ? '<div style="color:var(--text-secondary);margin-bottom:2px">' + c.review_text + '</div>' : '') +
                      (c.tomorrow_plan ? '<div style="color:var(--info);font-size:11px">📅 明日: ' + c.tomorrow_plan + '</div>' : '') +
                      '</div>';
                  });
                  html += '</div></div>';
                });
                pastList.innerHTML = html;

                // Toggle date expand
                pastList.querySelectorAll('.date-toggle').forEach(function(toggle) {
                  toggle.addEventListener('click', function() {
                    var date = toggle.dataset.date;
                    var detail = pastList.querySelector('.date-detail[data-date="' + date + '"]');
                    var arrow = toggle.querySelector('.date-arrow');
                    if (detail.style.display === 'none') {
                      detail.style.display = 'block';
                      arrow.textContent = '▼';
                    } else {
                      detail.style.display = 'none';
                      arrow.textContent = '▶';
                    }
                  });
                });

                // Edit checkin
                pastList.querySelectorAll('.edit-checkin').forEach(function(btn) {
                  btn.addEventListener('click', function(e) {
                    e.stopPropagation();
                    var id = btn.dataset.id;
                    var newText = prompt('修改复盘内容（心情: great/good/neutral/tired/bad）:\n\n请输入新的复盘文本：');
                    if (newText !== null) {
                      window.API.put('/checkins/' + id, { review_text: newText }).then(function() {
                        // Collapse and re-expand to refresh
                        pastList.querySelector('.date-detail[style*="block"]') && (pastList.querySelector('.date-detail[style*="block"]').style.display = 'none');
                        pastList.querySelectorAll('.date-arrow').forEach(function(a) { a.textContent = '▶'; });
                        reviewsLoaded = false;
                        toggleBtn.click(); toggleBtn.click();
                      }).catch(function(err) { alert('编辑失败: ' + err.message); });
                    }
                  });
                });

                // Delete checkin
                pastList.querySelectorAll('.delete-checkin').forEach(function(btn) {
                  btn.addEventListener('click', function(e) {
                    e.stopPropagation();
                    var id = btn.dataset.id;
                    if (confirm('确定删除这条复盘记录？')) {
                      window.API.delete('/checkins/' + id).then(function() {
                        reviewsLoaded = false;
                        toggleBtn.click(); toggleBtn.click(); // Refresh list
                      }).catch(function(err) { alert('删除失败: ' + err.message); });
                    }
                  });
                });
              }).catch(function() {
                pastList.innerHTML = '<p style="color:var(--danger);font-size:12px">加载失败</p>';
              });
            }
          } else {
            pastList.style.display = 'none';
            toggleArrow.textContent = '▼ 展开';
          }
        });
      }
    }
  });
})();
