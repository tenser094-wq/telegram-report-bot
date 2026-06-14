import os
import threading
import paho.mqtt.client as mqtt
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from http.server import HTTPServer, BaseHTTPRequestHandler

# ดึง Token จาก Environment Variables บน Render
TOKEN = os.environ.get("TELEGRAM_TOKEN")

# ==========================================
# ☁️ ตั้งค่า MQTT 
# ==========================================
MQTT_BROKER = "zef6190c.ala.asia-southeast1.emqxsl.com" 
MQTT_PORT = 8883                  
MQTT_TOPIC = "esp32/control"

MQTT_USERNAME = "TENSER065"   
MQTT_PASSWORD = "TENSER065"   

# 1. ฟังก์ชันดักฟังคำสั่ง /report
async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 ได้รับคำสั่ง /report แล้ว! กำลังส่งสัญญาณปลุกตู้ควบคุม...")
    try:
        client = mqtt.Client()
        client.tls_set() 
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.publish(MQTT_TOPIC, "WAKEUP")
        client.disconnect()
        print("✅ [MQTT] ยิงสัญญาณ WAKEUP ปลุกตู้สำเร็จ")
    except Exception as e:
        print(f"❌ [MQTT] เกิดข้อผิดพลาด: {e}")

def run_telegram_bot():
    if not TOKEN:
        print("⚠️ [ERROR] ยังไม่ได้ใส่ TELEGRAM_TOKEN")
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("report", report))
    print("🚀 บอทตัวที่ 2 พร้อมดักฟังคำสั่ง /report แล้ว...")
    application.run_polling() # 👈 อันนี้จะรันใน Main Thread

# 2. ฟังก์ชันจำลอง Web Server 
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Bot is running actively!")

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server_address = ('', port)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print(f"🌐 Web server is binding to port {port}...")
    httpd.serve_forever()

if __name__ == "__main__":
    # 🟢 ย้าย Web Server มารันใน Background Thread
    web_thread = threading.Thread(target=run_web_server)
    web_thread.daemon = True
    web_thread.start()
    
    # 🟢 รัน Telegram Bot หลัก (Main Thread) แก้ปัญหา Error เธรด
    run_telegram_bot()
