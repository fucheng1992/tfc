(() => {
  const header = document.getElementById('site-header');
  document.getElementById('year').textContent = new Date().getFullYear();

  const updateHeader = () => header.classList.toggle('is-scrolled', window.scrollY > 10);
  updateHeader();
  window.addEventListener('scroll', updateHeader, { passive: true });

  const motionPreference = window.matchMedia('(prefers-reduced-motion: reduce)');
  const videos = [...document.querySelectorAll('video[data-video]')];
  const visibleVideos = new Set();
  const userPausedVideos = new WeakSet();

  const loadVideo = (video) => {
    if (video.dataset.loaded === 'true') return;
    video.querySelectorAll('source[data-src]').forEach((source) => {
      source.src = source.dataset.src;
      source.removeAttribute('data-src');
    });
    video.dataset.loaded = 'true';
    video.preload = 'metadata';
    video.load();
  };

  const playVisibleVideo = (video) => {
    if (document.hidden || motionPreference.matches || userPausedVideos.has(video)) return;
    loadVideo(video);
    video.play().catch(() => {});
  };

  videos.forEach((video) => {
    // Native controls remain usable for keyboard users and manual playback.
    video.addEventListener('focus', () => loadVideo(video), { once: true });
    video.addEventListener('pointerdown', () => loadVideo(video), { once: true });
    video.addEventListener('play', () => userPausedVideos.delete(video));
    video.addEventListener('pause', () => {
      if (visibleVideos.has(video) && !document.hidden && !motionPreference.matches) {
        userPausedVideos.add(video);
      }
    });
  });

  if ('IntersectionObserver' in window) {
    const loadObserver = new IntersectionObserver((entries, observer) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        loadVideo(entry.target);
        observer.unobserve(entry.target);
      });
    }, { rootMargin: '250px 0px' });

    const playbackObserver = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting && entry.intersectionRatio >= 0.35) {
          visibleVideos.add(entry.target);
          playVisibleVideo(entry.target);
        } else {
          visibleVideos.delete(entry.target);
          entry.target.pause();
        }
      });
    }, { threshold: [0, 0.35] });

    videos.forEach((video) => {
      loadObserver.observe(video);
      playbackObserver.observe(video);
    });
  }

  document.addEventListener('visibilitychange', () => {
    visibleVideos.forEach((video) => {
      if (document.hidden) video.pause();
      else playVisibleVideo(video);
    });
  });

  const updateMotionPreference = () => {
    visibleVideos.forEach((video) => {
      if (motionPreference.matches) video.pause();
      else playVisibleVideo(video);
    });
  };
  if (motionPreference.addEventListener) {
    motionPreference.addEventListener('change', updateMotionPreference);
  } else if (motionPreference.addListener) {
    motionPreference.addListener(updateMotionPreference);
  }

  // Keep local previews out of the public page-view count.
  if (location.protocol === 'https:' && location.hostname === 'fucheng1992.github.io' &&
      location.pathname.startsWith('/tfc/')) {
    const counterScript = document.createElement('script');
    counterScript.async = true;
    counterScript.src = 'https://busuanzi.ibruce.info/busuanzi/2.3/busuanzi.pure.mini.js';
    document.head.appendChild(counterScript);
  }
})();
