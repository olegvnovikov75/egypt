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
