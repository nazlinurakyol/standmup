from sqlalchemy import func
from app.model import db
from app.model.video import Video, video_tag
from app.model.tag import Tag

def getTags():
    return db.session.query(Tag).order_by(Tag.name.asc()).all()

def getTagsWithCounts(countMoreThan=5):
    return (
        db.session.query(
            Tag.name,
            func.count(Video.id)
        ).join(
            video_tag,
            Tag.id == video_tag.c.tag_id
        ).join(
            Video,
            Video.id == video_tag.c.video_id
        ).group_by(Tag.name)
        .having(func.count(Video.id)>=countMoreThan)
        .all()
    )