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

/* === SHARED MAST-SLIDE v1 === */
/* Шапка-слайдер (идея Шефа 30.10): сдвигаешь верхнюю строку влево —
   из-за правого края выезжает карточка побратима; отпустил за порогом —
   переправляет на страницу другой веры. Палец и мышь. */
(function () {
  'use strict';
  var mast = document.querySelector('.masthead[data-twin-href]');
  if (!mast) return;
  var slide = mast.querySelector('.mslide');
  var peek = mast.querySelector('.mpeek');
  var href = mast.getAttribute('data-twin-href');
  if (!slide || !peek || !href) return;

  var x0 = 0, y0 = 0, px = 0, active = false, decided = false, horiz = false, t0 = 0, gone = false;

  function set(p) { // p: 0..1 — насколько уехали
    var w = mast.clientWidth || 1;
    if (p > 1) p = 1; if (p < 0) p = 0;
    slide.style.transform = 'translate3d(' + (-p * w) + 'px,0,0)';
    peek.style.transform = 'translate3d(' + ((1 - p) * w) + 'px,0,0)';
    slide.style.opacity = String(1 - 0.55 * p);
    peek.style.opacity = String(0.35 + 0.65 * p);
  }
  function snap(to, ms) {
    slide.style.transition = peek.style.transition = 'transform ' + ms + 'ms ease, opacity ' + ms + 'ms ease';
    set(to);
  }
  function start() {
    slide.style.transition = peek.style.transition = 'none';
    x0 = y0 = 0; px = 0; decided = false; horiz = false; t0 = Date.now();
  }
  function down(cx, cy, e) {
    if (gone) return;
    if (e && e.target && e.target.closest && e.target.closest('a,button')) return;
    active = true; start();
    x0 = cx; y0 = cy;
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
    var w = mast.clientWidth || 1;
    px = Math.max(0, Math.min(w, -ddx));      // тянем только влево
    set(px / w);
  }
  function up() {
    if (!active || gone) return;
    active = false;
    if (!horiz) return;
    var w = mast.clientWidth || 1;
    var v = px / Math.max(60, Date.now() - t0); // px/мс
    if (px > w * 0.38 || (v > 0.55 && px > 60)) {
      gone = true;
      snap(1, 180);
      setTimeout(function () { location.href = href; }, 190);
    } else {
      snap(0, 220);
    }
  }

  mast.addEventListener('touchstart', function (e) {
    if (e.touches.length === 1) down(e.touches[0].clientX, e.touches[0].clientY, e);
  }, { passive: true });
  mast.addEventListener('touchmove', function (e) {
    if (active && horiz) e.preventDefault();
    if (e.touches.length === 1) move(e.touches[0].clientX, e.touches[0].clientY);
  }, { passive: false });
  mast.addEventListener('touchend', up);
  mast.addEventListener('touchcancel', up);

  // мышь (десктоп)
  var mdown = false;
  mast.addEventListener('mousedown', function (e) { down(e.clientX, e.clientY, e); mdown = true; });
  window.addEventListener('mousemove', function (e) { if (mdown) move(e.clientX, e.clientY); });
  window.addEventListener('mouseup', function () { if (mdown) { mdown = false; up(); } });

  // клавиатура: Alt + стрелка вправо
  document.addEventListener('keydown', function (e) {
    if (e.altKey && e.key === 'ArrowRight') location.href = href;
  });
})();
