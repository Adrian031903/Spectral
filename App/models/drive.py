from App.database import db
from .drive_observer import DriveObserver

class Drive(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    driverId = db.Column(db.Integer, db.ForeignKey('driver.id'), nullable=False)
    areaId = db.Column(db.Integer, db.ForeignKey('area.id'), nullable=False)
    streetId = db.Column(db.Integer, db.ForeignKey('street.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(20), nullable=False)

    area = db.relationship("Area", backref="drives")
    street = db.relationship("Street", backref="drives")
    observers = db.relationship(
        "DriveObserver",
        backref="drive",
        cascade="all, delete-orphan",
        overlaps="drive,watcher_residents,subscribed_drives",
    )
    watcher_residents = db.relationship(
        "Resident",
        secondary="drive_observer",
        backref=db.backref(
            "subscribed_drives",
            overlaps="drive,watcher_residents,observers",
        ),
        overlaps="drive,observers,subscribed_drives",
    )

    def __init__(self, driverId, areaId, streetId, date, time, status):
        self.driverId = driverId
        self.areaId = areaId
        self.streetId = streetId
        self.date = date
        self.time = time
        self.status = status

    def attach_observer(self, resident):
        """Attach a resident to this drive's notifications if not already attached."""
        if not resident or getattr(resident, "id", None) is None:
            return None
        existing = DriveObserver.query.filter_by(driveId=self.id, residentId=resident.id).first()
        if existing:
            return existing
        link = DriveObserver(driveId=self.id, residentId=resident.id)
        db.session.add(link)
        return link

    def detach_observer(self, resident):
        if not resident or getattr(resident, "id", None) is None:
            return None
        existing = DriveObserver.query.filter_by(driveId=self.id, residentId=resident.id).first()
        if existing:
            db.session.delete(existing)
        return existing

    def notify_observers(self, message, target_resident_id=None):
        """Notify all attached residents (or a single target) with a message."""
        targets = self.watcher_residents
        if target_resident_id is not None:
            targets = [r for r in targets if r.id == target_resident_id]
        for resident in targets:
            if hasattr(resident, "receive_notif"):
                resident.receive_notif(message)

    def get_json(self):
        return {
            'id': self.id,
            'driverId': self.driverId,
            'areaId': self.areaId,
            'streetId': self.streetId,
            'date': self.date.strftime("%Y-%m-%d") if self.date else None,
            'time': self.time.strftime("%H:%M:%S") if self.time else None,
            'status': self.status
        }