/* Custom cursor: a triangle pointer with a curved bottom (in the spirit of Ubuntu's cursor)
   that follows the mouse exactly. Over links, buttons and covers its colours swap.
   Mouse devices only. */
(function () {
  if (!window.matchMedia('(hover: hover) and (pointer: fine)').matches) return;

  var el = document.createElement('div');
  el.className = 'ph-cursor';
  el.innerHTML =
    '<svg viewBox="0 0 24 24" aria-hidden="true">' +
      '<path d="M4 3L14.6 15.6Q8.6 15.46 2.85 19Z"' +
        ' stroke-width="1.5" stroke-linejoin="round" paint-order="stroke"/>' +
    '</svg>';
  document.body.appendChild(el);
  document.documentElement.classList.add('ph-cursor-on');

  var target = null;

  function update() {
    var t = target && target.closest ? target : null;
    el.classList.toggle('is-link', !!(t && t.closest('a, button, [data-cursor]')));
    // the video player hides its controls and the cursor while playing
    el.classList.toggle('is-hidden', !!(t && t.closest('.ph-player.is-idle')));
  }

  window.addEventListener('pointermove', function (e) {
    if (e.pointerType && e.pointerType !== 'mouse') return;
    el.style.transform = 'translate3d(' + e.clientX + 'px,' + e.clientY + 'px,0)';
    el.classList.add('is-on');
    if (e.target !== target) { target = e.target; update(); }
  }, { passive: true });

  // the player goes idle without the mouse moving, so re-check now and then
  setInterval(update, 250);

  // hide when the mouse leaves the window
  document.addEventListener('mouseout', function (e) {
    if (!e.relatedTarget) el.classList.remove('is-on');
  });
  window.addEventListener('mousedown', function () { el.classList.add('is-down'); });
  window.addEventListener('mouseup', function () { el.classList.remove('is-down'); });
})();
