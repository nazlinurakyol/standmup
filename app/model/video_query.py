from sqlalchemy import func, desc, or_

from app.model import db
from app.model.tag import Tag
from app.model.video import Video, video_tag


def getVideos(page, pagesSize=10):
    return (
            db.session.query(Video)
                .filter((Video.is_active))
                .order_by(desc(Video.creation_date))
                .limit(pagesSize)
                .offset((page - 1) * pagesSize)
                .all()
        )

def searchVideos(search, page, pagesSize=10):
    return (
        db.session.query(Video)
            .filter((Video.is_active))
            .outerjoin(video_tag)
            .outerjoin(Tag).filter(
                or_(
                    or_(
                        Video.title.ilike(f"%{search}%"),
                        Video.description.ilike(f"%{search}%"),
                    ),
                    Tag.name.ilike(f"%{search}%")
                )
            ).order_by(desc(Video.creation_date))
            .limit(pagesSize)
            .offset((page - 1) * pagesSize)
            .all()
    )

def getVideosByComedianId(comedian_id, page, pagesSize=10):
    return (
        db.session.query(Video)
            .filter((Video.is_active))
            .filter_by(comedian_id=comedian_id)
            .limit(pagesSize)
            .offset((page - 1) * pagesSize)
            .all()
    )

def getVideoCountByComedianId(comedian_id):
    return (
        db.session.query(func.count(Video.id))
            .filter(Video.is_active)
            .filter_by(comedian_id=comedian_id)
            .scalar()
    )

def getAllVideoCount():
    return db.session.query(db.func.count(Video.id)).scalar()

