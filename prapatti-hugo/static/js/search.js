// Client-side search over the updates table
(function () {
  const input = document.getElementById('search-input');
  if (!input) return;

  const rows = document.querySelectorAll('.updates-table tbody tr');
  if (!rows.length) return;

  input.addEventListener('input', function () {
    const q = this.value.trim().toLowerCase();
    rows.forEach(function (row) {
      const text = row.textContent.toLowerCase();
      row.style.display = (!q || text.includes(q)) ? '' : 'none';
    });
  });
})();
