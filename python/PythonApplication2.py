import asyncio
import socket
import struct
import mysql.connector as mysql  # pip install mysql-connector-python

# PLC connection settings
PLC_IP = "192.168.1.80"
PLC_PORT = 8080
OUTPUT_COUNT = 4
INPUT_COUNT = 4

# Read 4 digital inputs from PLC
def read_inputs():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(3)
        s.connect((PLC_IP, PLC_PORT))
        # Modbus TCP request to read coils/inputs
        request = struct.pack(">HHHBBHH", 1, 0, 6, 1, 2, 0, INPUT_COUNT)
        s.send(request)
        response = s.recv(1024)
        data_byte = response[9]
        inputs = [(data_byte >> i) & 1 for i in range(INPUT_COUNT)]
        return inputs

# Write digital output to PLC
def write_output(channel, value):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(3)
        s.connect((PLC_IP, PLC_PORT))
        address = channel
        on_off = 0xFF00 if value else 0x0000
        # Modbus TCP request to write single coil
        request = struct.pack(">HHHBBHH", 1, 0, 6, 1, 5, address, on_off)
        s.send(request)
        s.recv(1024)

# Connect to MySQL
conn = mysql.connect(
    host="localhost",     # MySQL host (use IP if remote)
    user="root",          # Username
    password="",          # Password
    database="plc_db"     # Database name
)
cursor = conn.cursor()

# Update inputs into MySQL
def insert_data(inputs):
    cursor.execute("""
        UPDATE iotable 
        SET input1=%s, input2=%s, input3=%s, input4=%s
        WHERE id = 0
    """, (inputs[0], inputs[1], inputs[2], inputs[3]))
    conn.commit()

# Read outputs from MySQL
def read_data():
    cursor.execute("SELECT output1, output2, output3, output4 FROM iotable WHERE id = 0")
    row = cursor.fetchone()
    if row:
        outputs = list(row)
        print("Latest outputs from DB:", outputs)
        return outputs
    return [0, 0, 0, 0]

# Main loop
async def main():
    while True:
        # Step 1: Read inputs from PLC
        inputs = read_inputs()
        print("Inputs:", inputs)

        # Step 2: Save inputs to MySQL
        insert_data(inputs)

        # Step 3: Read outputs from MySQL
        outputs = read_data()

        # Step 4: Send outputs to PLC
        for i, val in enumerate(outputs):
            write_output(i, val)

        # Wait 3 seconds before next cycle
        await asyncio.sleep(3)

if __name__ == "__main__":
    asyncio.run(main())

