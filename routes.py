"""
Redirect-only shim. Every request returns a 301 to the canonical
deployment, preserving the path and query string. Deployed to the
legacy URL while the app is being phased out.
"""
from app import app
from flask import redirect, request

REDIRECT_TARGET = "https://iitm-cgpa-196060321044.asia-south1.run.app"

ALL_METHODS = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']


@app.route('/', defaults={'path': ''}, methods=ALL_METHODS)
@app.route('/<path:path>', methods=ALL_METHODS)
def redirect_to_canonical(path):
    target = f"{REDIRECT_TARGET}/{path}"
    qs = request.query_string.decode()
    if qs:
        target += f"?{qs}"
    return redirect(target, code=301)
