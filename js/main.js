/* Abdul's portfolio — shared JS: year, scroll reveal, carousel */
(function () {
  'use strict';

  // Footer year
  var yearEl = document.getElementById('year');
  if (yearEl) yearEl.textContent = new Date().getFullYear();

  // Contact form success state (redirected back with ?sent=1)
  if (window.location.search.indexOf('sent=1') !== -1) {
    var ok = document.getElementById('form-success');
    if (ok) ok.hidden = false;
  }

  // Scroll-reveal (with automatic stagger of sibling groups)
  var els = Array.prototype.slice.call(document.querySelectorAll('.reveal'));

  // Stagger: siblings that share a parent fade in one-by-one (Apple-style cascade).
  var groups = {};
  els.forEach(function (el) {
    var parent = el.parentNode;
    (groups[parent] = groups[parent] || []).push(el);
  });
  Object.keys(groups).forEach(function (key) {
    var list = groups[key];
    if (list.length > 1) {
      list.forEach(function (el, i) {
        el.style.setProperty('--reveal-delay', Math.min(i * 70, 420) + 'ms');
      });
    }
  });

  if (!('IntersectionObserver' in window) || window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    els.forEach(function (el) { el.classList.add('is-visible'); });
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('is-visible'); io.unobserve(e.target); }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -8% 0px' });
    els.forEach(function (el) { io.observe(el); });
  }

  // Carousel (featured projects on homepage)
  var carousel = document.getElementById('carousel');
  if (carousel) {
    var track = carousel.querySelector('.carousel-track');
    var slides = carousel.querySelectorAll('.carousel-slide');
    var prev = carousel.querySelector('.carousel-prev');
    var next = carousel.querySelector('.carousel-next');
    var dotsWrap = carousel.querySelector('.carousel-dots');
    var index = 0;
    var count = slides.length;
    var timer = null;

    function buildDots() {
      for (var i = 0; i < count; i++) {
        (function (n) {
          var d = document.createElement('button');
          d.className = 'carousel-dot' + (n === 0 ? ' is-active' : '');
          d.setAttribute('aria-label', 'Go to project ' + (n + 1));
          d.addEventListener('click', function () { goTo(n); restart(); });
          dotsWrap.appendChild(d);
        })(i);
      }
    }

    function update() {
      track.style.transform = 'translateX(-' + (index * 100) + '%)';
      var dots = dotsWrap.querySelectorAll('.carousel-dot');
      dots.forEach(function (d, i) { d.classList.toggle('is-active', i === index); });
    }

    function goTo(n) {
      index = (n + count) % count;
      update();
    }

    function restart() {
      if (timer) clearInterval(timer);
      timer = setInterval(function () { goTo(index + 1); }, 5000);
    }

    if (count > 1) {
      buildDots();
      prev.addEventListener('click', function () { goTo(index - 1); restart(); });
      next.addEventListener('click', function () { goTo(index + 1); restart(); });
      carousel.addEventListener('mouseenter', function () { if (timer) clearInterval(timer); });
      carousel.addEventListener('mouseleave', restart);
      restart();
    } else {
      prev.style.display = 'none';
      next.style.display = 'none';
    }
  }
})();
