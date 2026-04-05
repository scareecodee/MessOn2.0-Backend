import csv
from io import StringIO


def generate_all_students_bill_csv(data):
    output = StringIO()
    writer = csv.writer(output)

    writer.writerow([
    "Name", "Email","Roll No",
    "Branch", "Batch", "Total Billing Periods",
    "Billing Start Date", "Billing End Date",
    "Total Bill"
    ])

    for row in data:
        writer.writerow([
            row.name,
            row.email,
            row.roll_no,
            row.branch,
            row.batch,
            row.total_billing_periods,
            row.start_date.strftime("%Y-%m-%d"),
            row.end_date.strftime("%Y-%m-%d"),
            row.total_bill,
        ])

    output.seek(0)
    return output

def generate_students_bill_history_csv(data):
    output = StringIO()
    writer = csv.writer(output)

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

    output.seek(0)
    return output