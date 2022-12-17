import os
import json
import shutil
import threading
import time
from ytmusicapi import YTMusic
from yt_dlp import YoutubeDL
from flask import Flask, render_template, request, url_for, flash, redirect, session

# Change the host and port
HOST = "0.0.0.0"
PORT = 81

print("Server started")

app = Flask(__name__)

audioformat = "webm"
ydl_opts = {"format": "bestaudio", "noplaylist": "True",
            "outtmpl": "static/cache/%(id)s." + audioformat}

#ydl_opts = {"format": "bestaudio", "noplaylist": "True",
#            "outtmpl": "static/cache/%(id)s.%(ext)s"}

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

        imageurl = info["thumbnail"]
        channelid = info["channel_id"]
        audiocontent = "/static/cache/" + id + "." + audioformat
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

        return redirect("/static/cache/" + id + "." + audioformat)


@app.route('/api/album/<id>/<number>')
def apialbum(id, number, methods=("GET", "POST")):
    results = GetAlbum(id)
    songresult = results["tracks"][int(number)]

    shutil.rmtree("static/cache", ignore_errors=False, onerror=None)
    os.mkdir("static/cache")

    with YoutubeDL(ydl_opts) as ydl:
        ytfile = download = ydl.download(songresult["videoId"])
        audiocontent = "/static/cache/" + songresult["videoId"] + "." + audioformat

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


if __name__ == "__main__":
    from waitress import serve
    serve(app, host=HOST, port=PORT)
    print("Server stopped")
