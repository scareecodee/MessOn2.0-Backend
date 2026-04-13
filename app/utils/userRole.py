import enum

class UserRole(str, enum.Enum):
    root_admin = "root_admin"
    college_admin = "college_admin"
    mess_admin = "mess_admin"
    student = "student"