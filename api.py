"""
api.py

A small Flask API that wraps the Search class in backend.py so the
Table.vue component can fetch archery equipment results over HTTP.

Run with:
    pip install -r requirements.txt
    python api.py

Then Table.vue (pointed at http://localhost:5000/search?...) will render
the results.
"""

from urllib.parse import urlparse

from flask import Flask, jsonify, request
from flask_cors import CORS

from backend import Search
from file_interactions import find_wordlist

app = Flask(__name__)

# Allow the Vue dev server (usually a different port, e.g. 5173/8080)
# to call this API. Tighten origins= for production.
CORS(app)


def hostname_from_url(url):
    """Best-effort 'website' label for a result, e.g. 'example.com'."""
    try:
        host = urlparse(url).hostname or url
        return host[4:] if host.startswith("www.") else host
    except Exception:
        return url


def result_to_product(url, result):
    """
    Convert one (url, (found, data)) entry from Search.search() into the
    shape Table.vue expects: { title, price, image, website, link }.

    `data` is either None (nothing usable found for that site) or a tuple
    of (link, title, image, price).
    """
    found, data = result

    if not found or data is None:
        return None

    link, title, image, price = data

    return {
        "title": title,
        "price": price,
        "image": image,
        "website": hostname_from_url(url),
        "link": link,
    }


@app.route("/search", methods=["GET"])
def search():
    """
    GET /search?item=<query>&category=<keyword category>&site_list=<sites wordlist>

    - item: the product to search for, e.g. "Shocq Triumph Recurve Limbs"
      (required)
    - category: which keyword wordlist to match titles/links against,
      e.g. "recurve_limbs" (optional, defaults to "recurve_limbs")
    - site_list: which wordlist of sites to crawl, e.g. "archery_urls"
      (optional, defaults to "archery_urls")
    - max_workers: how many sites to search concurrently (optional,
      defaults to 8)

    Returns: { "products": [ {title, price, image, website, link}, ... ] }
    """
    item = request.args.get("item", "").strip()
    category = request.args.get("category", "recurve_limbs").strip()
    # The list of sites to crawl is a separate wordlist from the keyword
    # category used for matching (see backend.py's own test call at the
    # bottom, which passes these as two different find_wordlist() calls).
    site_list = request.args.get("site_list", "archery_urls").strip()
    max_workers_raw = request.args.get("max_workers", "8").strip()

    try:
        max_workers = max(1, int(max_workers_raw))
    except ValueError:
        return jsonify({"error": "Query parameter 'max_workers' must be an integer."}), 400

    if not item:
        return jsonify({"error": "Query parameter 'item' is required."}), 400

    try:
        sites = find_wordlist(site_list)
    except Exception as exc:
        return jsonify({
            "error": f"Could not load site list '{site_list}': {exc}"
        }), 400

    if not sites:
        return jsonify({"error": f"No sites configured for site list '{site_list}'."}), 400

    try:
        searcher = Search()
        raw_results = searcher.search(category, sites, item, max_workers=max_workers)
    except Exception as exc:
        return jsonify({"error": f"Search failed: {exc}"}), 500

    products = []
    for url, result in raw_results:
        product = result_to_product(url, result)
        if product is not None:
            products.append(product)

    return jsonify({"products": products})


@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "status": "ok",
        "message": "Archery search API is running.",
        "usage": "/search?item=<product name>&category=<wordlist category>",
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)