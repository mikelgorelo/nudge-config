import json, datetime

# 1. Fetch the data
try:
    with open('sofa.json', 'r') as f:
        data = json.load(f)
except Exception as e:
    print("Error reading the downloaded SOFA feed.")
    exit(1)

# Extract N and N-1
major_n = data['OSVersions'][0]
major_n_minus_1 = data['OSVersions'][1]

now = datetime.datetime.utcnow()

def calculate_deadline(release_date_str, grace_days=14):
    clean_date_str = release_date_str.split('T')[0]
    release_date = datetime.datetime.strptime(clean_date_str, '%Y-%m-%d')
    deadline_date = release_date + datetime.timedelta(days=grace_days)
    if deadline_date < now:
        deadline_date = now + datetime.timedelta(days=3)
    return deadline_date.strftime('%Y-%m-%dT00:00:00Z')

# 2. Build the Requirements List
requirements = [
    # RULE 1: If on the newest Major OS, stay patched
    {
        "requiredMinimumOSVersion": major_n['Latest']['ProductVersion'],
        "requiredInstallationDate": calculate_deadline(major_n['Latest']['ReleaseDate']),
        "targetedOSVersionsRule": major_n['OSVersion']
    },
    # RULE 2: If on the N-1 Major OS, stay patched
    {
        "requiredMinimumOSVersion": major_n_minus_1['Latest']['ProductVersion'],
        "requiredInstallationDate": calculate_deadline(major_n_minus_1['Latest']['ReleaseDate']),
        "targetedOSVersionsRule": major_n_minus_1['OSVersion']
    },
    # RULE 3: THE FALLBACK. If on N-2 or older, force upgrade to the latest N-1
    {
        "requiredMinimumOSVersion": major_n_minus_1['Latest']['ProductVersion'],
        "requiredInstallationDate": (now + datetime.timedelta(days=7)).strftime('%Y-%m-%dT00:00:00Z'),
        "targetedOSVersionsRule": "default"
    }
]

# 3. Build the JSON
nudge_dict = {
    "osVersionRequirements": requirements,
    "userExperience": {
        "nudgeRefreshCycle": 60,
        "approachingRefreshCycle": 240,
        "imminentRefreshCycle": 30,
        "approachingWindow": 10,
        "imminentWindow": 3,
        "randomDelay": False
    },
    "userInterface": {
        "updateElements": [
            {
                "_language": "en",
                "actionButtonText": "Update Now",
                "customAdmissionText": "Your device is running an unsupported version of macOS.",
                "mainContentHeader": "Critical Security Upgrade Required",
                "mainContentText": "To maintain access to company resources, your Mac must be upgraded to a supported version of macOS. Please click 'Update Now' to begin.",
                "mainHeader": "macOS Upgrade Required"
            }
        ]
    }
}

with open('nudge.json', 'w') as f:
    json.dump(nudge_dict, f, indent=4)

print("Nudge config updated: N and N-1 supported. N-2 and older forced to N-1.")
