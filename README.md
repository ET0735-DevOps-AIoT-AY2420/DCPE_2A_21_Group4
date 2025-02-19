# Library Book Reservation and Collection System

The Library Book Reservation and Collection System is designed to enhance the book-borrowing experience for both library members and staff. This system provides convenient features like online book reservations, notifications, and book collection processes. 

## Table of Contents
- [Purpose](#purpose)
- [Features](#features)
- [Functional Requirements](#functional-requirements)
- [Non-Functional Requirements](#non-functional-requirements)
- [Software Architecture](#software-architecture)
- [Library System Website Flow](#library-websiteflow)
- [Installation](#installation)
- [Usage](#usage)
- [Demo Video Link](#videolink)
- [Contribution](#contribution)

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
- 
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
  - app.py
  - cr.py
  - barcode_scanner.py
  - rfid_scanner.py
- **Database**:
  - database.py
  - test_database.py
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
  - test_cr.py
  - test_camera.py   
---

## Library System Website Flow

### 1. Entry Point
- User opens the website → **Sign up** 

### 2. Authentication
- **Existing User**: Clicks **Sign In***, enters credentials, and accesses the system. ( Assuming user has already account )

### 3. Main Menu
--**Choose Branch**: Users can choose branch 1 or branch 2.
- **Home Page**:Users can seen books by branches
- **Book Search**: User searches by **title, author, or genre**.
- **Book Information** : Users can view book information and its availability status.
- **Book Reservation**: User reserves available books.
- **User dashboard**: View **borrowed books**, and **Fines**.

### 4. Book Borrowing & Reservation
- User can borrow and reserve books that shows Availability status is "Available" in each branch
- System updates book **status** accordingly.
- After user is reserved book, the Availability status change "Unavailable" for that branch

### 5. Exit
- User logs out or session.

---

## Installation

### Prequisites:
- Python 3.x
- Flask
- SQLite3
- Raspberry Pi (for hardware features)

### Steps to Set up the System:
- git clone --recurse-submodules https://github.com/ET0735-DevOps-AIoT-AY2420/DCPE_2A_21_Group4.git
- git pull from master branch 
- change database path in app.py, database.py 
- first, delete the database to ensure the program starts with a fresh setup
- Run database: python database.py
- Please run the cr.py from the src in the vnc viewer using Thonny. The required libraries must be installed before running. picamera2, libcamera, pyzbar and 
  thonny. 
  The app.py should be running first to collaborate with the database and check the functions. 
  Kindly use the qr codes provided to test the scanning. (Barcodes are attached in the docs/ barcodes folder)
 - Run app.py , and then the server will run on localhost

### Steps to Do in Website:
- Sign in using  John Doe Account (Email - john.doe@example.com, Password - password123)
- Choose Branches ( Branch 1 )
- View Page on HomePage, and can search books with title, author, genre and 5 books will display at first
- Click ViewMore link, and view more books categorized with sections
- Choose one book and bookinfo page will display with book information and status
- Process: Borrow Button -> Reserve Button
- Reserve books can be view with respective title and branch
- Process: Reserve Button
- Ater Reserved, Borrowed Books can view and also can check manually on Borrowed Page and extend period
- And On Userdashboard, can check borrowed books, payable fines and User Profile
---

## Usage
 - **User**:
   - Account Log in.
   - Search and reserve books.
   - Collect Books.
   - Return Books.
   - Pay fines.
   - View dashboard.
---

## Demo Video Link
https://drive.google.com/file/d/19RAwLimOIPwE7Q87uFYecK63_UsnMIHd/view?usp=drivesdk

---

## Contribution
- Sign in, Sign Up, Database, Collection, Return , Barcode Scanning, App.py first implementation- Kaung Su Hein
- User dashboard, payment, Exit cr.py first implementation, Docker Container- Gamaliel Hla Tun
- Testing files (test_cr.py, test_database.py and test_camera.py), Book Information, Borrowed Book with Extend period, App.py - Yu Thwe Thwe Htet
- Website, Branch, HomePage and ViewMore, Reserve System and Reserved, App.py and database.py - Chan Mya Mya Thein

---





