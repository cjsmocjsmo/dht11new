import RPi.GPIO as GPIO
import dht11
import time
import sqlite3
from datetime import datetime

# initialize GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.cleanup()

# initialize database
def init_database():
    conn = sqlite3.connect('temperature_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS temps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            C REAL NOT NULL,
            F REAL NOT NULL,
            humidity REAL NOT NULL,
            time TEXT NOT NULL,
            date TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# initialize database
init_database()

# function to insert temperature data
def insert_temperature_data(celsius, fahrenheit, humidity):
    try:
        conn = sqlite3.connect('temperature_data.db')
        cursor = conn.cursor()
        
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        current_date = now.strftime("%Y-%m-%d")
        
        cursor.execute('''
            INSERT INTO temps (C, F, humidity, time, date)
            VALUES (?, ?, ?, ?, ?)
        ''', (celsius, fahrenheit, humidity, current_time, current_date))
        
        conn.commit()
        conn.close()
        print(f"Data saved to database: {celsius}°C, {fahrenheit}°F, {humidity}% at {current_time} on {current_date}")
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")

# read data from pin 4
instance = dht11.DHT11(pin=4)

print("Starting temperature monitoring... Press Ctrl+C to stop")
print("Reading every 15 minutes...")

try:
    while True:
        try:
            result = instance.read()

            if result.is_valid():
                temp_celsius = round(result.temperature, 1)
                temp_fahrenheit = round(temp_celsius * (9/5) + 32, 1)
                humidity = round(result.humidity, 1)
                
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[{current_time}] Temperature: {temp_celsius}°C / {temp_fahrenheit}°F")
                print(f"[{current_time}] Humidity: {humidity}%")
                
                # Save to database
                insert_temperature_data(temp_celsius, temp_fahrenheit, humidity)
            else:
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[{current_time}] Sensor reading error: {result.error_code}")
                
        except Exception as e:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{current_time}] Unexpected error during sensor reading: {e}")
        
        # Wait 15 minutes (900 seconds)
        print("Waiting 15 minutes for next reading...")
        time.sleep(900)

except KeyboardInterrupt:
    print("\nMonitoring stopped by user")
except Exception as e:
    print(f"Critical error: {e}")
finally:
    print("Cleaning up GPIO...")
    GPIO.cleanup()
    print("Program terminated.")