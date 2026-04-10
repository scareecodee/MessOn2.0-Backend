import csv
from io import StringIO


# def generate_all_students_bill_csv(data):
#     output = StringIO()
#     writer = csv.writer(output)
#
#     writer.writerow([
#     "Name","Email","Roll No", "Branch","Batch","Total Billing Periods","Billing Start Date","Billing End Date", "Total Bill"
#     ])
#
#     for row in data:
#         writer.writerow([
#             row.name,
#             row.email,
#             row.roll_no,
#             row.branch,
#             row.batch,
#             row.total_billing_periods,
#             row.billing_start_date.strftime("%Y-%m-%d"),
#             row.billing_end_date.strftime("%Y-%m-%d"),
#             row.total_bill,
#         ])
#
#     output.seek(0)
#     return output

import io
import csv

def generate_all_students_bill_csv(data):
    import io, csv

    output = io.StringIO(newline='')  # ✅ IMPORTANT FIX

    writer = csv.writer(
        output,
        delimiter=',',
        quoting=csv.QUOTE_MINIMAL
    )

    writer.writerow([
        "Name","Email","Roll No","Branch","Batch",
        "Total Billing Periods","Billing Start Date",
        "Billing End Date","Total Bill"
    ])

    for row in data:
        writer.writerow([
            row.name.strip(),
            row.email.strip(),
            row.roll_no,
            row.branch,
            row.batch,
            row.total_billing_periods,
            row.billing_start_date.strftime("%Y-%m-%d"),
            row.billing_end_date.strftime("%Y-%m-%d"),
            round(row.total_bill,2),
        ])

    csv_string = output.getvalue()
    output.close()

    return io.BytesIO(
        b'\xef\xbb\xbf' + csv_string.encode("utf-8")
    )

def generate_students_bill_history_csv(data):
    output = io.StringIO(newline='')

    writer = csv.writer(
        output,
        delimiter=',',
        quoting=csv.QUOTE_MINIMAL
    )

    writer.writerow([
    "Date", "Breakfast","Consumed",
    "Lunch", "Consumed", "Dinner",
    "Consumed"
    ])

    for row in data:
        writer.writerow([
            row.date.strftime("%Y-%m-%d"),
            row.breakfast.meal_type,
            row.breakfast.consumed,
            row.lunch.meal_type,
            row.lunch.consumed,
            row.dinner.meal_type,
            row.dinner.consumed
        ])

    csv_string = output.getvalue()
    output.close()

    return io.BytesIO(
        b'\xef\xbb\xbf' + csv_string.encode("utf-8")
    )