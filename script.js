(function() {
  var pageWrapper = document.getElementById('pageWrapper');
  var nav = document.getElementById('nav');
  var revealSections = document.querySelectorAll('[data-reveal]');
  var staggerGrids = document.querySelectorAll('[data-reveal-stagger]');
  var mobileToggle = document.getElementById('mobileToggle');
  var navLinks = document.querySelector('.nav-links');
  var revealed = new Set();

  // Full page content floats in from bottom to top on load
  window.addEventListener('load', function() {
    requestAnimationFrame(function() {
      pageWrapper.classList.add('loaded');
    });
  });

  // Sections float in from bottom on first scroll down
  var observer = new IntersectionObserver(function(entries) {
    entries.forEach(function(entry) {
      if (entry.isIntersecting) {
        var el = entry.target;
        if (!revealed.has(el)) {
          revealed.add(el);
          el.classList.add('revealed');
        }
      }
    });
  }, { root: null, rootMargin: '0px 0px -60px 0px', threshold: 0.1 });

  revealSections.forEach(function(section) {
    observer.observe(section);
  });
  staggerGrids.forEach(function(grid) {
    observer.observe(grid);
  });

  // Nav scroll effect
  window.addEventListener('scroll', function() {
    if (window.scrollY > 20) {
      nav.classList.add('scrolled');
    } else {
      nav.classList.remove('scrolled');
    }
  });

  // Mobile toggle
  mobileToggle.addEventListener('click', function() {
    var links = navLinks;
    if (links.style.display === 'flex') {
      links.style.display = 'none';
    } else {
      links.style.display = 'flex';
      links.style.flexDirection = 'column';
      links.style.position = 'absolute';
      links.style.top = '100%';
      links.style.left = '0';
      links.style.right = '0';
      links.style.background = 'rgba(255, 255, 255, 0.98)';
      links.style.backdropFilter = 'blur(20px)';
      links.style.padding = '24px 32px';
      links.style.gap = '20px';
      links.style.borderBottom = '1px solid rgba(0, 0, 0, 0.06)';
    }
  });

  // Close mobile menu on link click
  navLinks.querySelectorAll('a').forEach(function(link) {
    link.addEventListener('click', function() {
      if (window.innerWidth <= 768) {
        navLinks.style.display = 'none';
      }
    });
  });
})();
