import csv
import json
import time
import os
import glob
from kafka import KafkaProducer

KAFKA_BROKER = "kafka:9092"
TOPIC = "sales_topic"
DATA_DIR = "/data"


def create_producer():
    while True:
        try:
            producer = KafkaProducer(
                bootstrap_servers=[KAFKA_BROKER],
                value_serializer=lambda x: json.dumps(x).encode("utf-8"),
            )
            print("Connected to Kafka")
            return producer
        except Exception as e:
            print(f"Waiting for Kafka... {e}")
            time.sleep(5)


def run():
    producer = create_producer()
    files = glob.glob(os.path.join(DATA_DIR, "*.csv"))
    files.sort()

    for file_path in files:
        print(f"Processing {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                producer.send(TOPIC, value=row)
        print(f"Finished {file_path}")
        time.sleep(5)  # искусственная пауза (можно закомментировать)

    producer.flush()
    print("All data sent.")


if __name__ == "__main__":
    time.sleep(20)  # ожидание, пока все контейнеры поднимутся
    run()
