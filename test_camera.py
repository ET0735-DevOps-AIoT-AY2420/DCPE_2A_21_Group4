import sys
import os
import cv2
import numpy as np
import pytest

# Ensure the parent directory (or the directory where your module resides) is in sys.path.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import your function from your module.
from src.barcode_scanner import scan_barcode

# --- Dummy Classes for Testing --- #

class DummyPicamera2:
    """A dummy replacement for Picamera2."""
    def __init__(self):
        self.started = False
        self.frames_captured = 0
        self.closed = False

    def create_preview_configuration(self, main):
        return "dummy_config"

    def configure(self, config):
        self.config = config

    def start_preview(self, preview):
        self.preview = preview

    def start(self):
        self.started = True

    def capture_array(self):
        self.frames_captured += 1
        # Return a dummy image (a black image) of size 480x640 with 3 channels.
        return np.zeros((480, 640, 3), dtype=np.uint8)

    def stop(self):
        self.started = False

    def close(self):
        self.closed = True

class DummyPreview:
    """A dummy replacement for Preview with only the needed attribute."""
    NULL = None

class DummyDecoded:
    """A dummy barcode decoded object."""
    def __init__(self, data):
        # data should be a bytes object.
        self.data = data

# --- Test Cases --- #

def test_scan_barcode_user(monkeypatch):
    """
    Test that scan_barcode returns a user dictionary when the scanned code matches a user.
    """
    # Patch dependencies in scan_barcode's global namespace.
    monkeypatch.setitem(scan_barcode.__globals__, "Picamera2", DummyPicamera2)
    monkeypatch.setitem(scan_barcode.__globals__, "Preview", DummyPreview)

    # Disable OpenCV GUI functions for testing.
    monkeypatch.setattr(cv2, "imshow", lambda winname, frame: None)
    monkeypatch.setattr(cv2, "waitKey", lambda delay: 0)  # Simulate no 'q' press.
    monkeypatch.setattr(cv2, "destroyAllWindows", lambda: None)

    # Create dummy database functions.
    def dummy_get_user_by_barcode(barcode):
        if barcode == "user123":
            return {"name": "Test User", "email": "test@example.com"}
        return None

    def dummy_get_book_by_barcode(barcode):
        return None  # For this test, no book is returned.

    monkeypatch.setitem(scan_barcode.__globals__, "get_user_by_barcode", dummy_get_user_by_barcode)
    monkeypatch.setitem(scan_barcode.__globals__, "get_book_by_barcode", dummy_get_book_by_barcode)

    # Patch the decode function to simulate a barcode scan that returns a user code.
    monkeypatch.setitem(scan_barcode.__globals__, "decode", lambda img: [DummyDecoded(b"user123")])

    # Call the function and check that a user is returned.
    result = scan_barcode()
    expected = {"type": "user", "data": {"name": "Test User", "email": "test@example.com"}}
    assert result == expected


def test_scan_barcode_book(monkeypatch):
    """
    Test that scan_barcode returns a book dictionary when the scanned code matches a book.
    """
    monkeypatch.setitem(scan_barcode.__globals__, "Picamera2", DummyPicamera2)
    monkeypatch.setitem(scan_barcode.__globals__, "Preview", DummyPreview)

    # Disable GUI functions.
    monkeypatch.setattr(cv2, "imshow", lambda winname, frame: None)
    monkeypatch.setattr(cv2, "waitKey", lambda delay: 0)
    monkeypatch.setattr(cv2, "destroyAllWindows", lambda: None)

    # Create dummy database functions.
    def dummy_get_user_by_barcode(barcode):
        return None  # No user for this test.

    def dummy_get_book_by_barcode(barcode):
        if barcode == "book123":
            return {"title": "Test Book", "author": "Test Author"}
        return None

    monkeypatch.setitem(scan_barcode.__globals__, "get_user_by_barcode", dummy_get_user_by_barcode)
    monkeypatch.setitem(scan_barcode.__globals__, "get_book_by_barcode", dummy_get_book_by_barcode)

    # Patch the decode function to simulate scanning a book barcode.
    monkeypatch.setitem(scan_barcode.__globals__, "decode", lambda img: [DummyDecoded(b"book123")])

    # Call the function and check that a book is returned.
    result = scan_barcode()
    expected = {"type": "book", "data": {"title": "Test Book", "author": "Test Author"}}
    assert result == expected
