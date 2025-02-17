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
- **Book Reservation**: Users can select a branch, search for books by title or author, modify their borrowed list, and reserve books with real-time availability updates.
- **Book Collection**:: A countdown timer reminds users to collect reserved books, with an option to extend the collection date.
- **User Accounts**: Manage user accounts, including login and profile updates.
- **Book Catalog and Search**: Search catalog functionality by title, author, genre, or keyword.
- **Reservation Management**:Users can modify their borrowed book list before confirming reservations and extending the borrowing period.
- **User Dashboard**: Users can view the number of borrowed books, payable fines for loans, and their profile information.
- **Accessibility**: Available on web and mobile platforms.
- **Security**: Implements secure login protocols and data protection.
- **Library Integration**: Synchronizes with existing library systems.

---

## System Architecture
The system comprises the following components:
1. **User Interface**: Web and mobile platforms for users and administrators.
2. **Backend Services**: Handles authentication,borrowing, reservations, and system integrations.
3. **Database**: Stores user data, branch books details, book details, and reservation records.
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

# Library System Website Flow

## 1. Entry Point
- User opens the website → **Sign up** 

## 2. Authentication
- **New User**: Clicks **Sign Up**, enters details, and creates an account.
- **Existing User**: Clicks **Login**, enters credentials, and accesses the system.

## 3. Main Menu
--**Choose Branch**: Users can choose branch 1 or branch 2.
- **Home Page**:Users can seen books by branches
- **Book Search**: User searches by **title, author, or genre**.
- **Book Information** : Users can view book information and its availability status.
- **Book Reservation**: User reserves available books.
- **User dashboard**: View borrowed books, due dates, and fines.
- **Notifications**: Alerts for due dates, availability, etc.

## 4. Book Borrowing & Reservation
- User can borrow and reserve books that shows Availability status is "Available" in each branch
- System updates book **status**.

## 5. Exit
- User logs out or session.


## Non-Functional Requirements
1. **Power Management**: Switch between low and high-power modes based on user activity.
2. **Performance**: Search results must load within 5 seconds.
3. **Security**: Automatic logout after 10 minutes of inactivity.

---

## Software Architecture
The static software architecture includes:
- **Application Layer**:
  - main.py
  - app.py
  - database.py
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
  - hal_usonic.py
  - barcode_scanner.py
  - cr.py
    
    
---

## Usage
1. **User**:
   - Register an account and log in.
   - Search and reserve books.
   - Collect Books.
   - Return Books.
   - Pay fines.
---



