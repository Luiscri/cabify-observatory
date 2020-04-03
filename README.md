# Cabify Sustainable Mobility Observatory
A docker-based project to track the sustainable mobility impact on society nowadays. [![Build Status](https://travis-ci.org/joemccann/dillinger.svg?branch=master)](https://travis-ci.org/joemccann/dillinger)

## About

[![Logo Cátedra](./cabify-dashboard/img/catedra_logo.svg)](http://catedra-cabify.gsi.upm.es/)

The Cabify Sustainable Mobility Observatory is a project which retrieves and analyses Spanish written articles related with sustainable mobility by using artificial intelligence processes. Moreover, a front panel or dashboard with which the reader can interact has been developped in order to capture and report the key performance indicators and enlighten how these issues impact on society nowadays.

This project has been carried out by the Cabify - UPM chair. A complete version of the project can be found in the following endpoint:

```
http://observatory-cabify.gsi.upm.es
```

## Authors
1. Álvaro de Pablo Marsal
2. Luis Cristóbal López García

## Requirements

Before being able to build and run the observatory, some previous steps need to be performed:
* Docker engine and docker-compose need to be installed in the host system in order to deploy the project. If you do not already meet this requirement, you can follow [this](https://docs.docker.com/install/) link for the engine installation, and [this](https://docs.docker.com/compose/install/) other one for docker-compose.
* The API used to collect the articles is [NewsApi](https://newsapi.org/). Although it is free for developers an API key is needed in order to use the service, so you would need to register and get one for your personal use.
* After the collection phase, several analysis processes are performed on those articles. One of them is know as entity-linking, which is responsible for relating each of the detected entities to a knowledge base. Again, you will need to register and get an API key on [Babelfy](http://babelfy.org/), the service performing that task.

## Usage

Once the requirements are met, you can proceed to download the project and move to the project's root directory. However, there are still some changes which need to be performed.

### .env file
The `.env` file contains some project-specific environment variables. You will need to define the following ones:
* **DATA_DIRECTORY_PATH:** this path must point to the `data/` directory included in the project. It is very import to use an **ABSOLUTE** path, otherwise the volume will not be mounted propertly.
* **NEWS_API_KEY:** the key you obtained by registering on the service.
* **BABELFY_API_KEY:** the key you obtained by registering on the service.

Unless you want to deploy the project on a cloud environment, it is recommended to do not change the value of the other environment variables in the file.

### Retrieve Senpy plugins
Next step is to retrieve the Senpy plugins hosted in GitLab. Just run the following command:

```
git submodule update --init --recursive
```

This will pull down locally on the `.senpy/` directory all submodules used in the project. You can only run that command for the first time once you download the project. If a new version of the plugins is released, go for this one instead to pull the changes:

```
git submodule update --recursive --remote
```

### Increase kernel max map count

In order to use ElasticSearch for production, we need to set the `vm.max_map_count` kernel setting to at least 262144. If you have not done this before, just open the `/etc/sysctl.conf` configuration file in a text editor with superuser privilegdes and add this line at the end:

```
vm.max_map_count=262144
```

This sets the memory limit permanently, so you only need to do this step one time. Finally, run the following command to apply the changes:

```
sudo sysctl -p
```

### Build the Docker images

At this point, you are ready to build and run the images. Open a terminal on the project's root folder and run:

```
docker-compose up --build
```

Note you may need to run the command as a `sudo` superuser depending on your configuration.

This process may take a while if you run the command for the first time. Once the process finishes, if you have followed the instructions propertly the observatory must be up and running, and the services available in their corresponding endpoints.

## Services

This project provides the user with a range of services:
* **Dashboard:** the observatory's front panel and the main visual tool to check the analysis performed results. It is accessible in the following endpoint `http://localhost:8080/`.
* **ElasticSearch:** the database used as persistence layer, saving data in indexes. The one used in the project can be accessed at `http://localhost:9200/articles/_search`.
* **Senpy:** a GSI powered framework to build analysis services. It is used in the project through an internal API, although a playground is also available at `http://localhost:5000/` in case you want to test the different plugins available.
* **Luigi:** used to build the project pipeline. Tasks are run once a day by the orchestrator container. Moreover, a luigi central-scheduler front panel is also available at `http://localhost:8082/` if you want to check each task state and dependencies.

## License

Copyright © 2020 Grupo de Sistemas Inteligentes.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at:

```
http://www.apache.org/licenses/LICENSE-2.0
```

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.