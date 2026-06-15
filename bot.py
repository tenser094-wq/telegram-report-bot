import os
import logging
import paho.mqtt.client as mqtt
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# เปิดระบบ Log เพื่อดู Error
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = os.environ.get("TELEGRAM_TOKEN")

# ตั้งค่า MQTT
MQTT_BROKER = "zef6190c.ala.asia-southeast1.emqxsl.com" 
MQTT_PORT = 8883                  
MQTT_TOPIC = "esp32/control"
MQTT_USERNAME = "YOUR_USERNAME"   
MQTT_PASSWORD = "YOUR_PASSWORD"   

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

# Web Server สำหรับให้ Render ไม่มองว่าเว็บตาย (Binding port $PORT)
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot is alive and listening!")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server_address = ('', port)
    httpd = HTTPServer(server_address, HealthCheckHandler)
    print(f"🌐 Health check server running on port {port}...")
    httpd.serve_forever()

if __name__ == "__main__":
    if not TOKEN:
        print("⚠️ ยังไม่ได้ใส่ TELEGRAM_TOKEN!")

    # 1. รัน Web Server เช็คสถานะไว้ที่ Background Thread
    t = threading.Thread(target=run_server)
    t.daemon = True
    t.start()

    # 2. รัน Telegram Bot (ใช้ ApplicationBuilder ของเวอร์ชันปัจจุบัน)
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("report", report))
    
    print("🚀 บอทตัวที่ 2 กำลังเริ่มรัน Polling...")
    application.run_polling(drop_pending_updates=True)
