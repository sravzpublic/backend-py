# Ensure double doubles in the dictionary keys
# Works
{"id": 1, "p_i": {"args": ["fut_copper_feb_17_usd_lme"], "kwargs": {"upload_to_aws": false}}, "k_i": {"return_aws_info_only": true}, "t_o": "development_api1"}
{"id": 4, "p_i": {"args": ["fut_gold_feb_17_usd_lme", "std"], "kwargs": {"upload_to_aws": true}}, "k_i": {"return_aws_info_only": true}, "t_o": "portfolio1", "d_o": null}
# PCA Components
{"id": 6, "p_i": {"args": [["fut_gold_feb_17_usd_lme", "fut_silver_feb_17_usd_lme"]], "kwargs": {"upload_to_aws": false}}, "k_i": {"return_aws_info_only": true}, "t_o": "portfolio1", "d_o": null}
# PCA Components upload to aws
{"id": 6, "p_i": {"args": [["fut_gold_feb_17_usd_lme", "fut_silver_feb_17_usd_lme"]], "kwargs": {"upload_to_aws": true}}, "k_i": {"return_aws_info_only": true}, "t_o": "portfolio1", "d_o": null}
{"id": 8, "p_i": {"args": ["stk_us_FB"], "kwargs": {"upload_to_aws": true}}, "k_i": {"return_aws_info_only": false}, "t_o": "api1", "d_o": null}
{"id": 9, "p_i": {"args": [["fut_gold_feb_17_usd_lme", "fut_silver_feb_17_usd_lme"]], "kwargs": {"upload_to_aws": false}}, "k_i": {"return_aws_info_only": true}, "t_o": "vagrant_api1", "d_o": null}
{"id":9,"p_i":{"args":[["testuser-daily_msft.1.csv-1548891136791"]],"kwargs":{"upload_to_aws":true,"device":"pc"}},"k_i":{"return_aws_info_only":true},"t_o":"vagrant_portfolio1","d_o":null,"cid":"sdr_alKoLlNkR37PAAAI","stopic":"combinedchart"}

#Start producer
sudo /home/kafka/kafka/bin/kafka-console-producer.sh --broker-list vagrant.sravz.com:9092 --topic vagrant_analytics1
#start consumer
sudo /home/kafka/kafka/bin/kafka-console-consumer.sh --bootstrap-server  vagrant.sravz.com:9092 --topic vagrant_portfolio1 --from-beginning

# To install virtualenvwrapper
pip3 install virtualenvwrapper
# Add these to ~/.profile and then source the profile
export WORKON_HOME=$HOME/.virtualenvs
export PROJECT_HOME=$HOME/workspace/sravz/backend-py
export VIRTUALENVWRAPPER_PYTHON=/usr/local/bin/python3.6
export VIRTUALENVWRAPPER_VIRTUALENV=/usr/local/bin/virtualenv
source ~/.local/bin/virtualenvwrapper.sh

 mkvirtualenv -p python3.6 python3.6
 workon python3.6
 cd workspace/sravz/backend-py/
 setvirtualenvproject
 #2to3 --output-dir=/Users/fd98279/workspace/sravz/backend-py.py3 -W -n /Users/fd98279/workspace/sravz/backend-py
 pip install -r ../ci-ansible/roles/sravz.node/files/requirements.txt



#Data
https://www.quandl.com/data/USTREASURY-US-Treasury
treasury_real_longterm_rate: https://www.quandl.com/api/v3/datasets/USTREASURY/REALLONGTERM.json?
api_key=My4TXrS2R1VeXt-shsYD
treasury_real_yieldcurve_rate: https://www.quandl.com/api/v3/datasets/USTREASURY/REALYIELD.json?api_key=My4TXrS2R1VeXt-shsYD
treasury_bill_rate: https://www.quandl.com/api/v3/datasets/USTREASURY/BILLRATES.json?api_key=My4TXrS2R1VeXt-shsYD
treasury_long_term_rate: https://www.quandl.com/api/v3/datasets/USTREASURY/LONGTERMRATES.json?api_key=My4TXrS2R1VeXt-shsYD


https://fred.stlouisfed.org/series/USD3MTD156N

# Restart Kafka services
sudo systemctl stop kafka_consumer_vagrant_analytics1@1.service
sudo systemctl stop kafka_consumer_vagrant_analytics1@2.service
sudo systemctl stop kafka_consumer_vagrant_analytics1@3.service
sudo systemctl start kafka_consumer_vagrant_analytics1@1.service
sudo systemctl start kafka_consumer_vagrant_analytics1@2.service
sudo systemctl start kafka_consumer_vagrant_analytics1@3.service

