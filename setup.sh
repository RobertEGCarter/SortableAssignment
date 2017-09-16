##First Perform Python setup, if python 2.7.5, wheel and pip are installed, this should be no problem.
##Upgrade pip
pip install --upgrade pip

##Install the python postgres driver
python -m pip install psycopg2

##Now the more complicated postgres setup
##Find and init postgres 9.3
updatedb

PGBINDIR=`locate /bin/pg_ctl | awk -F'/pg_ctl' '{print $(NF-1)}'`
[ -z "$PGBINDIR" ] && echo "Error: can't find postgresql" && exit 1

$PGBINDIR/postgresql93-setup initdb

systemctl enable postgresql-9.3
systemctl start postgresql-9.3

#gotta wait for postgres to get up and going
sleep 5
updatedb

##Now that postgres is initialized, we must ensure that it is configured
##To accept connections from python (running locally)
##Thankfully that is already in the configuration, we just need to change the ident method

PGHBA=`locate /data/pg_hba.conf`

sed -i 's/   ident/   md5/g' ${PGHBA}

##Reboot psql 
systemctl restart postgresql-9.3

##Now that we're running, we need to create a user for the current logged in user
USERID="$USER"

##Currently only the postgres user has an account, and it's in peer method, so we sudo in
sudo -u postgres psql postgres -c "CREATE USER $USERID with password '$USERID';"

##Now modify the local python script to take into account the new username/pwd (This only works once)
sed -i 's/root/'"$USERID"'/g' assignment.py