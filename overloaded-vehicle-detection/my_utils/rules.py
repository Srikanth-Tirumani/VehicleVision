# my_utils/rules.py

CAPACITY_RULES = {
    "bike": {"passengers": 2, "cargo": 25, "name": "Two-Wheeler / Bike"},
    "auto": {"passengers": 3, "cargo": 60, "name": "Auto Rickshaw"},
    "car": {"passengers": 5, "cargo": 200, "name": "Passenger Car"},
    "van": {"passengers": 8, "cargo": 500, "name": "Van / Minivan"},
    "bus": {"passengers": 45, "cargo": 2000, "name": "Bus / Coach"},
    "truck": {"passengers": 3, "cargo": 5000, "name": "Heavy Truck"},
    "lorry": {"passengers": 3, "cargo": 8000, "name": "Commercial Lorry"},
}

def check_overload(vehicle_type, passengers, cargo_est):
    """
    Evaluates passenger count and cargo load against road safety capacity rules.
    Returns (status, reason_string):
      - status: "Overloaded" or "OK" or "Unknown"
      - reason: Explanation of the violation if overloaded
    """
    vt = vehicle_type.lower()
    if vt not in CAPACITY_RULES:
        return "Unknown", "Unknown vehicle class"

    r = CAPACITY_RULES[vt]
    max_p = r["passengers"]
    max_c = r["cargo"]

    reasons = []
    if passengers > max_p:
        if vt == "bike" and passengers >= 3:
            reasons.append(f"Illegal Triple-Riding ({passengers} riders, max {max_p})")
        else:
            reasons.append(f"Exceeded passenger limit ({passengers}/{max_p} persons)")

    if cargo_est > max_c:
        reasons.append(f"Excess cargo weight (~{cargo_est}kg / max {max_c}kg)")

    if len(reasons) > 0:
        return "Overloaded", " & ".join(reasons)
    
    return "OK", "Within capacity limits"
