## Create realway project in the web

## Add a Postgres servive in the web

## Login to Railway and link to project using railway CLI: 
## And select project (ecuapassdocs), environment (production), service (ecuapassdocs)
#railway login
#railway link

## Get Railway vars:
railway variables --json > railway-vars.json

## Source variables:
source-dbvars.py railway-vars.json > railway-vars-PGDB.sh
source railway-vars-PGDB.sh

## Create DB, USER, and GRANT PRIVILEGES
db="ecuapassdocsdb"
usr="admindb"
psw="admindb"
##railway run echo "CREATE USER $usr WITH PASSWORD '$psw';"
##psql -c "CREATE USER $usr WITH PASSWORD '$psw';"
echo "CREATE DATABASE $db WITH OWNER='$usr';"
psql -c "CREATE DATABASE $db WITH OWNER='$usr';"
echo "GRANT ALL PRIVILEGES ON DATABASE $db TO $usr;"
psql -c "GRANT ALL PRIVILEGES ON DATABASE $db TO $usr;"


## Update Railway PG variables to current DB settings:
PGDATABASE=$db
PGUSER=$usr
PGPASSWORD=$psw

## Create vars for ecuapassdocs 
echo "PGDATABASE=$PGDATABASE" > db_vars.sh
echo "PGUSER=$PGUSER" >> db_vars.sh
echo "PGPASSWORD=$PGPASSWORD" >> db_vars.sh
echo "PGHOST=$PGHOST" >> db_vars.sh
echo "PGPORT=$PGPORT" >> db_vars.sh

