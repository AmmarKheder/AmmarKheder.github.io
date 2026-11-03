/* Shared behaviour for every page (no library): mobile menu, "New" badge expiry, video lightbox,
   language memory, the hero status line and the fade-up reveal on scroll. */
(function () {
    'use strict';

    var LABELS = {
        en: { player: 'Video player', close: 'Close video', video: 'Video' },
        fr: { player: 'Lecteur vidéo', close: 'Fermer la vidéo', video: 'Vidéo' }
    };
    var pageLang = (document.documentElement.getAttribute('lang') || 'en').toLowerCase().split('-')[0];
    var T = LABELS[pageLang] || LABELS.en;

    /* ── mobile menu ───────────────────────────────────────── */
    var toggle = document.getElementById('nav-toggle');
    function closeMenu() { if (toggle && toggle.checked) { toggle.checked = false; } }
    document.addEventListener('click', function (e) {
        var t = e.target;
        if (t && t.closest && t.closest('.nav-links a, .brand')) { closeMenu(); }
    });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') { closeMenu(); } });

    /* ── "New" badges expire on their own (data-until) ─────── */
    Array.prototype.forEach.call(document.querySelectorAll('.news-badge[data-until]'), function (b) {
        var until = Date.parse(b.getAttribute('data-until'));
        if (isNaN(until) || Date.now() <= until) { return; }
        var row = b.closest ? b.closest('li') : null;
        if (row) { row.classList.remove('news-featured'); }
        b.parentNode.removeChild(b);
    });

    /* ── reduced motion: looping clips stay on their poster ── */
    var reduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (reduced) {
        Array.prototype.forEach.call(document.querySelectorAll('video[autoplay]'), function (v) {
            v.removeAttribute('autoplay'); v.pause(); v.load();
        });
    }

    /* ── video lightbox: the YouTube player is created only after a click ── */
    var ALLOW = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share';
    var canDialog = typeof HTMLDialogElement === 'function' && typeof HTMLDialogElement.prototype.showModal === 'function';
    var dlg = null, frame = null, titleEl = null, opener = null;

    function build() {
        dlg = document.createElement('dialog');
        dlg.className = 'video-modal';
        dlg.setAttribute('aria-label', T.player);
        dlg.innerHTML = '<div class="video-modal-bar"><span class="video-modal-title"></span>' +
            '<button type="button" class="video-modal-close">&times;</button></div>' +
            '<div class="video-frame"></div>';
        dlg.querySelector('.video-modal-close').setAttribute('aria-label', T.close);
        document.body.appendChild(dlg);
        frame = dlg.querySelector('.video-frame');
        titleEl = dlg.querySelector('.video-modal-title');
        dlg.querySelector('.video-modal-close').addEventListener('click', function () { dlg.close(); });
        dlg.addEventListener('click', function (e) { if (e.target === dlg) { dlg.close(); } });
        dlg.addEventListener('close', function () {
            frame.innerHTML = '';
            document.documentElement.classList.remove('modal-open');
            if (opener) { try { opener.focus(); } catch (err) { /* ignore */ } opener = null; }
        });
    }

    function embedSrc(a) {
        var id = a.getAttribute('data-yt'), list = a.getAttribute('data-list'), start = a.getAttribute('data-start');
        var q = [];
        var path = id ? encodeURIComponent(id) : 'videoseries';
        if (!id && list) { q.push('list=' + encodeURIComponent(list)); }
        q.push('autoplay=1', 'rel=0');
        if (id && list) { q.push('list=' + encodeURIComponent(list)); }
        if (start) { q.push('start=' + encodeURIComponent(start)); }
        return 'https://www.youtube-nocookie.com/embed/' + path + '?' + q.join('&');
    }

    function openVideo(a) {
        if (!dlg) { build(); }
        var card = a.closest('.video-card');
        var heading = card && card.querySelector('.video-title');
        var title = (heading ? heading.textContent : (a.getAttribute('aria-label') || T.video)).trim();
        var ratio = (a.getAttribute('data-ratio') || '16/9').split('/');
        var portrait = Number(ratio[1]) > Number(ratio[0]);
        dlg.classList.toggle('is-portrait', portrait);
        titleEl.textContent = title;
        frame.innerHTML = '';
        var f = document.createElement('iframe');
        f.title = title;
        f.setAttribute('allow', ALLOW);
        f.setAttribute('referrerpolicy', 'strict-origin-when-cross-origin');
        f.setAttribute('allowfullscreen', '');
        f.src = embedSrc(a);
        frame.appendChild(f);
        opener = a;
        document.documentElement.classList.add('modal-open');
        dlg.showModal();
    }

    document.addEventListener('click', function (e) {
        if (e.defaultPrevented || e.button !== 0 || e.ctrlKey || e.metaKey || e.shiftKey || e.altKey) { return; }
        var a = e.target && e.target.closest ? e.target.closest('a.video-thumb') : null;
        if (!a || !canDialog) { return; }
        e.preventDefault();
        openVideo(a);
    });

    /* ── hero status line: the number of case studies of the Foehn viewer, read from its index (static "3" otherwise;
       same width, so nothing moves) ── */
    var cases = document.querySelector('[data-foehn-cases]');
    if (cases && window.fetch) {
        var ctl = ('AbortController' in window) ? new AbortController() : null;
        var timer = setTimeout(function () { if (ctl) { ctl.abort(); } }, 3000);
        fetch('https://ammarkheder.com/Foehn/viewer/index.json', { mode: 'cors', signal: ctl ? ctl.signal : undefined })
            .then(function (r) { return r.ok ? r.json() : null; })
            .then(function (d) {
                clearTimeout(timer);
                var n = d && d.cases ? Object.keys(d.cases).length : 0;
                if (n > 0) { cases.textContent = String(n); }
            })
            .catch(function () { clearTimeout(timer); });
    }

    /* ── fade-up on scroll (restrained; everything is visible without JS or with reduced motion) ── */
    var items = document.querySelectorAll('.reveal');
    if (!items.length) { return; }
    if (reduced || !('IntersectionObserver' in window)) {
        Array.prototype.forEach.call(items, function (el) { el.classList.add('is-in'); });
        return;
    }
    var pending = Array.prototype.slice.call(items);
    function show(el) {
        if (el.classList.contains('is-in')) { return; }
        el.classList.add('is-in');
        io.unobserve(el);
        var i = pending.indexOf(el);
        if (i > -1) { pending.splice(i, 1); }
    }
    var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) { if (en.isIntersecting) { show(en.target); } });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    pending.forEach(function (el) { io.observe(el); });
    /* Safety net: whatever sits in (or above) the viewport is shown even when the observer is late, e.g. during a
       programmatic scroll or on a stalled first paint. Cheap (a few rects), and it stops once everything is in. */
    function sweep() {
        var limit = (window.innerHeight || document.documentElement.clientHeight) * 0.96;
        pending.slice().forEach(function (el) {
            var r = el.getBoundingClientRect();
            if (r.top < limit && r.bottom > 0 || r.bottom <= 0) { show(el); }
        });
        if (!pending.length) { clearInterval(tick); window.removeEventListener('scroll', sweep); }
    }
    sweep();
    var tick = setInterval(sweep, 400);
    window.addEventListener('scroll', sweep, { passive: true });
})();

/* Language: on a first visit with a French browser, an English page opens its French version (once; the visitor's own
   choice on the EN · FR switch is remembered and always wins). */
(function () {
    var KEY = 'site-lang';
    document.addEventListener('click', function (e) {
        var a = e.target.closest && e.target.closest('a.lang-opt');
        if (!a) return;
        try { localStorage.setItem(KEY, (a.getAttribute('hreflang') || a.getAttribute('lang') || '').slice(0, 2)); } catch (_) {}
    });
    try {
        if (document.documentElement.lang !== 'en' || localStorage.getItem(KEY)) return;
        var first = ((navigator.languages && navigator.languages[0]) || navigator.language || '').toLowerCase();
        if (first.slice(0, 2) !== 'fr') return;
        var alt = document.querySelector('link[rel="alternate"][hreflang="fr"]');
        if (!alt || !alt.href) return;
        localStorage.setItem(KEY, 'fr');
        location.replace(alt.href + location.hash);
    } catch (_) {}
})();
