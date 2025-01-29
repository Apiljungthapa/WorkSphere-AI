
import pytz


def generate_initials(full_name: str) -> str:
  
    name_parts = full_name.split()

    # Get the first letter of the first name
    first_name_initial = name_parts[0][0].upper()

    # Get the first three letters of the last name (if available)
    last_name_initial = name_parts[1][:1].upper() if len(name_parts) > 1 else ""

    return first_name_initial + last_name_initial



nepal_tz = pytz.timezone("Asia/Kathmandu")

# Convert UTC time to Nepal's local time (Asia/Kathmandu)
def convert_utc_to_nepal_local(utc_dt):
    """ Convert UTC datetime to Nepal's local time (NPT) """
    utc_dt = utc_dt.replace(tzinfo=pytz.utc)  # Make sure it's timezone-aware
    nepal_local_time = utc_dt.astimezone(nepal_tz)  # Convert to Nepal's time zone
    return nepal_local_time