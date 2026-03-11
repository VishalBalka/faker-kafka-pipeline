# Real-Time Streaming Data Pipeline 🚀

A robust, end-to-end real-time data pipeline built to ingest, process, and store streaming financial transactions using **Apache Kafka**, **PySpark Structured Streaming**, and **PostgreSQL**. The entire infrastructure is fully containerized using **Docker Compose** and includes a real-time **Streamlit** dashboard for monitoring.

---

## 🏗️ Architecture Overview

The pipeline consists of four main components functioning simultaneously:

1. **Mock Data Producer (`producer/main.py`)**: A Python script simulating a live financial application. It uses the `Faker` library to continuously generate random JSON transaction events (purchases, refunds, transfers) and pushes them to a Kafka broker.
2. **Message Broker (Apache Kafka & Zookeeper)**: Acts as the high-throughput, fault-tolerant transport layer. It receives the raw data stream from the producer and queues it up in the `transactions_topic`.
3. **Stream Processor (`spark/streaming.py`)**: A PySpark Structured Streaming application (running inside a dedicated Docker worker node) that continuously polls Kafka. It schema-validates the raw JSON into structured DataFrames in real-time.
4. **Data Sink (PostgreSQL)**: The PySpark app utilizes a JDBC driver to continuously `APPEND` the processed structured micro-batches permanently into a relational PostgreSQL database.
5. **Live Operations Dashboard (`ui/app.py`)**: A Streamlit web application that actively queries PostgreSQL to visualize the ingestion rate and recent transactions.

---

## 🛠️ Technology Stack
- **Languages**: Python 3.11, SQL
- **Stream Processing**: Apache Spark (PySpark 3.5.0)
- **Message Broker**: Apache Kafka (kafka-python-ng)
- **Database**: PostgreSQL
- **UI & Analytics**: Streamlit, Pandas
- **Infrastructure**: Docker, Docker Compose

---

## 🚀 Getting Started

### Prerequisites
You only need two things installed on your system to run the entire pipeline:
1. [Docker Desktop](https://www.docker.com/products/docker-desktop/) (must be running in the background)
2. [Python 3.10+](https://www.python.org/downloads/)

### 1. Start the Pipeline Infrastructure
The database, Kafka message broker, and the PySpark stream processor have all been pre-configured into containers. Bring the entire cluster online with a single command:
```bash
docker-compose up -d --build
```

### 2. Start the Data Producer
In a new terminal window, install the required Python packages and start the mock data generator:
```bash
# Optional: Setup a virtual environment first
pip install -r requirements.txt
python producer/main.py
```
*You will immediately see JSON payloads beginning to stream to localhost:9092.*

### 3. Start the Live Dashboard
To watch the pipeline process the data in real-time, launch the Streamlit monitor in another terminal:
```bash
streamlit run ui/app.py
```
Wait a few seconds, then navigate to `http://localhost:8501` in your web browser. You will see the total database row count increasing and a live feed of the transaction amounts!

---

## 📁 Repository Structure
```text
📦 faker-kafka-pipeline
 ┣ 📂 db
 ┃ ┗ 📜 init.sql              # Auto-creates the 'transactions' PostgreSQL table
 ┣ 📂 producer
 ┃ ┗ 📜 main.py               # The Python script generating the fake JSON data
 ┣ 📂 spark
 ┃ ┗ 📜 streaming.py          # The PySpark script handling the Kafka -> Postgres logic
 ┣ 📂 ui
 ┃ ┗ 📜 app.py                # The Streamlit live dashboard
 ┣ 📜 docker-compose.yml      # Orchestrates Zookeeper, Kafka, Postgres, and Spark
 ┣ 📜 Dockerfile.spark        # Builds the isolated Linux PySpark environment
 ┗ 📜 requirements.txt        # Python dependencies for the Producer and UI
```

## 🧹 Teardown
To cleanly shut down the pipeline and wipe the database volumes, simply run:
```bash
docker-compose down -v
```
