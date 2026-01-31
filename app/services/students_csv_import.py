# import csv
# import io

# REQUIRED_HEADERS = {"email", "name","is_active"}

# def parse_and_preview_csv(csv_content: str, existing_rolls: set):
#     reader = csv.DictReader(io.StringIO(csv_content))

#     if set(reader.fieldnames) != REQUIRED_HEADERS:
#         raise ValueError("Invalid CSV headers")

#     to_insert = []
#     to_update = []
#     errors = []
#     seen_rolls = set()

#     for row_number, row in enumerate(reader, start=2):
#         name = row["roll_number"].strip()
#         email = row["email"].strip().lower()

#         if not roll or not email:
#             errors.append({"row": row_number, "error": "Empty roll/email"})
#             continue

#         if roll in seen_rolls:
#             errors.append({"row": row_number, "error": "Duplicate roll in CSV"})
#             continue

#         seen_rolls.add(roll)

#         if roll in existing_rolls:
#             to_update.append(roll)
#         else:
#             to_insert.append(roll)

#     return {
#         "total": len(to_insert) + len(to_update),
#         "to_insert": to_insert,
#         "to_update": to_update,
#         "errors": errors
#     }

import csv
import io

REQUIRED_HEADERS = {"email", "name", "is_active"}

def parse_and_preview_csv(csv_content: str, existing_emails: set):
    reader = csv.DictReader(io.StringIO(csv_content))

    if set(reader.fieldnames) != REQUIRED_HEADERS:
        raise ValueError(
            f"Invalid CSV headers. Required: {REQUIRED_HEADERS}"
        )

    to_insert = []
    to_update = []
    errors = []
    seen_emails = set()

    for row_number, row in enumerate(reader, start=2):
        email = row["email"].strip().lower()
        name = row["name"].strip()
        is_active_raw = row["is_active"].strip().lower()

        # basic validation
        if not email or not name:
            errors.append({
                "row": row_number,
                "error": "Empty email or name"
            })
            continue

        if is_active_raw not in {"true", "false"}:
            errors.append({
                "row": row_number,
                "error": "is_active must be true or false"
            })
            continue

        if email in seen_emails:
            errors.append({
                "row": row_number,
                "error": "Duplicate email in CSV"
            })
            continue

        seen_emails.add(email)

        student_data = {
            "email": email,
            "name": name,
            "is_active": is_active_raw == "true"
        }

        if email in existing_emails:
            to_update.append(student_data)
        else:
            to_insert.append(student_data)

    return {
        "total": len(to_insert) + len(to_update),
        "to_insert": to_insert,
        "to_update": to_update,
        "errors": errors
    }
