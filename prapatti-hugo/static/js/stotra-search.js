// Shared stotra search for the home page and /stotras/.
// Matches every word of the query, in any order, ignoring spaces and common
// transliteration variants (sreenivasa = sriinivaasa, venkateswara ~ venkatesha).
(function () {
  // Fold spelling variants so both the query and the stotra text reduce to one form
  function norm(s) {
    return String(s || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '')
      .replace(/x/g, 'ks').replace(/ee/g, 'i').replace(/oo/g, 'u').replace(/w/g, 'v')
      .replace(/([kgcjtdpbs])h/g, '$1').replace(/zh/g, 'z')
      .replace(/[^a-z0-9 ]+/g, ' ')
      .replace(/([a-z])\1+/g, '$1');
  }

  // A long word that is not found as typed may still match on its start (venkateswara -> venkates…)
  function stem(w) {
    return w.length >= 8 ? w.slice(0, Math.max(6, w.length - 4)) : w;
  }

  // items: [{name, author, tags}]; returns a function query -> [{item, score}] best first
  function makeSearch(items) {
    const hay = items.map(item => ({
      item,
      text: (norm(item.name) + norm(item.tags) + norm(item.author)).replace(/ /g, ''),
      name: norm(item.name).replace(/ /g, ''),
    }));
    return function (query) {
      const words = norm(query).split(/\s+/).filter(Boolean);
      if (!words.length) return [];
      const phrase = words.join('');
      const out = [];
      for (const h of hay) {
        let exact = 0, ok = true;
        for (const w of words) {
          if (h.text.includes(w)) exact++;
          else if (!h.text.includes(stem(w))) { ok = false; break; }
        }
        // Whole query inside the name ranks first, then the most words matched as typed
        if (ok) out.push({ item: h.item, score: (h.name.includes(phrase) ? 100 : 0) + exact });
      }
      return out.sort((a, b) => b.score - a.score);
    };
  }

  window.stotraSearch = { norm, makeSearch };
})();
