import datetime
import random

import pygments
import pygments.formatters
import pygments.lexers

from flask import abort, Flask, request, Response
from google.cloud import exceptions, ndb, storage

PROJECT_ID = "mxbin"
BUCKET = "%s.appspot.com" % PROJECT_ID
URL = "https://mxbin.io"
POST = "sprunge"
SYMBOLS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
HELP = f"""
    <html>
        <body>
            <style> a {{ text-decoration: none }} </style>
            <pre>
sprunge(1)                          SPRUNGE                          sprunge(1)

NAME
    sprunge: command line pastebin.

SYNOPSIS
    &lt;command&gt; | curl -F '{POST}=&lt;-' {URL}

DESCRIPTION
    add <a href="https://pygments.org/docs/lexers/">?&lt;lang&gt;</a> to resulting url for line numbers and syntax highlighting
    use <a href="/submit">this form</a> to paste from a browser

EXAMPLES
    ~$ cat bin/ching | curl -F '{POST}=&lt;-' {URL}
    {URL}/aXZI
    ~$ firefox {URL}/aXZI?py#n-7

SEE ALSO
    https://github.com/mxroute/sprunge

            </pre>
        </body>
    </html>
"""

app = Flask(__name__)
ds_client = ndb.Client()
gcs_client = storage.Client()


class Sprunge(ndb.Model):
    name = ndb.StringProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)


@app.route("/", methods=["GET", "POST"])
def main():
    if request.method == "POST":
        with ds_client.context():
            while True:
                name = "".join(
                    SYMBOLS[random.randint(0, len(SYMBOLS) - 1)] for i in range(4)
                )
                if not Sprunge.gql("WHERE name = :1", name).get():
                    break
        gcs_client.bucket(BUCKET).blob(name).upload_from_string(request.form["sprunge"])
        with ds_client.context():
            Sprunge(name=name).put()
        return f"{URL}/{name}\n"
    return HELP


@app.route("/<name>", methods=["GET"])
def get_sprunge(name):
    with ds_client.context():
        s = Sprunge.gql("WHERE name = :1", name).get()
        blob = gcs_client.bucket(BUCKET).blob(s.name) if s else None
        try:
            content = blob.download_as_text() if blob else None
        except exceptions.NotFound:
            content = None
        if not content:
            abort(404)
        syntax = request.query_string.decode()
        if not syntax:
            return Response(content, mimetype="text/plain")
        try:
            lexer = pygments.lexers.get_lexer_by_name(syntax)
        except Exception:
            lexer = pygments.lexers.TextLexer()
        return pygments.highlight(
            content,
            lexer,
            pygments.formatters.HtmlFormatter(
                full=True,
                style="borland",
                lineanchors="n",
                linenos="inline",
            ),
        )


@app.route("/submit", methods=["GET"])
def submit():
    return f"""
        <form action="{URL}" method="POST">
            <textarea name="{POST}" cols="80" rows="24"></textarea>
            <br/>
            <button type="submit">{POST}</button>
        </form>
    """


@app.route("/purge", methods=["GET"])
def purge():
    a_month_ago = (datetime.datetime.now() - datetime.timedelta(days=30)).strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    with ds_client.context():
        for record in Sprunge.gql("WHERE date < DATETIME(:1)", a_month_ago).fetch():
            try:
                gcs_client.bucket(BUCKET).blob(record.name).delete()
            except exceptions.NotFound:
                pass
            record.key.delete()
    return "OK"
