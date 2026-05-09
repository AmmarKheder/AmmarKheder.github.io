/* Home page interactions:
   1. Scroll-driven avatar swap (smooth crossfade as user scrolls)
   2. Initial reveal animation (subtle hint that the avatar swaps)
*/
(function () {
    const swap = document.querySelector('.avatar-swap');
    if (!swap) return;

    let ticking = false;
    function updateProgress() {
        const rect = swap.getBoundingClientRect();
        const vh = window.innerHeight || document.documentElement.clientHeight;
        // Progress = how far the avatar has travelled through the viewport.
        // 0 when fully below the viewport, 1 when fully above.
        const total = vh + rect.height;
        const scrolled = vh - rect.top;
        const raw = scrolled / total;
        // Bias towards the middle so the swap happens roughly when the avatar
        // is in the upper half of the viewport (most natural reading flow).
        const eased = Math.max(0, Math.min(1, (raw - 0.25) * 1.6));
        swap.style.setProperty('--scroll-progress', eased.toFixed(3));
        ticking = false;
    }
    function onScroll() {
        if (!ticking) {
            window.requestAnimationFrame(updateProgress);
            ticking = true;
        }
    }
    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', onScroll, { passive: true });
    // Initial position
    updateProgress();

    // Initial reveal animation: after 1.8s, briefly flip to Arita then back to photo,
    // signalling visitors that the avatar has a hidden state.
    setTimeout(function () {
        if (swap.matches(':hover')) return;  // skip if user already interacted
        swap.classList.add('avatar-reveal-once');
        setTimeout(function () { swap.classList.remove('avatar-reveal-once'); }, 1400);
    }, 1800);
})();
