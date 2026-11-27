#!/usr/bin/env python3
"""Offline, dependency-free integrity checks for the canonical public record.
Run from any directory: python3 tools/validate.py
Checks consistency, not external URL availability or independent factual accuracy.
"""
import json
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://khalid-saqr.github.io/khalid-saqr/"
PREFIX = "/khalid-saqr/"
errors = []
warnings = []

def check(condition, message):
    if not condition:
        errors.append(message)

def read(path):
    return (ROOT / path).read_text(encoding="utf-8")

def load(path):
    return json.loads(read(path))

def unique(items, name):
    counts = Counter(items)
    check(all(v == 1 for v in counts.values()), f"Duplicate {name}: {[k for k,v in counts.items() if v > 1]}")

def local_path(url):
    u = urlsplit(url)
    if u.scheme and u.scheme not in ("http", "https"):
        return None
    if u.netloc and u.netloc != urlsplit(SITE).netloc:
        return None
    path = unquote(u.path)
    if path.startswith(PREFIX):
        path = path[len(PREFIX):]
    elif path.startswith("/"):
        return None
    return path or "index.html"

def local_exists(url, source):
    path = local_path(url)
    if path is not None:
        check((ROOT / path).is_file(), f"{source}: missing local path {path}")

class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = []
        self.links = []
        self.refs = []
        self.script = False
        self.schema_text = []
        self.ref = None
        self.title = False
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get("id"):
            self.ids.append(a["id"])
        if tag == "a" and a.get("href"):
            self.links.append(a["href"])
            if self.ref is not None and a["href"].startswith("https://doi.org/"):
                self.ref["doi"] = a["href"].removeprefix("https://doi.org/")
        if tag == "link" and a.get("href"):
            self.links.append(a["href"])
        if tag == "li" and re.fullmatch(r"ref-\d+", a.get("id", "")):
            self.ref = {"id": a["id"], "type": a.get("data-original-ref"), "title": "", "doi": None}
        if self.ref is not None and tag == "span" and a.get("class") == "title":
            self.title = True
        if tag == "script" and a.get("type") == "application/ld+json":
            self.script = True
    def handle_data(self, text):
        if self.title and self.ref is not None:
            self.ref["title"] += text
        if self.script:
            self.schema_text.append(text)
    def handle_endtag(self, tag):
        if tag == "span" and self.title:
            self.title = False
        if tag == "li" and self.ref is not None:
            self.refs.append(self.ref)
            self.ref = None
        if tag == "script":
            self.script = False

def norm(text):
    return "".join(c for c in text.casefold() if c.isalnum())

