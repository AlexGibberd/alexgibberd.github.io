/* 28 Cromwell Road — nav, lightbox and scroll reveals. No dependencies. */
(function () {
  'use strict';

  /* ---------- sticky nav: solid once past the hero ---------- */

  var nav = document.getElementById('nav');
  var hero = document.getElementById('top');

  if (nav && hero && 'IntersectionObserver' in window) {
    new IntersectionObserver(function (entries) {
      nav.classList.toggle('is-solid', !entries[0].isIntersecting);
    }, { rootMargin: '-70px 0px 0px 0px' }).observe(hero);
  } else if (nav) {
    nav.classList.add('is-solid');
  }

  /* ---------- mobile menu ---------- */

  var toggle = document.getElementById('navToggle');
  var menu = document.getElementById('navMenu');

  function closeMenu() {
    if (!menu) return;
    menu.classList.remove('is-open');
    toggle.setAttribute('aria-expanded', 'false');
  }

  if (toggle && menu) {
    toggle.addEventListener('click', function () {
      var open = menu.classList.toggle('is-open');
      toggle.setAttribute('aria-expanded', String(open));
    });
    menu.addEventListener('click', function (e) {
      if (e.target.tagName === 'A') closeMenu();
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') closeMenu();
    });
  }

  /* ---------- lightbox ---------- */

  // Every button carrying data-full becomes a lightbox slide, in document order.
  var triggers = Array.prototype.slice.call(document.querySelectorAll('[data-full]'));
  var lb = document.getElementById('lightbox');
  var lbImg = document.getElementById('lbImg');
  var lbCap = document.getElementById('lbCap');
  var lbClose = document.getElementById('lbClose');
  var lbPrev = document.getElementById('lbPrev');
  var lbNext = document.getElementById('lbNext');
  var index = 0;
  var lastFocus = null;

  function show(i) {
    index = (i + triggers.length) % triggers.length;
    var btn = triggers[index];
    var img = btn.querySelector('img');
    lbImg.src = btn.getAttribute('data-full');
    lbImg.alt = img ? img.alt : '';
    lbCap.innerHTML = btn.getAttribute('data-caption') || '';
    var many = triggers.length > 1;
    lbPrev.hidden = !many;
    lbNext.hidden = !many;
  }

  function open(i) {
    lastFocus = document.activeElement;
    show(i);
    lb.hidden = false;
    document.body.classList.add('lb-open');
    lbClose.focus();
  }

  function close() {
    lb.hidden = true;
    lbImg.src = '';
    document.body.classList.remove('lb-open');
    if (lastFocus) lastFocus.focus();
  }

  if (lb && triggers.length) {
    triggers.forEach(function (btn, i) {
      btn.addEventListener('click', function () { open(i); });
    });

    lbClose.addEventListener('click', close);
    lbPrev.addEventListener('click', function () { show(index - 1); });
    lbNext.addEventListener('click', function () { show(index + 1); });

    // Click the backdrop (but not the image or a control) to dismiss.
    lb.addEventListener('click', function (e) {
      if (e.target === lb || e.target.classList.contains('lb__figure')) close();
    });

    document.addEventListener('keydown', function (e) {
      if (lb.hidden) return;
      if (e.key === 'Escape') close();
      else if (e.key === 'ArrowLeft') show(index - 1);
      else if (e.key === 'ArrowRight') show(index + 1);
      else if (e.key === 'Tab') {
        // Keep focus inside the dialog while it is open.
        var focusable = [lbClose, lbPrev, lbNext].filter(function (el) { return !el.hidden; });
        var first = focusable[0];
        var last = focusable[focusable.length - 1];
        if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
        else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
      }
    });

    // Swipe between photographs on touch devices.
    var startX = null;
    lb.addEventListener('touchstart', function (e) { startX = e.touches[0].clientX; }, { passive: true });
    lb.addEventListener('touchend', function (e) {
      if (startX === null) return;
      var dx = e.changedTouches[0].clientX - startX;
      if (Math.abs(dx) > 50) show(index + (dx < 0 ? 1 : -1));
      startX = null;
    }, { passive: true });
  }

  /* ---------- reveal sections on scroll ---------- */

  var targets = document.querySelectorAll('.split__text, .split__media, .gallery__item, .plan__image, .plan__rooms, .specs, .location__map, .location__lists');

  if ('IntersectionObserver' in window && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          io.unobserve(entry.target);
        }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.05 });

    Array.prototype.forEach.call(targets, function (el) {
      el.classList.add('reveal');
      io.observe(el);
    });
  }
})();
