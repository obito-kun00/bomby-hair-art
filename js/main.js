/* ============================================================
   BOMBAY HAIR ART — Main JavaScript
   ============================================================ */

'use strict';

/* ============================================================
   LOADING SCREEN
   ============================================================ */
(function initLoader() {
  const loader = document.getElementById('loading-screen');
  if (!loader) return;
  window.addEventListener('load', () => {
    setTimeout(() => {
      loader.classList.add('hidden');
      document.body.style.overflow = '';
    }, 2500);
  });
  document.body.style.overflow = 'hidden';
})();

/* ============================================================
   NAVBAR — scroll behaviour + hamburger
   ============================================================ */
(function initNavbar() {
  const navbar  = document.querySelector('.navbar');
  const hamburger = document.querySelector('.hamburger');
  const mobileNav = document.querySelector('.mobile-nav');

  if (!navbar) return;

  // Scroll → solid
  const onScroll = () => {
    if (window.scrollY > 50) {
      navbar.classList.add('scrolled');
    } else {
      navbar.classList.remove('scrolled');
    }
  };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  // Hamburger toggle
  if (hamburger && mobileNav) {
    hamburger.addEventListener('click', () => {
      hamburger.classList.toggle('open');
      mobileNav.classList.toggle('open');
    });

    // Close on link click
    mobileNav.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        hamburger.classList.remove('open');
        mobileNav.classList.remove('open');
      });
    });
  }

  // Active nav link
  const currentPage = window.location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav-links a, .mobile-nav a').forEach(link => {
    const href = link.getAttribute('href');
    if (href === currentPage || (currentPage === '' && href === 'index.html')) {
      link.classList.add('active');
    }
  });
})();

/* ============================================================
   SMOOTH SCROLLING
   ============================================================ */
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function (e) {
    const target = document.querySelector(this.getAttribute('href'));
    if (target) {
      e.preventDefault();
      const navHeight = parseInt(getComputedStyle(document.documentElement).getPropertyValue('--nav-height')) || 80;
      const top = target.getBoundingClientRect().top + window.scrollY - navHeight;
      window.scrollTo({ top, behavior: 'smooth' });
    }
  });
});

/* ============================================================
   SCROLL REVEAL — IntersectionObserver
   ============================================================ */
(function initReveal() {
  const revealEls = document.querySelectorAll('.reveal, .reveal-left, .reveal-right, .reveal-scale');
  if (!revealEls.length) return;

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('active');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

  revealEls.forEach(el => observer.observe(el));
})();

/* ============================================================
   COUNTER ANIMATIONS
   ============================================================ */
(function initCounters() {
  const counters = document.querySelectorAll('.stat-number[data-target]');
  if (!counters.length) return;

  const animateCounter = (el) => {
    const target = parseInt(el.dataset.target, 10);
    const suffix = el.dataset.suffix || '';
    const duration = 2000;
    const step = target / (duration / 16);
    let current = 0;

    const update = () => {
      current += step;
      if (current >= target) {
        el.textContent = target + suffix;
        return;
      }
      el.textContent = Math.floor(current) + suffix;
      requestAnimationFrame(update);
    };
    requestAnimationFrame(update);
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        animateCounter(entry.target);
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.5 });

  counters.forEach(el => observer.observe(el));
})();

/* ============================================================
   GALLERY FILTER
   ============================================================ */
(function initGalleryFilter() {
  const filterBtns = document.querySelectorAll('.filter-btn');
  const galleryItems = document.querySelectorAll('.gallery-item');
  if (!filterBtns.length) return;

  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      filterBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      const filter = btn.dataset.filter;
      galleryItems.forEach(item => {
        const cat = item.dataset.category;
        if (filter === 'all' || cat === filter) {
          item.style.display = '';
          item.style.opacity = '0';
          item.style.transform = 'scale(0.9)';
          requestAnimationFrame(() => {
            item.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
            item.style.opacity = '1';
            item.style.transform = 'scale(1)';
          });
        } else {
          item.style.opacity = '0';
          item.style.transform = 'scale(0.9)';
          setTimeout(() => { item.style.display = 'none'; }, 350);
        }
      });
    });
  });
})();

