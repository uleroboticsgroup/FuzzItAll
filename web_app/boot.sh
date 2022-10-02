#!/bin/sh
######################################################################
#
#   boot.sh - Script used to boot the FuzzItAll web service through a
#             Docker container.
#
######################################################################

# FUNCTIONS
#---------------------------------------------------------------------

function init_app() {
  flask create-db
  flask create-admin --username admin --password admin
}


# MAIN SCRIPT
#---------------------------------------------------------------------

# load python virtual environment
source venv/bin/activate

# initialize Flask app
while true; do
  init_app
  if [[ "$?" == "0" ]]; then
    break
  fi
    echo Deploy command failed, retrying in 5 secs...
    sleep 5
done

# deploy the application through gunicorn
exec gunicorn -b :5000 --access-logfile - --error-logfile - entrypoint:app --timeout 90

exit 0
