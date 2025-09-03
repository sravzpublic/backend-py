# Sravz Backend Python Codebase

## Overview

This repository contains the Python backend for Sravz, designed for flexible, scalable financial data processing, analytics, and integration with Kafka, NSQ, MongoDB, and cloud services.

## Features

- **Data Ingestion**: Supports ingestion from multiple sources including Kafka, NSQ, and web APIs.
- **Financial Analytics**: Provides PCA, risk, portfolio, and time series analytics using Python libraries.
- **Asset Processing**: Handles equities, commodities, crypto, forex, indices, and more.
- **Cloud Integration**: Uploads results and dashboards to AWS S3.
- **Modular Services**: Organized into services for quotes, assets, rates, dashboards, and more.
- **Docker Support**: Easily containerized for deployment.
- **Extensive Configuration**: Uses environment variables and config files for flexible deployment.

## Directory Structure

- `src/` - Main Python source code, including analytics, services, utilities, and asset modules.
- `tests/` - Test cases and message samples.
- `records/` - Data records and cache.
- `Dockerfile`, `Dockerfile-Complete` - Containerization support.
- `requirements.txt`, `Pipfile` - Python dependencies.
- `run.py` - Main entry point for analytics and chart generation.
- `job_trigger.py`, `kafka_consumer_producer.py`, `nsq_consumer_producer.py` - Messaging and job orchestration scripts.

## Getting Started

### Prerequisites

- Python 3.6+
- Kafka, NSQ, MongoDB (for messaging and storage)
- AWS credentials (for S3 uploads)

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Running

To run analytics or chart generation:

```bash
python run.py
```

To start NSQ consumer/producer:

```bash
python nsq_consumer_producer.py --topic <topic_name> --nsqd-host <nsqd_host> --nsq-lookupd-host <nsqlookupd_host>
```

### Docker Usage

Build and run the container:

```bash
docker build --tag sravzpublic/backend-py:v2 .
docker run --rm -it -e NODE_ENV='vagrant' -e TOPIC_NAME=vagrant_analytics1 -e NSQ_HOST=nsqd -e NSQ_LOOKUPD_HOST=nsqlookupd -v $(pwd):/pwd -v $HOME/.aws:/home/ubuntu/.aws:ro --network=sravz_internal sravzpublic/backend-py bash
```

## License
Sravz LLC
