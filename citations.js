/* Fetch citation counts from OpenAlex for each publication entry that has
   a data-doi attribute. Cache results in localStorage for 24h. */
(function () {
    const CACHE_KEY = 'ak_citations_v1';
    const TTL = 24 * 60 * 60 * 1000;

    let cache = {};
    try {
        const stored = localStorage.getItem(CACHE_KEY);
        if (stored) {
            const parsed = JSON.parse(stored);
            if (Date.now() - parsed.t < TTL && parsed.data) cache = parsed.data;
        }
    } catch (e) { /* ignore */ }

    async function fetchCount(doi) {
        if (Object.prototype.hasOwnProperty.call(cache, doi)) return cache[doi];
        try {
            const r = await fetch('https://api.openalex.org/works/doi:' + doi);
            if (!r.ok) {
                cache[doi] = null;
                return null;
            }
            const d = await r.json();
            const c = (typeof d.cited_by_count === 'number') ? d.cited_by_count : 0;
            cache[doi] = c;
            return c;
        } catch (e) {
            cache[doi] = null;
            return null;
        }
    }

    function renderBadge(el, count) {
        const titleEl = el.querySelector('.pub-title');
        if (!titleEl) return;
        const badge = document.createElement('span');
        badge.className = 'cite-count';
        const word = count === 1 ? 'citation' : 'citations';
        badge.textContent = count + ' ' + word;
        titleEl.appendChild(badge);
    }

    async function run() {
        const entries = document.querySelectorAll('[data-doi]');
        if (!entries.length) return;
        let total = 0;
        let counted = 0;
        const tasks = [];
        entries.forEach(function (el) {
            const doi = el.dataset.doi;
            tasks.push(fetchCount(doi).then(function (c) {
                if (c !== null) {
                    renderBadge(el, c);
                    total += c;
                    counted++;
                }
            }));
        });
        await Promise.all(tasks);
        try { localStorage.setItem(CACHE_KEY, JSON.stringify({ t: Date.now(), data: cache })); } catch (e) {}
        const totalEl = document.getElementById('citation-total');
        if (totalEl && counted) {
            totalEl.textContent = total + ' citation' + (total === 1 ? '' : 's') + ' across ' + counted + ' work' + (counted === 1 ? '' : 's');
            totalEl.style.display = '';
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', run);
    } else {
        run();
    }
})();
