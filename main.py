import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from aiogram import Bot
from aiogram.types import User

app = FastAPI()

# Разрешаем запросы с вашего React-приложения (по умолчанию Vite на порту 5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # в production поменяйте на ваш домен
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Инициализируем бота с вашим токеном
BOT_TOKEN = "8868692097:AAEd8wmp07CEbTNu1ju7AYl3kgv2psPXNVY"
bot = Bot(token=BOT_TOKEN)

@app.get("/api/user/{user_id}/avatar/")
async def get_user_avatar(user_id: int):
    """
    Возвращает прямую ссылку на аватар пользователя Telegram.
    Если у пользователя нет аватарки или он не найден — возвращает null.
    """
    try:
        # Запрашиваем фото профиля (берём самую свежую, самый большой размер)
        photos = await bot.get_user_profile_photos(user_id, limit=1)
        
        if not photos.photos:
            return {"avatar_url": None}
        
        # photos.photos[0] — список размеров одного фото (от маленького к большому)
        # Берём последний элемент — самый большой размер
        file_id = photos.photos[0][-1].file_id
        
        # Получаем информацию о файле для формирования прямой ссылки
        file = await bot.get_file(file_id)
        avatar_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file.file_path}"
        
        return {"avatar_url": avatar_url}
    
    except Exception as e:
        # Если пользователь никогда не взаимодействовал с ботом — ошибка "user not found"
        if "user not found" in str(e).lower():
            return {"avatar_url": None}
        print(f"Ошибка: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Опционально: закрываем сессию бота при выключении сервера
@app.on_event("shutdown")
async def shutdown():
    await bot.session.close()

# Точка входа (если запускаем файл напрямую)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
