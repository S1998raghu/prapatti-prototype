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

    currentMatches = index.filter(item =>
      item.title.toLowerCase().includes(q) ||
      (item.subtitle && item.subtitle.toLowerCase().includes(q))
    ).slice(0, 12);

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
