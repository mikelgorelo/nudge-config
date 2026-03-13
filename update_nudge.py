import json, datetime

# 1. Read Apple Release Data from the locally downloaded SOFA feed
try:
    with open('sofa.json', 'r') as f:
        data = json.load(f)
except Exception as e:
    print("Error reading the downloaded SOFA feed.")
    exit(1)

# 2. Get the latest active major OS version (e.g., Sonoma or Sequoia)
latest_os = data['OSVersions'][0]
latest_version = latest_os['Latest']['ProductVersion']

# 3. Calculate deadline (14 days from today)
deadline = (datetime.datetime.utcnow() + datetime.timedelta(days=14)).strftime('%Y-%m-%dT%H:%M:%SZ')

# 4. Build your custom Nudge JSON
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
        "randomDelay": False
    },
    "userInterface": {
        "updateElements": [
            {
                "_language": "en",
                "actionButtonText": "Update Now",
                "customAdmissionText": "This is an automated update requirement from IT.",
                "informationButtonText": "More Info",
                "mainContentHeader": "Your IT Department requires an update",
                "mainContentNote": "Important Security Update",
                "mainContentText": "A fully up-to-date device is required to ensure that IT can accurately protect your computer.\n\nIf you do not update your computer, you may lose access to company resources.",
                "mainHeader": "Your Mac requires an important update"
            }
        ]
    }
}

# 5. Save the final file
with open('nudge.json', 'w') as f:
    json.dump(nudge_dict, f, indent=4)
    
print(f"Successfully generated Nudge config for macOS {latest_version} with deadline {deadline}")
