from App.models import Resident, Stop, Drive, Area, Street, DriverStock, DriveSubscription
from App.database import db

# All resident-related business logic will be moved here as functions

def resident_create(username, password, area_id, street_id, house_number):
    resident = Resident(username=username, password=password, areaId=area_id, streetId=street_id, houseNumber=house_number)
    db.session.add(resident)
    db.session.commit()
    return resident

def resident_request_stop(resident, drive_id):
    try:
        drive_id = int(drive_id)
    except (TypeError, ValueError):
        raise ValueError("Invalid drive id.")

    drive = Drive.query.get(drive_id)
    if not drive:
        raise ValueError("Drive not found.")
    if drive.areaId != resident.areaId or drive.streetId != resident.streetId:
        raise ValueError("Drive is not scheduled for your area/street.")
    if drive.status not in ("Upcoming", "In Progress"):
        raise ValueError(f"Drive is not open for stop requests (status: {drive.status}).")

    existing_stop = Stop.query.filter_by(driveId=drive_id, residentId=resident.id).first()
    if existing_stop:
        raise ValueError(f"You have already requested a stop for drive {drive_id}.")
    stop = resident.request_stop(drive_id)
    if not stop:
        raise ValueError("Unable to create stop request.")
    _ensure_subscription(resident.id, drive_id)
    return stop

def resident_cancel_stop(resident, stop_id):
    try:
        stop_id = int(stop_id)
    except (TypeError, ValueError):
        raise ValueError("Invalid stop id.")
    stop = Stop.query.filter_by(id=stop_id, residentId=resident.id).first()
    if not stop:
        raise ValueError("Stop not found.")
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
