/* Citation counts, read from citations.json: a copy of the Google Scholar profile
   (scripts/update_citations.py rewrites it). A badge is shown only when the count is
   above zero, and no third-party request is made. */
(function () {
    'use strict';

    var MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

    function formatDate(iso) {
        var m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(iso || '');
        if (!m) { return ''; }
        return Number(m[3]) + ' ' + MONTHS[Number(m[2]) - 1] + ' ' + m[1];
    }

    function renderBadge(el, count) {
        var titleEl = el.querySelector('.pub-title');
        if (!titleEl) { return; }
        var badge = document.createElement('span');
        badge.className = 'cite-count';
        badge.textContent = count + (count === 1 ? ' citation' : ' citations');
        titleEl.appendChild(badge);
    }

    function run() {
        var entries = document.querySelectorAll('[data-doi]');
        if (!entries.length) { return; }
        fetch('citations.json', { cache: 'no-store' })
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
                    totalEl.textContent = total + (total === 1 ? ' citation' : ' citations') +
                        ' on Google Scholar' + (when ? ' (' + when + ')' : '');
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
