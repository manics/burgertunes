# Change the host and port
HOST = "0.0.0.0"
PORT = 81

# TESTING ONLY
#HOST = "localhost"
#PORT = 8080

from flask import Flask, render_template, request, url_for, flash, redirect, session
from yt_dlp import YoutubeDL
from ytmusicapi import YTMusic
import time
import threading
import shutil
import json
import os

print("Server started")

app = Flask(__name__)

ydl_opts = {"format": "bestaudio", "noplaylist": "True",
            "outtmpl": "static/cache/%(id)s.%(ext)s"}

shutil.rmtree("static/cache", ignore_errors=False, onerror=None)
os.mkdir("static/cache")

def SearchMusic(query, searchtype, limit):
    ytmusic = YTMusic()
    search_results = ytmusic.search(
        query, searchtype, None, limit, ignore_spelling=False)
    return search_results


def GetChannel(id):
    ytmusic = YTMusic()
    data = ytmusic.get_artist(id)
    return data


def GetAlbum(id):
    ytmusic = YTMusic()
    data = ytmusic.get_album(id)
    return data


@app.route("/", methods=("GET", "POST"))
def home():
    if request.method == "POST":
        searchkeyword = request.form["searchbar"]
        songresults = SearchMusic(searchkeyword, "songs", 40)
        albumresults = SearchMusic(searchkeyword, "albums", 6)
        return render_template("main.html", results=songresults, albumresults=albumresults, searchkeyword=searchkeyword)

    songresults = SearchMusic("music", "songs", 40)
    albumresults = SearchMusic("music", "albums", 40)

    return render_template("main.html", results=songresults, albumresults=albumresults, startPage=True)


@app.route('/music/<id>')
def music(id, methods=("GET", "POST")):
    shutil.rmtree("static/cache", ignore_errors=False, onerror=None)
    os.mkdir("static/cache")
    with YoutubeDL(ydl_opts) as ydl:
        ytfile = download = ydl.download(id)
        info = ydl.extract_info(id, download=False)
        audiourl = info["formats"][7]["url"]

        imageurl = info["thumbnail"]
        channelid = info["channel_id"]
        audiocontent = "/static/cache/" + id + ".webm"
        title = info["title"]
        artistname = info["creator"]

        results = GetChannel(channelid)

        return render_template("player.html", audiourl=audiocontent, info=info, results=results)


@app.route('/api/music/<id>')
def apimusic(id, methods=("GET", "POST")):
    shutil.rmtree("static/cache", ignore_errors=False, onerror=None)
    os.mkdir("static/cache")
    with YoutubeDL(ydl_opts) as ydl:
        ytfile = download = ydl.download(id)
        info = ydl.extract_info(id, download=False)

        audiocontent = "/static/cache/" + id + ".webm"

        return redirect("/static/cache/" + id + ".webm")

@app.route('/api/album/<id>/<number>')
def apialbum(id, number, methods=("GET", "POST")):
    results = GetAlbum(id)
    songresult = results["tracks"][int(number)]

    shutil.rmtree("static/cache", ignore_errors=False, onerror=None)
    os.mkdir("static/cache")

    with YoutubeDL(ydl_opts) as ydl:
        ytfile = download = ydl.download(songresult["videoId"])
        audiocontent = "/static/cache/" + songresult["videoId"] + ".webm"

    return redirect(audiocontent)

@app.route('/album/<id>')
def album(id, methods=("GET", "POST")):
    results = GetAlbum(id)
    return render_template("albumview.html", results=results, albumid=id)

@app.errorhandler(404)
def page_not_found(e):
    return render_template("error404.html")

@app.errorhandler(500)
def page_not_found(e):
    return render_template("error500.html")

@app.route('/about')
def about():
    return render_template("about.html")

if __name__ == "__main__":
    from waitress import serve
    serve(app, host=HOST, port=PORT)
    print("Server stopped")
