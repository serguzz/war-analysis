# TODO

1. Add to `soldier` models:
    - `age` (int, None),
    - `country` (str, None),
    - `source_url_accessible` (boolean, None)

    - When migrating `source_url_accessible` - set `True` to already existing records, since they were parsed by accessing the source url.

2. Completely manually test how fallback_failed_urls works.
    - What resulting Soldiers we have?
    - How they'll be written to DB?
    - Try a few writes to DB, with `source_url_accessible` - set `False`
    - Review the records in DB and related Units, Locations, Dates, etc.