# Just kill, restart is very slow
kill -9 `ps aux | grep kafka_consumer_producer.py | awk {'print$2'}`


# To run in docker
```bash
# backend-node
# Run
docker run --rm -it -e NODE_ENV='vagrant' -e TOPIC_NAME=vagrant_analytics1 -e NSQ_HOST=nsqd -e NSQ_LOOKUPD_HOST=nsqlookupd -v /Users/fd98279/workspace/sravz/docker_volume/backend-node/:/etc/certs -v $(pwd):/pwd -v $HOME/.aws:/home/ubuntu/.aws:ro --network=sravz_internal -p 3030:3030 sravzpublic/backend-node:v2 bash

# Export these variables in the docker container or update the command above
export PFX_PATH=/etc/certs/sravz.pfx
export  PFX_PASSWORD=VALUE_HERE
export  NSQ_LOOKUPD_HOST=nsqlookupd
export  NODE_PORT=3030
export  FACEBOOK_CLIENT_SECRET=FAKE
export  MONGOLAB_URI=mongodb://sravz:sravz@mongo:27017/sravz
export RECAPTCHA_SECRET=FAKE
export GOOGLE_CLIENT_SECRET=FAKE
export FACEBOOK_APP_ID=FAKE
export NSQ_HOST=nsqd
export NSQ_LOOKUPD_HOST=nsqlookupd
export GOOGLE_CLIENT_KEY=FAKE
export MONGOLAB_SRAVZ_HISTORICAL_URI=mongodb://sravz_historical:sravz_historical@mongo:27017/sravz_historical
export NODE_ENV=vagrant

# To build containers
cd backend-py
docker build --tag public.ecr.aws/b8h3z2a1/sravz/backend-py:v2 .

# To delete are exited containers
docker ps -a | grep Exit | cut -d ' ' -f 1 | xargs docker rm

# backend-py
# Run
docker run --rm -it -e NODE_ENV='vagrant' -e TOPIC_NAME=vagrant_analytics1 -e NSQ_HOST=nsqd -e NSQ_LOOKUPD_HOST=nsqlookupd -v $(pwd):/pwd -v $HOME/.aws:/home/ubuntu/.aws:ro --network=sravz_internal sravzpublic/backend-py bash
# Run this in the container
cd /pwd/backend-py
python nsq_consumer_producer.py --topic vagrant_analytics1 --nsqd-host nsqd --nsq-lookupd-host nsqlookupd

# backend-go
# Run
docker run --rm -it -e NODE_ENV='vagrant' -e TOPIC_NAME=vagrant_analytics1 -e NSQ_HOST=nsqd -e NSQ_LOOKUPD_HOST=nsqlookupd -v $(pwd):/pwd -v $HOME/.aws:/home/ubuntu/.aws:ro --network=sravz_internal -p 8080:8080 sravzpublic/backend-go:v1 sh
# Run this in the container
./main -server

# frontend-ng
# Run
docker run --rm -it -e NODE_ENV='vagrant' -v $(pwd):/pwd --network=sravz_internal -p 4200:4200 sravzpublic/frontend-ng:v1 sh -c "cd /pwd;ng serve --host 0.0.0.0 --disable-host-check"
# Build
export environment=development
docker run --rm -it -e NODE_ENV='vagrant' -v $(pwd):/pwd -v $(pwd)../docker_volume/frontend-ng:/dist --network=sravz_internal sravzpublic/frontend-ng:v1 ng build --configuration=$(environment) --output-path="/dist/$(environment).dist"

# ci-ansible
docker run --rm -it -v $(pwd):/pwd -v $(pwd)/../docker_volume/frontend_ng/:/vagrant -v $(pwd)/../../secrets/:/secrets -v ~/.ssh:/root/.ssh:ro sravzpublic/ci-ansible:v1 bash
# To deploy frontend-ng:
cd /pwd
tar -cvzf development.dist.tar.gz development.dist --transform s/development.dist/dist/
ansible-playbook -vvvvv  playbooks/development/sravz.website.yml --vault-password-file /secrets/vault_pass --limit localhost,portfoliodev.sravz.com --tags dist_portfolio
# Docker compose up
COMPOSE_HTTP_TIMEOUT=200 docker-compose up

``bash
