/* Home page: avatar swap interactions.
   - Default state: front photo fully visible, Arita illustration hidden.
   - Hover (desktop): instant cross-fade to Arita, returns on mouse leave.
   - Click / tap (any device): persistent toggle (.is-flipped).
   - Keyboard: Enter / Space toggles when focused.
   - On page load: a brief one-shot reveal animation hints that there is something to discover.
*/
(function () {
    const swap = document.querySelector('.avatar-swap');
    if (!swap) return;

    // Make it focusable + announce as a button to assistive tech.
    swap.setAttribute('role', 'button');
    swap.setAttribute('tabindex', '0');
    swap.setAttribute('aria-pressed', 'false');

    function toggle() {
        const flipped = swap.classList.toggle('is-flipped');
        swap.setAttribute('aria-pressed', flipped ? 'true' : 'false');
    }

    swap.addEventListener('click', function (e) {
        e.preventDefault();
        toggle();
    });

    swap.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            toggle();
        }
    });

    // One-shot reveal animation 1.8s after load: briefly flips to Arita then back,
    // signalling the hidden state to first-time visitors.
    setTimeout(function () {
        if (swap.matches(':hover') || swap.classList.contains('is-flipped')) return;
        swap.classList.add('avatar-reveal-once');
        setTimeout(function () { swap.classList.remove('avatar-reveal-once'); }, 1400);
    }, 1800);
})();
