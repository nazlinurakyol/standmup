from sqlalchemy import desc
from app.model import videodb
from application import application, db

# add video automatically
def addVideoAuto():
    with application.app_context():
        new_video = db.session.query(videodb.Video).filter_by(is_active=0).filter_by(is_ready=1).order_by(
            desc(videodb.Video.creation_date)).first()
        if new_video:
            new_video.is_active = 1
            db.session.add(new_video)
            db.session.commit()
        else:
            print("No new video at the moment.")