def main():
    for path in ROOT.rglob("*.json"):
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except (ValueError, OSError) as exc:
            errors.append(f"{path.relative_to(ROOT)}: {exc}")
    page = Page()
    page.feed(read("index.html"))
    unique(page.ids, "HTML ids")
    for link in page.links:
        if link.startswith("#"):
            check(link[1:] in page.ids, f"Missing anchor {link}")
        else:
            local_exists(link, "index.html")
    check(json.loads("".join(page.schema_text)) == load("data/person.schema.json"), "Inline and standalone JSON-LD disagree")
    publications, doi_index = load("data/publications.json"), load("data/doi-index.json")
    unique([p["id"] for p in publications], "publication ids")
    by_id = {p["id"]: p for p in publications}
    doi_pubs = [p for p in publications if p.get("doi")]
    unique([p["doi"].lower() for p in doi_pubs], "DOIs")
    unique([p["id"] for p in doi_index], "DOI index ids")
    check({p["id"] for p in doi_index} == {p["id"] for p in doi_pubs}, "DOI index coverage differs from publication export")
    for p in doi_index:
        check(p["id"] in by_id and all(by_id[p["id"]].get(k) == p.get(k) for k in ("title", "year", "venue", "doi", "doi_url", "scopus_url")), f"DOI index mismatch: {p['id']}")
    claims, evidence = load("data/claims.json"), load("data/evidence.json")
    unique([c["id"] for c in claims], "claim ids")
    unique([e["id"] for e in evidence], "evidence ids")
    cids, eids = {c["id"]: c for c in claims}, {e["id"]: e for e in evidence}
    for c in claims:
        for eid in c["evidence_ids"]:
            check(eid in eids and c["id"] in eids[eid]["supports_claim_ids"], f"Missing reciprocal evidence: {c['id']} -> {eid}")
        for cid in c.get("depends_on_claim_ids", []):
            check(cid in cids and cid != c["id"], f"Invalid claim dependency: {c['id']} -> {cid}")
    for e in evidence:
        for cid in e["supports_claim_ids"]:
            check(cid in cids and e["id"] in cids[cid]["evidence_ids"], f"Missing reciprocal claim: {e['id']} -> {cid}")
        if e.get("url"):
            local_exists(e["url"], e["id"])
    for p in load("data/projects.json"):
        for eid in p["evidenceIds"]:
            check(eid in eids, f"Missing project evidence: {p['id']} -> {eid}")
        if not p["evidenceIds"]:
            warnings.append(f"Project has no published supporting evidence: {p['id']}")
    books = load("data/books.json")
    unique([norm(b["title"]) for b in books], "book titles")
    for b in books:
        for eid in b.get("evidence", []):
            check(eid in eids, f"Missing book evidence: {b['title']} -> {eid}")
        if b.get("publisher_note"):
            warnings.append(b["title"] + ": " + b["publisher_note"])
    studies = [r for r in page.refs if r["type"] != "book"]
    book_refs = [r for r in page.refs if r["type"] == "book"]
    pub_titles = {norm(p["title"]) for p in publications}
    book_titles = {norm(b["title"]) for b in books}
    for r in studies:
        check(norm(r["title"]) in pub_titles, f"Biography study missing from export: {r['id']}")
    for r in book_refs:
        check(norm(r["title"]) in book_titles, f"Biography book missing from index: {r['id']}")
    citations = [l for l in page.links if re.fullmatch(r"#ref-\d+", l)]
    facts = load("data/facts.json")
    corpus = facts["publicationRecord"]
    check((len(publications), len(doi_pubs), len(publications)-len(doi_pubs)) == (corpus["records"], corpus["doi_linked_records"], corpus["records_without_doi"]), "Publication totals disagree with facts")
    scope = facts["biographyBibliography"]
    measured = dict(studies=len(studies), doiLinkedStudies=sum(bool(r["doi"]) for r in studies), books=len(book_refs), entries=len(page.refs), inlineCitationLinks=len(citations), distinctInlineCitedEntries=len(set(citations)))
    for key, value in measured.items():
        check(value == scope[key], f"Bibliography count mismatch: {key}: {value} != {scope[key]}")
    check(len(books) == facts["bookRecord"]["knownTitlesAcrossPublicRecords"], "Book index count differs from facts")
    graph = load("data/identity-graph.json")
    unique([n["id"] for n in graph["nodes"]], "graph node ids")
    nodes = {n["id"] for n in graph["nodes"]}
    for edge in graph["edges"]:
        check(edge["source"] in nodes and edge["target"] in nodes, f"Broken graph edge: {edge}")
    for r in load("data/resources.json"):
        check((ROOT / r["path"]).is_file(), f"Missing resource: {r['path']}")
        local_exists(r["url"], r["label"])
    sitemap = ET.fromstring(read("sitemap.xml"))
    for loc in sitemap.findall(".//{*}loc"):
        local_exists(loc.text, "sitemap")
    check(read("llms.txt") == read("content/llms.md"), "LLM guide mirror differs")
    print(f"Checked {len(publications)} publications, {len(doi_index)} DOI records, {len(page.refs)} bibliography entries, {len(books)} books, {len(claims)} claims, {len(evidence)} evidence records.")
    for w in warnings:
        print("WARNING:", w)
    for e in errors:
        print("ERROR:", e, file=sys.stderr)
    print("PASS" if not errors else f"FAIL: {len(errors)} issue(s)")
    return 1 if errors else 0

if __name__ == "__main__":
    sys.exit(main())
