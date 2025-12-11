from App.database import db

class DriveObserver(db.Model):
    __tablename__ = 'drive_observer'

    id = db.Column(db.Integer, primary_key=True)
    driveId = db.Column(db.Integer, db.ForeignKey('drive.id'), nullable=False)
    residentId = db.Column(db.Integer, db.ForeignKey('resident.id'), nullable=False)

    __table_args__ = (db.UniqueConstraint('driveId', 'residentId', name='uq_drive_resident'),)

    def __init__(self, driveId, residentId):
        self.driveId = driveId
        self.residentId = residentId

    def get_json(self):
        return {
            'id': self.id,
            'driveId': self.driveId,
            'residentId': self.residentId,
        }
