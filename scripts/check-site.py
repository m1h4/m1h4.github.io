#!/usr/bin/env python3
"""Validate site content, redirects, app collections, and preserved release assets."""

import argparse
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import unquote, urljoin, urlparse
from xml.etree import ElementTree

import html5lib


BASE_URL = "https://www.mihasoftware.com/"
PROJECT = Path(__file__).resolve().parent.parent


def main():
    arguments = argparse.ArgumentParser(description=__doc__)
    arguments.add_argument("directory", type=Path)
    arguments.add_argument("--analytics", choices=["on", "off"], required=True)
    args = arguments.parse_args()
    directory = args.directory.resolve()
    contract = json.loads((PROJECT / "tests/site-contract.json").read_text())
    errors = []

    def require(condition, message):
        if not condition:
            errors.append(message)

    def destination(path):
        relative = unquote(path).lstrip("/")
        target = directory / relative
        if path.endswith("/") or not relative:
            target /= "index.html"
        elif not target.suffix and (html := target.with_name(target.name + ".html")).is_file():
            target = html  # Cloudflare serves page.html at /page.
        return target

    def public_url(route):
        return urljoin(BASE_URL, route.removesuffix(".html"))

    for route in contract["pages"]:
        require(destination(route).is_file(), "Missing page: " + route)
    for route in contract.get("redirects", {}):
        require(destination(route).is_file(), "Missing redirect: " + route)
    for route in contract.get("retired_pages", []):
        require(not destination(route).exists(), "Retired page remains: " + route)
    for name in contract.get("retired_assets", []) + contract.get("retired_feeds", []):
        require(not (directory / name).exists(), "Retired asset/feed remains: " + name)
    for name, digest in contract["assets_sha256"].items():
        file = directory / name
        require(file.is_file(), "Missing original asset: " + name)
        if file.is_file():
            require(hashlib.sha256(file.read_bytes()).hexdigest() == digest,
                    "Original asset changed: " + name)

    documents = {}
    titles = set()
    for file in sorted(directory.rglob("*.html")):
        name = file.relative_to(directory).as_posix()
        parser = html5lib.HTMLParser(namespaceHTMLElements=False)
        text = file.read_text()
        document = parser.parse(text)
        documents[file] = document
        require(not parser.errors, "Invalid HTML in {}: {}".format(name, parser.errors))
        route = "/" + name.removesuffix("index.html") if name.endswith("index.html") else "/" + name
        if route in contract.get("redirects", {}):
            target = urljoin(BASE_URL, contract["redirects"][route])
            canonical = document.find("head/link[@rel='canonical']")
            refresh = document.find("head/meta[@http-equiv='refresh']")
            require(canonical is not None and canonical.get("href") == target,
                    "Incorrect redirect canonical: " + name)
            require(refresh is not None and refresh.get("content", "").endswith(target),
                    "Incorrect redirect destination: " + name)
            continue
        title = document.find("head/title")
        title_text = "".join(title.itertext()).strip() if title is not None else ""
        require(bool(title_text), "Missing title: " + name)
        require(title_text not in titles, "Duplicate title: " + name)
        titles.add(title_text)
        metadata = {m.get("name", m.get("property")): m.get("content", "")
                    for m in document.findall("head/meta")}
        require(bool(metadata.get("description", "").strip()), "Missing description: " + name)
        require(bool(metadata.get("og:title")) and bool(metadata.get("og:description")),
                "Missing social metadata: " + name)
        route = "/" + name.removesuffix("index.html") if name.endswith("index.html") else "/" + name
        canonical = document.find("head/link[@rel='canonical']")
        require(canonical is not None and canonical.get("href") == public_url(route),
                "Incorrect canonical URL: " + name)
        require(metadata.get("og:url") == public_url(route), "Incorrect social URL: " + name)
        require("https://mihasoftware.com" not in text, "Redirecting hostname in output: " + name)
        require("googletagmanager.com" not in text and "google-analytics.com" not in text,
                "Google Analytics remains in: " + name)
        beacons = document.findall(".//script[@src='https://static.cloudflareinsights.com/beacon.min.js']")
        require(len(beacons) == (1 if args.analytics == "on" and route not in contract.get("analytics_excluded", []) else 0),
                "Incorrect analytics inclusion: " + name)
        for beacon in beacons:
            try:
                token = json.loads(beacon.get("data-cf-beacon", "")).get("token", "")
                require(bool(re.fullmatch(r"[0-9a-f]{32}", token)), "Invalid beacon token: " + name)
            except (ValueError, AttributeError):
                require(False, "Malformed beacon configuration: " + name)
        navigation = document.find(".//nav[@id='main-navigation']")
        require(navigation is not None and [a.get("href") for a in navigation.findall(".//a")] == ["/", "/about/"],
                "Main navigation must contain Apps and About & Contact: " + name)
        require(document.find(".//main[@id='main-content']") is not None, "Missing main landmark: " + name)
        require(len(document.findall(".//h1")) == 1, "Expected one main heading: " + name)
        require(document.find(".//select[@id='appearance']") is not None,
                "Missing appearance preference: " + name)
        require("fonts.googleapis.com" not in text and "maxcdn.bootstrapcdn.com" not in text,
                "External font dependency remains: " + name)
        for image in document.findall(".//img"):
            require(image.get("alt") is not None, "Missing image alternative: " + name)
            require(image.get("width", "").isdigit() and image.get("height", "").isdigit(),
                    "Missing image dimensions: " + name)

    for file, document in documents.items():
        name = file.relative_to(directory).as_posix()
        page_url = urljoin(BASE_URL, name)
        for node in document.iter():
            references = [node.get(attribute) for attribute in ("href", "src") if node.get(attribute)]
            references.extend(candidate.strip().split()[0] for candidate in node.get("srcset", "").split(",")
                              if candidate.strip())
            for value in references:
                url = urlparse(urljoin(page_url, value))
                if url.scheme not in ("http", "https") or url.hostname != "www.mihasoftware.com":
                    continue
                target = destination(url.path)
                require(target.is_file(), "Broken internal reference in {}: {}".format(name, value))
                if url.fragment and target in documents:
                    ids = {element.get("id") for element in documents[target].iter()}
                    require(unquote(url.fragment) in ids,
                            "Missing fragment in {}: {}".format(name, value))

    for name in contract["feeds"]:
        file = directory / name
        require(file.is_file(), "Missing RSS feed: " + name)
        if file.is_file():
            try:
                feed = ElementTree.parse(file)
                require(feed.getroot().tag == "rss", "Not an RSS feed: " + name)
                require(bool(feed.findall("channel/item")), "Empty RSS feed: " + name)
                for link in feed.findall(".//link"):
                    require((link.text or "").startswith(BASE_URL), "Incorrect RSS hostname: " + name)
            except ElementTree.ParseError as error:
                require(False, "Invalid feed {}: {}".format(name, error))

    try:
        sitemap = ElementTree.parse(directory / "sitemap.xml")
        locations = [element.text for element in sitemap.findall(".//{*}loc")]
        require(set(locations) == {public_url(route) for route in contract["pages"]},
                "Sitemap does not match content pages")
    except (OSError, ElementTree.ParseError) as error:
        require(False, "Invalid sitemap: " + str(error))
    robots = directory / "robots.txt"
    require(robots.is_file() and "Sitemap: " + BASE_URL + "sitemap.xml" in robots.read_text(),
            "Missing robots sitemap declaration")
    require(not (directory / "tags").exists() and not (directory / "categories").exists(),
            "Unused taxonomy output remains")
    not_found = documents.get(directory / "404.html")
    require(not_found is not None and not_found.find("head/meta[@content='noindex']") is not None,
            "Missing noindex 404 page")
    for route, expected in (("/", {"/events/", "/apps/photo-resize/", "/apps/beam/"}),
                            ("/apps/archive/", {"/apps/analyzed/", "/apps/audio-analyzer/", "/apps/kurve/"})):
        page = documents.get(destination(route))
        cards = page.findall(".//a[@class='app-link']") if page is not None else []
        require({card.get("href") for card in cards} == expected and len(cards) == len(expected),
                "Incorrect app collection: " + route)
    for route, count in (("/", 2), ("/events/", 1), ("/events/index-hr.html", 1),
                         ("/apps/photo-resize/", 1), ("/apps/photo-resize/hr/", 1)):
        page = documents.get(destination(route))
        pictures = page.findall(".//picture[@class='theme-picture']") if page is not None else []
        require(len(pictures) == count, "Missing themed screenshots: " + route)
        for picture in pictures:
            source, image = picture.find("source"), picture.find("img")
            require(source is not None and source.get("media") == "(prefers-color-scheme: dark)"
                    and "-dark_" in source.get("srcset", "") and "data-theme-source" in source.attrib,
                    "Missing system/manual dark screenshot source: " + route)
            require(image is not None and "-light_" in image.get("srcset", "") and bool(image.get("alt", "").strip()),
                    "Missing light screenshot/alternative: " + route)
    for slug, filename in (("analyzed", "Analyzed.exe"), ("audio-analyzer", "AudioAnalyzer.zip"), ("kurve", "kurve.zip")):
        app = documents.get(directory / "apps" / slug / "index.html")
        button = app.find(".//a[@class='button download-button']") if app is not None else None
        require(button is not None and button.get("href") == "/downloads/" + filename,
                "Missing primary download for " + slug)
    unavailable = documents.get(directory / "apps/photo-resize/index.html")
    require(unavailable is not None and unavailable.find(".//a[@class='button download-button']") is None,
            "Unavailable app should not offer a download")

    if errors:
        raise SystemExit("\n".join(errors))
    print("Validated {} HTML pages, {} feeds, and {} unchanged assets; analytics {}.".format(
        len(documents), len(contract["feeds"]), len(contract["assets_sha256"]), args.analytics))


if __name__ == "__main__":
    main()
