// КЕМЕТ — интерактив: бургер-меню, подсветка текущего раздела, «звёзды»
(function () {
  'use strict';

  // бургер
  var burger = document.querySelector('.nav__burger');
  var links = document.querySelector('.nav__links');
  if (burger && links) {
    burger.addEventListener('click', function () { links.classList.toggle('on'); });
  }

  // подсветка активного пункта навигации
  var here = location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav__links a').forEach(function (a) {
    var href = a.getAttribute('href') || '';
    if (href.split('/').pop() === here) a.classList.add('on');
  });

  // мерцающие звёзды на главной (лёгкие, без библиотек)
  var hero = document.querySelector('.hero');
  if (hero) {
    for (var i = 0; i < 40; i++) {
      var s = document.createElement('span');
      s.textContent = '·';
      s.style.cssText = 'position:absolute;color:#cdd9f5;opacity:' + (0.2 + Math.random() * 0.6) +
        ';left:' + (Math.random() * 100) + '%;top:' + (Math.random() * 100) +
        '%;font-size:' + (10 + Math.random() * 18) + 'px;pointer-events:none;animation:bob ' +
        (3 + Math.random() * 5) + 's ease-in-out infinite';
      hero.appendChild(s);
    }
  }
})();

/* === SHARED MAST-SLIDE v2 === */
/* Слайдер «верхней строки» (идея Шефа 30.10): две зоны —
   шапка-наименование (.masthead) и верхняя строка навигации (.nav).
   Тянешь влево пальцем или мышью → выезжает золотая карточка побратима
   (или всего соседнего сайта); отпустил за порогом — переправляет.
   Клавиатура: Alt + →. */
(function () {
  'use strict';
  var zones = Array.prototype.slice.call(
    document.querySelectorAll('.masthead[data-twin-href], .nav[data-nav-href]'));
  if (!zones.length) return;

  function attach(zone) {
    var isMast = zone.classList.contains('masthead');
    var href = zone.getAttribute('data-twin-href') || zone.getAttribute('data-nav-href');
    if (!href) return;
    var track = isMast ? zone.querySelector('.mslide') : null;
    var peek;
    if (isMast) {
      peek = zone.querySelector('.mpeek');
    } else {
      var lab = zone.getAttribute('data-nav-label') || 'на другой берег';
      zone.insertAdjacentHTML('afterbegin',
        '<div class="npeekwrap"><div class="npeek" aria-hidden="true"><b></b><small>отпусти — переправишь →</small></div></div>');
      peek = zone.querySelector('.npeek');
      peek.querySelector('b').textContent = lab;
    }
    if (!peek) return;

    var x0 = 0, y0 = 0, px = 0, active = false, decided = false, horiz = false,
        t0 = 0, gone = false, moved = false;

    function set(p) {
      var w = zone.clientWidth || 1;
      if (p > 1) p = 1; if (p < 0) p = 0;
      peek.style.transform = 'translate3d(' + ((1 - p) * w) + 'px,0,0)';
      peek.style.opacity = String(0.35 + 0.65 * p);
      if (track) {
        track.style.transform = 'translate3d(' + (-p * w) + 'px,0,0)';
        track.style.opacity = String(1 - 0.55 * p);
      }
    }
    function snap(to, ms) {
      var tr = 'transform ' + ms + 'ms ease, opacity ' + ms + 'ms ease';
      peek.style.transition = tr;
      if (track) track.style.transition = tr;
      set(to);
    }
    function down(cx, cy, e) {
      if (gone) return;
      if (e && e.target && e.target.closest &&
          e.target.closest('button,.nav__burger,.nav__links')) return;
      active = true; decided = false; horiz = false; px = 0; t0 = Date.now();
      x0 = cx; y0 = cy;
      track && (track.style.transition = 'none');
      peek.style.transition = 'none';
      document.body.style.userSelect = 'none';
    }
    function move(cx, cy) {
      if (!active || gone) return;
      var ddx = cx - x0, ddy = cy - y0;
      if (!decided) {
        if (Math.abs(ddx) + Math.abs(ddy) < 10) return;
        decided = true;
        horiz = Math.abs(ddx) > Math.abs(ddy) * 1.4;
      }
      if (!horiz) return;
      var w = zone.clientWidth || 1;
      px = Math.max(0, Math.min(w, -ddx));
      set(px / w);
    }
    function up() {
      if (!active || gone) return;
      active = false;
      document.body.style.userSelect = '';
      if (!horiz) return;
      var w = zone.clientWidth || 1;
      if (px > 8) moved = true;
      setTimeout(function () { moved = false; }, 400);
      var v = px / Math.max(60, Date.now() - t0);
      if (px > w * 0.3 || (v > 0.5 && px > 50)) {
        gone = true;
        snap(1, 170);
        setTimeout(function () { location.href = href; }, 180);
      } else {
        snap(0, 220);
      }
    }

    // чтобы затяжка не «рождала» клик по ссылке под пальцем
    zone.addEventListener('click', function (e) {
      if (moved) { e.preventDefault(); e.stopPropagation(); }
    }, true);

    zone.addEventListener('touchstart', function (e) {
      if (e.touches.length === 1) down(e.touches[0].clientX, e.touches[0].clientY, e);
    }, { passive: true });
    zone.addEventListener('touchmove', function (e) {
      if (active && horiz) e.preventDefault();
      if (e.touches.length === 1) move(e.touches[0].clientX, e.touches[0].clientY);
    }, { passive: false });
    zone.addEventListener('touchend', up);
    zone.addEventListener('touchcancel', up);

    var mdown = false;
    zone.addEventListener('mousedown', function (e) { down(e.clientX, e.clientY, e); mdown = true; });
    window.addEventListener('mousemove', function (e) { if (mdown) move(e.clientX, e.clientY); });
    window.addEventListener('mouseup', function () { if (mdown) { mdown = false; up(); } });
  }

  zones.forEach(attach);

  // клавиатура: Alt + стрелка вправо → на соседний берег
  document.addEventListener('keydown', function (e) {
    if (e.altKey && e.key === 'ArrowRight') {
      var z = zones[0];
      location.href = z.getAttribute('data-twin-href') || z.getAttribute('data-nav-href');
    }
  });
})();
