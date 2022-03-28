import datetime
import os

import requests

try:
    import requests_cache
except ImportError:
    pass
else:
    requests_cache.install_cache()

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from dateutil import parser as time_parser


def get_star_data(repo):
    headers = {"Accept": "application/vnd.github.v3.star+json"}

    if os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = "Bearer " + os.environ.get("GITHUB_TOKEN")

    return requests.get(
        f"https://api.github.com/repos/{repo}/stargazers",
        headers=headers,
        params={"per_page": 100},
    ).json()


def get_metrics(repo):
    headers = {}
    if os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = "Bearer " + os.environ.get("GITHUB_TOKEN")

    return requests.get(f"https://api.github.com/repos/{repo}", headers=headers).json()


def get_largest_time(dates):
    """Omit year for dates if all dates are within the current month"""
    months = [d.month for d in dates]

    if months.count(months[0]) == len(months):
        return "%b %d"

    return "%d %b %Y"


def diff_month(d1, d2):
    return (d1.year - d2.year) * 12 + d1.month - d2.month


repo = input("Enter a repository to view star graph for: ")

if get_metrics(repo).get("stargazer_count", 0):
    print(
        "An error occured, the repository has more than 100 stars or rate limit reached"
    )
    exit()

data = get_star_data(repo)

if isinstance(data, dict) and data.get("message"):
    print(data["message"])
    print('Please make sure the repository is in the format "user/repo"')
    exit()

list_x = []
list_y = []

for amount_of_stars, star in enumerate(data, start=1):
    star_time = time_parser.parse(star["starred_at"])

    list_x.append(star_time)
    list_y.append(amount_of_stars)

list_x.append(datetime.datetime.today())
list_y.append(amount_of_stars)

# plot
fig, ax = plt.subplots()
ax.plot(list_x, list_y, marker=".")
ax.xaxis_date()  # interpret the x-axis values as dates
fig.autofmt_xdate()  # make space for and rotate the x-axis tick labels

# date formatting
myFmt = mdates.DateFormatter(get_largest_time(list_x))
ax.xaxis.set_major_formatter(myFmt)

# metadata
plt.title("Star history for " + repo)
plt.xlabel("Time")
plt.ylabel("Stars")

plt.show()
