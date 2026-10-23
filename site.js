/* Shared behaviour for every page (no library).
   - the CSS-only mobile menu closes after a tap on one of its links, on the brand, and on Escape */
(function () {
    'use strict';

    var toggle = document.getElementById('nav-toggle');
    function closeMenu() {
        if (toggle && toggle.checked) { toggle.checked = false; }
    }

    document.addEventListener('click', function (e) {
        var t = e.target;
        if (t && t.closest && t.closest('.nav-links a, .brand')) { closeMenu(); }
    });
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') { closeMenu(); }
    });
})();