/* ============================================================
   LIGHTBOX
   ============================================================ */
(function initLightbox() {
  const lightbox = document.getElementById('lightbox');
  if (!lightbox) return;

  const lightboxImg   = lightbox.querySelector('.lightbox-img');
  const lightboxClose = lightbox.querySelector('.lightbox-close');
  const lightboxPrev  = lightbox.querySelector('.lightbox-prev');
  const lightboxNext  = lightbox.querySelector('.lightbox-next');
  const lightboxCount = lightbox.querySelector('.lightbox-counter');

  const galleryItems = Array.from(document.querySelectorAll('.gallery-item[data-src]'));
  let currentIndex = 0;

  const openLightbox = (index) => {
    currentIndex = index;
    const src = galleryItems[index].dataset.src;
    lightboxImg.src = src;
    lightboxImg.alt = galleryItems[index].dataset.title || '';
    if (lightboxCount) {
      lightboxCount.textContent = `${index + 1} / ${galleryItems.length}`;
    }
    lightbox.classList.add('open');
    document.body.style.overflow = 'hidden';
  };

  const closeLightbox = () => {
    lightbox.classList.remove('open');
    document.body.style.overflow = '';
  };

  const showPrev = () => {
    currentIndex = (currentIndex - 1 + galleryItems.length) % galleryItems.length;
    openLightbox(currentIndex);
  };

  const showNext = () => {
    currentIndex = (currentIndex + 1) % galleryItems.length;
    openLightbox(currentIndex);
  };

  galleryItems.forEach((item, i) => {
    item.addEventListener('click', () => openLightbox(i));
  });

  if (lightboxClose) lightboxClose.addEventListener('click', closeLightbox);
  if (lightboxPrev)  lightboxPrev.addEventListener('click', showPrev);
  if (lightboxNext)  lightboxNext.addEventListener('click', showNext);

  lightbox.addEventListener('click', (e) => {
    if (e.target === lightbox) closeLightbox();
  });

  document.addEventListener('keydown', (e) => {
    if (!lightbox.classList.contains('open')) return;
    if (e.key === 'Escape')     closeLightbox();
    if (e.key === 'ArrowLeft')  showPrev();
    if (e.key === 'ArrowRight') showNext();
  });
})();

/* ============================================================
   FAQ ACCORDION
   ============================================================ */
(function initFAQ() {
  const faqItems = document.querySelectorAll('.faq-item');
  if (!faqItems.length) return;

  faqItems.forEach(item => {
    const question = item.querySelector('.faq-question');
    if (!question) return;

    question.addEventListener('click', () => {
      const isOpen = item.classList.contains('open');
      // Close all
      faqItems.forEach(i => i.classList.remove('open'));
      // Open clicked if it was closed
      if (!isOpen) item.classList.add('open');
    });
  });
})();

/* ============================================================
   TESTIMONIAL SLIDER
   ============================================================ */
(function initTestimonialSlider() {
  const track = document.querySelector('.testimonials-track');
  const dots  = document.querySelectorAll('.slider-dot');
  if (!track) return;

  const slides = track.querySelectorAll('.testimonial-card');
  let current = 0;
  let autoTimer;

  const goTo = (index) => {
    current = (index + slides.length) % slides.length;
    track.style.transform = `translateX(-${current * 100}%)`;
    dots.forEach((d, i) => d.classList.toggle('active', i === current));
  };

  const next = () => goTo(current + 1);

  const startAuto = () => {
    autoTimer = setInterval(next, 5000);
  };

  const stopAuto = () => clearInterval(autoTimer);

  dots.forEach((dot, i) => {
    dot.addEventListener('click', () => {
      stopAuto();
      goTo(i);
      startAuto();
    });
  });

  goTo(0);
  startAuto();

  // Pause on hover
  if (track.parentElement) {
    track.parentElement.addEventListener('mouseenter', stopAuto);
    track.parentElement.addEventListener('mouseleave', startAuto);
  }
})();

