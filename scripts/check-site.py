#!/usr/bin/env python3
"""Validate the published site, including the pre-migration URL/asset contract."""

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
    contract = json.loads((PROJECT / "tests/legacy-contract.json").read_text())
    errors = []

    def require(condition, message):
        if not condition:
            errors.append(message)

    def destination(path):
        relative = unquote(path).lstrip("/")
        target = directory / relative
        if path.endswith("/") or not relative:
            target /= "index.html"
        return target

    for route in contract["pages"]:
        require(destination(route).is_file(), "Missing legacy page: " + route)
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
        require(canonical is not None and canonical.get("href") == urljoin(BASE_URL, route),
                "Incorrect canonical URL: " + name)
        require(metadata.get("og:url") == urljoin(BASE_URL, route), "Incorrect social URL: " + name)
        require("https://mihasoftware.com" not in text, "Redirecting hostname in output: " + name)
        require("googletagmanager.com" not in text and "google-analytics.com" not in text,
                "Google Analytics remains in: " + name)
        beacons = document.findall(".//script[@src='https://static.cloudflareinsights.com/beacon.min.js']")
        require(len(beacons) == (1 if args.analytics == "on" else 0),
                "Incorrect analytics inclusion: " + name)
        for beacon in beacons:
            try:
                token = json.loads(beacon.get("data-cf-beacon", "")).get("token", "")
                require(bool(re.fullmatch(r"[0-9a-f]{32}", token)), "Invalid beacon token: " + name)
            except (ValueError, AttributeError):
                require(False, "Malformed beacon configuration: " + name)
        toggle = document.find(".//button[@id='menu-toggle']")
        require(toggle is not None and bool(toggle.get("aria-label"))
                and toggle.get("aria-expanded") == "false"
                and toggle.get("aria-controls") == "main-navigation", "Inaccessible menu button: " + name)
        require(document.find(".//main[@id='main-content']") is not None, "Missing main landmark: " + name)
        require(len(document.findall(".//h1")) == 1, "Expected one main heading: " + name)
        require(document.find(".//select[@id='appearance']") is not None,
                "Missing appearance preference: " + name)
        require("fonts.googleapis.com" not in text and "maxcdn.bootstrapcdn.com" not in text,
                "External font dependency remains: " + name)
        for image in document.findall(".//img"):
            require(bool(image.get("alt", "").strip()), "Missing image alternative: " + name)
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
        require(set(locations) == {urljoin(BASE_URL, route) for route in contract["pages"]},
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
    photos = documents.get(directory / "photos/index.html")
    if photos is not None:
        images = photos.findall(".//img")
        require(len(images) == 4 and images[0].get("loading") == "eager"
                and all(image.get("loading") == "lazy" for image in images[1:]),
                "Photo loading priorities regressed")
        require(all(image.get("srcset") and image.get("sizes") for image in images),
                "Gallery images need responsive sources")
        links = photos.findall(".//a[@data-gallery]")
        require(len(links) == 4 and all(link.get("href", "").startswith("/photos/")
                                      and destination(link.get("href")).is_file() for link in links),
                "Gallery must preserve original-image fallbacks")

    catalogue = documents.get(directory / "apps/index.html")
    if catalogue is not None:
        cards = catalogue.findall(".//a[@class='card-link']")
        app_routes = {route for route in contract["pages"] if route.startswith("/apps/") and route != "/apps/"}
        require({card.get("href") for card in cards} == app_routes,
                "App catalogue must include every app")
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
