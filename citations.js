/* Citation counts, read from citations.json: a copy of the Google Scholar profile
   (scripts/update_citations.py rewrites it). A badge is shown only when the count is
   above zero, and no third-party request is made. The texts follow <html lang>; citations.json is
   read next to this script, so the pages in fr/ find it too. */
(function () {
    'use strict';

    var TEXTS = {
        en: { months: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
              one: ' citation', many: ' citations', where: ' on Google Scholar', first: '1' },
        fr: { months: ['janv.', 'févr.', 'mars', 'avr.', 'mai', 'juin', 'juil.', 'août', 'sept.', 'oct.', 'nov.', 'déc.'],
              one: '\u00a0citation', many: '\u00a0citations', where: ' sur Google Scholar', first: '1er' }
    };
    var pageLang = (document.documentElement.getAttribute('lang') || 'en').toLowerCase().split('-')[0];
    var T = TEXTS[pageLang] || TEXTS.en;
    var DATA_URL = 'citations.json';
    try { DATA_URL = new URL('citations.json', document.currentScript.src).href; } catch (err) { /* page-relative */ }

    function formatDate(iso) {
        var m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(iso || '');
        if (!m) { return ''; }
        var day = Number(m[3]);
        return (day === 1 ? T.first : String(day)) + ' ' + T.months[Number(m[2]) - 1] + ' ' + m[1];
    }

    function renderBadge(el, count) {
        var titleEl = el.querySelector('.pub-title');
        if (!titleEl) { return; }
        var badge = document.createElement('span');
        badge.className = 'cite-count';
        badge.textContent = count + (count === 1 ? T.one : T.many);
        titleEl.appendChild(badge);
    }

    function run() {
        var entries = document.querySelectorAll('[data-doi]');
        if (!entries.length) { return; }
        fetch(DATA_URL, { cache: 'no-store' })
            .then(function (r) { return r.ok ? r.json() : null; })
            .then(function (d) {
                if (!d || !d.counts) { return; }
                var sum = 0;
                Array.prototype.forEach.call(entries, function (el) {
                    var c = d.counts[el.getAttribute('data-doi')];
                    if (typeof c === 'number' && c > 0) { renderBadge(el, c); sum += c; }
                });
                var total = (typeof d.total === 'number') ? d.total : sum;
                var totalEl = document.getElementById('citation-total');
                if (totalEl && total > 0) {
                    var when = formatDate(d.updated);
                    totalEl.textContent = total + (total === 1 ? T.one : T.many) +
                        T.where + (when ? ' (' + when + ')' : '');
                    totalEl.hidden = false;
                }
            })
            .catch(function () { /* no badge, no total */ });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', run);
    } else {
        run();
    }
})();