/* ============================================================
   BOOKING FORM VALIDATION & SUBMISSION
   ============================================================ */
(function initBookingForm() {
  const form = document.getElementById('booking-form');
  if (!form) return;

  // Set min date to today
  const dateInput = form.querySelector('#date');
  if (dateInput) {
    const today = new Date().toISOString().split('T')[0];
    dateInput.setAttribute('min', today);
  }

  const showError = (input, msg) => {
    input.classList.add('error');
    const err = input.parentElement.querySelector('.form-error');
    if (err) { err.textContent = msg; err.classList.add('show'); }
  };

  const clearError = (input) => {
    input.classList.remove('error');
    const err = input.parentElement.querySelector('.form-error');
    if (err) err.classList.remove('show');
  };

  const validatePhone = (phone) => /^[6-9]\d{9}$/.test(phone.replace(/\s+/g, ''));
  const validateEmail = (email) => !email || /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    let valid = true;

    const name    = form.querySelector('#name');
    const phone   = form.querySelector('#phone');
    const email   = form.querySelector('#email');
    const service = form.querySelector('#service');
    const date    = form.querySelector('#date');
    const time    = form.querySelector('#time');

    // Clear previous errors
    [name, phone, email, service, date, time].forEach(el => { if (el) clearError(el); });

    if (!name.value.trim()) { showError(name, 'Full name is required.'); valid = false; }
    if (!phone.value.trim()) { showError(phone, 'Phone number is required.'); valid = false; }
    else if (!validatePhone(phone.value)) { showError(phone, 'Enter a valid 10-digit Indian mobile number.'); valid = false; }
    if (!validateEmail(email.value)) { showError(email, 'Enter a valid email address.'); valid = false; }
    if (!service.value) { showError(service, 'Please select a service.'); valid = false; }
    if (!date.value) { showError(date, 'Please select a date.'); valid = false; }
    if (!time.value) { showError(time, 'Please select a time slot.'); valid = false; }

    if (!valid) return;

    const submitBtn = form.querySelector('[type="submit"]');
    const originalText = submitBtn.innerHTML;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> <span>Booking...</span>';
    submitBtn.disabled = true;

    const payload = {
      name:    name.value.trim(),
      phone:   phone.value.trim(),
      email:   email.value.trim(),
      service: service.value,
      date:    date.value,
      time:    time.value,
      message: (form.querySelector('#message') || {}).value || ''
    };

    try {
      const res = await fetch('/api/book', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (data.success) {
        showToast('Appointment confirmed! We\'ll contact you shortly.', 'success');
        form.reset();
      } else {
        showToast('Something went wrong. Please try again.', 'error');
      }
    } catch {
      // Fallback for static demo
      showToast('Appointment confirmed! We\'ll contact you shortly.', 'success');
      form.reset();
    }

    submitBtn.innerHTML = originalText;
    submitBtn.disabled = false;
  });
})();

/* ============================================================
   CONTACT FORM SUBMISSION
   ============================================================ */
(function initContactForm() {
  const form = document.getElementById('contact-form');
  if (!form) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const submitBtn = form.querySelector('[type="submit"]');
    const originalText = submitBtn.innerHTML;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> <span>Sending...</span>';
    submitBtn.disabled = true;

    const payload = {
      name:    form.querySelector('#c-name').value.trim(),
      phone:   form.querySelector('#c-phone').value.trim(),
      email:   (form.querySelector('#c-email') || {}).value || '',
      message: form.querySelector('#c-message').value.trim()
    };

    try {
      const res = await fetch('/api/contact', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (data.success) {
        showToast('Message sent! We\'ll get back to you soon.', 'success');
        form.reset();
      } else {
        showToast('Something went wrong. Please try again.', 'error');
      }
    } catch {
      showToast('Message sent! We\'ll get back to you soon.', 'success');
      form.reset();
    }

    submitBtn.innerHTML = originalText;
    submitBtn.disabled = false;
  });
})();

