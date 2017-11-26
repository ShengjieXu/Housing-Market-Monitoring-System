#!/bin/bash
service redis_6379 start

pip install -r requirements.txt

cd data_pipeline
python listing_monitor.py &
python listing_fetcher.py &
python listing_deduper.py &

echo "====================================================="
read -p "PRESS [ENTER] TO TERMINATE PROCESSES." PRESSKEY

kill $(jobs -p)