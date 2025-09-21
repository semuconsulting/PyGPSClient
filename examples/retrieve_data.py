"""
retrieve_data.py

Illustration of pygpsclient's `retrieve_data()` helper method
to retrieve data from the pygpsclient.sqlite database.

Results will be ordered by utc timestamp. By default, only the
first 100 rows will be returned - override this with the
`limit` and `offset` arguments. The optional `sqlwhere` argument
must be a valid SQL WHERE clause.

Created on 18 Sep 2025

:author: semuadmin (Steve Smith)
:copyright: 2025 semuadmin
:license: BSD 3-Clause
"""

from pygpsclient import retrieve_data

result = retrieve_data(
    "/Users/myuser/pygpsclient.sqlite",
    sqlwhere="WHERE fix!='NO FIX'",
    limit=9999999,
    offset=0,
)
print(f"{len(result)} rows returned")
for row in result:
    print(row)
