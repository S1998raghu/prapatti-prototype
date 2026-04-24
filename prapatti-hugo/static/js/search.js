const FONT_CLASSES = ['', 'font-lg', 'font-xl'];
function setFont(level) {
  FONT_CLASSES.forEach(c => c && document.documentElement.classList.remove(c));
  if (FONT_CLASSES[level]) document.documentElement.classList.add(FONT_CLASSES[level]);
  document.querySelectorAll('.font-btn').forEach((b, i) => b.classList.toggle('active', i === level));
  localStorage.setItem('fontSize', level);
}
(function() {
  const saved = localStorage.getItem('fontSize');
  if (saved) setFont(+saved);
  else document.getElementById('fb0') && document.getElementById('fb0').classList.add('active');
})();

function toggleUpdate(btn) {
  const panel = btn.nextElementSibling;
  const isOpen = btn.classList.contains('open');
  btn.classList.toggle('open', !isOpen);
  panel.classList.toggle('open', !isOpen);
}

(function () {
  const input = document.getElementById('search-input');
  const resultsBox = document.getElementById('search-results');
  if (!input || !resultsBox) return;

  let index = null;
  let currentMatches = [];

  async function loadIndex() {
    if (index) return;
    const res = await fetch('/index.json');
    index = await res.json();
  }

  function norm(s) {
    return String(s || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[^a-z0-9]/g, '');
  }

  function trigrams(s) {
    const out = new Set();
    for (let i = 0; i < s.length - 1; i++) out.add(s.slice(i, i + 3));
    return out;
  }

  function fuzzyMatch(token, hay) {
    if (hay.includes(token)) return true;          // exact substring
    if (token.length < 4) return hay.includes(token); // short tokens: exact only
    // trigram overlap: ≥55% of token's trigrams must appear in hay
    const tg = trigrams(token);
    if (!tg.size) return false;
    let hits = 0;
    tg.forEach(g => { if (hay.includes(g)) hits++; });
    return hits / tg.size >= 0.55;
  }

  function matches(item, q) {
    const hay = norm(item.title) + norm(item.subtitle) + norm(item.tags);
    const tokens = q.trim().split(/\s+/).map(norm).filter(Boolean);
    return tokens.every(t => fuzzyMatch(t, hay));
  }

  function escHtml(s) {
    return String(s || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  function navigate(item) {
    if (item.type === 'stotra') {
      window.location.href = '/stotras/?q=' + encodeURIComponent(item.title);
    } else {
      window.location.href = item.url;
    }
  }

  input.addEventListener('focus', loadIndex);

  input.addEventListener('input', async function () {
    const q = this.value.trim().toLowerCase();
    if (!q) { resultsBox.innerHTML = ''; resultsBox.style.display = 'none'; currentMatches = []; return; }

    await loadIndex();

    currentMatches = index.filter(item => matches(item, q)).slice(0, 12);

    if (!currentMatches.length) {
      resultsBox.innerHTML = '<div class="search-noresult">No results</div>';
    } else {
      resultsBox.innerHTML = currentMatches.map((m, i) => `
        <a href="#" class="search-result-item" data-idx="${i}">
          <span class="search-result-title">${escHtml(m.title)}</span>
          <span class="search-result-sub">${escHtml(m.subtitle)} · ${m.type}</span>
        </a>
      `).join('');

      resultsBox.querySelectorAll('.search-result-item').forEach(el => {
        el.addEventListener('click', function (e) {
          e.preventDefault();
          navigate(currentMatches[+this.dataset.idx]);
        });
      });
    }
    resultsBox.style.display = 'block';
  });

  input.addEventListener('keydown', function (e) {
    if (e.key === 'Enter' && currentMatches.length) {
      navigate(currentMatches[0]);
    }
  });

  document.addEventListener('click', function (e) {
    if (!input.contains(e.target) && !resultsBox.contains(e.target)) {
      resultsBox.style.display = 'none';
    }
  });
})();
