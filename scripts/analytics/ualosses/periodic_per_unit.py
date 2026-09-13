"""
Script to accept parameters:
--period (week, month, day)
--date-from (e.g., 2022-02-24)
--date-to
--unit-name (e.g., "5th brigade")


The script to draw a diagram of losses
- (distinct sum of died, + dissapeared (and not released from captivity))
- or all: distinct sum of died + dissapeared (regardless if released later)

Put the diagram to
- data/analysis/ualosses/diagrams

Q: 
1. Should the path be in config.py?
2. What should be in src/services/analytics/ualosses/service.py ?
3. Any other considerations?
4. Should the analytics be done mostly by Postgres SQL queries or by Python code?

"""
