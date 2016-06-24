# Script to validate the YAML entries and check links

import sys
import glob

import six
import yaml
import requests

REQUIRED = ('title', 'creators', 'description')
OPTIONAL = ('source-url', 'live-url', 'doi', 'images',
            'contact-email', 'contact-github', 'orcid')
URLS = ('source-url', 'live-url')

status = 0

def check_link(url):
    try:
        r = requests.get(url, timeout=30)
    except Exception:
        return False
    else:
        return r.status_code == 200

yaml_files = glob.glob('*/*.yml')
yaml_files.remove('site_generator/events.yml')

print("Processing {0} file(s)".format(len(yaml_files)))

urls = []
errors = []

for yaml_file in yaml_files:

    # Check that YAML validates
    try:
        with open(yaml_file) as f:
            entry = yaml.load(f)
    except Exception:
        errors.append("Failed to parse {0}".format(yaml_file))
        continue

    if entry is None:
        errors.append("Empty file: {0}".format(yaml_file))
        continue

    # Check that required keywords are present
    missing = []
    for keyword in REQUIRED:
        if not keyword in entry:
            missing.append(keyword)
    if missing:
        errors.append("Missing keywords: {0}".format(", ".join(missing)))

    # Check that there are no unknown keywords
    unknown = []
    for keyword in entry:
        if not keyword in REQUIRED + OPTIONAL:
            unknown.append(keyword)
    if unknown:
        errors.append("Unknown keywords: {0}".format(", ".join(unknown)))

    # Find all links
    for keyword in URLS:
        if keyword in entry:
            value = entry[keyword]
            if value is None:
                pass
            elif isinstance(value, six.string_types):
                urls.append(value)
            else:  # list of links
                for link in value:
                    urls.append(link)

# Check links
import multiprocessing
p = multiprocessing.Pool(processes=10)
print("Checking {0} link(s)".format(len(urls)))
results = p.map(check_link, urls)
failed = []
for success, url in zip(results, urls):
    if not success:
        failed.append(url)
if failed:
    errors.append("Found broken links:")
    for url in failed:
        errors.append('- ' + url)

if errors:
    for error in errors:
        print(error)
    sys.exit(1)
