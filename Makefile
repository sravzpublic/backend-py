# Makefile
SHELL := /bin/bash

cd-backend-py-dir:
	cd ${BACKEND-PY-DIR}

run:
	python nsq_consumer_producer.py --nsqd-host ${NSQ_HOST} --nsq-lookupd-host ${NSQ_LOOKUPD_HOST}

run_in_container:
	docker run --rm -it -v $(CURDIR):/pwd -v $(HOME)/.aws:/home/airflow/.aws:ro  -e NODE_ENV=vagrant -e MONGOLAB_URI=$(MONGOLAB_URI) -e MONGOLAB_SRAVZ_HISTORICAL_URI=$(MONGOLAB_SRAVZ_HISTORICAL_URI) -e NSQ_HOST=nsqd-1:4150,nsqd-2:4150,nsqd-3:4150 -e NSQ_LOOKUPD_HOST=nsqlookupd-1:4161,nsqlookupd-2:4161,nsqlookupd-3:4161  -e EODHISTORICALDATA_API_KEY=$(EODHISTORICALDATA_API_KEY) -v $(HOME)/.aws:/home/ubuntu/.aws:ro --network=sravz_default public.ecr.aws/b8h3z2a1/sravz/backend-py:$(BACKEND_PY_IMAGE_Version) bash -c 'cd /pwd; exec "bash"'

run_cmd_in_container:
	docker run --rm -it -v $(CURDIR):/pwd -v $(HOME)/.aws:/home/airflow/.aws:ro  -e NODE_ENV=vagrant -e MONGOLAB_URI=$(MONGOLAB_URI) -e MONGOLAB_SRAVZ_HISTORICAL_URI=$(MONGOLAB_SRAVZ_HISTORICAL_URI) -e NSQ_HOST=nsqd-1:4150,nsqd-2:4150,nsqd-3:4150 -e NSQ_LOOKUPD_HOST=nsqlookupd-1:4161,nsqlookupd-2:4161,nsqlookupd-3:4161  -e EODHISTORICALDATA_API_KEY=$(EODHISTORICALDATA_API_KEY) -v $(HOME)/.aws:/home/ubuntu/.aws:ro --network=sravz_default public.ecr.aws/b8h3z2a1/sravz/backend-py:$(BACKEND_PY_IMAGE_Version) bash -c 'cd /pwd; export PYTHONPATH=/pwd; python ./src/analytics/price_stats.py'

run_job_trigger_in_container:
	docker run --rm -it sravzpublic/backend-py:$(BACKEND_PY_IMAGE_Version) python job_trigger.py --id 39 --topic production_backend-py --nsq-host nsq.sravz.com --cache_message True

build_complete:
	docker build -f Dockerfile-Complete --tag public.ecr.aws/b8h3z2a1/sravz/backend-py:$(BACKEND_PY_IMAGE_Version) .

build_from_previous_version:
	docker build --tag public.ecr.aws/b8h3z2a1/sravz/backend-py:$(BACKEND_PY_IMAGE_Version) .

build-airflow:
	docker build --tag public.ecr.aws/b8h3z2a1/sravz/airflow:$(AIRFLOW_IMAGE_Version) -f Dockerfile-Airflow .

submit_job_by_id: ## make submit_job_by_id id=48
	python job_trigger.py --id $(id) --topic vagrant_backend-py --nsq-host nsqd

deploy_docker_stack_on_prem: cd-backend-py-dir
	docker run --rm -v $(CURDIR)/../ci-ansible/:/pwd \
	-v $(CURDIR)/../docker_volume/frontend-ng/:/vagrant \
	-v $(CURDIR)/../../secrets/:/secrets \
	-v ~/.ssh:/root/.ssh:ro \
	-v $(HOME)/.aws:/root/.aws:ro \
	sravzpublic/ci-ansible:$(CI-ANSIBLE-IMAGE-Version) \
	sh -c "cd /pwd; pwd; ls -al /secrets; ansible-playbook playbooks/$(environment)/sravz.website.yml --vault-password-file /secrets/vault_pass --limit kafka1.sravz.com  --tags=docker-stack -v"

copy-dags:
	# cp ./dags/* /home/ubuntu/contabo_storage/dags
	rsync -av --delete ./dags/ /home/ubuntu/contabo_storage/dags
	
