from App.models import Driver, Drive, Street, Item, DriverStock, Resident, DriveSubscription
from App.database import db
from datetime import datetime, timedelta

# All driver-related business logic will be moved here as functions

def driver_schedule_drive(driver, area_id, street_id, date_str, time_str):
    try:
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
        time = datetime.strptime(time_str, "%H:%M").time()
    except ValueError:
        raise ValueError("Invalid date or time format. Use YYYY-MM-DD and HH:MM.")
    scheduled_datetime = datetime.combine(date, time)
    # Allow past dates for tests/demo data; still prevent excessively far future drives.
    one_year_later = datetime.now() + timedelta(days=60)
    if scheduled_datetime > one_year_later:
        raise ValueError("Cannot schedule a drive more than 60 days in advance.")
    existing_drive = Drive.query.filter_by(areaId=area_id, streetId=street_id, date=date).first()
    new_drive = driver.schedule_drive(area_id, street_id, date_str, time_str)
    if new_drive:
        _ensure_default_subscriptions(new_drive)
        _notify_drive_event(new_drive, "SCHEDULED")
    return new_drive

def driver_cancel_drive(driver, drive_id):
    drive = driver.cancel_drive(drive_id)
    if drive:
        _notify_drive_event(drive, "CANCELLED")
    return drive

def driver_view_drives(driver):
    return [d for d in driver.view_drives() if d.status in ("Upcoming", "In Progress")]

def driver_start_drive(driver, drive_id):
    current_drive = Drive.query.filter_by(driverId=driver.id, status="In Progress").first()
    if current_drive:
        raise ValueError(f"You are already on drive {current_drive.id}.")
    drive = Drive.query.filter_by(driverId=driver.id, id=drive_id, status="Upcoming").first()
    if not drive:
        raise ValueError("Drive not found or cannot be started.")
    result = driver.start_drive(drive_id)
    if result:
        _notify_drive_event(result, "STARTED")
    return result

def driver_end_drive(driver):
    current_drive = Drive.query.filter_by(driverId=driver.id, status="In Progress").first()
    if not current_drive:
        raise ValueError("No drive in progress.")
    drive = driver.end_drive(current_drive.id)
    if drive:
        _notify_drive_event(drive, "COMPLETED")
    return drive

def driver_view_requested_stops(driver, drive_id):
    stops = driver.view_requested_stops(drive_id)
    if not stops:
        return []
    return stops

def driver_update_stock(driver, item_id, quantity):
    item =  Item.query.get(item_id)
    if not item:
        raise ValueError("Invalid item ID.")
    stock =  DriverStock.query.filter_by(driverId=driver.id, itemId=item_id).first()
    if stock:
        stock.quantity = quantity
    else:
        stock = DriverStock(driverId=driver.id, itemId=item_id, quantity=quantity)
        db.session.add(stock)
    db.session.commit()
    return stock

def driver_view_stock(driver):
    stocks = DriverStock.query.filter_by(driverId=driver.id).all() 
    return stocks


def _ensure_default_subscriptions(drive: Drive):
    if not drive or not drive.streetId:
        return
    street = Street.query.get(drive.streetId)
    if not street:
        return
    for resident in street.residents:
        exists = DriveSubscription.query.filter_by(driveId=drive.id, residentId=resident.id).first()
        if not exists:
            db.session.add(DriveSubscription(driveId=drive.id, residentId=resident.id))
    db.session.commit()


def _notify_drive_event(drive: Drive, event_type: str, stop=None, target_resident_id=None):
    if not drive:
        return
    recipients = set(
        sub.residentId for sub in DriveSubscription.query.filter_by(driveId=drive.id).all()
    )
    message_map = {
        "SCHEDULED": f"Drive {drive.id} scheduled on {drive.date} at {drive.time}.",
        "STARTED": f"Drive {drive.id} is now in progress.",
        "COMPLETED": f"Drive {drive.id} has completed.",
        "CANCELLED": f"Drive {drive.id} has been cancelled.",
        "STOP_REQUESTED": f"A stop was requested on drive {drive.id}.",
    }
    message = message_map.get(event_type, f"Drive {drive.id} update: {event_type}")

    if target_resident_id:
        recipients.add(target_resident_id)

    for resident_id in recipients:
        resident = Resident.query.get(resident_id)
        if resident:
            resident.receive_notif(message)

    db.session.commit()
    
    
    
