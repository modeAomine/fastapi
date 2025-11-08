from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import mysql.connector
import os
from typing import Optional

app = FastAPI(
    title="VK Mini App API",
    description="API для VK Mini App - Вынос мусора",
    version="1.0.0",
)

# Модели данных
class VKUserData(BaseModel):
    id: int
    first_name: str
    last_name: str
    photo_100: Optional[str] = None
    photo_200: Optional[str] = None
    access_token: Optional[str] = None

class UserUpdate(BaseModel):
    phone: Optional[str] = None
    email: Optional[str] = None

class AddressCreate(BaseModel):
    user_id: int
    title: str
    address_text: str

# Подключение к БД
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )

# Эндпоинты для пользователей

@app.post("/api/auth/vk")
async def auth_vk(user_data: VKUserData):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Проверяем существование пользователя
        cursor.execute("SELECT * FROM users WHERE vk_id = %s", (user_data.id,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            # Обновляем существующего пользователя
            cursor.execute(
                """UPDATE users 
                SET first_name = %s, last_name = %s, photo_100 = %s, photo_200 = %s, updated_at = NOW() 
                WHERE vk_id = %s""",
                (user_data.first_name, user_data.last_name, user_data.photo_100, user_data.photo_200, user_data.id)
            )
            user = existing_user
        else:
            # Создаем нового пользователя
            cursor.execute(
                """INSERT INTO users (vk_id, first_name, last_name, photo_100, photo_200) 
                VALUES (%s, %s, %s, %s, %s)""",
                (user_data.id, user_data.first_name, user_data.last_name, user_data.photo_100, user_data.photo_200)
            )
            user_id = cursor.lastrowid
            
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
        
        conn.commit()
        
        return {
            "success": True,
            "data": user
        }
        
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.get("/api/users/{vk_id}")
async def get_user_by_vk_id(vk_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT * FROM users WHERE vk_id = %s", (vk_id,))
        user = cursor.fetchone()
        
        if user:
            return {
                "success": True,
                "data": user
            }
        else:
            raise HTTPException(status_code=404, detail="User not found")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.put("/api/users/{vk_id}/phone")
async def update_user_phone(vk_id: int, user_update: UserUpdate):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute(
            "UPDATE users SET phone = %s, updated_at = NOW() WHERE vk_id = %s",
            (user_update.phone, vk_id)
        )
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="User not found")
        
        cursor.execute("SELECT * FROM users WHERE vk_id = %s", (vk_id,))
        user = cursor.fetchone()
        
        conn.commit()
        
        return {
            "success": True,
            "data": user
        }
        
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.put("/api/users/{vk_id}/email")
async def update_user_email(vk_id: int, user_update: UserUpdate):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute(
            "UPDATE users SET email = %s, updated_at = NOW() WHERE vk_id = %s",
            (user_update.email, vk_id)
        )
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="User not found")
        
        cursor.execute("SELECT * FROM users WHERE vk_id = %s", (vk_id,))
        user = cursor.fetchone()
        
        conn.commit()
        
        return {
            "success": True,
            "data": user
        }
        
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

# Эндпоинты для адресов

@app.get("/api/users/{user_id}/addresses")
async def get_user_addresses(user_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT * FROM addresses WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
        addresses = cursor.fetchall()
        
        return {
            "success": True,
            "data": addresses
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.post("/api/addresses")
async def create_address(address_data: AddressCreate):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute(
            "INSERT INTO addresses (user_id, title, address_text) VALUES (%s, %s, %s)",
            (address_data.user_id, address_data.title, address_data.address_text)
        )
        
        address_id = cursor.lastrowid
        cursor.execute("SELECT * FROM addresses WHERE id = %s", (address_id,))
        address = cursor.fetchone()
        
        conn.commit()
        
        return {
            "success": True,
            "data": address
        }
        
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.delete("/api/addresses/{address_id}")
async def delete_address(address_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM addresses WHERE id = %s", (address_id,))
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Address not found")
        
        conn.commit()
        
        return {
            "success": True,
            "message": "Address deleted successfully"
        }
        
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

# Тестовые эндпоинты (можно удалить)

@app.get("/api/data")
def get_sample_data():
    return {
        "data": [
            {"id": 1, "name": "Sample Item 1", "value": 100},
            {"id": 2, "name": "Sample Item 2", "value": 200},
            {"id": 3, "name": "Sample Item 3", "value": 300}
        ],
        "total": 3,
        "timestamp": "2024-01-01T00:00:00Z"
    }

@app.get("/api/items/{item_id}")
def get_item(item_id: int):
    return {
        "item": {
            "id": item_id,
            "name": "Sample Item " + str(item_id),
            "value": item_id * 100
        },
        "timestamp": "2024-01-01T00:00:00Z"
    }

# Главная страница
@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>VK Mini App API</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, sans-serif;
                margin: 0;
                padding: 2rem;
                background: #f5f5f5;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                background: white;
                padding: 2rem;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #333;
                border-bottom: 2px solid #0070f3;
                padding-bottom: 0.5rem;
            }
            .endpoint {
                background: #f8f9fa;
                padding: 1rem;
                margin: 1rem 0;
                border-radius: 6px;
                border-left: 4px solid #0070f3;
            }
            .method {
                display: inline-block;
                background: #0070f3;
                color: white;
                padding: 0.25rem 0.5rem;
                border-radius: 4px;
                font-weight: bold;
                margin-right: 1rem;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 VK Mini App API</h1>
            <p>API сервер для приложения "Вынос мусора"</p>
            
            <div class="endpoint">
                <span class="method">POST</span>
                <strong>/api/auth/vk</strong> - Аутентификация через VK
            </div>
            
            <div class="endpoint">
                <span class="method">GET</span>
                <strong>/api/users/&#123;vk_id&#125;</strong> - Получить пользователя по VK ID
            </div>
            
            <div class="endpoint">
                <span class="method">PUT</span>
                <strong>/api/users/&#123;vk_id&#125;/phone</strong> - Обновить телефон
            </div>
            
            <div class="endpoint">
                <span class="method">PUT</span>
                <strong>/api/users/&#123;vk_id&#125;/email</strong> - Обновить email
            </div>
            
            <div class="endpoint">
                <span class="method">GET</span>
                <strong>/api/users/&#123;user_id&#125;/addresses</strong> - Получить адреса пользователя
            </div>
            
            <div class="endpoint">
                <span class="method">POST</span>
                <strong>/api/addresses</strong> - Создать адрес
            </div>
            
            <div class="endpoint">
                <span class="method">DELETE</span>
                <strong>/api/addresses/&#123;address_id&#125;</strong> - Удалить адрес
            </div>
            
            <p><a href="/docs">📚 Interactive API Documentation</a></p>
        </div>
    </body>
    </html>
    """