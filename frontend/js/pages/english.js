/**
 * English page: 英语专项
 * Vocab (flashcard + spaced repetition), Reading (records + sentence analysis), Writing (essay + AI feedback).
 */
console.log('english.js loading...');
(function() {
  try {
  window.App.registerPage('english', async function(container) {
  console.log('english page rendering...');
    var activeTab = 'vocab';
    var vocabData = { items: [], total: 0 };
    var currentVocabIdx = 0;
    var vocabSearch = '';
    var vocabFreqFilter = '';

    function renderTabs() {
      return '<div class="page-tabs">' +
        '<button class="page-tab' + (activeTab === 'vocab' ? ' active' : '') + '" data-tab="vocab">背单词</button>' +
        '<button class="page-tab' + (activeTab === 'reading' ? ' active' : '') + '" data-tab="reading">阅读</button>' +
        '<button class="page-tab' + (activeTab === 'writing' ? ' active' : '') + '" data-tab="writing">写作</button>' +
        '</div><div id="english-tab-content"></div>';
    }

    // ======================== VOCAB ========================

    async function loadVocabData() {
      var url = '/vocab?due=true&limit=20&offset=0';
      if (vocabSearch) url += '&search=' + encodeURIComponent(vocabSearch);
      if (vocabFreqFilter) url += '&frequency=' + encodeURIComponent(vocabFreqFilter);
      try {
        vocabData = await window.API.get(url);
        currentVocabIdx = 0;
      } catch (err) {
        vocabData = { items: [], total: 0 };
        console.error('Load vocab error:', err);
      }
    }

    async function renderVocab() {
      await loadVocabData();
      var content = document.getElementById('english-tab-content');
      if (!content) return;

      var html = '';

      // Progress bar
      if (vocabData.total > 0) {
        var dueCount = vocabData.items ? vocabData.items.length : 0;
        html += '<div class="card" style="text-align:center">' +
          '<div style="font-size:13px;color:var(--text-secondary);margin-bottom:8px">词汇总量: ' + vocabData.total + ' | 待复习: ' + dueCount + '</div>' +
          '<div class="progress-bar" style="height:10px">' +
          '<div class="progress-fill" style="width:' + Math.max(5, (vocabData.total - dueCount) / Math.max(vocabData.total, 1) * 100) + '%;background:var(--info)"></div>' +
          '</div>' +
          '</div>';
      }

      // Flashcard
      if (vocabData.items && vocabData.items.length > 0) {
        var currentWord = vocabData.items[currentVocabIdx];
        html += '<div class="flashcard-container" style="margin-bottom:16px">' +
          '<div class="flashcard" id="vocab-flashcard" style="position:relative">' +
          '<div class="flashcard-front">' +
          '<div style="text-align:center">' +
          '<div style="font-size:32px;font-weight:700;margin-bottom:4px;display:flex;align-items:center;justify-content:center;gap:10px">' +
          '<span>' + escapeHtml(currentWord.word) + '</span>' +
          '<button class="btn-sm speak-word" data-word="' + escapeHtml(currentWord.word) + '" title="朗读" style="font-size:20px;padding:4px 8px;border-radius:50%;cursor:pointer;background:#eff6ff;border:1px solid #bfdbfe;line-height:1">🔊</button>' +
          '</div>' +
          '<div style="font-size:14px;color:var(--text-secondary)">' + (currentWord.phonetic || '') + '</div>' +
          '<div style="font-size:12px;color:var(--info);margin-top:4px">' + (currentWord.part_of_speech || '') + '</div>' +
          '<div style="margin-top:16px;font-size:12px;color:var(--text-secondary)">点击翻转查看释义</div>' +
          '</div></div>' +
          '<div class="flashcard-back">' +
          '<div style="text-align:center">' +
          '<div style="font-size:20px;font-weight:600;margin-bottom:12px">' + escapeHtml(currentWord.meaning) + '</div>' +
          (currentWord.example_sentence ? '<div style="font-size:14px;color:var(--text-secondary);margin-bottom:4px"><em>' + escapeHtml(currentWord.example_sentence) + '</em></div>' : '') +
          (currentWord.example_translation ? '<div style="font-size:12px;color:var(--text-secondary)">' + escapeHtml(currentWord.example_translation) + '</div>' : '') +
          '</div></div>' +
          '</div></div>';

        // Rating buttons
        html += '<div style="display:flex;gap:10px;justify-content:center;margin-bottom:16px">' +
          '<button class="btn-sm vocab-review" data-id="' + currentWord.id + '" data-feedback="forgot" style="color:var(--danger);border-color:var(--danger);padding:8px 20px;font-size:14px">不认识</button>' +
          '<button class="btn-sm vocab-review" data-id="' + currentWord.id + '" data-feedback="blurry" style="color:var(--warning);border-color:var(--warning);padding:8px 20px;font-size:14px">模糊</button>' +
          '<button class="btn-sm vocab-review" data-id="' + currentWord.id + '" data-feedback="remembered" style="color:var(--success);border-color:var(--success);padding:8px 20px;font-size:14px">认识</button>' +
          '</div>';

        // Navigation
        html += '<div style="display:flex;justify-content:center;gap:12px;margin-bottom:10px;font-size:13px;color:var(--text-secondary)">' +
          '<span>' + (currentVocabIdx + 1) + ' / ' + vocabData.items.length + '</span>' +
          '</div>';
      } else {
        html += '<div class="card" style="text-align:center"><p style="color:var(--text-secondary);font-size:13px">' +
          (vocabSearch || vocabFreqFilter ? '没有搜到匹配的单词。' : '暂无待复习单词，去添加一些生词吧!') +
          '</p></div>';
      }

      // Search and filters + custom word
      html += '<div class="card"><div class="card-header"><h3>单词管理</h3></div>';
      html += '<div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-bottom:12px">' +
        '<input id="vocab-search" placeholder="搜索单词..." value="' + escapeHtml(vocabSearch) + '" style="padding:6px 10px;border:1px solid var(--border);border-radius:var(--radius-sm);width:180px;font-size:13px">' +
        '<select id="vocab-freq-filter" style="padding:6px 10px;border:1px solid var(--border);border-radius:var(--radius-sm);font-size:13px">' +
        '<option value=""' + (vocabFreqFilter === '' ? ' selected' : '') + '>全部词频</option>' +
        '<option value="high"' + (vocabFreqFilter === 'high' ? ' selected' : '') + '>高频</option>' +
        '<option value="mid"' + (vocabFreqFilter === 'mid' ? ' selected' : '') + '>中频</option>' +
        '<option value="low"' + (vocabFreqFilter === 'low' ? ' selected' : '') + '>低频</option>' +
        '</select>' +
        '<button class="btn-primary-sm" id="add-custom-word">+ 自定义生词</button>' +
        '</div>';

      // Word list
      if (vocabData.items && vocabData.items.length > 0) {
        html += '<div style="max-height:300px;overflow-y:auto;border:1px solid var(--border);border-radius:var(--radius-sm)">';
        vocabData.items.forEach(function(w) {
          var freqClass = w.frequency_level === 'high' ? 'politics' : (w.frequency_level === 'mid' ? 'english' : 'math');
          html += '<div style="padding:10px;border-bottom:1px solid var(--border);font-size:13px;cursor:pointer" class="vocab-list-item" data-idx="' + vocabData.items.indexOf(w) + '">' +
            '<div style="display:flex;align-items:center;gap:8px;margin-bottom:2px">' +
            '<strong style="font-size:16px">' + escapeHtml(w.word) + '</strong>' +
            '<span style="color:var(--text-secondary)">' + (w.phonetic || '') + '</span>' +
            '<span style="color:var(--info);font-size:11px">' + (w.part_of_speech || '') + '</span>' +
            '<span class="subj-badge ' + freqClass + '">' + (w.frequency_level === 'high' ? '高频' : w.frequency_level === 'mid' ? '中频' : '低频') + '</span>' +
            '</div>' +
            '<div style="color:var(--text-secondary);font-size:12px">' + (w.meaning || '') + '</div>' +
            '</div>';
        });
        html += '</div>';
      }
      html += '</div>';

      content.innerHTML = html;

      // Flashcard flip
      var card = document.getElementById('vocab-flashcard');
      if (card) {
        card.addEventListener('click', function() {
          card.classList.toggle('flipped');
        });
      }

      // Speak word button
      document.querySelectorAll('.speak-word').forEach(function(btn) {
        btn.addEventListener('click', function(e) {
          e.stopPropagation();
          var word = btn.dataset.word;
          if (word && window.speechSynthesis) {
            window.speechSynthesis.cancel();
            var utter = new SpeechSynthesisUtterance(word);
            utter.lang = 'en-US';
            utter.rate = 0.8;
            window.speechSynthesis.speak(utter);
          }
        });
      });

      // Also speak on word list items
      document.querySelectorAll('.vocab-list-item').forEach(function(item) {
        item.addEventListener('click', function() {
          currentVocabIdx = parseInt(item.dataset.idx);
          renderVocab();
        });
      });

      // Rating buttons
      document.querySelectorAll('.vocab-review').forEach(function(btn) {
        btn.addEventListener('click', function(e) {
          e.stopPropagation();
          var id = btn.dataset.id;
          var feedback = btn.dataset.feedback;
          window.API.post('/vocab/' + id + '/review', { feedback: feedback }).then(function() {
            // Move to next word or reload
            if (currentVocabIdx < vocabData.items.length - 1) {
              currentVocabIdx++;
              renderVocab();
            } else {
              renderVocab();
            }
          }).catch(function(err) {
            alert('提交失败: ' + err.message);
          });
        });
      });

      // Search
      var searchInput = document.getElementById('vocab-search');
      if (searchInput) {
        searchInput.addEventListener('keyup', function(e) {
          if (e.key === 'Enter') {
            vocabSearch = e.target.value.trim();
            renderVocab();
          }
        });
      }

      // Frequency filter
      var freqFilter = document.getElementById('vocab-freq-filter');
      if (freqFilter) {
        freqFilter.addEventListener('change', function() {
          vocabFreqFilter = freqFilter.value;
          renderVocab();
        });
      }

      // Custom word form
      var addCustomBtn = document.getElementById('add-custom-word');
      if (addCustomBtn) {
        addCustomBtn.addEventListener('click', function() {
          showCustomWordForm();
        });
      }
    }

    function showCustomWordForm() {
      var existing = document.getElementById('custom-word-overlay');
      if (existing) existing.remove();

      var html = '<div class="modal-overlay" id="custom-word-overlay">' +
        '<div class="modal">' +
        '<h3>添加自定义生词</h3>' +
        '<div class="form-group"><label>单词</label><input id="cw-word" placeholder="输入英文单词"></div>' +
        '<div class="form-group"><label>释义</label><input id="cw-meaning" placeholder="中文释义"></div>' +
        '<div class="form-group"><label>音标 (可选)</label><input id="cw-phonetic" placeholder="e.g. /ˈeksəmpəl/"></div>' +
        '<div class="form-group"><label>词性 (可选)</label><input id="cw-pos" placeholder="e.g. n./v./adj."></div>' +
        '<div class="form-group"><label>例句 (可选)</label><textarea id="cw-example" rows="2" placeholder="英文例句"></textarea></div>' +
        '<div class="modal-actions">' +
        '<button class="btn" id="cw-cancel">取消</button>' +
        '<button class="btn-primary-sm" id="cw-save">添加</button>' +
        '</div>' +
        '</div></div>';

      document.body.insertAdjacentHTML('beforeend', html);

      document.getElementById('cw-cancel').addEventListener('click', function() {
        document.getElementById('custom-word-overlay').remove();
      });
      document.getElementById('cw-save').addEventListener('click', function() {
        var word = document.getElementById('cw-word').value.trim();
        var meaning = document.getElementById('cw-meaning').value.trim();
        if (!word || !meaning) { alert('单词和释义不能为空'); return; }
        var data = {
          word: word,
          meaning: meaning,
          phonetic: document.getElementById('cw-phonetic').value.trim() || null,
          part_of_speech: document.getElementById('cw-pos').value.trim() || null,
          example_sentence: document.getElementById('cw-example').value.trim() || null
        };
        window.API.post('/vocab/custom', data).then(function() {
          document.getElementById('custom-word-overlay').remove();
          renderVocab();
        }).catch(function(err) {
          alert('添加失败: ' + err.message);
        });
      });
    }

    // ======================== READING ========================

    async function renderReading() {
      var content = document.getElementById('english-tab-content');
      if (!content) return;

      var records = [];
      var sentences = [];
      try { records = await window.API.get('/reading'); } catch (err) { records = []; }
      // Fetch sentences for each reading record
      var sentencePromises = records.map(function(r) {
        return window.API.get('/reading/' + r.id + '/sentences').then(function(sents) {
          // Tag each sentence with its record info
          return (sents || []).map(function(s) { s._record_id = r.id; s._record_info = r.year + '-P' + r.passage_no; return s; });
        }).catch(function() { return []; });
      });
      try {
        var allSentences = await Promise.all(sentencePromises);
        sentences = [].concat.apply([], allSentences);
      } catch (err) { sentences = []; }

      var html = '';

      // Reading records
      html += '<div class="card"><div class="card-header"><h3>阅读练习记录</h3><button class="btn-primary-sm" id="add-reading">+ 添加记录</button></div>';
      if (!records || records.length === 0) {
        html += '<p style="color:var(--text-secondary);font-size:13px">暂无阅读记录，开始记录你的练习!</p>';
      } else {
        html += '<div class="batch-bar" id="reading-batch-bar"><span>已选 <span class="selected-count" id="reading-batch-count">0</span> 项</span>' +
          '<button class="btn-delete" id="reading-batch-delete">批量删除</button>' +
          '<button class="btn-cancel" id="reading-batch-cancel">取消选择</button></div>';
        html += '<table class="table"><thead><tr><th><input type="checkbox" class="batch-checkbox" id="reading-select-all" title="全选"></th><th>年份</th><th>篇目</th><th>题型</th><th>题数</th><th>错题</th><th>正确率</th><th>用时</th><th>得分</th><th>操作</th></tr></thead><tbody>';
        records.forEach(function(r) {
          var acc = r.total_questions > 0 ? (((r.total_questions - r.wrong_count) / r.total_questions) * 100).toFixed(0) : '-';
          var typeLabel = r.type === 'reading' ? '阅读理解' : r.type === 'translation' ? '翻译' : r.type === 'cloze' ? '完形填空' : (r.type === 'new_type' ? '新题型' : (r.type || '-'));
          html += '<tr>' +
            '<td><input type="checkbox" class="batch-checkbox reading-batch-sel" data-id="' + r.id + '"></td>' +
            '<td>' + (r.year || '-') + '</td>' +
            '<td>第' + (r.passage_no || '-') + '篇</td>' +
            '<td>' + typeLabel + '</td>' +
            '<td>' + (r.total_questions || 0) + '</td>' +
            '<td>' + (r.wrong_count || 0) + '</td>' +
            '<td>' + (acc !== '-' ? acc + '%' : '-') + '</td>' +
            '<td>' + (r.time_spent_minutes || 0) + '分钟</td>' +
            '<td>' + (r.score !== undefined ? r.score : '-') + '</td>' +
            '<td><button class="btn-sm reading-delete" data-id="' + r.id + '" style="color:var(--danger)">删除</button></td>' +
            '</tr>';
        });
        html += '</tbody></table>';
      }
      html += '</div>';

      // Accuracy trend chart
      if (records && records.length > 0) {
        html += '<div class="card"><div class="card-header"><h3>正确率趋势</h3></div>';
        html += '<div style="height:200px"><canvas id="accuracy-chart"></canvas></div></div>';
      }

      // Long sentence analysis
      html += '<div class="card"><div class="card-header"><h3>长难句分析</h3><button class="btn-primary-sm" id="add-sentence">+ 添加句子</button></div>';
      if (!sentences || sentences.length === 0) {
        html += '<p style="color:var(--text-secondary);font-size:13px">暂无长难句记录。</p>';
      } else {
        html += '<div style="max-height:300px;overflow-y:auto">';
        sentences.forEach(function(s) {
          html += '<div style="padding:10px;border-bottom:1px solid var(--border);font-size:13px">' +
            '<div style="margin-bottom:4px"><strong>原句:</strong> ' + escapeHtml(s.sentence_text || '') + '</div>' +
            '<div style="color:var(--text-secondary);font-size:12px"><strong>分析:</strong> ' + escapeHtml(s.grammar_analysis || '') + '</div>' +
            (s.translation ? '<div style="color:var(--text-secondary);font-size:12px"><strong>翻译:</strong> ' + escapeHtml(s.translation) + '</div>' : '') +
            '<button class="btn-sm sentence-delete" data-id="' + s.id + '" style="color:var(--danger);margin-top:4px">删除</button>' +
            '</div>';
        });
        html += '</div>';
      }
      html += '</div>';

      content.innerHTML = html;

      // Add reading record
      var addReadingBtn = document.getElementById('add-reading');
      if (addReadingBtn) {
        addReadingBtn.addEventListener('click', function() { showReadingForm(); });
      }

      // Delete reading
      // Batch reading handlers
      var rSelected = [];
      function updateReadingBatch() {
        document.getElementById('reading-batch-bar').style.display = rSelected.length > 0 ? 'flex' : 'none';
        document.getElementById('reading-batch-count').textContent = rSelected.length;
      }
      var rsa = document.getElementById('reading-select-all');
      if (rsa) rsa.addEventListener('change', function() {
        document.querySelectorAll('.reading-batch-sel').forEach(function(cb) { cb.checked = rsa.checked; });
        rSelected = rsa.checked ? records.map(function(rr) { return rr.id; }) : [];
        updateReadingBatch();
      });
      document.querySelectorAll('.reading-batch-sel').forEach(function(cb) {
        cb.addEventListener('change', function() {
          var id = parseInt(cb.dataset.id);
          if (cb.checked) { if (rSelected.indexOf(id) < 0) rSelected.push(id); }
          else { rSelected = rSelected.filter(function(x) { return x !== id; }); }
          updateReadingBatch();
        });
      });
      var rbd = document.getElementById('reading-batch-delete');
      if (rbd) rbd.addEventListener('click', function() {
        if (!confirm('确定删除选中的 ' + rSelected.length + ' 条阅读记录？')) return;
        window.API.post('/reading/batch-delete', { ids: rSelected.slice() }).then(function() { renderReading(); })
          .catch(function(err) { alert('删除失败: ' + err.message); });
      });
      var rbc = document.getElementById('reading-batch-cancel');
      if (rbc) rbc.addEventListener('click', function() {
        document.querySelectorAll('.reading-batch-sel').forEach(function(cb) { cb.checked = false; });
        if (rsa) rsa.checked = false;
        rSelected = [];
        updateReadingBatch();
      });

      document.querySelectorAll('.reading-delete').forEach(function(btn) {
        btn.addEventListener('click', function() {
          if (confirm('确认删除此阅读记录?')) {
            window.API.delete('/reading/' + btn.dataset.id).then(function() { renderReading(); }).catch(function(err) { alert(err.message); });
          }
        });
      });

      // Accuracy chart
      var accCtx = document.getElementById('accuracy-chart');
      if (accCtx && records && records.length > 0) {
        new Chart(accCtx, {
          type: 'line',
          data: {
            labels: records.map(function(r) { return (r.year || '') + '-P' + (r.passage_no || ''); }),
            datasets: [{
              label: '正确率 %',
              data: records.map(function(r) {
                return r.total_questions > 0 ? parseFloat(((r.total_questions - r.wrong_count) / r.total_questions * 100).toFixed(1)) : 0;
              }),
              borderColor: '#3b82f6',
              backgroundColor: 'rgba(59,130,246,0.1)',
              fill: true,
              tension: 0.3
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: { y: { min: 0, max: 100, title: { display: true, text: '%' } } }
          }
        });
      }

      // Add sentence
      var addSentBtn = document.getElementById('add-sentence');
      if (addSentBtn) {
        addSentBtn.addEventListener('click', function() { showSentenceForm(); });
      }

      // Delete sentence
      document.querySelectorAll('.sentence-delete').forEach(function(btn) {
        btn.addEventListener('click', function() {
          if (confirm('确认删除此长难句?')) {
            window.API.delete('/reading/sentences/' + btn.dataset.id).then(function() { renderReading(); }).catch(function(err) { alert(err.message); });
          }
        });
      });
    }

    function showReadingForm() {
      var existing = document.getElementById('reading-form-overlay');
      if (existing) existing.remove();

      var types = [
        { value: 'reading', label: '阅读理解' },
        { value: 'translation', label: '翻译' },
        { value: 'cloze', label: '完形填空' },
        { value: 'new_type', label: '新题型' }
      ];
      var typeOpts = types.map(function(t) { return '<option value="' + t.value + '">' + t.label + '</option>'; }).join('');

      var html = '<div class="modal-overlay" id="reading-form-overlay">' +
        '<div class="modal">' +
        '<h3>添加阅读记录</h3>' +
        '<div class="form-group"><label>年份</label><input type="number" id="rf-year" value="2025" min="2000" max="2030"></div>' +
        '<div class="form-group"><label>篇目号</label><input type="number" id="rf-passage" value="1" min="1"></div>' +
        '<div class="form-group"><label>题型</label><select id="rf-type">' + typeOpts + '</select></div>' +
        '<div class="form-group"><label>总题数</label><input type="number" id="rf-total" value="5" min="0"></div>' +
        '<div class="form-group"><label>错题数</label><input type="number" id="rf-wrong" value="0" min="0"></div>' +
        '<div class="form-group"><label>得分</label><input type="number" id="rf-score" value="0" min="0" step="0.5"></div>' +
        '<div class="form-group"><label>用时 (分钟)</label><input type="number" id="rf-time" value="0" min="0"></div>' +
        '<div class="modal-actions">' +
        '<button class="btn" id="rf-cancel">取消</button>' +
        '<button class="btn-primary-sm" id="rf-save">添加</button>' +
        '</div>' +
        '</div></div>';

      document.body.insertAdjacentHTML('beforeend', html);

      document.getElementById('rf-cancel').addEventListener('click', function() { document.getElementById('reading-form-overlay').remove(); });
      document.getElementById('rf-save').addEventListener('click', function() {
        var data = {
          year: parseInt(document.getElementById('rf-year').value) || 2025,
          passage_no: parseInt(document.getElementById('rf-passage').value) || 1,
          type: document.getElementById('rf-type').value,
          total_questions: parseInt(document.getElementById('rf-total').value) || 0,
          wrong_count: parseInt(document.getElementById('rf-wrong').value) || 0,
          score: parseFloat(document.getElementById('rf-score').value) || 0,
          time_spent_minutes: parseInt(document.getElementById('rf-time').value) || 0
        };
        window.API.post('/reading', data).then(function() {
          document.getElementById('reading-form-overlay').remove();
          renderReading();
        }).catch(function(err) { alert(err.message); });
      });
    }

    function showSentenceForm() {
      var existing = document.getElementById('sentence-form-overlay');
      if (existing) existing.remove();

      // Fetch reading records for the dropdown
      var readingRecords = [];
      window.API.get('/reading').then(function(recs) { readingRecords = recs || []; }).catch(function() {});

      var html = '<div class="modal-overlay" id="sentence-form-overlay">' +
        '<div class="modal">' +
        '<h3>添加长难句</h3>' +
        '<div class="form-group"><label>所属阅读记录</label><select id="sf-record-id"></select></div>' +
        '<div class="form-group"><label>原句</label><textarea id="sf-sentence-text" rows="3" placeholder="粘贴英文原句"></textarea></div>' +
        '<div class="form-group"><label>分析</label><textarea id="sf-grammar-analysis" rows="3" placeholder="句子结构分析"></textarea></div>' +
        '<div class="form-group"><label>翻译 (可选)</label><textarea id="sf-translation" rows="2" placeholder="中文翻译"></textarea></div>' +
        '<div class="modal-actions">' +
        '<button class="btn" id="sf-cancel">取消</button>' +
        '<button class="btn-primary-sm" id="sf-save">添加</button>' +
        '</div>' +
        '</div></div>';

      document.body.insertAdjacentHTML('beforeend', html);

      // Populate the record dropdown
      var recordSelect = document.getElementById('sf-record-id');
      if (readingRecords.length > 0) {
        readingRecords.forEach(function(r) {
          recordSelect.innerHTML += '<option value="' + r.id + '">' + (r.year || '') + ' P' + (r.passage_no || '') + ' (' + (r.type || '') + ')</option>';
        });
      } else {
        recordSelect.innerHTML = '<option value="">请先添加阅读记录</option>';
      }

      document.getElementById('sf-cancel').addEventListener('click', function() { document.getElementById('sentence-form-overlay').remove(); });
      document.getElementById('sf-save').addEventListener('click', function() {
        var recordId = parseInt(document.getElementById('sf-record-id').value);
        if (!recordId) { alert('请选择阅读记录'); return; }
        var data = {
          sentence_text: document.getElementById('sf-sentence-text').value.trim(),
          grammar_analysis: document.getElementById('sf-grammar-analysis').value.trim(),
          translation: document.getElementById('sf-translation').value.trim() || null
        };
        if (!data.sentence_text) { alert('请输入原句'); return; }
        if (!data.grammar_analysis) { alert('请输入句子分析'); return; }
        window.API.post('/reading/' + recordId + '/sentences', data).then(function() {
          document.getElementById('sentence-form-overlay').remove();
          renderReading();
        }).catch(function(err) { alert(err.message); });
      });
    }

    // ======================== WRITING ========================

    async function renderWriting() {
      var content = document.getElementById('english-tab-content');
      if (!content) return;

      var essays = [];
      try { essays = await window.API.get('/writing'); } catch (err) { essays = []; }

      var html = '';

      // Essay list
      html += '<div class="card"><div class="card-header"><h3>作文管理</h3><button class="btn-primary-sm" id="add-essay">+ 写新作文</button></div>';
      if (!essays || essays.length === 0) {
        html += '<p style="color:var(--text-secondary);font-size:13px">暂无作文记录，开始练习写作!</p>';
      } else {
        html += '<div class="batch-bar" id="essay-batch-bar"><span>已选 <span class="selected-count" id="essay-batch-count">0</span> 项</span>' +
          '<button class="btn-delete" id="essay-batch-delete">批量删除</button>' +
          '<button class="btn-cancel" id="essay-batch-cancel">取消选择</button></div>';
        html += '<table class="table"><thead><tr><th><input type="checkbox" class="batch-checkbox" id="essay-select-all" title="全选"></th><th>标题</th><th>类型</th><th>AI评分</th><th>时间</th><th>操作</th></tr></thead><tbody>';
        essays.forEach(function(e) {
          var scoreDisplay = e.overall_score > 0 ? (e.overall_score + ' / 15') : '未批改';
          html += '<tr>' +
            '<td><input type="checkbox" class="batch-checkbox essay-batch-sel" data-id="' + e.id + '"></td>' +
            '<td>' + escapeHtml(e.title || '未命名') + '</td>' +
            '<td>' + (e.type === 'small' ? '小作文' : '大作文') + '</td>' +
            '<td>' + scoreDisplay + '</td>' +
            '<td>' + (e.created_at ? e.created_at.slice(0, 10) : '') + '</td>' +
            '<td>' +
            '<button class="btn-sm essay-view" data-id="' + e.id + '">查看</button> ' +
            '<button class="btn-sm essay-feedback" data-id="' + e.id + '">' + (e.overall_score > 0 ? '重新批改' : 'AI批改') + '</button> ' +
            '<button class="btn-sm essay-delete" data-id="' + e.id + '" style="color:var(--danger)">删除</button>' +
            '</td>' +
            '</tr>';
        });
        html += '</tbody></table>';
      }
      html += '</div>';

      // Template library - load from API
      html += '<div class="card"><div class="card-header"><h3>模板库</h3></div>';
      html += '<div id="template-list" style="display:flex;gap:8px;flex-wrap:wrap">加载中...</div></div>';

      content.innerHTML = html;

      // Load templates from API
      window.API.get('/writing?include_templates=true').then(function(templateData) {
        var tplContainer = document.getElementById('template-list');
        if (!tplContainer) return;
        if (!templateData || templateData.length === 0) {
          tplContainer.innerHTML = '<span style="color:var(--text-secondary);font-size:13px">暂无模板</span>';
          return;
        }
        tplContainer.innerHTML = '';
        templateData.forEach(function(tmpl) {
          var btn = document.createElement('button');
          btn.className = 'tag-filter writing-template';
          btn.style.cssText = 'cursor:pointer';
          btn.textContent = tmpl.title;
          btn.addEventListener('click', function() {
            var modal = document.createElement('div');
            modal.className = 'modal-overlay';
            modal.innerHTML = '<div class="modal" style="max-width:600px;max-height:80vh;overflow-y:auto">' +
              '<h3>' + tmpl.title + ' <span style="font-size:12px;color:var(--text-secondary)">' + (tmpl.type === 'small' ? '小作文' : '大作文') + '</span></h3>' +
              '<div style="white-space:pre-wrap;font-size:13px;border:1px solid var(--border);padding:12px;border-radius:8px;max-height:400px;overflow-y:auto;background:#fafafa;line-height:1.8">' + (tmpl.content || '') + '</div>' +
              '<div class="modal-actions" style="margin-top:12px">' +
              '<button class="btn" id="tpl-cancel">关闭</button>' +
              '<button class="btn-primary-sm" id="tpl-use">使用此模板</button>' +
              '</div></div>';
            document.body.appendChild(modal);
            modal.querySelector('#tpl-cancel').addEventListener('click', function() { modal.remove(); });
            modal.addEventListener('click', function(e) { if (e.target === modal) modal.remove(); });
            modal.querySelector('#tpl-use').addEventListener('click', function() {
              modal.remove();
              showEssayForm({ type: tmpl.type, title: '', content: tmpl.content });
            });
          });
          tplContainer.appendChild(btn);
        });
      }).catch(function() {
        var tplContainer = document.getElementById('template-list');
        if (tplContainer) tplContainer.innerHTML = '<span style="color:var(--text-secondary);font-size:13px">加载模板失败</span>';
      });

      // Add essay button
      var addBtn = document.getElementById('add-essay');
      if (addBtn) { addBtn.addEventListener('click', function() { showEssayForm(null); }); }

      // View essay
      document.querySelectorAll('.essay-view').forEach(function(btn) {
        btn.addEventListener('click', function() {
          var essay = essays.find(function(e) { return e.id == btn.dataset.id; });
          if (essay) viewEssay(essay);
        });
      });

      // AI feedback
      document.querySelectorAll('.essay-feedback').forEach(function(btn) {
        btn.addEventListener('click', function() {
          var id = btn.dataset.id;
          btn.textContent = '批改中...';
          btn.disabled = true;
          window.API.post('/writing/' + id + '/ai-feedback').then(function(result) {
            showFeedbackResult(result, id);
          }).catch(function(err) {
            alert('AI批改失败: ' + err.message);
          }).finally(function() {
            btn.textContent = '查看批改';
            btn.disabled = false;
          });
        });
      });

      // Delete essay
      // Batch essay handlers
      var eSelected = [];
      function updateEssayBatch() {
        document.getElementById('essay-batch-bar').style.display = eSelected.length > 0 ? 'flex' : 'none';
        document.getElementById('essay-batch-count').textContent = eSelected.length;
      }
      var esa = document.getElementById('essay-select-all');
      if (esa) esa.addEventListener('change', function() {
        document.querySelectorAll('.essay-batch-sel').forEach(function(cb) { cb.checked = esa.checked; });
        eSelected = esa.checked ? essays.map(function(ee) { return ee.id; }) : [];
        updateEssayBatch();
      });
      document.querySelectorAll('.essay-batch-sel').forEach(function(cb) {
        cb.addEventListener('change', function() {
          var id = parseInt(cb.dataset.id);
          if (cb.checked) { if (eSelected.indexOf(id) < 0) eSelected.push(id); }
          else { eSelected = eSelected.filter(function(x) { return x !== id; }); }
          updateEssayBatch();
        });
      });
      var ebd = document.getElementById('essay-batch-delete');
      if (ebd) ebd.addEventListener('click', function() {
        if (!confirm('确定删除选中的 ' + eSelected.length + ' 篇作文？')) return;
        window.API.post('/writing/batch-delete', { ids: eSelected.slice() }).then(function() { renderWriting(); })
          .catch(function(err) { alert('删除失败: ' + err.message); });
      });
      var ebc = document.getElementById('essay-batch-cancel');
      if (ebc) ebc.addEventListener('click', function() {
        document.querySelectorAll('.essay-batch-sel').forEach(function(cb) { cb.checked = false; });
        if (esa) esa.checked = false;
        eSelected = [];
        updateEssayBatch();
      });

      document.querySelectorAll('.essay-delete').forEach(function(btn) {
        btn.addEventListener('click', function() {
          if (confirm('确认删除此作文?')) {
            window.API.delete('/writing/' + btn.dataset.id).then(function() { renderWriting(); }).catch(function(err) { alert(err.message); });
          }
        });
      });
    }

    function showEssayForm(preset) {
      var existing = document.getElementById('essay-form-overlay');
      if (existing) existing.remove();

      var typeVal = preset ? preset.type : 'small';
      var titleVal = preset ? preset.title : '';

      var html = '<div class="modal-overlay" id="essay-form-overlay">' +
        '<div class="modal" style="min-width:550px">' +
        '<h3>写作文</h3>' +
        '<div class="form-group"><label>类型</label><select id="ef-type">' +
        '<option value="small"' + (typeVal === 'small' ? ' selected' : '') + '>小作文 (应用文)</option>' +
        '<option value="large"' + (typeVal === 'large' ? ' selected' : '') + '>大作文 (论说文)</option>' +
        '</select></div>' +
        '<div class="form-group"><label>标题</label><input id="ef-title" value="' + escapeHtml(titleVal) + '" placeholder="作文标题"></div>' +
        '<div class="form-group"><label>内容 (英文)</label><textarea id="ef-content" rows="10" placeholder="在这里输入你的英文作文..."></textarea></div>' +
        '<div class="modal-actions">' +
        '<button class="btn" id="ef-cancel">取消</button>' +
        '<button class="btn-primary-sm" id="ef-save">保存</button>' +
        '</div>' +
        '</div></div>';

      document.body.insertAdjacentHTML('beforeend', html);

      document.getElementById('ef-cancel').addEventListener('click', function() { document.getElementById('essay-form-overlay').remove(); });
      document.getElementById('ef-save').addEventListener('click', function() {
        var data = {
          type: document.getElementById('ef-type').value,
          title: document.getElementById('ef-title').value.trim(),
          content: document.getElementById('ef-content').value.trim()
        };
        if (!data.title) { alert('请输入标题'); return; }
        if (!data.content) { alert('请输入作文内容'); return; }
        window.API.post('/writing', data).then(function() {
          document.getElementById('essay-form-overlay').remove();
          renderWriting();
        }).catch(function(err) { alert(err.message); });
      });
    }

    function viewEssay(essay) {
      var existing = document.getElementById('essay-view-overlay');
      if (existing) existing.remove();

      var html = '<div class="modal-overlay" id="essay-view-overlay">' +
        '<div class="modal" style="min-width:550px;max-height:80vh;overflow-y:auto">' +
        '<h3>' + escapeHtml(essay.title || '未命名') + ' <span style="font-size:12px;color:var(--text-secondary)">(' + (essay.type === 'small' ? '小作文' : '大作文') + ')</span></h3>' +
        (essay.overall_score > 0 ? '<div style="margin-bottom:12px;padding:10px;background:var(--bg);border-radius:var(--radius-sm)">' +
          '<div style="font-weight:600">AI评分: ' + essay.overall_score + ' / 15</div>' +
          '<div style="font-size:12px;color:var(--text-secondary)">词汇: ' + (essay.vocabulary_score || '-') + '/5 | 句子: ' + (essay.sentence_score || '-') + '/5 | 内容: ' + (essay.content_score || '-') + '/5</div>' +
          (essay.feedback ? '<div style="margin-top:8px;font-size:13px;white-space:pre-wrap">' + escapeHtml(essay.feedback) + '</div>' : '') +
          '<div style="font-size:11px;color:var(--text-secondary);margin-top:4px">' + (essay.revised_at ? '批改时间: ' + essay.revised_at : '') + '</div>' +
          '</div>' : '') +
        '<div style="white-space:pre-wrap;font-size:13px;border:1px solid var(--border);padding:12px;border-radius:var(--radius-sm);max-height:300px;overflow-y:auto">' + escapeHtml(essay.content || '') + '</div>' +
        '<div class="modal-actions" style="margin-top:12px">' +
        '<button class="btn" id="ev-close">关闭</button>' +
        '</div>' +
        '</div></div>';

      document.body.insertAdjacentHTML('beforeend', html);
      document.getElementById('ev-close').addEventListener('click', function() { document.getElementById('essay-view-overlay').remove(); });
    }

    function showFeedbackResult(result, essayId) {
      var existing = document.getElementById('feedback-overlay');
      if (existing) existing.remove();

      var html = '<div class="modal-overlay" id="feedback-overlay">' +
        '<div class="modal" style="min-width:500px;max-height:80vh;overflow-y:auto">' +
        '<h3>AI批改结果</h3>' +
        '<div style="text-align:center;margin-bottom:16px">' +
        '<div style="font-size:48px;font-weight:700;color:var(--info)">' + (result.overall_score || 0) + '<span style="font-size:20px;color:var(--text-secondary)"> / 15</span></div>' +
        '</div>' +
        '<div style="display:flex;gap:16px;justify-content:center;margin-bottom:16px">' +
        '<div style="text-align:center"><div style="font-weight:600">词汇</div><div style="font-size:24px;color:var(--success)">' + (result.vocabulary_score || 0) + '/5</div></div>' +
        '<div style="text-align:center"><div style="font-weight:600">句子</div><div style="font-size:24px;color:var(--info)">' + (result.sentence_score || 0) + '/5</div></div>' +
        '<div style="text-align:center"><div style="font-weight:600">内容</div><div style="font-size:24px;color:var(--warning)">' + (result.content_score || 0) + '/5</div></div>' +
        '</div>' +
        (result.feedback ? '<div style="padding:12px;background:var(--bg);border-radius:var(--radius-sm);white-space:pre-wrap;font-size:13px">' + escapeHtml(result.feedback) + '</div>' : '') +
        (result.suggestions ? '<div style="margin-top:12px"><strong>改进建议:</strong><div style="white-space:pre-wrap;font-size:13px;color:var(--text-secondary)">' + escapeHtml(result.suggestions) + '</div></div>' : '') +
        '<div class="modal-actions" style="margin-top:12px">' +
        '<button class="btn" id="fb-close">关闭</button>' +
        '</div>' +
        '</div></div>';

      document.body.insertAdjacentHTML('beforeend', html);
      document.getElementById('fb-close').addEventListener('click', function() {
        document.getElementById('feedback-overlay').remove();
        renderWriting();
      });
    }

    // ======================== TAB SWITCHING ========================

    async function renderTab() {
      if (activeTab === 'vocab') await renderVocab();
      else if (activeTab === 'reading') await renderReading();
      else if (activeTab === 'writing') await renderWriting();
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

  function escapeHtml(str) {
    if (!str) return '';
    return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }
  } catch(e) { console.error('english.js error:', e); }
})();
