"""
This class to use client.py and parser.py (and models.py)
to crawl the ualoosses website.


The problem with ualosses is that it paginates only up to page 499,
while there are about 215000 soldiers links and hense, 2000+ pages.

https://ualosses.org/en/soldiers/?page=499&dob_start=&dob_end=&dod_start=&dod_end=&military_unit=&first_name=&last_name=&military_rank=&category=&casualty_type=&sort=dob&direction=asc
https://ualosses.org/en/soldiers/?page=499&sort=dob&direction=asc&dob_start=1977-02-22

https://ualosses.org/en/soldiers/?page=1&dod_start=01.01.2014&dod_end=01.09.2026&sort=dod&direction=asc&
this works if there is date of death in the info.

https://ualosses.org/en/soldiers/?page=1&sort=last_name&direction=desc
This works for sorting by last names.

The dod and dob, are present for not all records/links, so we cannot use that.

last_name , though exist for all records, and we can use it:

https://ualosses.org/en/soldiers/?page=1&sort=last_name&direction=asc&last_name=ni
- this searches substring in last_name.

If filter by 1 letter : last_name=a , we'll again get too many records 
and to many pages. So, we can try with 2-letter combinations:

aa, ab, ac, ...
...
za, zb, zc, ...

And with binary search find pages, that have the combination (e.g., "ni")
at the last_name start, not only substring in the middle.

Implement a crawler that collects all soldier URLs from UA Losses by splitting the dataset into two-letter last-name prefixes (`aa`–`zz`). For each prefix, use the site's last-name substring filter to locate the relevant results, then keep only records whose last name actually starts with that prefix. Efficiently locate the first relevant page instead of scanning from the beginning, then process subsequent pages until the prefix ends. Deduplicate soldier URLs across all queries.

Implement a crawler that collects all soldier URLs from UA Losses by splitting the dataset into two-letter last-name prefixes (`aa`–`zz`). The crawler input is a list of two-letter prefixes to process, and its output is a deduplicated list of soldier URLs.

For each prefix, use the site's last-name substring filter to find candidate records, then keep only records whose last name actually starts with the requested two-letter prefix (case-insensitive).

To locate the first relevant page efficiently, use binary search over the available pages. Check the last name of the first/last records on each candidate page and adjust the search range accordingly. Once the first matching page is found, process pages sequentially (`page + 1`) until the records no longer start with the requested prefix. Stop when the prefix has ended or the available pages are exhausted.

Deduplicate soldier URLs across all prefixes.


"""