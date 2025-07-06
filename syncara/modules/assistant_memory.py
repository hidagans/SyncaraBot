from syncara.database import users
from datetime import datetime

async def kenalan_dan_update(client, user):
    """Kenalan dengan user dan simpan/update ke database"""
    user_data = await users.find_one({"user_id": user.id})
    if not user_data:
        # User baru, simpan ke database
        await users.insert_one({
            "user_id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "last_interaction": datetime.utcnow(),
            "notes": ""
        })
        await client.send_message(
            user.id,
            f"Halo {user.first_name or user.username}! Aku AERIS, asisten AI kamu. Senang kenalan denganmu! 😊"
        )
    else:
        # User lama, update waktu interaksi
        await users.update_one(
            {"user_id": user.id},
            {"$set": {
                "last_interaction": datetime.utcnow(),
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name
            }}
        )
        # Contoh: assistant bisa mengingat dan menyapa user lama
        await client.send_message(
            user.id,
            f"Halo lagi, {user.first_name or user.username}! Aku masih ingat kamu kok 😁"
        )

async def get_user_memory(user_id):
    """Ambil data user (ingatan) dari database berdasarkan user_id"""
    return await users.find_one({"user_id": user_id}) 