
from helper.dashboard import Dashboard

from helper.dashboard_commands import unlock_protective_stop, running, robotmode, is_in_remote_control, program_state, safety_status

dashboard = Dashboard("169.254.46.85")
response = dashboard.send_command(robotmode())
print(response)

print("is_faulty", dashboard.is_faulty())
print("is_in_remote_control", dashboard.is_in_remote_control())

# Nothalt: safetystatus == ROBOT_EMERGENCY_STOP

# Fehler robotmode == "POWER_OFF"
# program_state == "STOPPED"
# safety_status == "FAULT"

# Zurücksetzen:
# close safety popup, 
# restart safety, 
# power on, 
# brake release
# - Neustart x2
# - Start
# - Fensteg schließen
# - Local

# - Minimal Hochfahren
# - Emergency Open (Abfrage, ob schon geöffnet ist)
# - Weiter hoch
# - Activate Gripper