/* Citation counts.
   Primary source: citations.json (committed to repo, refreshed by
   scripts/update_citations.py — Google Scholar via the GitHub Actions
   workflow). Fallback: OpenAlex API for any DOI not in the JSON.
   Cache fallbacks 24h in localStorage. */
(function () {
    const CACHE_KEY = 'ak_citations_v1';
    const TTL = 24 * 60 * 60 * 1000;

    let openAlexCache = {};
    try {
        const stored = localStorage.getItem(CACHE_KEY);
        if (stored) {
            const parsed = JSON.parse(stored);
            if (Date.now() - parsed.t < TTL && parsed.data) openAlexCache = parsed.data;
        }
    } catch (e) { /* ignore */ }

    async function loadScholar() {
        try {
            const r = await fetch('citations.json', { cache: 'no-store' });
            if (!r.ok) return null;
            const d = await r.json();
            return (d && d.counts) ? d : null;
        } catch (e) { return null; }
    }

    async function fromOpenAlex(doi) {
        if (Object.prototype.hasOwnProperty.call(openAlexCache, doi)) {
            return openAlexCache[doi];
        }
        try {
            const r = await fetch('https://api.openalex.org/works/doi:' + doi);
            if (!r.ok) { openAlexCache[doi] = null; return null; }
            const d = await r.json();
            const c = (typeof d.cited_by_count === 'number') ? d.cited_by_count : 0;
            openAlexCache[doi] = c;
            return c;
        } catch (e) { openAlexCache[doi] = null; return null; }
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

        const scholar = await loadScholar();
        const sCounts = (scholar && scholar.counts) ? scholar.counts : {};
        let total = 0;
        let counted = 0;
        const tasks = [];

        entries.forEach(function (el) {
            const doi = el.dataset.doi;
            if (Object.prototype.hasOwnProperty.call(sCounts, doi)) {
                const c = sCounts[doi];
                renderBadge(el, c);
                total += c;
                counted++;
                return;
            }
            tasks.push(fromOpenAlex(doi).then(function (c) {
                if (c !== null) {
                    renderBadge(el, c);
                    total += c;
                    counted++;
                }
            }));
        });

        await Promise.all(tasks);
        try {
            localStorage.setItem(CACHE_KEY,
                JSON.stringify({ t: Date.now(), data: openAlexCache }));
        } catch (e) {}

        const totalEl = document.getElementById('citation-total');
        if (totalEl && counted) {
            const src = scholar ? ' (Google Scholar)' : '';
            totalEl.textContent = total + ' citation' + (total === 1 ? '' : 's')
                + ' across ' + counted + ' work' + (counted === 1 ? '' : 's')
                + src;
            totalEl.style.display = '';
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', run);
    } else {
        run();
    }
})();
