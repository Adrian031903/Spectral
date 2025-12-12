# 🍞 Bread Van App
Flask app with Admin/Driver/Resident portals, JWT auth, Observer-powered notifications, and supporting CLI tools.

## 🚀 Quick start (local)
```bash
pip install -r requirements.txt
export FLASK_APP=wsgi.py
flask init            # create tables + seed demo users
flask run             # dev server
```

### Seeded accounts (after `flask init`)
- Admin: admin / adminpass
- Drivers: bob / bobpass, mary / marypass
- Residents: alice / alicepass, jane / janepass, john / johnpass

### Sign up (web)
- Resident: requires area_id, street_id, house_number (seed data: Area 1 has streets 1-3; Area 2 has streets 4-5).
- Driver: username + password only.

### Portals
- `/portal/admin` – manage areas/streets/users
- `/portal/driver` – schedule/start/end/cancel drives
- `/portal/resident` – subscribe, request stops, view inbox notifications

## 🖥️ CLI usage (still available)
- Run commands: `flask <group> <command> [args...]`

## 👤 User Commands | Group: flask user
### Login
```bash
 flask user login <username> <password>
```

### Logout
```bash
flask user logout
```

### View Drives on a Street
```bash
flask user view_street_drives
```
Prompts to select an area and street, then lists scheduled drives.



## 🛠️ Admin Commands | Group: flask admin
Admins manage drivers, areas, and streets.
### List Users
```bash
flask admin list
```

### Create Driver
```bash
flask admin create_driver <username> <password>
```

### Delete Driver
```bash
flask admin delete_driver <driver_id>
```

### Add Area
```bash
flask admin add_area <name>
```

### Add Street
```bash
flask admin add_street <area_id> <name>
```

### Delete Area
```bash
flask admin delete_area <area_id>
```

### Delete Street
```bash
flask admin delete_street <street_id>
```

### View All Areas
```bash
flask admin view_all_areas
```

### View All Streets
```bash
flask admin view_all_streets
```


## 🚐 Driver Commands | Group: flask driver
Drivers manage drives and stops.
### Schedule Drive
```bash
flask driver schedule_drive YYYY-MM-DD HH:MM
```
Prompts to select area & street.
Drives cannot be scheduled in the past nor more than 1 year ahead of the current date.


### Cancel Drive
```bash
flask driver cancel_drive <drive_id>
```

### View My Drives
```bash
flask driver view_my_drives
```

### Start Drive
```bash
flask driver start_drive <drive_id>
```

### End Drive
```bash
flask driver end_drive
```

### View Requested Stops
```bash
flask driver view_requested_stops <drive_id>
```


## 🏠 Resident Commands | Group: flask resident
Residents can request stops and view their inbox.
### Create Resident
```bash
flask resident create <username> <password>
```
Prompts for area, street, and house number. 
A logged-in account is not required to create a resident.

### Request Stop
```bash
flask resident request_stop
```

### Cancel Stop
```bash
flask resident cancel_stop <drive_id>
```

### View Inbox
```bash
flask resident view_inbox
```

### View Driver Stats
```bash
flask resident view_driver_stats <driver_id>
```


## 🔑 Role Requirements
- flask admin ... → must be logged in as Admin
- flask driver ... → must be logged in as Driver
- flask resident ... → must be logged in as Resident


General user commands (login/logout/view_street_drives) are available to all.
