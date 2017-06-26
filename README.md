# eldo

## Requirements
* python 2.7
* pip

pip install CMRESHandler

## Start Polling with

python src/start_polling_ticker.py

## Run in a cron job

chmod 755 src/import_data.py

*/5 * * * * ~/eldo/eldo/src/import_data.py