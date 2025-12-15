import socket
import threading
import random

HOST = "10.117.104.127"   # IP ของเครื่องที่รัน server ตั้งค่าเบื้องต้น
PORT = 5555


clients = []   # เก็บ socket ของผู้เล่นที่เชื่อมต่อมา
names = [] # เก็บค่า ชื่อของผู้เล่น
lock = threading.Lock()

chars = "ABC12345"  # ชุดตัวอักษร+ตัวเลข 1
SECRET = "".join(random.sample(chars, 6)) #random.sample สุ่มตัวอย่างที่ไม่ซ้ำกัน จาก chars
print("[SECRET]", SECRET)

turn_index = 0
round_count = 0
MAX_ROUNDS = 12




def check_guess(secret, guess): #การตรวจคำตอบ
    hit = sum(s == g for s, g in zip(secret, guess))   # Ex SECRET  = AB1234   # guess = A51234   (A == A ) = True = 1  ,(B == 5) = FALSE =0
    near = sum(min(secret.count(s), guess.count(s)) for s in set(guess)) - hit  # 6 - (ตามจำนวน hit ที่มี)
    return hit, near

def broadcast(message):  #ฺbroadcast ส่งข้อความถึง ูclient ทุกคน
    with lock: # กันไม่ให้โปรแกรมถูกทำงานหลายเธรด(thread) พร้อมกัน
        # --- Critical Section เริ่มต้น ---
        # ณ จุดนี้ มีเพียง Thread เดียวเท่านั้นที่ทำงานในนี้ได้
        for c in clients[:]:
            try:
                # พยายามส่งข้อความไปหา client แต่ละคน
                c.sendall(message.encode())  #encode() = แปลง Sting เป็น bytes
            except:
                # ถ้าส่งไม่ได้ (เช่น client ปิดโปรแกรมไปแล้ว)
                # จะทำการลบ client นั้นออกจากลิสต์
                clients.remove(c)
        # --- Critical Section สิ้นสุด ---



def handle_client(conn, addr):   #conn = connect   addr = address
    global turn_index, round_count   # ใน  ถ้าเราเขียนตัวแปรไว้ นอกฟังก์ชัน → ตัวแปรนั้นเป็น global variable (ตัวแปรส่วนกลาง) แต่ถ้าเราไป แก้ไขค่า ของตัวแปรนั้น ภายในฟังก์ชัน จะต้องประกาศก่อนว่าเป็น global

    try:
        conn.sendall("กรุณาใส่ชื่อผู้เล่น: ".encode())
        name = conn.recv(1024).decode().strip()  #recv(1024) = รับได้สูงสุด 1024 byte  decode() = แปลง bytes เป็น sting
        names.append(name)  #เก็บ name ไว้ใน list names
        clients.append(conn) #เก็บ connect ไว้ใน list clients
        print(f"[JOIN] {name} เข้ามาจาก {addr}")
        broadcast(f"[ระบบ] {name} เข้ามาในเกมแล้ว\n")

        # รอจนมีครบ 4 คน
        while len(clients) < 4 :
            pass

        broadcast("[ระบบ] ผู้เล่นครบแล้ว เกมเริ่ม!\n")

    # วนเล่น
        while round_count < MAX_ROUNDS:
            with lock:
                current = turn_index % len(clients) #ใช้ ดูว่าถึงตาใครแล้ว  0 % 2 = (0 เรา)  1 % 2 = (1 อีกเครื่อง) 2 % 2 = (0 เรา) 3 % 2 = (1 อีกเครื่อง)
                conn_turn = clients[current]
                name_turn = names[current]

            if conn != conn_turn:
                continue  # ไม่ใช่ตาเรา → รอ

            conn.sendall(f"ถึงตาของคุณ {name_turn} รอบที(่{turn_index + 1}/{MAX_ROUNDS}), เดารหัส 6 ตัว: ".encode())
            guess = conn.recv(1024).decode().strip().upper()

            Hit, Near = check_guess(SECRET, guess)
            broadcast(f"{name_turn} เดา: {guess} → {Hit} ถูกตำแหน่ง (Hit), {Near} ถูกแต่ผิดตำแหน่ง (Near)\n")

            if Hit == 6:
                broadcast(f"[ผลลัพธ์] {name_turn} ชนะ! 🎉 รหัสคือ {SECRET}\n")
                break

            round_count += 1
            turn_index += 1

        if round_count >= MAX_ROUNDS:
            broadcast(f"[ผลลัพธ์] หมดรอบแล้ว! รหัสที่ถูกต้องคือ {SECRET}\n")
            game_over = True
    except:
        pass
        conn.close()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  #สร้าง socket สำหรับ server  AF_INET = ใช้ IPV4   SOCK_STREAM คือ การใช้ TCP เป็นการรับประกันว่าข้อมูลส่งครบ
    server.bind((HOST, PORT))  # bind() = บอกว่า “ให้ server รันบน IP และ Port นี้”
    server.listen(4)  # รอ 4 คน
    print(f"Server started on {HOST}:{PORT}")

    while True: # การทำงานหลายเธรด (Thread) เกิดขึ้นในลูป while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr)) # เป็นการส่ง อาร์กิวเมนต์ ของค่า conn , addr ไปยัง ฟังก์ชั่นของ handle_client ให้ทำงาน
        thread.start()

if __name__ == "__main__":
    main()