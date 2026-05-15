(function() {
  var pageWrapper = document.getElementById('pageWrapper');
  var nav = document.getElementById('nav');
  var revealSections = document.querySelectorAll('[data-reveal]');
  var staggerGrids = document.querySelectorAll('[data-reveal-stagger]');
  var mobileToggle = document.getElementById('mobileToggle');
  var navLinks = document.querySelector('.nav-links');
  var revealed = new Set();

  // ===== SIDERAL TALENT LOGO (canvas) =====
  function drawLogo() {
    var c = document.getElementById('navLogo');
    if (!c) return;
    var ctx = c.getContext('2d');
    c.width = 900; c.height = 655;

    ctx.scale(2.2, 2.2);
    ctx.translate(-136, -97);

    var cx = 340, cy = 186, a = 126, b = 32, omega = 1;
    var Omega = 15 * Math.PI / 180 / (2 * Math.PI);
    var T = 9.8 * Math.PI;
    var phase = -46 * Math.PI / 180;

    function pt(t) {
      var angle = Omega * t + phase;
      return [
        cx + a * Math.cos(omega * t) * Math.cos(angle) + b * Math.sin(omega * t) * Math.sin(angle),
        cy + a * Math.cos(omega * t) * Math.sin(angle) - b * Math.sin(omega * t) * Math.cos(angle)
      ];
    }
    function alpha(t) {
      if (t < 0.5) return 0.15 + Math.pow(t / 0.5, 2.0) * 0.20;
      return 0.35 + Math.pow((t - 0.5) / 0.5, 1.8) * 0.61;
    }
    function lineW(t) {
      if (t < 0.85) return 1.8 + Math.pow(t / 0.85, 1.4) * 1.0;
      var s = (t - 0.85) / 0.15;
      return 2.8 + Math.pow(s, 1.2) * 3.2;
    }

    // Colors adapted from white to blue scheme
    var accent = '74,123,181';  // #4A7BB5
    var dark = '30,30,48';      // #1E1E30

    ctx.save();
    ctx.translate(340, 226); ctx.rotate(-3 * Math.PI / 180); ctx.translate(-340, -226);

    var N = 1000, tStart = 2.87 * Math.PI, tStop = 30.70;
    for (var i = 0; i < N; i++) {
      var tAbs = tStart + (i + 0.5) / N * (T - tStart);
      if (tAbs > tStop) continue;
      var t = (i + 0.5) / N;
      var p0 = pt(tStart + i / N * (T - tStart));
      var p1 = pt(tStart + (i + 1) / N * (T - tStart));
      ctx.beginPath(); ctx.moveTo(p0[0], p0[1]); ctx.lineTo(p1[0], p1[1]);
      ctx.strokeStyle = 'rgba(' + accent + ',' + alpha(t).toFixed(3) + ')';
      ctx.lineWidth = lineW(t); ctx.lineCap = 'round'; ctx.stroke();
    }

    var endPt = pt(31.01);
    ctx.beginPath(); ctx.arc(endPt[0], endPt[1], 10, 0, Math.PI * 2);
    ctx.fillStyle = '#' + rgbToHex(accent);
    ctx.fill();
    ctx.restore();

    function spaced(text, y, font, gap, al, clr) {
      ctx.font = font; ctx.textAlign = 'left'; ctx.textBaseline = 'alphabetic';
      ctx.fillStyle = 'rgba(' + clr + ',' + al + ')';
      var tw = 0;
      for (var j = 0; j < text.length; j++) tw += ctx.measureText(text[j]).width;
      tw += gap * (text.length - 1);
      var sx = 340 - tw / 2;
      for (var k = 0; k < text.length; k++) {
        ctx.fillText(text[k], sx, y);
        sx += ctx.measureText(text[k]).width + gap;
      }
    }

    spaced('SIDERAL', 312, '600 54px "Playfair Display", serif', 18, 1, dark);
    ctx.strokeStyle = 'rgba(' + accent + ',0.6)'; ctx.lineWidth = 0.9;
    ctx.beginPath(); ctx.moveTo(218, 332); ctx.lineTo(272, 332); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(408, 332); ctx.lineTo(462, 332); ctx.stroke();
    spaced('TALENT', 344, '400 16px "Playfair Display", serif', 10, 0.85, accent);
  }

  function rgbToHex(rgb) {
    var parts = rgb.split(',');
    return parts.map(function(p) {
      var h = parseInt(p, 10).toString(16);
      return h.length === 1 ? '0' + h : h;
    }).join('');
  }

  // Draw logo once font loads
  if (document.fonts && document.fonts.load) {
    document.fonts.load('600 54px "Playfair Display"').then(drawLogo).catch(drawLogo);
  } else {
    drawLogo();
  }

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
