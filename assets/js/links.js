/* Links on the site have no .html (GitHub Pages serves /other as other.html).
   When the pages are opened straight from disk (file://) the browser can't do that,
   so add .html / index.html on click. Online nothing changes. */
(function () {
  if (location.protocol !== 'file:') return;
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[href]');
    if (!a || a.target === '_blank') return;
    var href = a.getAttribute('href');
    if (/^(?:[a-z]+:|#|\/\/)/i.test(href)) return;
    var hash = href.indexOf('#') >= 0 ? href.slice(href.indexOf('#')) : '';
    var path = hash ? href.slice(0, href.indexOf('#')) : href;
    if (path === '' || /\.[a-z0-9]+$/i.test(path)) return;
    path = /\/$/.test(path) ? path + 'index.html' : path + '.html';
    e.preventDefault();
    location.href = path + hash;
  }, true);
})();
