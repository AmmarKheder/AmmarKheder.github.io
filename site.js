/* Shared behaviour for every page (no library).
   - the CSS-only mobile menu closes after a tap on one of its links, on the brand, and on Escape
   - a "New" badge in the news list disappears after its data-until date
   - looping gallery clips do not autoplay when the visitor prefers reduced motion
   - video cards: a plain click opens the video in a lightbox; the YouTube player is created only then,
     so nothing is requested from YouTube before a click. Ctrl/Cmd/Shift-click, a middle click and
     browsers without <dialog> follow the link to YouTube instead.
   - the labels this script writes follow <html lang> (English pages at the root, French ones in fr/) */
(function () {
    'use strict';

    /* ── labels in the language of the page ──────────────────── */
    var LABELS = {
        en: { player: 'Video player', close: 'Close video', video: 'Video' },
        fr: { player: 'Lecteur vidéo', close: 'Fermer la vidéo', video: 'Vidéo' }
    };
    var pageLang = (document.documentElement.getAttribute('lang') || 'en').toLowerCase().split('-')[0];
    var T = LABELS[pageLang] || LABELS.en;

    /* ── mobile menu ───────────────────────────────────────── */
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

    /* ── "New" badges expire on their own (data-until, a date); the highlighted row goes back to a normal row ── */
    Array.prototype.forEach.call(document.querySelectorAll('.news-badge[data-until]'), function (b) {
        var until = Date.parse(b.getAttribute('data-until'));
        if (isNaN(until) || Date.now() <= until) { return; }
        var row = b.closest ? b.closest('li') : null;
        if (row) { row.classList.remove('news-featured'); }
        b.parentNode.removeChild(b);
    });

    /* ── reduced motion: the looping clips in the galleries stay on their poster ── */
    if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        Array.prototype.forEach.call(document.querySelectorAll('video[autoplay]'), function (v) {
            v.removeAttribute('autoplay');
            v.pause();
            v.load();   /* back to the poster */
        });
    }

    /* ── video lightbox ───────────────────────────────────── */
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
        dlg.addEventListener('click', function (e) { if (e.target === dlg) { dlg.close(); } });   /* backdrop */
        dlg.addEventListener('close', function () {                                              /* button, Escape, backdrop */
            frame.innerHTML = '';                                                                /* removing the iframe stops the sound */
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
})();
