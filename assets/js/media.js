/* Media loading.
   Images: load only when the visitor gets within a screen of them, in reading order
   (top to bottom), a few at a time — so the first ones arrive fast instead of every
   picture on the page sharing the connection at once.
   Looping videos: download and play only near the screen, pause when far away.
   Markup: <img data-src> and <video data-src data-poster data-autoplay>.
   Pages that add media later (the home grid) call phMedia.scan(). */
(function () {
  var MAX = 4;                      // images downloading at the same time
  var active = 0, queue = [];
  var hasIO = 'IntersectionObserver' in window;

  // what is on screen or just below comes first (top to bottom, left to right within a row);
  // anything already scrolled past waits until the rest is done
  function priority(el) {
    var r = el.getBoundingClientRect();
    var key = r.bottom < 0 ? 1e7 - r.bottom : Math.max(0, r.top);
    return key + r.left / 10000;
  }

  function loadImg(img) {
    active++;
    var done = function () { active--; pump(); };
    img.addEventListener('load', done, { once: true });
    img.addEventListener('error', done, { once: true });
    img.src = img.getAttribute('data-src');
    img.removeAttribute('data-src');
  }

  function pump() {
    if (!queue.length) return;
    queue.sort(function (a, b) { return priority(a) - priority(b); });
    while (active < MAX && queue.length) loadImg(queue.shift());
  }

  function play(v) {
    var p = v.play();
    if (p && p.catch) p.catch(function () {});
  }

  function startVideo(v) {
    var poster = v.getAttribute('data-poster');
    if (poster) { v.poster = poster; v.removeAttribute('data-poster'); }
    var src = v.getAttribute('data-src');
    if (src) { v.preload = 'auto'; v.src = src; v.removeAttribute('data-src'); }
    if (v.hasAttribute('data-autoplay')) {
      v.muted = true;
      play(v);
      if (onScreen) onScreen.observe(v);
    }
  }

  // looping videos pause once they are well off screen and resume when they come back
  var onScreen = hasIO ? new IntersectionObserver(function (entries) {
    entries.forEach(function (e) { if (e.isIntersecting) play(e.target); else e.target.pause(); });
  }, { rootMargin: '50% 0px' }) : null;

  // media inside a sideways scroller, a marquee or a scrolling landing frame is clipped by it,
  // so the container is what gets watched
  var waiting = new Map();
  var near = hasIO ? new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (!e.isIntersecting) return;
      near.unobserve(e.target);
      (waiting.get(e.target) || []).forEach(function (el) {
        if (el.tagName === 'VIDEO') startVideo(el); else queue.push(el);
      });
      waiting.delete(e.target);
    });
    pump();
  }, { rootMargin: '100% 0px' }) : null;

  function scan(root) {
    (root || document).querySelectorAll('img[data-src], video[data-src]').forEach(function (el) {
      if (el._phMedia) return;
      el._phMedia = true;
      if (!hasIO) { if (el.tagName === 'VIDEO') startVideo(el); else queue.push(el); return; }
      var target = el.closest('.ph-marquee, .ph-row-many, .ph-browser-view') || el;
      if (!waiting.has(target)) { waiting.set(target, []); near.observe(target); }
      waiting.get(target).push(el);
    });
    if (!hasIO) pump();
  }

  window.phMedia = { scan: scan };
  scan();
})();
