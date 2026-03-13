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

# 2. Extract ONLY the number from the OS Name (e.g., "Tahoe 26" -> "26")
def get_major_version_number(os_string):
    # This splits the string and takes the last part (the number)
    return os_string.split()[-1]

version_n = get_major_version_number(major_n['OSVersion'])
version_n_minus_1 = get_major_version_number(major_n_minus_1['OSVersion'])

# 3. Build the Requirements List
requirements = [
    {
        "requiredMinimumOSVersion": major_n['Latest']['ProductVersion'],
        "requiredInstallationDate": calculate_deadline(major_n['Latest']['ReleaseDate']),
        "targetedOSVersionsRule": version_n
    },
    {
        "requiredMinimumOSVersion": major_n_minus_1['Latest']['ProductVersion'],
        "requiredInstallationDate": calculate_deadline(major_n_minus_1['Latest']['ReleaseDate']),
        "targetedOSVersionsRule": version_n_minus_1
    },
    {
        "requiredMinimumOSVersion": major_n_minus_1['Latest']['ProductVersion'],
        "requiredInstallationDate": (now + datetime.timedelta(days=7)).strftime('%Y-%m-%dT00:00:00Z'),
        "targetedOSVersionsRule": "default",
        "aboutUpdateURL": "https://support.apple.com/en-us/HT201222"
    }
]

# 4. Build the JSON
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
                "mainContentHeader": "Security Upgrade Required",
                "mainContentText": "To maintain access to company resources, your Mac must be upgraded to a supported version of macOS. Please click 'Update Now' to begin.",
                "mainHeader": "macOS Upgrade Required"
            }
        ]
    }
}

with open('nudge.json', 'w') as f:
    json.dump(nudge_dict, f, indent=4)

print(f"Nudge config generated. N={version_n}, N-1={version_n_minus_1}")
