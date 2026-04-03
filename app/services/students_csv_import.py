import csv
import io

REQUIRED_HEADERS = {"name", "roll_number", "email", "branch", "batch", "is_active"}


def parse_and_preview_csv(csv_content: str, existing_emails: set, mode: str):
    reader = csv.DictReader(io.StringIO(csv_content))

    if not reader.fieldnames:
        return {
            "status": False,
            "errors": [{
                "row_number": 1,
                "message": "CSV file has no headers"
            }],
            "to_insert": [],
            "to_update": [],
            "conflicts": []
        }

    csv_headers = {h.strip() for h in reader.fieldnames}

    missing_headers = REQUIRED_HEADERS - csv_headers
    extra_headers = csv_headers - REQUIRED_HEADERS

    if missing_headers or extra_headers:
        header_errors = []

        if missing_headers:
            header_errors.append(
                f"Missing columns: {', '.join(sorted(missing_headers))}"
            )

        if extra_headers:
            header_errors.append(
                f"Unexpected columns: {', '.join(sorted(extra_headers))}"
            )

        return {
            "status": False,
            "errors": [{
                "row_number": 0,
                "message": msg
            } for msg in header_errors],
            "to_insert": [],
            "to_update": [],
            "conflicts": []
        }

    to_insert = []
    to_update = []
    errors = []
    conflicts = []

    seen_emails = set()
    seen_roll_numbers = set()

    for row_number, row in enumerate(reader, start=2):
        row_errors = []

        name = row["name"].strip()
        roll_number = row["roll_number"].strip().lower()
        email = row["email"].strip().lower()
        branch = row["branch"].strip().lower()
        batch_raw = row["batch"].strip()
        is_active_raw = row["is_active"].strip().lower()

        if not name:
            row_errors.append("name is required")
        if not roll_number:
            row_errors.append("roll_number is required")
        if not email:
            row_errors.append("email is required")
        if not branch:
            row_errors.append("branch is required")

        try:
            batch = int(batch_raw)
            if batch <= 0:
                row_errors.append("batch must be positive integer")
        except:
            row_errors.append("batch must be positive integer")

        if is_active_raw not in {"true", "false"}:
            row_errors.append("is_active must be true or false")

        # ---------- IF VALIDATION FAILED ----------
        if row_errors:
            for msg in row_errors:
                errors.append({
                    "row_number": row_number,
                    "message": msg
                })
            continue

        conflict_messages = []

        # Duplicate email inside CSV
        if email in seen_emails:
            conflict_messages.append("Duplicate email found")

        # Duplicate roll number inside CSV
        if roll_number in seen_roll_numbers:
            conflict_messages.append("Duplicate roll number found")

        # DB conflicts
        if mode == "insert" and email in existing_emails:
            conflict_messages.append("Email already exists in database")

        if mode == "update" and email not in existing_emails:
            conflict_messages.append("Email does not exist for update")

        if conflict_messages:
            for msg in conflict_messages:
                conflicts.append({
                    "row_number": row_number,
                    "message": msg
                })
            continue

        seen_emails.add(email)
        seen_roll_numbers.add(roll_number)

        student_data = {
            "name": name,
            "roll_number": roll_number,
            "email": email,
            "branch": branch,
            "batch": batch,
            "is_active": is_active_raw == "true"
        }

        if mode == "insert":
            to_insert.append(student_data)
        else:
            to_update.append(student_data)

    if errors or conflicts:
        return {
            "status": False,
            "errors": errors,
            "to_insert": [],
            "to_update": [],
            "conflicts": conflicts
        }

    return {
        "status": True,
        "errors": [],
        "to_insert": to_insert,
        "to_update": to_update,
        "conflicts": []
    }