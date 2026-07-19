/**
 * Resources page: 学习资源 (Notes, Wrong Questions, Materials, Flashcards)
 */
(function() {
  window.App.registerPage('resources', async function(container) {
    var activeTab = 'notes';
    var subjectColors = { 1: 'politics', 2: 'english', 3: 'math', 4: 'statistics' };

    function renderTabs() {
      return '<div class="page-tabs">' +
        '<button class="page-tab ' + (activeTab === 'notes' ? 'active' : '') + '" data-tab="notes">笔记</button>' +
        '<button class="page-tab ' + (activeTab === 'wrong' ? 'active' : '') + '" data-tab="wrong">错题</button>' +
        '<button class="page-tab ' + (activeTab === 'materials' ? 'active' : '') + '" data-tab="materials">资料</button>' +
        '<button class="page-tab ' + (activeTab === 'flashcards' ? 'active' : '') + '" data-tab="flashcards">闪卡</button>' +
        '</div><div id="resources-tab-content"></div>';
    }

    var noteSelectedIds = [];

    async function renderNotes() {
      var notes;
      try {
        notes = await window.API.get('/notes?type=note');
      } catch (err) {
        document.getElementById('resources-tab-content').innerHTML = '<div class="card"><p style="color:var(--danger)">加载失败: ' + err.message + '</p></div>';
        return;
      }
      noteSelectedIds = [];
      var html = '<div class="card"><div class="card-header"><h3>笔记</h3><button class="btn-primary-sm" id="add-note">+ 添加笔记</button></div>';
      if (notes.length === 0) {
        html += '<p style="color:var(--text-secondary);font-size:13px">暂无笔记。</p>';
      } else {
        html += '<div class="batch-bar" id="note-batch-bar"><span>已选 <span class="selected-count" id="note-batch-count">0</span> 项</span>' +
          '<button class="btn-delete" id="note-batch-delete">批量删除</button>' +
          '<button class="btn-cancel" id="note-batch-cancel">取消选择</button></div>';
        html += '<div class="select-all-row"><input type="checkbox" class="batch-checkbox" id="note-select-all"> <label for="note-select-all" style="cursor:pointer">全选</label></div>';
        html += '<div style="margin-bottom:12px;display:flex;gap:8px">' +
          '<select id="notes-subject-filter" style="padding:4px 10px;border:1px solid var(--border);border-radius:var(--radius-sm);font-size:12px">' +
            '<option value="">全部科目</option>' +
            '<option value="1">政治</option><option value="2">英语</option><option value="3">数学</option><option value="4">统计</option>' +
          '</select>' +
          '<input id="notes-search" placeholder="搜索笔记..." style="padding:4px 10px;border:1px solid var(--border);border-radius:var(--radius-sm);font-size:12px;flex:1">' +
          '</div>';
        notes.forEach(function(n) {
          html += '<div style="padding:10px;border-bottom:1px solid var(--border)" data-subject="' + (n.subject_id || '') + '" data-title="' + (n.title || '') + '" class="note-row">' +
            '<div style="display:flex;align-items:center;gap:8px;margin-bottom:4px">' +
              '<input type="checkbox" class="batch-checkbox note-batch-sel" data-id="' + n.id + '">' +
              '<span class="subj-badge ' + (subjectColors[n.subject_id] || '') + '">' + (n.subject_name || '-') + '</span>' +
              '<strong>' + n.title + '</strong>' +
              '<span style="margin-left:auto;font-size:11px;color:var(--text-secondary)">' + (n.created_at ? n.created_at.slice(0, 10) : '') + '</span>' +
            '</div>' +
            '<div style="font-size:12px;color:var(--text-secondary);margin-left:24px">' + (n.tags ? '标签: ' + n.tags : '') + '</div>' +
            '<div style="margin-top:4px;margin-left:24px;display:flex;gap:6px">' +
              '<button class="btn-sm note-edit" data-id="' + n.id + '" data-title="' + (n.title || '') + '" data-content="' + (n.content || '') + '" data-subject="' + (n.subject_id || '') + '" data-tags="' + (n.tags || '') + '">编辑</button>' +
              '<button class="btn-sm note-delete" data-id="' + n.id + '" style="color:var(--danger)">删除</button>' +
            '</div>' +
          '</div>';
        });
      }
      html += '</div>';
      document.getElementById('resources-tab-content').innerHTML = html;

      // Batch handlers
      function updateNoteBatchBar() {
        var bar = document.getElementById('note-batch-bar');
        var countEl = document.getElementById('note-batch-count');
        if (!bar) return;
        bar.style.display = noteSelectedIds.length > 0 ? 'flex' : 'none';
        if (countEl) countEl.textContent = noteSelectedIds.length;
      }
      var selAll = document.getElementById('note-select-all');
      if (selAll) selAll.addEventListener('change', function() {
        document.querySelectorAll('.note-batch-sel').forEach(function(cb) { cb.checked = selAll.checked; });
        noteSelectedIds = selAll.checked ? notes.map(function(n) { return n.id; }) : [];
        updateNoteBatchBar();
      });
      document.querySelectorAll('.note-batch-sel').forEach(function(cb) {
        cb.addEventListener('change', function() {
          var id = parseInt(cb.dataset.id);
          if (cb.checked) { if (noteSelectedIds.indexOf(id) < 0) noteSelectedIds.push(id); }
          else { noteSelectedIds = noteSelectedIds.filter(function(x) { return x !== id; }); }
          updateNoteBatchBar();
        });
      });
      var bd = document.getElementById('note-batch-delete');
      if (bd) bd.addEventListener('click', function() {
        if (!confirm('确定删除选中的 ' + noteSelectedIds.length + ' 条笔记？')) return;
        window.API.post('/notes/batch-delete', { ids: noteSelectedIds.slice() }).then(function() { renderNotes(); })
          .catch(function(err) { alert('删除失败: ' + err.message); });
      });
      var bc = document.getElementById('note-batch-cancel');
      if (bc) bc.addEventListener('click', function() {
        document.querySelectorAll('.note-batch-sel').forEach(function(cb) { cb.checked = false; });
        if (selAll) selAll.checked = false;
        noteSelectedIds = [];
        updateNoteBatchBar();
      });

      // Subject filter
      var subjectFilter = document.getElementById('notes-subject-filter');
      var searchInput = document.getElementById('notes-search');
      if (subjectFilter) {
        subjectFilter.addEventListener('change', filterNotes);
      }
      if (searchInput) {
        searchInput.addEventListener('input', filterNotes);
      }
      function filterNotes() {
        var subj = subjectFilter ? subjectFilter.value : '';
        var search = searchInput ? searchInput.value.toLowerCase() : '';
        document.querySelectorAll('.note-row').forEach(function(row) {
          var matchSubj = !subj || row.dataset.subject === subj;
          var matchSearch = !search || (row.dataset.title || '').toLowerCase().indexOf(search) >= 0;
          row.style.display = matchSubj && matchSearch ? '' : 'none';
        });
      }

      // Add note
      document.getElementById('add-note').addEventListener('click', function() {
        showNoteModal(null, '', '', '', '');
      });

      // Edit note
      document.querySelectorAll('.note-edit').forEach(function(btn) {
        btn.addEventListener('click', function() {
          showNoteModal(btn.dataset.id, btn.dataset.title, btn.dataset.content, btn.dataset.subject, btn.dataset.tags);
        });
      });

      // Delete note
      document.querySelectorAll('.note-delete').forEach(function(btn) {
        btn.addEventListener('click', async function() {
          if (confirm('确认删除?')) {
            try { await window.API.delete('/notes/' + btn.dataset.id); } catch (err) { alert(err.message); return; }
            renderNotes();
          }
        });
      });

      function showNoteModal(id, title, content, subject, tags) {
        var isEdit = !!id;
        var overlay = document.createElement('div');
        overlay.className = 'modal-overlay';
        overlay.innerHTML = '<div class="modal" style="min-width:650px;max-width:800px">' +
          '<h3>' + (isEdit ? '编辑笔记' : '添加笔记') + '</h3>' +
          '<div class="form-group"><label>标题</label><input id="note-modal-title" value="' + (title || '') + '"></div>' +
          '<div style="display:flex;gap:8px">' +
            '<div class="form-group" style="flex:1"><label>科目</label><select id="note-modal-subject"><option value="">不限</option><option value="1"' + (subject == '1' ? ' selected' : '') + '>政治</option><option value="2"' + (subject == '2' ? ' selected' : '') + '>英语</option><option value="3"' + (subject == '3' ? ' selected' : '') + '>数学</option><option value="4"' + (subject == '4' ? ' selected' : '') + '>统计</option></select></div>' +
            '<div class="form-group" style="flex:1"><label>标签 (逗号分隔)</label><input id="note-modal-tags" value="' + (tags || '') + '" placeholder="e.g. 重点, 难点"></div>' +
          '</div>' +
          '<div class="form-group"><label>内容 (支持 Markdown，可直接粘贴图片)</label><textarea id="note-modal-content" style="display:none">' + (content || '') + '</textarea></div>' +
          '<div class="modal-actions" style="margin-top:12px">' +
            '<button class="btn" id="note-modal-cancel">关闭</button>' +
            '<button class="btn-primary-sm" id="note-modal-save">' + (isEdit ? '更新' : '保存') + '</button>' +
          '</div>' +
        '</div>';
        document.body.appendChild(overlay);

        // Init EasyMDE with image upload
        var easyMDE = new EasyMDE({
          element: overlay.querySelector('#note-modal-content'),
          spellChecker: false,
          placeholder: '支持 Markdown 语法，可直接粘贴图片...',
          uploadImage: true,
          imageUploadEndpoint: '/api/upload/image',
          imageUploadFunction: function(file, onSuccess, onError) {
            var formData = new FormData();
            formData.append('image', file);
            fetch('/api/upload/image', {
              method: 'POST',
              headers: { 'Authorization': 'Bearer ' + localStorage.getItem('kaoyan_token') },
              body: formData
            }).then(function(resp) {
              if (!resp.ok) throw new Error('Upload failed');
              return resp.json();
            }).then(function(data) {
              onSuccess(data.url);
            }).catch(function(err) {
              onError(err.message);
            });
          },
          imageMaxSize: 1024 * 1024 * 10, // 10MB
          imageAccept: 'image/png, image/jpeg, image/gif, image/webp'
        });

        overlay.querySelector('#note-modal-cancel').addEventListener('click', function() { overlay.remove(); });
        overlay.addEventListener('click', function(e) { if (e.target === overlay) overlay.remove(); });

        overlay.querySelector('#note-modal-save').addEventListener('click', async function() {
          var data = {
            type: 'note',
            title: overlay.querySelector('#note-modal-title').value.trim(),
            content: easyMDE.value(),
            subject_id: parseInt(overlay.querySelector('#note-modal-subject').value) || null,
            tags: overlay.querySelector('#note-modal-tags').value.trim() || null
          };
          if (!data.title) { alert('请输入标题'); return; }
          try {
            if (isEdit) {
              await window.API.put('/notes/' + id, data);
            } else {
              await window.API.post('/notes', data);
            }
          } catch (err) { alert(err.message); return; }
          overlay.remove();
          renderNotes();
        });
      }
    }

    async function renderWrong() {
      var items;
      try {
        items = await window.API.get('/notes?type=wrong_question');
      } catch (err) {
        document.getElementById('resources-tab-content').innerHTML = '<div class="card"><p style="color:var(--danger)">加载失败: ' + err.message + '</p></div>';
        return;
      }
      var html = '<div class="card"><div class="card-header"><h3>错题</h3><button class="btn-primary-sm" id="add-wrong">+ 添加错题</button></div>';
      if (items.length === 0) {
        html += '<p style="color:var(--text-secondary);font-size:13px">暂无错题。</p>';
      } else {
        html += '<div class="batch-bar" id="wrong-batch-bar"><span>已选 <span class="selected-count" id="wrong-batch-count">0</span> 项</span>' +
          '<button class="btn-delete" id="wrong-batch-delete">批量删除</button>' +
          '<button class="btn-cancel" id="wrong-batch-cancel">取消选择</button></div>';
        html += '<div class="select-all-row"><input type="checkbox" class="batch-checkbox" id="wrong-select-all"> <label for="wrong-select-all" style="cursor:pointer">全选</label></div>';
        items.forEach(function(item) {
          html += '<div style="padding:10px;border-bottom:1px solid var(--border)">' +
            '<div style="display:flex;align-items:center;gap:8px">' +
              '<input type="checkbox" class="batch-checkbox wrong-batch-sel" data-id="' + item.id + '">' +
              '<span class="subj-badge ' + (subjectColors[item.subject_id] || '') + '">' + (item.subject_name || '-') + '</span>' +
              '<strong>' + item.title + '</strong>' +
              '<span style="font-size:11px;color:var(--danger)">错' + (item.wrong_count || 0) + '次</span>' +
              '<span style="font-size:11px;' + (item.mastered ? 'color:var(--success)' : 'color:var(--text-secondary)') + ';margin-left:auto">' + (item.mastered ? '已掌握' : '未掌握') + '</span>' +
            '</div>' +
            (item.last_reviewed_at ? '<div style="font-size:11px;color:var(--text-secondary);margin-top:2px;margin-left:24px">最近复习: ' + item.last_reviewed_at.slice(0, 10) + '</div>' : '') +
            '<div style="margin-top:4px;margin-left:24px;display:flex;gap:6px">' +
              '<button class="btn-sm wrong-edit" data-id="' + item.id + '" data-title="' + (item.title || '') + '" data-content="' + (item.content || '') + '" data-subject="' + (item.subject_id || '') + '" data-tags="' + (item.tags || '') + '">编辑</button>' +
              '<button class="btn-sm wrong-toggle-mastered" data-id="' + item.id + '" data-mastered="' + (item.mastered ? '1' : '0') + '" style="color:' + (item.mastered ? 'var(--warning)' : 'var(--success)') + '">' + (item.mastered ? '标记未掌握' : '标记已掌握') + '</button>' +
              '<button class="btn-sm wrong-incr" data-id="' + item.id + '" style="color:var(--danger)">+1错</button>' +
              '<button class="btn-sm wrong-delete" data-id="' + item.id + '" style="color:var(--danger)">删除</button>' +
            '</div>' +
          '</div>';
        });
      }
      html += '</div>';
      document.getElementById('resources-tab-content').innerHTML = html;

      // Batch handlers
      var wSelected = [];
      function updateWrongBatch() {
        document.getElementById('wrong-batch-bar').style.display = wSelected.length > 0 ? 'flex' : 'none';
        document.getElementById('wrong-batch-count').textContent = wSelected.length;
      }
      var wsa = document.getElementById('wrong-select-all');
      if (wsa) wsa.addEventListener('change', function() {
        document.querySelectorAll('.wrong-batch-sel').forEach(function(cb) { cb.checked = wsa.checked; });
        wSelected = wsa.checked ? items.map(function(it) { return it.id; }) : [];
        updateWrongBatch();
      });
      document.querySelectorAll('.wrong-batch-sel').forEach(function(cb) {
        cb.addEventListener('change', function() {
          var id = parseInt(cb.dataset.id);
          if (cb.checked) { if (wSelected.indexOf(id) < 0) wSelected.push(id); }
          else { wSelected = wSelected.filter(function(x) { return x !== id; }); }
          updateWrongBatch();
        });
      });
      var wbd = document.getElementById('wrong-batch-delete');
      if (wbd) wbd.addEventListener('click', function() {
        if (!confirm('确定删除选中的 ' + wSelected.length + ' 条错题？')) return;
        window.API.post('/notes/batch-delete', { ids: wSelected.slice() }).then(function() { renderWrong(); })
          .catch(function(err) { alert('删除失败: ' + err.message); });
      });
      var wbc = document.getElementById('wrong-batch-cancel');
      if (wbc) wbc.addEventListener('click', function() {
        document.querySelectorAll('.wrong-batch-sel').forEach(function(cb) { cb.checked = false; });
        if (wsa) wsa.checked = false;
        wSelected = [];
        updateWrongBatch();
      });

      document.getElementById('add-wrong').addEventListener('click', function() {
        showWrongModal();
      });

      document.querySelectorAll('.wrong-toggle-mastered').forEach(function(btn) {
        btn.addEventListener('click', async function() {
          var newMastered = btn.dataset.mastered === '0';
          try {
            await window.API.patch('/notes/' + btn.dataset.id + '/wrong', { mastered: newMastered });
          } catch (err) { alert(err.message); return; }
          renderWrong();
        });
      });

      document.querySelectorAll('.wrong-edit').forEach(function(btn) {
        btn.addEventListener('click', function() {
          showWrongModal(btn.dataset.id, btn.dataset.title, btn.dataset.content, btn.dataset.subject, btn.dataset.tags);
        });
      });

      document.querySelectorAll('.wrong-incr').forEach(function(btn) {
        btn.addEventListener('click', async function() {
          try { await window.API.patch('/notes/' + btn.dataset.id + '/wrong'); } catch (err) { alert(err.message); return; }
          renderWrong();
        });
      });

      document.querySelectorAll('.wrong-delete').forEach(function(btn) {
        btn.addEventListener('click', async function() {
          if (confirm('确认删除?')) {
            try { await window.API.delete('/notes/' + btn.dataset.id); } catch (err) { alert(err.message); return; }
            renderWrong();
          }
        });
      });

      function showWrongModal(id, title, content, subject, tags) {
        var isEdit = !!id;
        var overlay = document.createElement('div');
        overlay.className = 'modal-overlay';
        overlay.innerHTML = '<div class="modal">' +
          '<h3>' + (isEdit ? '编辑错题' : '添加错题') + '</h3>' +
          '<div class="form-group"><label>错题标题 / 题目来源</label><input id="wrong-modal-title" value="' + (title || '') + '" placeholder="e.g. 2024年真题选择题第5题"></div>' +
          '<div class="form-group"><label>科目</label><select id="wrong-modal-subject"><option value="">不限</option><option value="1"' + (subject == '1' ? ' selected' : '') + '>政治</option><option value="2"' + (subject == '2' ? ' selected' : '') + '>英语</option><option value="3"' + (subject == '3' ? ' selected' : '') + '>数学</option><option value="4"' + (subject == '4' ? ' selected' : '') + '>统计</option></select></div>' +
          '<div class="form-group"><label>错误原因 / 解析</label><textarea id="wrong-modal-content" rows="4">' + (content || '') + '</textarea></div>' +
          '<div class="form-group"><label>标签</label><input id="wrong-modal-tags" value="' + (tags || '') + '" placeholder="e.g. 粗心, 知识点缺失"></div>' +
          '<div class="modal-actions">' +
            '<button class="btn" id="wrong-modal-cancel">取消</button>' +
            '<button class="btn-primary-sm" id="wrong-modal-save">' + (isEdit ? '更新' : '保存') + '</button>' +
          '</div>' +
        '</div>';
        document.body.appendChild(overlay);

        overlay.querySelector('#wrong-modal-cancel').addEventListener('click', function() { overlay.remove(); });
        overlay.addEventListener('click', function(e) { if (e.target === overlay) overlay.remove(); });

        overlay.querySelector('#wrong-modal-save').addEventListener('click', async function() {
          var titleVal = overlay.querySelector('#wrong-modal-title').value.trim();
          if (!titleVal) { alert('请输入标题'); return; }
          var data = {
            title: titleVal,
            content: overlay.querySelector('#wrong-modal-content').value,
            subject_id: parseInt(overlay.querySelector('#wrong-modal-subject').value) || null,
            tags: overlay.querySelector('#wrong-modal-tags').value.trim() || null
          };
          try {
            if (isEdit) {
              await window.API.put('/notes/' + id, data);
            } else {
              data.type = 'wrong_question';
              await window.API.post('/notes', data);
            }
          } catch (err) { alert(err.message); return; }
          overlay.remove();
          renderWrong();
        });
      }
    }

    async function renderMaterials() {
      var mats;
      try {
        mats = await window.API.get('/materials');
      } catch (err) {
        document.getElementById('resources-tab-content').innerHTML = '<div class="card"><p style="color:var(--danger)">加载失败: ' + err.message + '</p></div>';
        return;
      }

      var typeIcons = { pdf: '📄', link: '🔗', book: '📖', other: '📁' };
      var html = '<div class="card"><div class="card-header"><h3>学习资料</h3>' +
        '<button class="btn-primary-sm" id="add-material">+ 添加资料</button>' +
        '<button class="btn-primary-sm" id="import-file" style="background:#16a34a;margin-left:4px">📤 导入文件</button></div>';
      if (mats.length === 0) {
        html += '<p style="color:var(--text-secondary);font-size:13px">暂无资料，点击"导入文件"上传PDF/文档，或"添加资料"记录书籍/链接。</p>';
      } else {
        mats.forEach(function(m) {
          var fileInfo = '';
          if (m.file_path) {
            var fileName = m.file_path.split('/').pop().replace(/^[a-f0-9]+/, '');
            fileInfo = '<span style="font-size:11px;color:var(--info);cursor:pointer" onclick="window.open(\'' + m.file_path + '\')" title="打开文件">📎 已上传</span>';
          }
          html += '<div style="padding:10px;border-bottom:1px solid var(--border)">' +
            '<div style="display:flex;align-items:center;gap:8px">' +
              '<input type="checkbox" class="batch-checkbox mat-batch-sel" data-id="' + m.id + '">' +
              '<span style="font-size:18px">' + (typeIcons[m.type] || '📁') + '</span>' +
              '<span class="subj-badge ' + (subjectColors[m.subject_id] || '') + '">' + (m.subject_name || '-') + '</span>' +
              '<strong>' + m.title + '</strong>' +
              '<span style="font-size:11px;color:var(--text-secondary)">' + (m.type || '') + '</span>' +
              fileInfo +
              '<span style="margin-left:auto;font-size:12px;color:var(--text-secondary)">' + (m.reading_progress || 0) + '%</span>' +
            '</div>' +
            '<div style="margin-top:4px;display:flex;align-items:center;gap:8px">' +
              '<input type="range" min="0" max="100" value="' + (m.reading_progress || 0) + '" class="material-progress" data-id="' + m.id + '" style="flex:1;max-width:200px">' +
              '<span class="material-progress-val" style="font-size:11px;color:var(--text-secondary)">' + (m.reading_progress || 0) + '%</span>' +
              (m.source_url ? '<a href="' + m.source_url + '" target="_blank" style="font-size:11px;color:var(--info)">🔗 打开链接</a>' : '') +
            '</div>' +
            '<div style="margin-top:4px">' +
              '<button class="btn-sm material-delete" data-id="' + m.id + '" style="color:var(--danger)">删除</button>' +
            '</div>' +
          '</div>';
        });
      }
      html += '</div>';
      document.getElementById('resources-tab-content').innerHTML = html;

      // Add material
      document.getElementById('add-material').addEventListener('click', function() {
        showMaterialModal();
      });

      // Import file button
      var importBtn = document.getElementById('import-file');
      if (importBtn) {
        importBtn.addEventListener('click', function() { showImportDialog(); });
      }

      // Progress slider
      document.querySelectorAll('.material-progress').forEach(function(slider) {
        slider.addEventListener('input', function() {
          var valEl = slider.parentElement.querySelector('.material-progress-val');
          if (valEl) valEl.textContent = slider.value + '%';
        });
        slider.addEventListener('change', async function() {
          try {
            await window.API.patch('/materials/' + slider.dataset.id + '/progress', { reading_progress: parseInt(slider.value) });
          } catch (err) { alert(err.message); }
        });
      });

      // Delete material
      document.querySelectorAll('.material-delete').forEach(function(btn) {
        btn.addEventListener('click', async function() {
          if (confirm('确认删除?')) {
            try { await window.API.delete('/materials/' + btn.dataset.id); } catch (err) { alert(err.message); return; }
            renderMaterials();
          }
        });
      });

      function showImportDialog() {
        var overlay = document.createElement('div');
        overlay.className = 'modal-overlay';
        overlay.innerHTML = '<div class="modal" style="max-width:480px">' +
          '<h3>导入文件</h3>' +
          '<p style="font-size:13px;color:var(--text-secondary);margin-bottom:12px">支持PDF、Word、PPT、图片、文本文件等</p>' +
          '<div id="import-drop-zone" style="border:2px dashed #bfdbfe;border-radius:12px;padding:40px;text-align:center;cursor:pointer;background:#f8fafc;margin-bottom:12px">' +
          '<div style="font-size:36px;margin-bottom:8px">📤</div>' +
          '<div style="font-size:14px;font-weight:600;margin-bottom:4px">点击选择文件，或拖拽到此处</div>' +
          '<div style="font-size:11px;color:var(--text-secondary)">单个文件最大50MB</div>' +
          '<input type="file" id="import-file-input" multiple style="display:none" accept=".pdf,.doc,.docx,.ppt,.pptx,.xls,.xlsx,.txt,.md,.png,.jpg,.jpeg">' +
          '</div>' +
          '<div id="import-file-list" style="max-height:150px;overflow-y:auto;font-size:12px"></div>' +
          '<div class="form-group"><label>标签/科目</label><select id="import-subject"><option value="">自动识别</option><option value="1">政治</option><option value="2">英语</option><option value="3">数学</option><option value="4">统计</option></select></div>' +
          '<div class="modal-actions">' +
          '<button class="btn" id="import-cancel">取消</button>' +
          '<button class="btn-primary-sm" id="import-start" disabled>导入</button>' +
          '</div></div>';
        document.body.appendChild(overlay);

        var selectedFiles = [];
        var dropZone = overlay.querySelector('#import-drop-zone');
        var fileInput = overlay.querySelector('#import-file-input');

        dropZone.addEventListener('click', function() { fileInput.click(); });
        dropZone.addEventListener('dragover', function(e) { e.preventDefault(); dropZone.style.borderColor = '#2563eb'; dropZone.style.background = '#eff6ff'; });
        dropZone.addEventListener('dragleave', function() { dropZone.style.borderColor = '#bfdbfe'; dropZone.style.background = '#f8fafc'; });
        dropZone.addEventListener('drop', function(e) {
          e.preventDefault();
          dropZone.style.borderColor = '#bfdbfe'; dropZone.style.background = '#f8fafc';
          handleFiles(e.dataTransfer.files);
        });
        fileInput.addEventListener('change', function() { handleFiles(fileInput.files); });

        function handleFiles(files) {
          selectedFiles = Array.from(files);
          var listEl = overlay.querySelector('#import-file-list');
          listEl.innerHTML = selectedFiles.map(function(f, i) {
            return '<div style="padding:4px 0;display:flex;align-items:center;gap:8px">' +
              '<span>' + (i + 1) + '.</span><span style="flex:1">' + f.name + '</span>' +
              '<span style="color:var(--text-secondary);font-size:11px">' + (f.size / 1024).toFixed(1) + ' KB</span></div>';
          }).join('');
          overlay.querySelector('#import-start').disabled = selectedFiles.length === 0;
        }

        overlay.querySelector('#import-cancel').addEventListener('click', function() { overlay.remove(); });
        overlay.addEventListener('click', function(e) { if (e.target === overlay) overlay.remove(); });

        overlay.querySelector('#import-start').addEventListener('click', async function() {
          var subjId = overlay.querySelector('#import-subject').value;
          var btn = overlay.querySelector('#import-start');
          btn.textContent = '导入中...'; btn.disabled = true;
          var success = 0;
          for (var i = 0; i < selectedFiles.length; i++) {
            var f = selectedFiles[i];
            var fd = new FormData();
            fd.append('title', f.name);
            fd.append('type', getFileType(f.name));
            if (subjId) fd.append('subject_id', subjId);
            fd.append('file', f);
            try {
              await fetch('/api/materials/upload', {
                method: 'POST',
                headers: { 'Authorization': 'Bearer ' + localStorage.getItem('kaoyan_token') },
                body: fd
              }).then(function(r) { if (!r.ok) throw new Error('Failed'); return r.json(); });
              success++;
            } catch (err) { console.error('Upload failed:', f.name, err); }
          }
          overlay.remove();
          if (success > 0) renderMaterials();
          else alert('导入失败，请重试');
        });

        function getFileType(name) {
          var ext = name.split('.').pop().toLowerCase();
          if (ext === 'pdf') return 'pdf';
          if (['doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx'].indexOf(ext) >= 0) return 'other';
          if (['txt', 'md'].indexOf(ext) >= 0) return 'other';
          if (['png', 'jpg', 'jpeg', 'gif'].indexOf(ext) >= 0) return 'other';
          return 'other';
        }
      }

      function showMaterialModal() {
        var overlay = document.createElement('div');
        overlay.className = 'modal-overlay';
        overlay.innerHTML = '<div class="modal">' +
          '<h3>添加学习资料</h3>' +
          '<div class="form-group"><label>资料标题</label><input id="material-modal-title" placeholder="e.g. 统计学教材"></div>' +
          '<div class="form-group"><label>类型</label><select id="material-modal-type"><option value="book">书本</option><option value="pdf">PDF</option><option value="link">链接</option><option value="other">其他</option></select></div>' +
          '<div class="form-group"><label>科目</label><select id="material-modal-subject"><option value="">不限</option><option value="1">政治</option><option value="2">英语</option><option value="3">数学</option><option value="4">统计</option></select></div>' +
          '<div class="form-group"><label>上传文件 (可选)</label><input type="file" id="material-modal-file"></div>' +
          '<div class="modal-actions">' +
            '<button class="btn" id="material-modal-cancel">取消</button>' +
            '<button class="btn-primary-sm" id="material-modal-save">保存</button>' +
          '</div>' +
        '</div>';
        document.body.appendChild(overlay);

        overlay.querySelector('#material-modal-cancel').addEventListener('click', function() { overlay.remove(); });
        overlay.addEventListener('click', function(e) { if (e.target === overlay) overlay.remove(); });

        overlay.querySelector('#material-modal-save').addEventListener('click', async function() {
          var titleVal = overlay.querySelector('#material-modal-title').value.trim();
          if (!titleVal) { alert('请输入标题'); return; }
          var fileInput = overlay.querySelector('#material-modal-file');
          try {
            if (fileInput && fileInput.files && fileInput.files.length > 0) {
              var formData = new FormData();
              formData.append('title', titleVal);
              formData.append('type', overlay.querySelector('#material-modal-type').value);
              formData.append('subject_id', overlay.querySelector('#material-modal-subject').value);
              formData.append('file', fileInput.files[0]);
              await fetch('/api/materials/upload', {
                method: 'POST',
                headers: { 'Authorization': 'Bearer ' + localStorage.getItem('kaoyan_token') },
                body: formData
              }).then(function(r) {
                if (!r.ok) return r.json().then(function(e) { throw new Error(e.detail || 'Upload failed'); });
                return r.json();
              });
            } else {
              await window.API.post('/materials', {
                title: titleVal,
                type: overlay.querySelector('#material-modal-type').value,
                subject_id: parseInt(overlay.querySelector('#material-modal-subject').value) || null
              });
            }
          } catch (err) { alert(err.message); return; }
          overlay.remove();
          renderMaterials();
        });
      }
    }

    async function renderFlashcards() {
      var cards;
      try {
        cards = await window.API.get('/flashcards?due=true');
      } catch (err) {
        document.getElementById('resources-tab-content').innerHTML = '<div class="card"><p style="color:var(--danger)">加载失败: ' + err.message + '</p></div>';
        return;
      }
      var currentCardIndex = 0;
      var html = '<div class="card"><div class="card-header"><h3>闪卡复习</h3><button class="btn-primary-sm" id="add-card">+ 添加闪卡</button></div>';

      if (cards.length === 0) {
        html += '<p style="color:var(--text-secondary);font-size:13px">暂无闪卡，点击右上角添加。</p>';
      } else {
        // Current flashcard for review
        html += '<div id="flashcard-review-area">' +
          '<div class="flashcard-container" id="flashcard-container">' +
            '<div class="flashcard" id="flashcard">' +
              '<div class="flashcard-front" id="flashcard-front">' + (cards[0].front_text || '') + '</div>' +
              '<div class="flashcard-back" id="flashcard-back">' + (cards[0].back_text || '') + '</div>' +
            '</div>' +
          '</div>' +
          '<div style="text-align:center;margin-top:12px;font-size:12px;color:var(--text-secondary)">点击卡片翻转 | 第 <span id="card-index-display">1</span> / ' + cards.length + ' 张</div>' +
          '<div style="display:flex;gap:8px;justify-content:center;margin-top:12px">' +
            '<button class="btn-sm card-review" data-id="' + cards[0].id + '" data-feedback="forgot" style="color:var(--danger)">忘了 (1天)</button>' +
            '<button class="btn-sm card-review" data-id="' + cards[0].id + '" data-feedback="hard" style="color:var(--warning)">困难 (保持)</button>' +
            '<button class="btn-sm card-review" data-id="' + cards[0].id + '" data-feedback="good" style="color:var(--success)">掌握 (升级)</button>' +
          '</div>' +
        '</div>';
      }

      // Flashcard list
      html += '<div style="margin-top:16px"><strong>闪卡列表</strong></div>';
      html += '<div class="batch-bar" id="card-batch-bar"><span>已选 <span class="selected-count" id="card-batch-count">0</span> 项</span>' +
        '<button class="btn-delete" id="card-batch-delete">批量删除</button>' +
        '<button class="btn-cancel" id="card-batch-cancel">取消选择</button></div>';
      html += '<div class="select-all-row"><input type="checkbox" class="batch-checkbox" id="card-select-all"> <label for="card-select-all" style="cursor:pointer">全选</label></div>';
      html += '<div id="card-list" style="max-height:300px;overflow-y:auto">';
      if (cards.length === 0) {
        html += '<p style="color:var(--text-secondary);font-size:13px">暂无闪卡。</p>';
      } else {
        var fcSelectedIds = [];
        var grouped = {};
        cards.forEach(function(c) {
          var key = c.tags || c.subject_name || '未分类';
          if (!grouped[key]) grouped[key] = [];
          grouped[key].push(c);
        });
        Object.keys(grouped).forEach(function(group) {
          html += '<div style="padding:4px 0;font-size:11px;font-weight:600;color:var(--text-secondary)">' + group + '</div>';
          grouped[group].forEach(function(c) {
            html += '<div style="padding:6px 0;font-size:12px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid var(--border)">' +
              '<input type="checkbox" class="batch-checkbox card-batch-sel" data-id="' + c.id + '">' +
              '<span style="flex:1">' + c.front_text + '</span>' +
              '<span style="color:var(--text-secondary);margin:0 8px">复习' + (c.review_count || 0) + '次 | ' + (c.next_review_date ? c.next_review_date.slice(0, 10) : '-') + '</span>' +
              '<button class="btn-sm card-edit" data-id="' + c.id + '" data-front="' + (c.front_text || '') + '" data-back="' + (c.back_text || '') + '" data-subject="' + (c.subject_id || '') + '" data-tags="' + (c.tags || '') + '">编辑</button>' +
              '<button class="btn-sm card-delete" data-id="' + c.id + '" style="color:var(--danger)">删除</button>' +
            '</div>';
          });
        });
      }
      html += '</div>';
      html += '</div>';

      document.getElementById('resources-tab-content').innerHTML = html;

      // Store cards for review navigation
      var allReviewCards = cards;

      // Flashcard flip
      var cardEl = document.getElementById('flashcard');
      if (cardEl) {
        cardEl.addEventListener('click', function() { cardEl.classList.toggle('flipped'); });
      }

      // Add card
      document.getElementById('add-card').addEventListener('click', function() {
        showCardModal();
      });

      // Review buttons
      document.querySelectorAll('.card-review').forEach(function(btn) {
        btn.addEventListener('click', async function() {
          try {
            await window.API.post('/flashcards/' + btn.dataset.id + '/review', { feedback: btn.dataset.feedback });
          } catch (err) { alert(err.message); return; }
          // Move to next card or reload
          currentCardIndex++;
          if (currentCardIndex < allReviewCards.length) {
            var nextCard = allReviewCards[currentCardIndex];
            document.getElementById('flashcard-front').textContent = nextCard.front_text || '';
            document.getElementById('flashcard-back').textContent = nextCard.back_text || '';
            if (cardEl && cardEl.classList.contains('flipped')) cardEl.classList.remove('flipped');
            document.getElementById('card-index-display').textContent = currentCardIndex + 1;
            document.querySelectorAll('.card-review').forEach(function(b) { b.dataset.id = nextCard.id; });
          } else {
            renderFlashcards();
          }
        });
      });

      // Batch flashcard handlers
      var cardSelAll = document.getElementById('card-select-all');
      var cardSelectedIds = [];
      if (cardSelAll) cardSelAll.addEventListener('change', function() {
        document.querySelectorAll('.card-batch-sel').forEach(function(cb) { cb.checked = cardSelAll.checked; });
        cardSelectedIds = cardSelAll.checked ? cards.map(function(c) { return c.id; }) : [];
        document.getElementById('card-batch-bar').style.display = cardSelectedIds.length > 0 ? 'flex' : 'none';
        document.getElementById('card-batch-count').textContent = cardSelectedIds.length;
      });
      document.querySelectorAll('.card-batch-sel').forEach(function(cb) {
        cb.addEventListener('change', function() {
          var id = parseInt(cb.dataset.id);
          if (cb.checked) { if (cardSelectedIds.indexOf(id) < 0) cardSelectedIds.push(id); }
          else { cardSelectedIds = cardSelectedIds.filter(function(x) { return x !== id; }); }
          document.getElementById('card-batch-bar').style.display = cardSelectedIds.length > 0 ? 'flex' : 'none';
          document.getElementById('card-batch-count').textContent = cardSelectedIds.length;
        });
      });
      var cbd = document.getElementById('card-batch-delete');
      if (cbd) cbd.addEventListener('click', function() {
        if (!confirm('确定删除选中的 ' + cardSelectedIds.length + ' 张闪卡？')) return;
        window.API.post('/flashcards/batch-delete', { ids: cardSelectedIds.slice() }).then(function() { renderFlashcards(); })
          .catch(function(err) { alert('删除失败: ' + err.message); });
      });
      var cbc = document.getElementById('card-batch-cancel');
      if (cbc) cbc.addEventListener('click', function() {
        document.querySelectorAll('.card-batch-sel').forEach(function(cb) { cb.checked = false; });
        if (cardSelAll) cardSelAll.checked = false;
        cardSelectedIds = [];
        document.getElementById('card-batch-bar').style.display = 'none';
      });

      // Delete card
      document.querySelectorAll('.card-edit').forEach(function(btn) {
        btn.addEventListener('click', function() {
          showCardModal(btn.dataset.id, btn.dataset.front, btn.dataset.back, btn.dataset.subject, btn.dataset.tags);
        });
      });

      document.querySelectorAll('.card-delete').forEach(function(btn) {
        btn.addEventListener('click', async function() {
          if (confirm('确认删除?')) {
            try { await window.API.delete('/flashcards/' + btn.dataset.id); } catch (err) { alert(err.message); return; }
            renderFlashcards();
          }
        });
      });

      function showCardModal(id, front, back, subject, tags) {
        var isEdit = !!id;
        var overlay = document.createElement('div');
        overlay.className = 'modal-overlay';
        overlay.innerHTML = '<div class="modal">' +
          '<h3>' + (isEdit ? '编辑闪卡' : '添加闪卡') + '</h3>' +
          '<div class="form-group"><label>正面 (问题)</label><input id="card-modal-front" value="' + (front || '') + '" placeholder="e.g. 什么是置信区间?"></div>' +
          '<div class="form-group"><label>反面 (答案)</label><textarea id="card-modal-back" rows="3" placeholder="e.g. 在给定置信水平下，总体参数可能落入的区间范围。">' + (back || '') + '</textarea></div>' +
          '<div style="display:flex;gap:8px">' +
            '<div class="form-group" style="flex:1"><label>科目</label><select id="card-modal-subject"><option value="">不限</option><option value="1"' + (subject == '1' ? ' selected' : '') + '>政治</option><option value="2"' + (subject == '2' ? ' selected' : '') + '>英语</option><option value="3"' + (subject == '3' ? ' selected' : '') + '>数学</option><option value="4"' + (subject == '4' ? ' selected' : '') + '>统计</option></select></div>' +
            '<div class="form-group" style="flex:1"><label>标签 (逗号分隔)</label><input id="card-modal-tags" value="' + (tags || '') + '" placeholder="e.g. 统计学, 基础概念"></div>' +
          '</div>' +
          '<div class="modal-actions">' +
            '<button class="btn" id="card-modal-cancel">取消</button>' +
            '<button class="btn-primary-sm" id="card-modal-save">' + (isEdit ? '更新' : '保存') + '</button>' +
          '</div>' +
        '</div>';
        document.body.appendChild(overlay);

        overlay.querySelector('#card-modal-cancel').addEventListener('click', function() { overlay.remove(); });
        overlay.addEventListener('click', function(e) { if (e.target === overlay) overlay.remove(); });

        overlay.querySelector('#card-modal-save').addEventListener('click', async function() {
          var frontVal = overlay.querySelector('#card-modal-front').value.trim();
          var backVal = overlay.querySelector('#card-modal-back').value.trim();
          if (!frontVal || !backVal) { alert('请填写正面和反面内容'); return; }
          var data = {
            front_text: frontVal,
            back_text: backVal,
            subject_id: parseInt(overlay.querySelector('#card-modal-subject').value) || null,
            tags: overlay.querySelector('#card-modal-tags').value.trim() || null
          };
          try {
            if (isEdit) {
              await window.API.put('/flashcards/' + id, data);
            } else {
              await window.API.post('/flashcards', data);
            }
          } catch (err) { alert(err.message); return; }
          overlay.remove();
          renderFlashcards();
        });
      }
    }

    async function renderTab() {
      if (activeTab === 'notes') await renderNotes();
      else if (activeTab === 'wrong') await renderWrong();
      else if (activeTab === 'materials') await renderMaterials();
      else if (activeTab === 'flashcards') await renderFlashcards();
    }

    function switchTab(newTab) {
      if (newTab === activeTab) return;
      activeTab = newTab;
      container.innerHTML = renderTabs();
      bindTabClicks();
      renderTab();
    }

    function bindTabClicks() {
      var tabs = container.querySelector('.page-tabs');
      if (!tabs) return;
      tabs.querySelectorAll('.page-tab').forEach(function(btn) {
        btn.addEventListener('click', function(e) {
          e.preventDefault();
          e.stopPropagation();
          switchTab(btn.dataset.tab);
        });
      });
    }

    container.innerHTML = renderTabs();
    bindTabClicks();
    await renderTab();
  });
})();
