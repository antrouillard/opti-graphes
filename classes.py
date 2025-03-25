class Shift:
    def __init__(self, shift_id, length, forbidden_following_shifts):
        self.shift_id = shift_id
        self.length = length
        self.forbidden_following_shifts = forbidden_following_shifts.split('|') if forbidden_following_shifts else []
    
    def __repr__(self):
        return f"Shift(shift_id={self.shift_id}, length={self.length}, forbidden_following_shifts={self.forbidden_following_shifts})"


class Staff:
    def __init__(self, staff_id, max_shifts, max_total_minutes, min_total_minutes,
                 max_consecutive_shifts, min_consecutive_shifts, min_consecutive_days_off, max_weekends):
        self.staff_id = staff_id
        self.max_shifts = max_shifts
        self.max_total_minutes = max_total_minutes
        self.min_total_minutes = min_total_minutes
        self.max_consecutive_shifts = max_consecutive_shifts
        self.min_consecutive_shifts = min_consecutive_shifts
        self.min_consecutive_days_off = min_consecutive_days_off
        self.max_weekends = max_weekends
    
    def __repr__(self):
        return (f"Staff(staff_id={self.staff_id}, max_shifts={self.max_shifts}, max_total_minutes={self.max_total_minutes}, "
                f"min_total_minutes={self.min_total_minutes}, max_consecutive_shifts={self.max_consecutive_shifts}, "
                f"min_consecutive_shifts={self.min_consecutive_shifts}, min_consecutive_days_off={self.min_consecutive_days_off}, "
                f"max_weekends={self.max_weekends})")


class DaysOff:
    def __init__(self, staff_id, days_off):
        self.staff_id = staff_id
        self.days_off = list(map(int, days_off.split(',')))
    
    def __repr__(self):
        return f"DaysOff(staff_id={self.staff_id}, days_off={self.days_off})"


class ShiftRequest:
    def __init__(self, staff_id, day, shift_id, weight):
        self.staff_id = staff_id
        self.day = int(day)
        self.shift_id = shift_id
        self.weight = int(weight)
    
    def __repr__(self):
        return f"ShiftRequest(staff_id={self.staff_id}, day={self.day}, shift_id={self.shift_id}, weight={self.weight})"


class CoverRequirement:
    def __init__(self, day, shift_id, requirement, weight_under, weight_over):
        self.day = int(day)
        self.shift_id = shift_id
        self.requirement = int(requirement)
        self.weight_under = int(weight_under)
        self.weight_over = int(weight_over)
    
    def __repr__(self):
        return (f"CoverRequirement(day={self.day}, shift_id={self.shift_id}, requirement={self.requirement}, "
                f"weight_under={self.weight_under}, weight_over={self.weight_over})")
