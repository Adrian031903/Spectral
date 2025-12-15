from App.models import Admin, Driver, Area, Street, Item, User
from App.database import db

# All admin-related business logic will be moved here as functions

def admin_create_driver(username, password):
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        raise ValueError("Username already taken.")

    # Driver.areaId is NOT NULL and is a foreign key to Area.
    # Using 0 will crash on Postgres with FK violations (Render).
    area = Area.query.order_by(Area.id.asc()).first()
    if not area:
        area = Area(name="Unassigned")
        db.session.add(area)
        db.session.commit()

    driver = Driver(username=username, password=password, status="Offline", areaId=area.id, streetId=None)
    db.session.add(driver)
    db.session.commit()
    return driver

def admin_delete_driver(driver_id):
    driver = Driver.query.get(driver_id)
    if not driver:
        raise ValueError("Invalid driver ID.")
    db.session.delete(driver)
    db.session.commit()
    return driver

def admin_add_area(name):
    area = Area(name=name)
    db.session.add(area)
    db.session.commit()
    return area

def admin_add_street(area_id, name):
    area = Area.query.get(area_id)
    if not area:
        raise ValueError("Invalid area ID.")
    street = Street(name=name, areaId=area_id)
    db.session.add(street)
    db.session.commit()
    return street

def admin_add_item(name, price, description, tags):
    item = Item(name=name, price=price, description=description, tags=tags)
    db.session.add(item)
    db.session.commit()
    return item

def admin_delete_area(area_id):
    area = Area.query.get(area_id)
    if not area:
        raise ValueError("Invalid area ID.")
    db.session.delete(area)
    db.session.commit()

def admin_delete_street(street_id):
    street = Street.query.get(street_id)
    if not street:
        raise ValueError("Invalid street ID.")
    db.session.delete(street)
    db.session.commit()

def admin_delete_item(item_id):
    item = Item.query.get(item_id)
    if not item:
        raise ValueError("Invalid item ID.")
    db.session.delete(item)
    db.session.commit()

def admin_view_all_areas():
    return Area.query.all()

def admin_view_all_streets():
    return Street.query.all()

def admin_view_all_items():
     return Item.query.all()
