import os
import paho.mqtt.client as mqtt
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ดึง Token จาก Environment Variables บน Render
TOKEN = os.environ.get("TELEGRAM_TOKEN")

# ตั้งค่า MQTT Broker (ให้ตรงกับฝั่ง ESP32)
MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_TOPIC = "esp32/control"

async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # แจ้งเตือนในแชททันทีที่มีคนพิมพ์ /report
    await update.message.reply_text("🤖 ได้รับคำสั่ง /report แล้ว! กำลังส่งสัญญาณปลุกตู้ควบคุม...")
    
    # ยิงสัญญาณ MQTT ไปปลุก ESP32 ผ่านโมดูล 4G
    try:
        client = mqtt.Client()
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.publish(MQTT_TOPIC, "WAKEUP")
        client.disconnect()
        print("✅ [MQTT] ยิงสัญญาณ WAKEUP ปลุกตู้สำเร็จ")
    except Exception as e:
        print(f"❌ [MQTT] เกิดข้อผิดพลาด: {e}")

if __name__ == "__main__":
    if not TOKEN:
        print("⚠️ [ERROR] ยังไม่ได้ใส่ TELEGRAM_TOKEN")
    
    # สร้างแอปพลิเคชันบอท
    application = ApplicationBuilder().token(TOKEN).build()
    
    # ผูกคำสั่ง /report เข้ากับฟังก์ชัน
    application.add_handler(CommandHandler("report", report))
    
    print("🚀 บอทตัวที่ 2 พร้อมดักฟังคำสั่ง /report แล้ว...")
    application.run_polling()
