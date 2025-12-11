from App.models import Resident, Stop, Drive, Area, Street, DriverStock, DriveSubscription
from App.database import db

# All resident-related business logic will be moved here as functions

def resident_create(username, password, area_id, street_id, house_number):
    resident = Resident(username=username, password=password, areaId=area_id, streetId=street_id, houseNumber=house_number)
    db.session.add(resident)
    db.session.commit()
    return resident

def resident_request_stop(resident, drive_id):
    drives = Drive.query.filter_by(areaId=resident.areaId, streetId=resident.streetId, status="Upcoming").all()
    if not any(d.id == drive_id for d in drives):
        raise ValueError("Invalid drive choice.")
    existing_stop = Stop.query.filter_by(driveId=drive_id, residentId=resident.id).first()
    if existing_stop:
        raise ValueError(f"You have already requested a stop for drive {drive_id}.")
    stop = resident.request_stop(drive_id)
    _ensure_subscription(resident.id, drive_id)
    return stop

def resident_cancel_stop(resident, drive_id):
    stop = Stop.query.filter_by(driveId=drive_id, residentId=resident.id).first()
    if not stop:
        raise ValueError("No stop requested for this drive.")
    resident.cancel_stop(stop.id)
    return stop


def resident_subscribe_to_drive(resident, drive_id):
    drive = Drive.query.get(drive_id)
    if not drive:
        raise ValueError("Drive not found.")
    _ensure_subscription(resident.id, drive_id)
    db.session.commit()
    return DriveSubscription.query.filter_by(driveId=drive_id, residentId=resident.id).first()


def resident_unsubscribe_from_drive(resident, drive_id):
    subscription = DriveSubscription.query.filter_by(driveId=drive_id, residentId=resident.id).first()
    if not subscription:
        raise ValueError("Not subscribed to this drive.")
    db.session.delete(subscription)
    db.session.commit()
    return True


def resident_list_subscriptions(resident):
    return DriveSubscription.query.filter_by(residentId=resident.id).all()

def resident_view_inbox(resident):
    return resident.view_inbox()

def resident_view_driver_stats(resident, driver_id):
    driver = resident.view_driver_stats(driver_id)
    if not driver:
        raise ValueError("Driver not found.")
    return driver

def resident_view_stock(resident, driver_id):
    driver = resident.view_driver_stats(driver_id)
    if not driver:
         raise ValueError("Driver not found.")
    stocks =  DriverStock.query.filter_by(driverId=driver_id).all()
    return stocks


def _ensure_subscription(resident_id, drive_id):
    existing = DriveSubscription.query.filter_by(driveId=drive_id, residentId=resident_id).first()
    if existing:
        return existing
    subscription = DriveSubscription(driveId=drive_id, residentId=resident_id)
    db.session.add(subscription)
    db.session.commit()
    return subscription
