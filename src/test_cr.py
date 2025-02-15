import sys
from types import ModuleType

# --- Inject Dummy barcode_scanner Module ---
dummy_barcode_scanner = ModuleType("barcode_scanner")
# Provide a dummy scan_barcode function.
# Adjust the return value as needed for your tests.
dummy_barcode_scanner.scan_barcode = lambda: {"type": "user", "data": {"id": 1, "name": "Dummy User", "email": "dummy@example.com"}}
sys.modules["barcode_scanner"] = dummy_barcode_scanner

# --- Inject Dummy RPi.GPIO Modules --- #
dummy_gpio = ModuleType("RPi.GPIO")
dummy_gpio.setmode = lambda mode: None
dummy_gpio.setwarnings = lambda flag: None
dummy_gpio.setup = lambda pin, mode: None
dummy_rpi = ModuleType("RPi")
dummy_rpi.GPIO = dummy_gpio
sys.modules["RPi"] = dummy_rpi
sys.modules["RPi.GPIO"] = dummy_gpio

# --- Inject Dummy 'hal' Modules --- #

# Dummy for hal.hal_lcd
dummy_hal_lcd = ModuleType("hal.hal_lcd")
class DummyLCD:
    def lcd_clear(self):
        pass
    def lcd_display_string(self, msg, line):
        pass
dummy_hal_lcd.lcd = lambda: DummyLCD()
sys.modules["hal.hal_lcd"] = dummy_hal_lcd

# Dummy for hal.hal_servo
dummy_hal_servo = ModuleType("hal.hal_servo")
dummy_hal_servo.set_servo_position = lambda pos: None
sys.modules["hal.hal_servo"] = dummy_hal_servo

# Dummy for hal.hal_usonic
dummy_hal_usonic = ModuleType("hal.hal_usonic")
dummy_hal_usonic.init = lambda: None  # Simulate usonic_init
dummy_hal_usonic.get_distance = lambda: 100  # Return a safe value (e.g., no user detected)
sys.modules["hal.hal_usonic"] = dummy_hal_usonic

# Dummy for hal.hal_keypad
dummy_hal_keypad = ModuleType("hal.hal_keypad")
dummy_hal_keypad.init = lambda callback: None
dummy_hal_keypad.get_key = lambda: ""
sys.modules["hal.hal_keypad"] = dummy_hal_keypad

# Dummy for hal.hal_rfid_reader
dummy_hal_rfid = ModuleType("hal.hal_rfid_reader")
class DummySimpleMFRC522:
    def read(self):
        return (None, None)
dummy_hal_rfid.SimpleMFRC522 = DummySimpleMFRC522
sys.modules["hal.hal_rfid_reader"] = dummy_hal_rfid

# Dummy for hal.hal_buzzer
dummy_hal_buzzer = ModuleType("hal.hal_buzzer")
dummy_hal_buzzer.init = lambda: None
dummy_hal_buzzer.beep = lambda: None
sys.modules["hal.hal_buzzer"] = dummy_hal_buzzer

# --- End Dummy Module Injection --- #

import pytest
import src.cr as cr  # Now your main module should import correctly


# --- Dummy Database Connection and Cursor Classes --- #

class DummyCursor:
    def __init__(self, return_value):
        self.return_value = return_value
        self.executed = []

    def execute(self, query, params):
        self.executed.append((query, params))

    def fetchone(self):
        return self.return_value

    def close(self):
        pass

class DummyConnection:
    def __init__(self, return_value):
        self.return_value = return_value
        self.commit_called = False
        self.closed = False

    def cursor(self):
        return DummyCursor(self.return_value)

    def commit(self):
        self.commit_called = True

    def close(self):
        self.closed = True

def dummy_get_db_connection_factory(return_value):
    """
    Returns a dummy get_db_connection function that, when called,
    returns a DummyConnection with the specified return_value.
    """
    def dummy_get_db_connection():
        return DummyConnection(return_value)
    return dummy_get_db_connection

# --- Test Cases --- #

def test_verify_and_remove_loan_success(monkeypatch):
    """
    Test that verify_and_remove_loan returns True when a valid loan exists.
    We simulate the database returning a valid loan row.
    """
    # Simulate a valid loan row (e.g., (loan_id, isbn, user_id, returnDate) where returnDate is None)
    dummy_loan = (1, "isbn123", 1, None)
    monkeypatch.setattr(cr, "get_db_connection", dummy_get_db_connection_factory(dummy_loan))

    # Provide book_isbn input as a dict with nested data (as expected by the function)
    book_input = {"data": {"isbn": "isbn123"}}
    user_id = 1

    result = cr.verify_and_remove_loan(book_input, user_id)
    assert result is True

def test_verify_book_code_failure(monkeypatch):
    """
    Test that verify_book_code returns False when no matching loan exists.
    We simulate the database returning None.
    """
    # Simulate no matching loan: fetchone returns None
    monkeypatch.setattr(cr, "get_db_connection", dummy_get_db_connection_factory(None))

    book_code = "book999"
    user_id = 1

    result = cr.verify_book_code(book_code, user_id)
    assert result is False


test_Cr.py