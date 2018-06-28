I'm not to familiar with making web apps efficient with regards to deployment
/devops

I can de-duplicate any tables using pandas functions.

I added the id to consumption file before importing to aid in any querying
which may involve joining the two tables.

Set USE_TZ = False as it was causing an issue with import the timestamps
in the dataset. Having this as False isn't as impactful as country is not
provided in the dataset.

Could implement functionality to only add new rows if new data is collected
which needs to be imported.

Other tables/graphs I could have made are with relative ease:

- Number of users for each tariff
- Number of users for each area
- Number of users for each area on a specific tariff and vice versa
- Details on a specific area and/or tariff
