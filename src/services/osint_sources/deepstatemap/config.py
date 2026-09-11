from datetime import date


BASE_URL = (
    "https://raw.githubusercontent.com/"
    "cyterat/deepstate-map-data/"
    "refs/heads/main/data"
)

FILE_NAME_TEMPLATE = "deepstatemap_data_{date:%Y%m%d}.geojson"

FIRST_AVAILABLE_DATE = date(2024, 7, 8)

REQUEST_TIMEOUT = 30