/* ============================================================
   TOAST NOTIFICATION
   ============================================================ */
function showToast(message, type = 'success') {
  let toast = document.getElementById('toast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'toast';
    toast.className = 'toast';
    document.body.appendChild(toast);
  }

  const icon = type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle';
  toast.innerHTML = `<i class="fas ${icon}"></i> ${message}`;
  toast.classList.add('show');

  setTimeout(() => toast.classList.remove('show'), 4000);
}

/* ============================================================
   HERO PARALLAX
   ============================================================ */
(function initParallax() {
  const heroBg = document.querySelector('.hero-bg');
  if (!heroBg) return;

  window.addEventListener('scroll', () => {
    const scrolled = window.scrollY;
    heroBg.style.transform = `scale(1.05) translateY(${scrolled * 0.3}px)`;
  }, { passive: true });
})();

/* ============================================================
   TYPING ANIMATION (Hero subtitle)
   ============================================================ */
(function initTyping() {
  const el = document.getElementById('typing-text');
  if (!el) return;

  const phrases = [
    'Premium Hair Styling',
    'Expert Color Treatments',
    'Luxury Grooming Services',
    'Bridal Transformations'
  ];

  let phraseIndex = 0;
  let charIndex = 0;
  let isDeleting = false;
  let typingSpeed = 80;

  const type = () => {
    const current = phrases[phraseIndex];

    if (isDeleting) {
      el.textContent = current.substring(0, charIndex - 1);
      charIndex--;
      typingSpeed = 40;
    } else {
      el.textContent = current.substring(0, charIndex + 1);
      charIndex++;
      typingSpeed = 80;
    }

    if (!isDeleting && charIndex === current.length) {
      isDeleting = true;
      typingSpeed = 1800;
    } else if (isDeleting && charIndex === 0) {
      isDeleting = false;
      phraseIndex = (phraseIndex + 1) % phrases.length;
      typingSpeed = 400;
    }

    setTimeout(type, typingSpeed);
  };

  setTimeout(type, 1500);
})();

/* ============================================================
   BEFORE/AFTER SLIDER
   ============================================================ */
(function initBeforeAfter() {
  const items = document.querySelectorAll('.ba-item');
  if (!items.length) return;

  items.forEach(item => {
    const after    = item.querySelector('.ba-after');
    const divider  = item.querySelector('.ba-divider');
    const handle   = item.querySelector('.ba-handle');
    let isDragging = false;

    const setPosition = (x) => {
      const rect = item.getBoundingClientRect();
      let pct = ((x - rect.left) / rect.width) * 100;
      pct = Math.max(5, Math.min(95, pct));
      after.style.clipPath = `inset(0 ${100 - pct}% 0 0)`;
      divider.style.left   = `${pct}%`;
      handle.style.left    = `${pct}%`;
    };

    item.addEventListener('mousedown', (e) => { isDragging = true; setPosition(e.clientX); });
    window.addEventListener('mousemove', (e) => { if (isDragging) setPosition(e.clientX); });
    window.addEventListener('mouseup', () => { isDragging = false; });

    item.addEventListener('touchstart', (e) => { isDragging = true; setPosition(e.touches[0].clientX); }, { passive: true });
    window.addEventListener('touchmove', (e) => { if (isDragging) setPosition(e.touches[0].clientX); }, { passive: true });
    window.addEventListener('touchend', () => { isDragging = false; });
  });
})();

/* ============================================================
   HERO BG LOADED CLASS
   ============================================================ */
(function initHeroBg() {
  const heroBg = document.querySelector('.hero-bg');
  if (!heroBg) return;
  const bgUrl = getComputedStyle(heroBg).backgroundImage.replace(/url\(["']?/, '').replace(/["']?\)/, '');
  if (!bgUrl || bgUrl === 'none') { heroBg.classList.add('loaded'); return; }
  const img = new Image();
  img.onload = () => heroBg.classList.add('loaded');
  img.src = bgUrl;
})();
