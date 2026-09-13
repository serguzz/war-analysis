# How to reparse failed URLs

We've saved URLs in the file.
The url part contains name: second name - space - first name.
Also it contains country and DOB.

**We can:**

- search by second name as prefix;
- parse the page - validate if it's the right person
  - check country, other name parts (first name, e.g.)
  - check DOB
- if validated, save to DB those who validated

**Notes:**

1. new table column needed: `country`, defaulting to `Null`:

```python
country: Mapped[str | None] = mapped_column(
    String(100),
    nullable=True,
)
```

2. URL's second name does not have symbols: `'`, `-` , but search should be done with the symbols, if they are in the second name. This can be achieved after reviewing URLs that were not found/detected after the first pass without symbol accounting. Then, we can create relation dictionary, e.g.:

```python
NAME_VARIANTS = {
    "alvarez": ["alvarez", "al'varez"],
    "bonjakob": ["bonjakob", "bon-jakob"],
}
```
