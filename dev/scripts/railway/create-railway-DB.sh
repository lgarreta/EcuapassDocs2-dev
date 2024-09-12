## Create realway project in the web (https://railway.app/)

## Add a Postgres service in the web

## Login to Railway and link to project using railway CLI: 
    # railway login
    # railway link : project (ecuapassdocs), environment (production), service (ecuapassdocs)

## Get Railway vars:
railway variables --json > railway-vars.json

## Create and source Postgres DB variables from Railway vars:
source-dbvars.py railway-vars.json > railway-vars-PGDB.sh
source railway-vars-PGDB.sh

## Create database, user, and GRANT privileges
db="ecuapassdocsdb"
usr="admindb"
psw="admindb"
psql -c "CREATE USER $usr WITH PASSWORD '$psw';"
psql -c "CREATE DATABASE $db WITH OWNER='$usr';"
psql -c "GRANT ALL PRIVILEGES ON DATABASE $db TO $usr;"

## Update Railway PG variables to current DB settings:
PGDATABASE=$db
PGUSER=$usr
PGPASSWORD=$psw

## Create Railway Postgres vars for ecuapassdocs 
echo "export PGDATABASE=$PGDATABASE" > railway-dbvars.sh
echo "export PGUSER=$PGUSER" >> railway-dbvars.sh
echo "export PGPASSWORD=$PGPASSWORD" >> railway-dbvars.sh
echo "export PGHOST=$PGHOST" >> railway-dbvars.sh
echo "export PGPORT=$PGPORT" >> railway-dbvars.sh

## Change (manually) variables values on the web: postgress service:
    # set PGDATABASE : "ecupassdocsdb"
    # set PGUSER     : "admin"
    # set PGPASSWORD : "admin"
    # set PGHOST     : public domain host (see Variables)
    # set PGPORT     : public domain port (see Variables)
