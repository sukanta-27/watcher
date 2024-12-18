# Game Data Platform

## Table of Contents

- [Introduction](#introduction)
- [Database Schema](#database-schema)
- [Deployed Application](#deployed-application)
- [API Endpoints](#api-endpoints)
  - [1. Load CSV Data to Database](#1-load-csv-data-to-database)
  - [2. Track Task Status](#2-track-task-status)
  - [3. Query Data](#3-query-data)
- [API Documentation](#api-documentation)
- [Development Setup](#development-setup)
  - [Prerequisites](#prerequisites)
  - [Setup Instructions](#setup-instructions)
  - [Docker Compose Configuration](#docker-compose-configuration)
- [Database Schema Link](#database-schema-link)
- [Cost Estimate](#cost-estimate)


---

## Introduction

The **Watcher** is a web application designed to manage and query a large dataset of game-related information. It allows users to:

- **Load game data** from a CSV file into a PostgreSQL database asynchronously.
- **Track the status** of data loading tasks.
- **Query game data** using various filters and pagination.

The platform provides a RESTful API built with FastAPI and serves a frontend interface using static files.

---

## Database Schema

The application uses a PostgreSQL database to store game data. The schema is designed to efficiently handle complex queries and relationships between different entities such as games, developers, publishers, genres, and more.

**Key Points:**

- **Relational Database**: Utilizes tables and foreign key relationships to model data.
- **Optimized for Queries**: Indexes and relationships are set up to enhance query performance.

For a visual representation of the database schema, please refer to the [Database Schema Link](#database-schema-link).

---

## Deployed Application (Currently this deployment has been stopped, you can continue with a local setup)

Access the deployed application at:

- **URL**: [https://watcher-sukanta.fly.dev](https://watcher-sukanta.fly.dev)

### Disclaimer: 
The application is deployed on Fly.io, and the database is configured to scale down to zero after one hour of inactivity to save costs, as it is an assignment project. Consequently, the first request might be slower than expected, as the database needs to spin up again after being idle.


### Known Issue:
There is an ongoing issue in the hosted application in the `/track_task` endpoint, where the API endpoint is getting redirected to http from https.
Most modern web browsers do not support the redirection, so the API endpoint is not accessible.
I have tried adding app level middleware to solve this issue where I am enforcing https redirect but it too is not solving the issue.
I will fix this issue in the future. But for now you can access this api from the Swagger UI. 
I regret the inconvenience.
You can access this API from: [Swagger UI](https://watcher-sukanta.fly.dev/docs#/Async%20Upload/get_task_status_api_upload_data_async_status__get)

---

## API Endpoints

### 1. Load CSV Data to Database

**Endpoint**: `/api/upload_data_async/`  
**Method**: `POST`

This endpoint allows you to load game data from a CSV file into the database asynchronously.

**Sample Request:**

```bash
curl --location 'https://watcher-sukanta.fly.dev/api/upload_data_async/' \
--header 'Content-Type: application/json' \
--data '{
    "file_url": "https://example.com/path/to/your.csv"
}'
```

**Request Body Parameters:**

- `file_url` (string): The URL of the CSV file to be loaded.

**Sample Response:**

```json
{
    "task_id": "a18a873c-3e9b-4d5c-a565-e437a995f1e0",
    "message": "Added Request to Queue with ID: a18a873c-3e9b-4d5c-a565-e437a995f1e0"
}
```

**Response Details:**

- `task_id` (string): A unique identifier for the data loading task.
- `message` (string): A message indicating that the task has been queued.
- **HTTP Status Code**: `202 Accepted`

### 2. Track Task Status

**Endpoint**: `/api/upload_data_async/status`  
**Method**: `GET`

This endpoint allows you to track the status of a data loading task using the `task_id` provided when the task was initiated.

**Sample Request:**

```bash
curl --location 'https://watcher-sukanta.fly.dev/api/upload_data_async/status?task_id=a18a873c-3e9b-4d5c-a565-e437a995f1e0'
```

**Query Parameters:**

- `task_id` (string): The unique identifier of the task to track.

**Sample Response:**

```json
{
    "task_id": "a18a873c-3e9b-4d5c-a565-e437a995f1e0",
    "status": "partially_completed",
    "message": "Not all rows could be processed successfully",
    "result": {
        "message": "Not all rows could be processed successfully",
        "rows_processed_successfully": 99,
        "rows_could_not_be_processed": 1,
        "errors": {
            "92": "Invalid date format for release date: May 2020"
        }
    },
    "created_at": "2023-10-27T13:42:56.639735",
    "completed_at": "2023-10-27T13:43:00.819368"
}
```

**Response Details:**

- `task_id` (string): The unique identifier of the task.
- `status` (string): Current status of the task.
- `message` (string): A descriptive message about the task.
- `result` (object): Detailed results of the task.
- `created_at` (datetime): When the task was created.
- `completed_at` (datetime): When the task was completed (if applicable).

**Task Status Values:**

- `pending`
- `processing`
- `completed`
- `failed`
- `partially_completed`

### 3. Query Data

**Endpoint**: `/api/query`  
**Method**: `GET`

This endpoint allows you to query game data using various filters and pagination options.

**Query Parameters:**

- **Pagination Parameters:**
  - `page` (int, default `1`): Page number (starting from 1).
  - `page_size` (int, default `10`): Number of items per page (1-100).
- **Filter Parameters:**
  - `name` (string): Filter by game name.
  - `about_the_game` (string): Filter by game description.
  - `developers` (list of strings): Filter by developers.
  - `publishers` (list of strings): Filter by publishers.
  - `categories` (list of strings): Filter by categories.
  - `supported_languages` (list of strings): Filter by supported languages.
  - `genres` (list of strings): Filter by genres.
  - `tags` (list of strings): Filter by tags.
  - `platforms` (list of strings): Filter by platforms.
  - `release_date` (date): Filter by release date.
  - `app_id` (int): Filter by app ID.
  - `price` (float): Filter by price.
  - `dlc_count` (int): Filter by DLC count.
  - `score_rank` (int): Filter by score rank.
  - `positive_reviews` (int): Filter by positive reviews count.
  - `negative_reviews` (int): Filter by negative reviews count.
  - `required_age` (int): Filter by required age.
- **Range Filters:**
  - `release_date_min` (date): Minimum release date.
  - `release_date_max` (date): Maximum release date.
  - `price_min` (float): Minimum price.
  - `price_max` (float): Maximum price.
  - `positive_reviews_min` (int): Minimum positive reviews.
  - `positive_reviews_max` (int): Maximum positive reviews.
  - `negative_reviews_min` (int): Minimum negative reviews.
  - `negative_reviews_max` (int): Maximum negative reviews.

**Sample Request:**

```bash
curl --location 'https://watcher-sukanta.fly.dev/api/query?page=1&page_size=10&app_id=20200'
```

**Sample Response:**

```json
{
    "page": 1,
    "page_size": 10,
    "total_items": 1,
    "total_pages": 1,
    "items": [
        {
            "app_id": 20200,
            "name": "Game Title",
            "release_date": "2020-05-20",
            "price": 19.99,
            "developers": ["Developer Name"],
            "publishers": ["Publisher Name"],
            "genres": ["Action", "Adventure"],
            "platforms": ["windows", "mac"],
            // Additional fields...
        }
    ]
}
```

**Response Details:**

- `page` (int): Current page number.
- `page_size` (int): Number of items per page.
- `total_items` (int): Total number of items matching the query.
- `total_pages` (int): Total number of pages.
- `items` (list): List of game data objects matching the query.

---

## API Documentation

Access the interactive API documentation (Swagger UI) at:

- **URL**: [https://watcher-sukanta.fly.dev/docs](https://watcher-sukanta.fly.dev/docs)

This documentation provides detailed information about all available endpoints, parameters, and models.

---

## Development Setup

### Prerequisites

- **Docker**: Ensure that Docker is installed and running on your machine.
- **Docker Compose**: Required to run multiple containers.

### Setup Instructions

1. **Clone the Repository**

   ```bash
   git clone git@github.com:sukanta-27/watcher.git
   ```

2. **Navigate to the Project Directory**

   ```bash
   cd watcher
   ```

3. **Start the Application**

   Run the following command to build and start the containers:

   ```bash
   docker-compose -f docker/docker-compose.yml up --build
   ```

   This command will:

   - Build the Docker images for the application.
   - Start the PostgreSQL database container.
   - Start the FastAPI application container.

4. **Access the Application**

   - **Frontend**: Open your browser and navigate to `http://localhost:8080`.
   - **API Documentation**: Access Swagger UI at `http://localhost:8080/docs`.

### Docker Compose Configuration

The `docker-compose.yml` file is located at `docker/docker-compose.yml`.
Tables are created using SQLAlchemy's `create_all` method. The tables are created as part of docker-compose setup. 
So no additional settings are required.

<details>
<summary>Click to view the Docker Compose configuration</summary>

```yaml
version: '3.8'

services:
  db:
    image: postgres:13
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: watcherdb
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    ports:
      - "5432:5432"
    restart: always

  backend-server:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    working_dir: /app
    command: sh -c "python -m server.scripts.create_schema && uvicorn server.main:app --host 0.0.0.0 --port 8000 --reload"
    volumes:
      - ..:/app
    ports:
      - "8080:8000"
    depends_on:
      - db
    environment:
      DATABASE_URL: postgresql://postgres:postgres@db:5432/watcherdb
      ENV: local
      PYTHONPATH: /app
      DEBUG: 1
    restart: always

volumes:
  postgres_data:
```

</details>

---

## Database Schema Link

For a detailed view of the database schema, please visit:

- **Database Schema**: [https://drawsql.app/teams/pixis-3/diagrams/sample](https://drawsql.app/teams/pixis-3/diagrams/sample)

This link provides a graphical representation of the database tables and their relationships.

---
<a name="cost-estimate"></a>
# Cost Estimate For Production
To understand the cost estimate for the production requirement, it is important to understand what the resource utilisation is for the development environment.
The project is deployed in fly.io so all the estimates are based on the pricing of fly.io.

It is to be noted, that if we need to take it to production I will go for AWS instead of going for fly.io.

Cost details for fly.io are in the following link:
[Fly.io Pricing Page](https://fly.io/docs/about/pricing/)

## Cost Estimate of Development Environment based on the resource used:

### App Server (Service 1)
- Machines: 2 × shared-cpu-1x@1024MB
- Scale to zero after 1hr inactivity
- Current usage metrics:
  - Memory: 339MB/1GB
  - Load: 0.06 (very low)
  - Network: 5kbps in, 100bits/s out
  - **Active hours estimation: ~8 hours/workday = 160 hours/month**

### Database (Service 2)
- Machines: 1 × shared-cpu-1x@1024MB
- Scale to zero after 1hr inactivity
- Current usage metrics:
  - Load: 0.32
  - Network: 400bits/s in, 6KB/s out
  - **Active hours estimation: ~8 hours/workday = 160 hours/month**

### Storage
- Volume size: 1GB
- Current usage: 127MB
- Data source: 166KB CSV

## Cost Calculation

1. **App Servers**
- Base rate: $5.70/month for shared-cpu-1x@1024MB
- Actual cost with scale to zero:
  - $5.70 × (160 hours / 730 hours) × 2 machines
  - = $5.70 × 0.219 × 2
  - = $2.50/month

2. **Database Server**
- Base rate: $5.70/month for shared-cpu-1x@1024MB
- Actual cost with scale to zero:
  - $5.70 × (160 hours / 730 hours)
  - = $5.70 × 0.219
  - = $1.25/month

3. **Persistent Volume**
- Rate: $0.15/GB/month
- Size: 1GB
- Cost: $0.15/month

4. **Network Transfer**
- Current usage well within free tier (160GB/month)
- Cost: $0.00

### Total Monthly Cost Estimate

| Component | Base Cost | Actual Cost (with scale to zero) |
|-----------|-----------|----------------------------------|
| App Servers (2×) | $11.40 | $2.50 |
| Database Server | $5.70 | $1.25 |
| Persistent Volume | $0.15 | $0.15 |
| Network Transfer | $0.00 | $0.00 |
| **Total** | **$17.25** | **$3.90** |



## Cost Estimate For Production Scale (Educated Guesses)

## Production Requirements
### Base Requirements
- File uploads: 50MB × 1/day = 1.5GB/month (Took the max file size provided in the assignment pdf for estimate)
- Queries: 100/day = 3000/month
- Storage growth: ~500MB/month
### Additional Requirements
- 24x7 uptime (730 hours/month)
- No scale to zero
- High availability

## Recommended Production Setup

1. **App Servers**
- Configuration: 2 × shared-cpu-2x@2048MB (2GB)
- Always running (730 hours/month)
- Deployed across different regions for HA
- Cost: \$13.40/month × 2 = \$26.80/month

2. **Database Server**
- Primary: 1 × shared-cpu-2x@2048MB (2GB)
- Read Replica: 1 × shared-cpu-2x@2048MB (2GB)
- Always running (730 hours/month)
- Cost: \$13.40/month × 2 = \$26.80/month

3. **Persistent Volume**
- Primary DB: 5GB
- Replica DB: 5GB
- Cost: \$0.15/GB × 10GB = $1.50/month

4. **Network Transfer**
- Included free tier: 160GB/month outbound
- Expected usage well within free tier
- Inter-region transfer for replication: ~2GB/month (included) -> This is an estimate I made based on the inbound and outbound data transfer rate I noticed while developing.


## Total Monthly Cost Estimate
| Component | Projected Cost |
|-----------|----------------|
| App Servers (2×) | $26.80         |
| Database (Primary + Replica) | $26.80         |
| Persistent Volume | $1.50          |
| Network Transfer | $0.00          |
| **Total** | **$55.10**     |



## Future Features
- Add Authentication in both API Endpoints and Frontend.
- Add Robust Testcases
