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
