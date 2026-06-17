// Toggle the collapsible side navigation via #side-nav-trigger.
(function () {
  'use strict';

  document.addEventListener('DOMContentLoaded', function () {
    var trigger = document.getElementById('side-nav-trigger');
    var sideNav = document.getElementById('appSideNav');
    var overlay = document.getElementById('side-nav-overlay');
    var closeBtn = document.getElementById('side-nav-close');

    // Side nav only renders on non-dashboard pages; bail out otherwise.
    if (!sideNav) {
      return;
    }

    function openNav() {
      sideNav.classList.add('app-side-nav--open');
      sideNav.setAttribute('aria-hidden', 'false');
      if (overlay) {
        overlay.classList.add('app-side-nav__overlay--visible');
      }
      document.body.classList.add('side-nav-open');
    }

    function closeNav() {
      sideNav.classList.remove('app-side-nav--open');
      sideNav.setAttribute('aria-hidden', 'true');
      if (overlay) {
        overlay.classList.remove('app-side-nav__overlay--visible');
      }
      document.body.classList.remove('side-nav-open');
    }

    function toggleNav(event) {
      event.preventDefault();
      if (sideNav.classList.contains('app-side-nav--open')) {
        closeNav();
      } else {
        openNav();
      }
    }

    if (trigger) {
      trigger.addEventListener('click', toggleNav);
    }
    if (closeBtn) {
      closeBtn.addEventListener('click', closeNav);
    }
    if (overlay) {
      overlay.addEventListener('click', closeNav);
    }

    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape') {
        closeNav();
      }
    });
  });
})();
