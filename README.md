# Simple Model API

Very simple and minimalistic ML model HTTP service.

**Author:** Tural Mahmudov

**Time spent:** 2 hours

## Overview

This documentation provides an in-depth explanation of a microservice with a REST API designed to handle very basic ML model operations. The microservice is structured into three layers, each responsible for specific functionalities, and integrates with a PostgreSQL database. The microservice uses Flask for the HTTP API, SQLAlchemy for ORM, and unittest for unit testing. Gunicorn is used as the production server with four threads, and data isolation is implemented to prevent race conditions.

For simplicity and as per the requirements, no creation, update, or deletion of either user or model is supported. Effectively, no `POST`, `PUT`, `PATCH`, or `DELETE` requests on users or models.

The microservice consists of the following layers, from the lowest to the highest:

* DB Layer: Integrates with PostgreSQL.
* ORM Layer: Defines data object models using SQLAlchemy.
* _Repository Layer: Contains repositories for each object model._
* _Service Layer: Provides an interface for all service operations._
* HTTP API Layer: Handles HTTP requests and responses using Flask.

Ones in italic are not implemented since that would be an overkill for this simple task.

The microservice records all calls from the user to the API in a non-blocking way with background threads. It uses a simple logger with file handler.

The microservice is fully dockerized and integrates with a Postgres service (waiting for it to be ready before connecting at start up).

The code is clean, type-checked. It uses the best practices in Python, REST API design, microservices architecture, and virtualization for easy deployment. Yet it is also simple and has a relatively flat hierarchical structure.

## Usage

### Initial Setup

Before running, you have to:

- manually add users and models to the database;
- implement desired algorithms in `api/algorithms.py`.

### Start Up

You can start the system by running

```sh
docker-compose up -d
```

### Monitoring

You can get the entire docker logs by running

```sh
docker-compose logs --follow
```

or, alternately, you can get the logs from an individual container by running

```sh
docker container logs <container-name> --follow
```

### Testing

To run tests, run:

```sh
docker exec paretos-task-tswpbk_api_1 python3 -m unittest
```

## Scripts

To lint, format, and check static typing, run:

```sh
chmod +x cleanup.sh
./cleanup.sh
```

from the project root.

