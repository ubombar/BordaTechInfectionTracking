FROM python:3.8

# set the working directory in the container
WORKDIR /academy2020-BuildInfectionTree

# copy the dependencies file to the working directory
# COPY requirements.txt .

# install dependencies
# RUN pip install -r requirements.txt
RUN pip install --upgrade pip
RUN pip install jsonlib-python3

# copy the content of the local src directory to the working directory
COPY academy2020-BuildInfectionTree/ .

# command to run on container start
CMD [ "python", "./new_lambda.py" ]