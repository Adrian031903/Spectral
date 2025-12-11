from App.database import db


class DriveSubscription(db.Model):
    __tablename__ = "drive_subscription"

    id = db.Column(db.Integer, primary_key=True)
    driveId = db.Column(db.Integer, db.ForeignKey('drive.id'), nullable=False)
    residentId = db.Column(db.Integer, db.ForeignKey('resident.id'), nullable=False)

    drive = db.relationship("Drive", backref="subscriptions")
    resident = db.relationship("Resident", backref="subscriptions")

    __table_args__ = (
        db.UniqueConstraint('driveId', 'residentId', name='uq_drive_resident_subscription'),
    )

    def __init__(self, driveId, residentId):
        self.driveId = driveId
        self.residentId = residentId

    def get_json(self):
        return {
            'id': self.id,
            'driveId': self.driveId,
            'residentId': self.residentId
        }
