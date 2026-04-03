

def build_unsigned_from_coupon(coupon):
    return (
        f"{coupon.id}|{coupon.student_id}|{coupon.mess_id}|"
        f"{coupon.college_id}|{coupon.date}|"
        f"{coupon.meal_type.value}|{coupon.meal_slot.value}"
    )


def build_unsigned_from_payload(payload):
    return (
        f"{payload.coupon_id}|{payload.student_id}|{payload.mess_id}|"
        f"{payload.college_id}|{payload.date}|"
        f"{payload.meal_type.value}|{payload.meal_slot.value}"
    )