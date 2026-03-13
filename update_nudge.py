import json, datetime

# 1. Read Apple Release Data from the locally downloaded SOFA feed
try:
    with open('sofa.json', 'r') as f:
        data = json.load(f)
except Exception as e:
    print("Error reading the downloaded SOFA feed.")
    exit(1)

# 2. Get the latest active major OS version
latest_os = data['OSVersions'][0]
latest_version = latest_os['Latest']['ProductVersion']
release_date_str = latest_os['Latest']['ReleaseDate'] # e.g., "2026-03-10T00:00:00Z"

# 3. Handle the Date (Fixes the ValueError)
# We split by 'T' to just get the date part (2026-03-10)
clean_date_str = release_date_str.split('T')[0]
release_date = datetime.datetime.strptime(clean_date_str, '%Y-%m-%d')

# 4. Calculate Deadline (Release Date + 14 Days)
deadline_date = release_date + datetime.timedelta(days=14)

# 5. Logic Check: Don't set a deadline in the past for current users
# If 14 days after release is ALREADY in the past, give them a 3-day grace period from today
now = datetime.datetime.utcnow()
if deadline_date < now:
    deadline_date = now + datetime.timedelta(days=3)

deadline = deadline_date.strftime('%Y-%m-%dT00:00:00Z')

# 6. Build the custom Nudge JSON
nudge_dict = {
    "osVersionRequirements": [
        {
            "requiredMinimumOSVersion": latest_version,
            "requiredInstallationDate": deadline,
            "targetedOSVersionsRule": "default"
        }
    ],
    "userExperience": {
        "nudgeRefreshCycle": 60,
        "approachingRefreshCycle": 240,  # 4 hours when far from deadline
        "imminentRefreshCycle": 30,      # 30 mins when very close
        "approachingWindow": 10,         # Start "approaching" 10 days out
        "imminentWindow": 3,             # Start "imminent" 3 days out
        "randomDelay": False
    },
    "userInterface": {
        "updateElements": [
            {
                "_language": "en",
                "actionButtonText": "Update Now",
                "customAdmissionText": "This update is required for company security compliance.",
                "informationButtonText": "Learn Why...",
                "mainContentHeader": "Help us keep your Mac secure",
                "mainContentText": "A security update is available for your Mac. To ensure continued access to company resources, please install this update before the deadline.",
                "mainHeader": "macOS Update Required"
            }
        ]
    }
}

# 7. Save the final file
with open('nudge.json', 'w') as f:
    json.dump(nudge_dict, f, indent=4)
    
print(f"Successfully generated Nudge config for macOS {latest_version}")
print(f"Release Date: {clean_date_str} | Target Deadline: {deadline}")
