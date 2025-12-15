import socket

HOST = "10.117.104.127"
PORT = 5555

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # ใช้ IPv4 address กับ TCP เพื่อให้ข้อมูลครบ และ มีความน่าเชื่อถือ
    client.connect((HOST, PORT))  # พยายา่มเชื่อมไปยัง Server ที่กำหนด HOST PORT ไว้

    while True:
        data = client.recv(1024).decode()
        if not data: # ถ้า server ปิด connection → ออกจาก loop
            break
        print(data, end="")

        if "ใส่ชื่อผู้เล่น" in data: # ตรวจข้อความว่า Server ต้องการชื่อผู้เล่นไหม
            name = input("พิมพ์ชื่อของคุณ: ").strip()
            client.sendall(name.encode()) # ส่งไปข้อมูลชื่อ ไป Server_
            print(f"[DEBUG] ส่งชื่อ {name} ไปที่ server แล้ว")

        elif "เดารหัส" in data: # ตรวจข้อความ Server ว่า ถึงตาเรา เดา รหัส(SECRET code)ยัง
            guess = input("ใส่รหัสที่คุณเดา: ").strip()
            client.sendall(guess.encode()) # ส่งไปข้อมูล เดารหัส ไป Server
            print(f"[DEBUG] ส่งเดา {guess} ไปที่ server แล้ว")

if __name__ == "__main__":
    main()