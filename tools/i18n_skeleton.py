#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Language versions of the site, built from the English pages and kept in step with them.

The English pages stay at the root (the default language). Every other language lives in a
directory named after it, with the same page names:

    index.html               ->  fr/index.html            (https://ammarkheder.com/fr/)
    projects/foehn.html      ->  fr/projects/foehn.html

Commands (run from anywhere; the site root is the parent of this tools/ directory):

  python3 tools/i18n_skeleton.py [build]   For every language of LANGS, create the pages that do not
                                           exist yet from the English page, then run "sync".
                                           A new page keeps the ENGLISH text (translators replace it) and gets:
                                             - <html lang="fr">
                                             - relative paths of styles, scripts, images, videos, PDFs...
                                               rewritten for the extra directory level (../, ../../)
                                             - internal page links pointing to the same language (anchors kept);
                                               root-absolute links (/projects.html, used by 404.html) get /fr/
                                             - canonical and og:url = the French URL
                                           Existing pages are never overwritten (their translation is kept),
                                           unless named with --force.
  python3 tools/i18n_skeleton.py sync      Rewrite the language markup of EVERY page of every language,
                                           without touching the text:
                                             - <html lang>, canonical / og:url of the translated pages
                                             - <link rel="alternate" hreflang="en|fr|x-default"> (indexable pages)
                                             - og:locale and og:locale:alternate
                                             - JSON-LD: a WebPage node (ProfilePage for a Person, CollectionPage
                                               for an ItemList) with url + inLanguage, the original entity as mainEntity
                                             - the language switch "EN · FR" at the end of the navbar, after the menu links
                                               (current language marked with aria-current, links to the same page)
                                             - 404.html: GitHub Pages serves only the root 404.html, so a missing
                                               address under /fr/ is sent to /fr/404.html by a two-line script
                                             - sitemap.xml with <xhtml:link> alternates
  python3 tools/i18n_skeleton.py check     Read-only. Tag balance, JSON-LD, inline scripts (node --check),
                                           local links / assets / #anchors, language markup, missing pages.
                                           Exit status 1 when something is wrong.

Options:
  --lang fr [es ...]        build only these languages (sync and check always cover all of them)
  --force fr/news.html ...  rebuild these pages from English (THEIR TRANSLATION IS LOST); "news.html"
                            means that page in every language of --lang
  --dry-run                 print what would be written, write nothing

Adding a language: add one row to LANGS below, run `python3 tools/i18n_skeleton.py`, translate the new
<code>/ pages (tools/i18n_glossary_<code>.md for the wording), run `python3 tools/i18n_skeleton.py check`.
Adding a page: write the English page (it must match PAGE_GLOBS), run the script: its other-language
skeletons, hreflang links, switch and sitemap entries follow.
The switch sits after the menu links, at the end of the navbar; its styles are in style.css (.lang-switch); site.js and citations.js pick their visible
strings from <html lang>.

Python 3.6+ standard library only.
"""

import argparse
import datetime
import glob
import json
import os
import posixpath
import re
import shutil
import subprocess
import sys
import tempfile
from collections import OrderedDict
from html.parser import HTMLParser
from urllib.parse import urlsplit

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://ammarkheder.com/"
SITE_HOSTS = ("ammarkheder.com", "www.ammarkheder.com")

# One row per language; the first row is the default language, served at the root.
#   code    <html lang>, hreflang, and the inLanguage of the JSON-LD
#   dir     the URL directory of the language ("" for the default language)
#   og      og:locale
#   short   the label in the switch;  name: its tooltip, written in that language
#   switch  the aria-label of the switch, written in that language
LANGS = [
    dict(code="en", dir="", og="en_US", short="EN", name="English", switch="Language"),
    dict(code="fr", dir="fr", og="fr_FR", short="FR", name="Français", switch="Langue"),
]
DEFAULT = LANGS[0]

PAGE_GLOBS = ("*.html", "projects/*.html")   # the pages of the default language
ROOT_ABSOLUTE_PAGES = ("404.html",)          # served at any address: their links stay root-absolute
SITEMAP = "sitemap.xml"

# JSON-LD: the node that carries the page language, by type of the page's main entity.
JSONLD_PAGE_TYPES = ("WebPage", "ProfilePage", "CollectionPage", "AboutPage", "ItemPage", "ContactPage")
JSONLD_WRAPPER = {"Person": "ProfilePage", "ItemList": "CollectionPage"}   # anything else: WebPage

VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param",
             "source", "track", "wbr"}

# ── small helpers ───────────────────────────────────────────────────────────────────────────

ATTR_RE = re.compile(r"""(\s)([^\s=/>"']+)(\s*=\s*)("[^"]*"|'[^']*')""")
SCHEME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")
REFRESH_RE = re.compile(r"""(url\s*=\s*)(['"]?)([^'";\s]+)\2""", re.I)


def read(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8", newline="") as f:
        return f.read()


def exists(rel):
    return os.path.isfile(os.path.join(ROOT, rel))


def write(rel, text, dry_run):
    """Write atomically (the content is complete in memory before the file is opened)."""
    path = os.path.join(ROOT, rel)
    if dry_run:
        print("would write", rel)
        return
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".i18n-", dir=os.path.dirname(path) or ".")
    with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    if os.path.exists(path):
        shutil.copymode(path, tmp)
    else:
        mask = os.umask(0)
        os.umask(mask)
        os.chmod(tmp, 0o666 & ~mask)            # what a plain new file would get
    os.replace(tmp, path)
    print("wrote", rel)


def lang_by_code(code):
    for lang in LANGS:
        if lang["code"] == code:
            return lang
    sys.exit("unknown language %r (LANGS has %s)" % (code, ", ".join(l["code"] for l in LANGS)))


def english_pages():
    """Site paths of the default-language pages, e.g. 'index.html', 'projects/foehn.html'."""
    pages = set()
    for pattern in PAGE_GLOBS:
        for path in glob.glob(os.path.join(ROOT, pattern)):
            pages.add(os.path.relpath(path, ROOT).replace(os.sep, "/"))
    return sorted(pages)


def lang_path(lang, page):
    """File of `page` in `lang`: 'fr/projects/foehn.html'."""
    return posixpath.join(lang["dir"], page) if lang["dir"] else page


def url_path(lang, page):
    """Public path of `page` in `lang`, no leading slash: '' for the home page, 'fr/', 'fr/news.html'."""
    path = lang_path(lang, page)
    if posixpath.basename(path) == "index.html":
        folder = posixpath.dirname(path)
        return folder + "/" if folder else ""
    return path


def page_url(lang, page):
    return SITE + url_path(lang, page)


def present_langs(page):
    return [lang for lang in LANGS if exists(lang_path(lang, page))]


def split_url(url):
    """'a/b.html?x#y' -> ('a/b.html', '?x#y')."""
    cut = len(url)
    for ch in "?#":
        i = url.find(ch)
        if i != -1:
            cut = min(cut, i)
    return url[:cut], url[cut:]


def relative(from_file, to_path, as_dir=False):
    """Relative URL from the page file `from_file` to the site path `to_path` (a directory when as_dir)."""
    rel = posixpath.relpath(to_path or ".", posixpath.dirname(from_file) or ".")
    if as_dir:
        return "./" if rel == "." else rel + "/"
    return rel


def resolve(from_file, path):
    """Site path a relative URL path of `from_file` points to, and whether it names a directory.
    None when it leaves the site."""
    as_dir = path.endswith("/") or posixpath.basename(path) in (".", "..")
    joined = posixpath.normpath(posixpath.join(posixpath.dirname(from_file), path))
    if joined == ".":
        joined = ""
    if joined == ".." or joined.startswith("../"):
        return None, as_dir
    return joined, as_dir


class TagScanner(HTMLParser):
    """Start tags of a page with their exact position: (offset, raw text, tag, attrs).
    Script and style contents are not scanned (the parser treats them as raw text)."""

    def __init__(self, text):
        HTMLParser.__init__(self, convert_charrefs=True)
        self.text = text
        self.line_starts = [0] + [m.end() for m in re.finditer("\n", text)]
        self.tags = []
        self.feed(text)
        self.close()

    def _tag(self, tag, attrs):
        raw = self.get_starttag_text()
        line, col = self.getpos()
        offset = self.line_starts[line - 1] + col
        if not self.text.startswith(raw, offset):
            raise RuntimeError("tag position lost at line %d: %r" % (line, raw[:60]))
        self.tags.append((offset, raw, tag, attrs))

    handle_starttag = _tag
    handle_startendtag = _tag


def rewrite_tags(text, fn):
    """Replace each start tag by fn(tag, attrs_dict, raw); fn returns the new raw text (or None)."""
    out, last = [], 0
    for offset, raw, tag, attrs in TagScanner(text).tags:
        new = fn(tag, {k: (v or "") for k, v in attrs}, raw)
        if new is not None and new != raw:
            out.append(text[last:offset])
            out.append(new)
            last = offset + len(raw)
    out.append(text[last:])
    return "".join(out)


def sub_attrs(raw, fn):
    """Rewrite the quoted attribute values of one raw start tag: fn(name, value) -> new value."""
    def repl(m):
        quoted = m.group(4)
        value = quoted[1:-1]
        new = fn(m.group(2).lower(), value)
        if new is None or new == value:
            return m.group(0)
        return m.group(1) + m.group(2) + m.group(3) + quoted[0] + new + quoted[-1]
    return ATTR_RE.sub(repl, raw)


def is_navigation(tag, attrs, name):
    """Does this attribute name a page to visit (then it follows the language), or a file to load?"""
    rel = attrs.get("rel", "").lower().split()
    if tag in ("a", "area") and name == "href":
        return True
    if tag == "form" and name == "action":
        return True
    if name == "formaction":
        return True
    if tag == "link" and name == "href" and "canonical" in rel:
        return True
    if tag == "meta" and name == "content" and attrs.get("property") == "og:url":
        return True
    return False


# ── URL conversion: English page -> the same page in another language ─────────────────────

class Converter(object):
    def __init__(self, pages):
        self.pages = set(pages)

    def as_page(self, site_path, as_dir):
        """English page named by a site path ('', 'news.html', 'projects/'), or None."""
        candidate = posixpath.join(site_path, "index.html") if (as_dir or site_path == "") else site_path
        return candidate if candidate in self.pages else None

    def url(self, url, page, lang, navigation):
        """`url` as written in the English page `page`, as it must be written in lang's copy of it."""
        if not url or url.startswith("#"):
            return url
        path, rest = split_url(url)
        if url.startswith("//") or SCHEME_RE.match(url):
            if not navigation or not url.lower().startswith(("http://", "https://", "//")):
                return url                      # mailto:, tel:, data:, other sites...
            parts = urlsplit("https:" + url if url.startswith("//") else url)
            if parts.hostname not in SITE_HOSTS:
                return url
            target = self.as_page(parts.path.lstrip("/").rstrip("/"), parts.path.endswith("/"))
            if target is None:
                return url                      # /Foehn/, /TopoFlow/... (other sites on the domain)
            return page_url(lang, target) + rest
        if not path:
            return url                          # "?x": the page itself
        if path.startswith("/"):                # root-absolute: files work at any depth, pages move
            as_dir = path.endswith("/")
            target = self.as_page(path.strip("/"), as_dir) if navigation else None
            if target is None:
                return url
            if as_dir or path == "/":
                return "/" + url_path(lang, target) + rest
            return "/" + lang_path(lang, target) + rest
        site_path, as_dir = resolve(page, path)
        if site_path is None:
            return url
        target = self.as_page(site_path, as_dir) if navigation else None
        new_file = lang_path(lang, page)
        if target is not None:
            dest = lang_path(lang, target)
            if as_dir:
                return relative(new_file, posixpath.dirname(dest), as_dir=True) + rest
            return relative(new_file, dest) + rest
        return relative(new_file, site_path, as_dir=as_dir) + rest

    def srcset(self, value, page, lang):
        out, changed = [], False
        for candidate in value.split(","):
            bits = candidate.strip().split(None, 1)
            if not bits:
                continue
            new = self.url(bits[0], page, lang, False)
            changed = changed or new != bits[0]
            out.append(new + (" " + bits[1] if len(bits) > 1 else ""))
        return ", ".join(out) if changed else value

    def refresh(self, value, page, lang):
        return REFRESH_RE.sub(lambda m: m.group(1) + m.group(2) + self.url(m.group(3), page, lang, True)
                              + m.group(2), value)

    def page(self, text, page, lang):
        """The English page text, converted for `lang` (text untouched)."""
        def tag_fn(tag, attrs, raw):
            rel = attrs.get("rel", "").lower().split()
            if tag == "link" and "alternate" in rel and "hreflang" in attrs:
                return None                     # rewritten by sync

            def attr_fn(name, value):
                if tag == "html" and name == "lang":
                    return lang["code"]
                if name in ("href", "src", "poster", "action", "formaction") or (tag == "object" and name == "data"):
                    return self.url(value, page, lang, is_navigation(tag, attrs, name))
                if name in ("srcset", "imagesrcset"):
                    return self.srcset(value, page, lang)
                if tag == "meta" and name == "content":
                    if attrs.get("property") == "og:url":
                        return self.url(value, page, lang, True)
                    if attrs.get("http-equiv", "").lower() == "refresh":
                        return self.refresh(value, page, lang)
                return None
            return sub_attrs(raw, attr_fn)
        return rewrite_tags(text, tag_fn)


# ── language markup (sync) ──────────────────────────────────────────────────────────────────

ALT_LINE_RE = re.compile(r"^[ \t]*<link\b[^>\n]*\bhreflang=[^>\n]*>[ \t]*\n", re.M)
OGLOC_LINE_RE = re.compile(r"""^[ \t]*<meta\b[^>\n]*\bproperty=["']og:locale(?::alternate)?["'][^>\n]*>[ \t]*\n""", re.M)
SWITCH_LINE_RE = re.compile(r'^[ \t]*<span class="lang-switch"[^\n]*</span>[ \t]*\n', re.M)
SCRIPT404_RE = re.compile(r'^[ \t]*<script id="i18n-404">.*?</script>[ \t]*\n', re.M | re.S)
JSONLD_RE = re.compile(r'(<script type="application/ld\+json">)(.*?)(</script>)', re.S)
NAVBAR_RE = re.compile(r'<nav class="navbar"[^>]*>.*?</nav>', re.S)


def head_value(text, kind):
    """href of the canonical link, or content of og:url."""
    for _, _, tag, attrs in TagScanner(text).tags:
        a = {k: (v or "") for k, v in attrs}
        if kind == "canonical" and tag == "link" and "canonical" in a.get("rel", "").lower().split():
            return a.get("href")
        if kind == "og:url" and tag == "meta" and a.get("property") == "og:url":
            return a.get("content")
    return None


def set_head_value(text, kind, value):
    def tag_fn(tag, attrs, raw):
        if kind == "canonical" and tag == "link" and "canonical" in attrs.get("rel", "").lower().split():
            return sub_attrs(raw, lambda n, v: value if n == "href" else None)
        if kind == "og:url" and tag == "meta" and attrs.get("property") == "og:url":
            return sub_attrs(raw, lambda n, v: value if n == "content" else None)
        return None
    return rewrite_tags(text, tag_fn)


def is_noindex(text):
    for _, _, tag, attrs in TagScanner(text).tags:
        a = {k: (v or "") for k, v in attrs}
        if tag == "meta" and a.get("name", "").lower() == "robots" and "noindex" in a.get("content", "").lower():
            return True
    return False


def indexable(text, lang, page):
    """A page that is its own canonical and not noindex: it gets hreflang links and a sitemap entry."""
    return head_value(text, "canonical") == page_url(lang, page) and not is_noindex(text)


def insert_after_line(text, pattern, block):
    """Insert `block` (lines without indentation) after the first line matching `pattern`,
    with that line's indentation. Returns None when no line matches."""
    m = re.search(r"^([ \t]*)" + pattern + r"[^\n]*\n", text, re.M)
    if not m:
        return None
    indent = m.group(1)
    lines = "".join(indent + line + "\n" for line in block)
    return text[:m.end()] + lines + text[m.end():]


def switch_html(cur, page, langs):
    items = []
    here = lang_path(cur, page)
    for lang in langs:
        if lang is cur:
            items.append('<span class="lang-opt" aria-current="true" lang="%s">%s</span>' % (lang["code"], lang["short"]))
            continue
        if page in ROOT_ABSOLUTE_PAGES:
            href = "/" + lang_path(lang, page)
        else:
            href = relative(here, lang_path(lang, page))
        items.append('<a class="lang-opt" href="%s" hreflang="%s" lang="%s" rel="alternate" title="%s">%s</a>'
                     % (href, lang["code"], lang["code"], lang["name"], lang["short"]))
    sep = '<span class="lang-sep" aria-hidden="true">&middot;</span>'
    return ('<span class="lang-switch" role="group" aria-label="%s" translate="no">%s</span>'
            % (cur["switch"], sep.join(items)))


def insert_switch(text, html_line):
    """Put the switch at the end of the navbar, after the menu links (just before </nav>):
    it stays in the bar at every width, next to the hamburger on phones."""
    m = NAVBAR_RE.search(text)
    if not m:
        return text
    i = text.rfind("</nav>", m.start(), m.end())
    if i < 0:
        return text
    line_start = text.rfind("\n", 0, i) + 1
    indent = text[line_start:i]
    if indent.strip():
        return text[:i] + html_line + text[i:]
    return text[:line_start] + indent + "    " + html_line + "\n" + text[line_start:]


def jsonld_with_language(data, lang, page):
    if not isinstance(data, dict) or "@graph" in data:
        return data
    url = page_url(lang, page)
    if data.get("@type") in JSONLD_PAGE_TYPES:
        data["url"] = url
        data["inLanguage"] = lang["code"]
        return data
    context = data.pop("@context", "https://schema.org")
    wrapper = OrderedDict()
    wrapper["@context"] = context
    wrapper["@type"] = JSONLD_WRAPPER.get(data.get("@type"), "WebPage")
    wrapper["url"] = url
    wrapper["inLanguage"] = lang["code"]
    wrapper["mainEntity"] = data
    return wrapper


def dump_jsonld(data, indent):
    """Compact JSON, with the page node on the first line and one key of its mainEntity per line."""
    def compact(value):
        return json.dumps(value, ensure_ascii=False, separators=(", ", ": "))
    entity = data.get("mainEntity") if isinstance(data, dict) else None
    if not isinstance(entity, dict):
        return compact(data)
    head = ", ".join("%s: %s" % (compact(k), compact(v)) for k, v in data.items() if k != "mainEntity")
    keys = ["%s: %s" % (compact(k), compact(v)) for k, v in entity.items()]
    return "{" + head + ",\n" + indent + ' "mainEntity": {' + (",\n" + indent + "  ").join(keys) + "}}"


def fix_jsonld(text, lang, page):
    def repl(m):
        body = m.group(2)
        try:
            data = json.loads(body, object_pairs_hook=OrderedDict)
        except ValueError:
            return m.group(0)                   # check reports it
        data = jsonld_with_language(data, lang, page)
        line_start = text.rfind("\n", 0, m.start()) + 1
        indent = re.match(r"[ \t]*", text[line_start:m.start()]).group(0)
        dumped = dump_jsonld(data, indent).replace("</", "<\\/")
        return m.group(1) + "\n" + indent + dumped + "\n" + indent + m.group(3)
    return JSONLD_RE.sub(repl, text)


def script_404(langs):
    codes = "|".join(re.escape(lang["dir"]) for lang in langs)
    return ('<script id="i18n-404">/* GitHub Pages answers every missing address with this page: under /%s/ '
            'the page of that language is shown (tools/i18n_skeleton.py). */\n'
            "    (function () { var p = location.pathname, m = /^\\/(%s)\\//.exec(p); "
            "if (m && !/\\/404\\.html$/.test(p)) { location.replace('/' + m[1] + '/404.html'); } })();</script>"
            % ("/, /".join(lang["dir"] for lang in langs), codes))


def apply_language_markup(text, lang, page, langs, converter):
    """Everything sync maintains, for one page of one language."""
    # <html lang>
    text = rewrite_tags(text, lambda tag, attrs, raw: sub_attrs(raw, lambda n, v: lang["code"] if n == "lang" else None)
                        if tag == "html" else None)
    # canonical and og:url of a translated page follow the English ones
    if lang is not DEFAULT:
        english = read(lang_path(DEFAULT, page))
        for kind in ("canonical", "og:url"):
            value = head_value(english, kind)
            if value is not None and head_value(text, kind) is not None:
                text = set_head_value(text, kind, converter.url(value, page, lang, True))
    # hreflang alternates
    text = ALT_LINE_RE.sub("", text)
    if len(langs) > 1 and indexable(text, lang, page):
        block = ['<link rel="alternate" hreflang="%s" href="%s">' % (l["code"], page_url(l, page)) for l in langs]
        block.append('<link rel="alternate" hreflang="x-default" href="%s">' % page_url(DEFAULT, page))
        text = insert_after_line(text, r'<link\b[^>\n]*\brel="canonical"', block) or text
    # og:locale
    text = OGLOC_LINE_RE.sub("", text)
    block = ['<meta property="og:locale" content="%s">' % lang["og"]]
    block += ['<meta property="og:locale:alternate" content="%s">' % l["og"] for l in langs if l is not lang]
    new = (insert_after_line(text, r'<meta\b[^>\n]*\bproperty="og:site_name"', block)
           or insert_after_line(text, r'<meta\b[^>\n]*\bproperty="og:type"', block))
    if new is not None:
        text = new
    # JSON-LD
    text = fix_jsonld(text, lang, page)
    # language switch
    text = SWITCH_LINE_RE.sub("", text)
    if len(langs) > 1:
        text = insert_switch(text, switch_html(lang, page, langs))
    # 404: GitHub Pages serves only the root 404.html
    text = SCRIPT404_RE.sub("", text)
    if lang is DEFAULT and page == "404.html":
        others = [l for l in langs if l is not DEFAULT]
        if others:
            m = re.search(r"^([ \t]*)</head>", text, re.M)
            if m:
                text = text[:m.start()] + "    " + script_404(others) + "\n" + text[m.start():]
    return text


# ── sitemap ─────────────────────────────────────────────────────────────────────────────────

def lastmod(rel):
    """Date of the last commit of the file, or today when it has uncommitted changes."""
    today = datetime.date.today().isoformat()
    try:
        status = subprocess.check_output(["git", "-C", ROOT, "status", "--porcelain", "--", rel],
                                         universal_newlines=True, stderr=subprocess.DEVNULL)
        if status.strip():
            return today
        date = subprocess.check_output(["git", "-C", ROOT, "log", "-1", "--format=%cd", "--date=short", "--", rel],
                                       universal_newlines=True, stderr=subprocess.DEVNULL).strip()
        return date or today
    except (OSError, subprocess.CalledProcessError):
        return datetime.date.fromtimestamp(os.path.getmtime(os.path.join(ROOT, rel))).isoformat()


def build_sitemap(pages, converter):
    """sitemap.xml: every indexable page in every language, with its alternates.
    Keeps the order of the current sitemap; new pages are appended."""
    order = []
    if exists(SITEMAP):
        for loc in re.findall(r"<loc>([^<]+)</loc>", read(SITEMAP)):
            parts = urlsplit(loc.strip())
            if parts.hostname in SITE_HOSTS and not any(l["dir"] and parts.path.startswith("/" + l["dir"] + "/")
                                                        for l in LANGS):
                p = converter.as_page(parts.path.strip("/"), parts.path.endswith("/"))
                if p and p not in order:
                    order.append(p)
    order += [p for p in pages if p not in order]
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for page in order:
        if page not in pages or not exists(page) or not indexable(read(page), DEFAULT, page):
            continue
        langs = present_langs(page)
        for lang in langs:
            lines.append("  <url>")
            lines.append("    <loc>%s</loc>" % page_url(lang, page))
            lines.append("    <lastmod>%s</lastmod>" % lastmod(lang_path(lang, page)))
            if len(langs) > 1:
                for alt in langs:
                    lines.append('    <xhtml:link rel="alternate" hreflang="%s" href="%s"/>' % (alt["code"], page_url(alt, page)))
                lines.append('    <xhtml:link rel="alternate" hreflang="x-default" href="%s"/>' % page_url(DEFAULT, page))
            lines.append("  </url>")
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


# ── commands ────────────────────────────────────────────────────────────────────────────────

def cmd_sync(pages, converter, dry_run):
    changed = 0
    for page in pages:
        langs = present_langs(page)
        for lang in langs:
            rel = lang_path(lang, page)
            text = read(rel)
            new = apply_language_markup(text, lang, page, langs, converter)
            if new != text:
                write(rel, new, dry_run)
                changed += 1
    sitemap = build_sitemap(pages, converter)
    if not exists(SITEMAP) or read(SITEMAP) != sitemap:
        write(SITEMAP, sitemap, dry_run)
        changed += 1
    print("sync: %d file(s) %s" % (changed, "to change" if dry_run else "changed"))


def cmd_build(pages, converter, langs, force, dry_run):
    forced = set()
    for item in force:
        item = item.strip("/")
        if any(item == lang_path(l, p) for l in langs for p in pages):
            forced.add(item)
        elif item in pages:
            forced.update(lang_path(l, item) for l in langs)
        else:
            sys.exit("--force: %s is not a page of %s" % (item, ", ".join(l["code"] for l in langs)))
    created = 0
    for lang in langs:
        if lang is DEFAULT:
            continue
        for page in pages:
            rel = lang_path(lang, page)
            if exists(rel) and rel not in forced:
                continue
            text = converter.page(read(page), page, lang)
            # language markup of the English page does not belong to the copy; sync writes it anew
            text = SCRIPT404_RE.sub("", SWITCH_LINE_RE.sub("", OGLOC_LINE_RE.sub("", ALT_LINE_RE.sub("", text))))
            write(rel, text, dry_run)
            created += 1
    print("build: %d page(s) %s" % (created, "to write" if dry_run else "written"))
    if dry_run:
        print("(sync after a real build would then update every page and %s)" % SITEMAP)
        return
    cmd_sync(pages, converter, dry_run)


class Balance(HTMLParser):
    """Every non-void element closed, in order."""

    def __init__(self):
        HTMLParser.__init__(self, convert_charrefs=True)
        self.stack, self.errors = [], []

    def handle_starttag(self, tag, attrs):
        if tag not in VOID_TAGS:
            self.stack.append((tag, self.getpos()[0]))

    def handle_startendtag(self, tag, attrs):
        pass                                    # <path ... />, <br/>: nothing left open

    def handle_endtag(self, tag):
        if tag in VOID_TAGS:
            self.errors.append("line %d: </%s> on a void element" % (self.getpos()[0], tag))
            return
        if self.stack and self.stack[-1][0] == tag:
            self.stack.pop()
            return
        top = self.stack[-1] if self.stack else ("nothing", 0)
        self.errors.append("line %d: </%s> closes <%s> of line %d" % (self.getpos()[0], tag, top[0], top[1]))
        if tag in [t for t, _ in self.stack]:
            while self.stack[-1][0] != tag:
                self.stack.pop()
            self.stack.pop()


def check_page(rel, text, lang, page, langs, ids_of, node):
    problems = []
    bal = Balance()
    bal.feed(text)
    bal.close()
    problems += bal.errors
    problems += ["line %d: <%s> never closed" % (line, tag) for tag, line in bal.stack]
    # scripts
    for m in re.finditer(r"<script\b([^>]*)>(.*?)</script>", text, re.S):
        attrs, body = m.group(1), m.group(2)
        if "src=" in attrs or not body.strip():
            continue
        if "application/ld+json" in attrs:
            try:
                json.loads(body)
            except ValueError as e:
                problems.append("JSON-LD does not parse: %s" % e)
        elif node:
            with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as f:
                f.write(body)
            res = subprocess.run([node, "--check", f.name], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 universal_newlines=True)
            os.unlink(f.name)
            if res.returncode:
                lines = [l for l in res.stderr.splitlines() if "Error" in l] or res.stderr.strip().splitlines()[-1:]
                problems.append("inline script: node --check failed: %s" % lines[0].strip())
    # links, files and anchors
    for _, raw, tag, attrs in TagScanner(text).tags:
        a = {k: (v or "") for k, v in attrs}
        urls = []
        for name in ("href", "src", "poster", "action"):
            if name in a:
                urls.append(a[name])
        for name in ("srcset", "imagesrcset"):
            if name in a:
                urls += [c.strip().split()[0] for c in a[name].split(",") if c.strip()]
        if tag == "meta" and a.get("http-equiv", "").lower() == "refresh":
            m = REFRESH_RE.search(a.get("content", ""))
            if m:
                urls.append(m.group(3))
        for url in urls:
            if not url or url.startswith("//") or SCHEME_RE.match(url):
                continue
            path, rest = split_url(url)
            frag = rest.split("#", 1)[1] if "#" in rest else ""
            if not path:
                target = rel
            elif path.startswith("/"):
                target, as_dir = path.lstrip("/"), path.endswith("/")
                target = posixpath.normpath(target) if target else ""
                if target == ".":
                    target = ""
                if as_dir or target == "" or os.path.isdir(os.path.join(ROOT, target)):
                    target = posixpath.join(target, "index.html") if target else "index.html"
            else:
                target, as_dir = resolve(rel, path)
                if target is None:
                    problems.append("%s leaves the site" % url)
                    continue
                if as_dir or target == "" or os.path.isdir(os.path.join(ROOT, target)):
                    target = posixpath.join(target, "index.html") if target else "index.html"
            if not exists(target):
                problems.append("<%s> %s: no file %s" % (tag, url, target))
                continue
            if frag and target.endswith(".html") and frag not in ids_of(target):
                problems.append("<%s> %s: no id=\"%s\" in %s" % (tag, url, frag, target))
    # language markup
    m = re.search(r"<html\b[^>]*\blang=\"([^\"]*)\"", text)
    if not m or m.group(1) != lang["code"]:
        problems.append("<html lang> is %r, expected %r" % (m.group(1) if m else None, lang["code"]))
    if len(langs) > 1 and NAVBAR_RE.search(text):
        n = len(re.findall(r'class="lang-switch"', text))
        if n != 1:
            problems.append("%d language switch(es) in the page, expected 1" % n)
    english = read(page)
    if len(langs) > 1 and indexable(english, DEFAULT, page):
        found = set(re.findall(r'<link rel="alternate" hreflang="([^"]+)" href="([^"]+)">', text))
        wanted = {(l["code"], page_url(l, page)) for l in langs} | {("x-default", page_url(DEFAULT, page))}
        if found != wanted:
            problems.append("hreflang links: missing %s, unexpected %s" % (sorted(wanted - found), sorted(found - wanted)))
        if head_value(text, "canonical") != page_url(lang, page):
            problems.append("canonical is %s, expected %s" % (head_value(text, "canonical"), page_url(lang, page)))
    if 'property="og:' in text and ('<meta property="og:locale" content="%s">' % lang["og"]) not in text:
        problems.append("og:locale %s missing" % lang["og"])
    return problems


def cmd_check(pages):
    node = shutil.which("node")
    if not node:
        print("note: node not found, inline scripts are not checked")
    cache = {}

    def ids_of(rel):
        if rel not in cache:
            cache[rel] = set(re.findall(r'\bid="([^"]+)"', read(rel)))
        return cache[rel]

    total = 0
    for page in pages:
        langs = present_langs(page)
        for lang in LANGS:
            rel = lang_path(lang, page)
            if lang not in langs:
                print("MISSING  %s (run: python3 tools/i18n_skeleton.py)" % rel)
                total += 1
                continue
            problems = check_page(rel, read(rel), lang, page, langs, ids_of, node)
            total += len(problems)
            for p in problems:
                print("%-34s %s" % (rel, p))
    if exists(SITEMAP):
        sm = read(SITEMAP)
        for lang in LANGS:
            for page in pages:
                if exists(lang_path(lang, page)) and indexable(read(page), DEFAULT, page) \
                        and "<loc>%s</loc>" % page_url(lang, page) not in sm:
                    print("%-34s not in %s" % (lang_path(lang, page), SITEMAP))
                    total += 1
    print("check: %d page file(s), %d problem(s)" % (sum(len(present_langs(p)) for p in pages), total))
    return 1 if total else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog="See the top of this file for what each command writes.")
    ap.add_argument("command", nargs="?", default="build", choices=("build", "sync", "check"))
    ap.add_argument("--lang", nargs="+", default=None, help="languages to build (default: all of LANGS)")
    ap.add_argument("--force", nargs="+", default=[], help="pages to rebuild from English (loses their translation)")
    ap.add_argument("--dry-run", action="store_true", help="write nothing, print what would change")
    args = ap.parse_args()

    pages = english_pages()
    converter = Converter(pages)
    if args.command == "check":
        sys.exit(cmd_check(pages))
    if args.command == "sync":
        cmd_sync(pages, converter, args.dry_run)
        return
    langs = [lang_by_code(c) for c in args.lang] if args.lang else LANGS
    cmd_build(pages, converter, langs, args.force, args.dry_run)


if __name__ == "__main__":
    main()
