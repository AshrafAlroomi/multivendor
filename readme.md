# Multi-vendor-api



## Dependence
python 3.8 +

[postgresSQL](https://adamtheautomator.com/install-postgresql-on-a-ubuntu/)

[pgadmin](https://www.pgadmin.org/download/pgadmin-4-apt/) 

requirements.txt file 


### Run locally
First create db with same config in settings_local

```bash
python manage.py migrate --settings=project.settings_local 
python manage.py runserver 8000 --settings=project.settings_local 
```

## Branches and Pull request

Create new branch for each ticket on jira , with prefix and the id of that ticket 

for example :
```bash
task/ISO-6770-add-new-product
```

for production bugs fixes branch 
```bash
hotfix/ISO-1770-product-not-shown
```

for uat/staging bugs fixes branch 
```bash
fix/ISO-3770-product-not-shown
```

All tasks commit should point to develop for example [task/ISO-6770] -> [develop]

Please follow these rules for commit messages [commit-stranded](https://cbea.ms/git-commit/)

include the ticket url/s in the PRs. 

### Migrations

steps to edit models 

1 - after finish editing the model locally , 
and creating migrations files and make migrations to the db.

2 - after you get approve on the PR .

3 - you should revert the migration to the old version before 
you push the changes
[see](https://docs.djangoproject.com/en/3.2/topics/migrations/#reversing-migrations)

4 - you should also delete the created migrations files on your branch

5 - then pull from develop to your branch and create migrations and migrate to the db

6 - now you made sure the version of migration are correct and dependence
and without corrupting you database
