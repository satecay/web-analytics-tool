from flask import Flask, render_template, request
from analyzer import analyze_website

app = Flask(__name__)

@app.route(, methods=[GET, POST])
def index()
    data = None
    if request.method == POST
        domain = request.form.get(domain)
        data = analyze_website(domain)
    return render_template(index.html, data=data)

import os

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))