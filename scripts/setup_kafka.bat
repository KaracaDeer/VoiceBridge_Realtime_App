@echo off
echo Setting up Kafka for VoiceBridge...

REM Create Kafka directory
if not exist "kafka_data" mkdir kafka_data

REM Download Kafka (if not exists)
if not exist "kafka_data\kafka_2.13-2.8.1" (
    echo Downloading Kafka...
    powershell -Command "Invoke-WebRequest -Uri 'https://downloads.apache.org/kafka/2.8.1/kafka_2.13-2.8.1.tgz' -OutFile 'kafka_data\kafka.tgz'"
    
    REM Extract Kafka
    echo Extracting Kafka...
    powershell -Command "Expand-Archive -Path 'kafka_data\kafka.tgz' -DestinationPath 'kafka_data'"
    
    REM Clean up
    del kafka_data\kafka.tgz
)

REM Start Zookeeper
echo Starting Zookeeper...
start "Zookeeper" cmd /k "cd kafka_data\kafka_2.13-2.8.1\bin\windows && zookeeper-server-start.bat ..\..\config\zookeeper.properties"

REM Wait for Zookeeper to start
timeout /t 10 /nobreak

REM Start Kafka
echo Starting Kafka server...
start "Kafka" cmd /k "cd kafka_data\kafka_2.13-2.8.1\bin\windows && kafka-server-start.bat ..\..\config\server.properties"

echo Kafka setup complete!
echo Zookeeper: localhost:2181
echo Kafka: localhost:9092
