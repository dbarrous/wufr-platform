FROM public.ecr.aws/lambda/python:3.9

COPY requirements.txt  .

# Install the function's dependencies using file requirements.txt
# from your project folder.

RUN yum update -y \
    && yum -y install libpq-dev gcc postgresql-libs musl-dev postgresql python-devel postgresql-devel


RUN  pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

# Copy function code
COPY . ${LAMBDA_TASK_ROOT}

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "review_controller.handler" ] 