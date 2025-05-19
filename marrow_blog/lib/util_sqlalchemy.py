import datetime

from sqlalchemy import DateTime
from sqlalchemy.types import TypeDecorator

from marrow_blog.extensions import db

def tzware_datetime():
    """
    Return a timezone aware datetime.
    """
    return datetime.datetime.now(datetime.timezone.utc)

class AwareDateTime(TypeDecorator):
    impl = DateTime(timezone=True)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if isinstance(value, datetime.datetime) and value.tzinfo is None:
            raise ValueError("{!r} must be TZ-aware".format(value))
        return value

    def __repr__(self):
        return "AwareDateTime()"

class ResourceMixin(object):
    created_on = db.Column(AwareDateTime(), default=tzware_datetime)
    updated_on = db.Column(
        AwareDateTime(), default=tzware_datetime, onupdate=tzware_datetime
    )

    def save(self):
        db.session.add(self)
        db.session.commit()
        return self

    def delete(self):
        db.session.delete(self)
        return db.session.commit()

    def __str__(self):
        obj_id = hex(id(self))
        columns = self.__table__.c.keys()
        values = ", ".join("%s=%r" % (n, getattr(self, n)) for n in columns)
        return "<%s %s(%s)>" % (obj_id, self.__class__.__name__, values)
