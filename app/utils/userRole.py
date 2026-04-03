import enum

class UserRole(str, enum.Enum):
    platform_admin = "platform_admin"
    college_admin = "college_admin"
    mess_admin = "mess_admin"
    student = "student"