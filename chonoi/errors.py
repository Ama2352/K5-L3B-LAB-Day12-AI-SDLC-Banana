"""Lỗi theo Test Contract: BadInput -> mã thoát 2, các lỗi còn lại -> mã 1."""


class BadInput(Exception):
    """Tham số / file đầu vào sai hoặc mâu thuẫn. Thoát với mã 2, TRƯỚC khi ghi đầu ra."""
