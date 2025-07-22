FROM public.ecr.aws/b8h3z2a1/sravz/backend-py:v186
LABEL MAINTAINER=contactus@sravz.com

USER airflow
WORKDIR /home/airflow
ADD . /home/airflow/
# Copy dag files, s2fs is unreliable and services die
ADD ./dags /opt/airflow/dags/
# Switch to root user temporarily to perform tasks
USER root
RUN rm -r /home/airflow/dags/
RUN rm -r /home/airflow/tests/

USER airflow

HEALTHCHECK  --interval=10m --timeout=30s CMD bash healthcheck.sh > /dev/null || exit 1

ENTRYPOINT []

CMD ["make", "run"]
