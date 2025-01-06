# Library Book Reservation and Collection System

The Library Book Reservation and Collection System is designed to enhance the book-borrowing experience for both library members and staff. This system provides convenient features like online book reservations, notifications, and book collection processes. 

## Table of Contents
- [Purpose](#purpose)
- [Features](#features)
- [System Architecture](#system-architecture)
- [Functional Requirements](#functional-requirements)
- [Non-Functional Requirements](#non-functional-requirements)
- [Software Architecture](#software-architecture)
- [Usage](#usage)

---

## Purpose

Target audience: Readers of all ages who value a modern and efficient library experience.

The Library Book Reservation and Collection System is designed to:
- Improve the efficiency of library operations.
- Provide a seamless user experience for book reservations and collections.
- Enhance user engagement with timely notifications and personalized profiles.

---

## Features
- **Book Reservation**: Search and reserve books online with real-time availability updates.
- **Book Collection**:Once reserved, users will receive notifications when books are available for collection.
- **User Accounts**: Manage user accounts, including login and profile updates.
- **Book Catalog and Search**: Search catalog functionality by title, author, genre, or keyword.
- **Notifications**: Alerts for reservations, availability, and collection reminders.
- **Reservation Management**: Users can modify or cancel their reservations, within library policies.
- **Admin Dashboard**: Staff manage books, users, and generate usage reports.
- **Data and Reporting**: The system tracks reservations and user activity, generating reports for staff.
- **Accessibility**: Available on web and mobile platforms.
- **Security**: Implements secure login protocols and data protection.
- **Library Integration**: Synchronizes with existing library systems.

---

## System Architecture
The system comprises the following components:
1. **User Interface**: Web and mobile platforms for users and administrators.
2. **Backend Services**: Handles authentication, reservations, notifications, and system integrations.
3. **Database**: Stores user data, book details, and reservation records.
4. **Hardware Integration**: Includes RFID scanners, barcode readers, and book dispensing units.

---

## Functional Requirements
1. Users can search and reserve books via website or mobile apps.
2. Users can choose specific branch.
3. Authentication via RFID or QR code scanning.
4. Automatic cancellation of uncollected reservations after 5 days.
5. Loan period of 18 days, with a one-time renewal for 7 days.
6. Payment management for overdue fines.
7. Barcode scanning for book returns.

---

## Non-Functional Requirements
1. **Power Management**: Switch between low and high-power modes based on user activity.
2. **Performance**: Search results must load within 5 seconds.
3. **Security**: Automatic logout after 10 minutes of inactivity.

---

## Software Architecture
The static software architecture includes:
- **Application Layer**:
  - Main.py
  - Power_Mgt.py
  - Auth.py
  - calculation.py
- **Hardware Abstraction Layer (HAL)**:
  - hal_servo.py
  - hal_keypad.py
  - hal_adc.py
  - hal_rfid_reader.py
  - hal_picam2.py
  - hal_lcd.py
  - hal_led.py
  - hal_buzzer.py
    
---

## Usage
1. **User**:
   - Register an account and log in.
   - Search and reserve books.
   - Receive notifications and pay fines for overdue returns.
2. **Admin**:
   - Add or update book details.
   - Monitor reservations and usage reports.

---



