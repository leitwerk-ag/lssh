import csv

def convert_field(value):
    if value == "*":
        return None
    return value

def convert_row(row):
    user, hostname, command = row
    return convert_field(user), convert_field(hostname), command

def load(filename):
    try:
        with open(filename, "r") as f:
            reader = csv.reader(f)
            return [convert_row(row) for row in reader]
    except FileNotFoundError:
        return []
