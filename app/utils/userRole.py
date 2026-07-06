from enum import Enum

class UserRole(str, Enum):
    root_admin = "root_admin"
    college_admin = "college_admin"
    mess_admin = "mess_admin"
    student = "student"