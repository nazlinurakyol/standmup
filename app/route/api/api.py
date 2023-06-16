import json
from flask import make_response, jsonify, request, render_template, redirect, url_for
from sqlalchemy import func

from app.model.comedian import Comedian
from app.model.tag import Tag
from app.model.video import Video

from app.model.youtubeLink import YoutubeLink
from app.model import db

# api page
from app.route.api import bp


@bp.route("/api")
def api():
    return render_template("api.html")

# submit form page
@bp.route('/api/submit', methods=['POST'])
def submit():
    youtube_link = request.form.get('youtube_link')
    message = request.form.get('message')
    video_link = YoutubeLink(youtube_link=youtube_link, message=message)

    count = db.session.query(func.count(YoutubeLink.id)).scalar()
    if count > 100:
        print("Server is overload.")
        return redirect(url_for('fail'))

    else:
        if youtube_link is not None:
            if "youtube" in youtube_link:
                db.session.add(video_link)
                db.session.commit()
                return redirect(url_for('api.success'))
            else:
                print("Invalid YouTube link provided.")
                return redirect(url_for('api.fail'))
        else:
            print("YouTube link not provided.")
            return redirect(url_for('api.fail'))

# submit fail page
@bp.route('/api/fail')
def fail():
    return render_template('fail.html')

# submit success page
@bp.route('/api/success')
def success():
    return render_template('success.html')

@bp.route("/api/videos", methods=["POST"])
def addVideo():
    #if application.config["ENV"] == 'development':
    #    return addVideo()
    #else:
    #    return make_response(jsonify({"error": "Not authorized."}), 401)

    content = request.json

    new_video = Video(
        comedian_id=content["comedian_id"],
        title=content["title"],
        link=content["link"],
        description=content["description"],
        is_active=content["isActive"],
        is_ready=content["isReady"]
    )

    db.session.add(new_video)
    db.session.commit()

    return json.dumps(new_video.to_dict())


# get video by id
@bp.route("/api/videos/<video_id>", methods=["GET"])
def getVideo(video_id):
    video = Video.query.get(video_id)
    if video is None:
        return make_response(jsonify({"error": "Video not found"}), 404)
    return json.dumps(video.to_dict())

# get all comedian names with count
@bp.route("/api/comedians", methods=["GET"])
def getCountByName():
    names = (
        db.session.query(Comedian.name, func.count(Video.id))
            .join(Video)
            .group_by(Comedian.id)
            .all()
    )
    if not names:
        return make_response(jsonify({"error": "No comedians found"}), 404)
    namesToDict = dict((x, y) for x, y in names)
    response = json.dumps(namesToDict)
    return json.dumps(response)


# get all comedians
@bp.route("/api/comedians/all", methods=["GET"])
def allComedians():
    comedians = db.session.query(Comedian).all()
    if not comedians:
        return make_response(jsonify({"error": "No comedians found"}), 404)
    response = [comedian.to_dict() for comedian in comedians]
    return json.dumps(response)


# get videos by comedian
@bp.route("/api/comedians/<id>/videos", methods=["GET"])
def getVideoByComedian(id):
    comedians = Video.query.filter_by(comedian_id=id).all()
    response = [comedian.to_dict() for comedian in comedians]
    return json.dumps(response)

# get all videos
@bp.route("/api/videos/all", methods=["GET"])
def allVideos():
    args = request.args
    limit = args.get("limit")
    search = args.get("search")

    query = db.session.query(Video)

    if limit:
        query.limit(limit)
    if search:
        query.filter_by(search)

    videos = query.all()
    response = [video.to_dict() for video in videos]
    return json.dumps(response)


# get random video
@bp.route("/api/random", methods=["GET"])
def order_by_random():
    random = Video.query.order_by(func.random()).first()
    return json.dumps(random.to_dict())

# delete video by id
@bp.route("/api/videos/<video_id>", methods=["DELETE"])
#if application.config["ENV"] == 'development':
    #    return handle_delete_video()
    #else:
    #    return make_response(jsonify({"error": "Not authorized."}), 401)
def delete_video(video_id):
    video = Video.query.get(video_id)
    db.session.delete(video)
    db.session.commit()
    return json.dumps(video.to_dict())



# show stat
@bp.route("/api/stat", methods=["GET"])
def stat():
    total_video_count = db.session.query(db.func.count(Video.id)).scalar()
    total_comedian_count = db.session.query(db.func.count(Comedian.id)).scalar()
    total_tag_count = db.session.query(db.func.count(Tag.id)).scalar()
    names = (
        db.session.query(Comedian.id,Comedian.name, func.count(Video.id))
            .join(Video)
            .group_by(Comedian.id)
            .order_by(Comedian.name.asc())
            .all()
    )
    result = {
        "total video count": total_video_count,
        "total comedian count": total_comedian_count,
        "total tag count": total_tag_count,
        "video count by comedian": [{"id": id, "name": name, "video count": count} for id, name, count in names]
    }

    return jsonify(result)

