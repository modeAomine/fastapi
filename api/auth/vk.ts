import { VercelRequest, VercelResponse } from '@vercel/node';
import mysql from 'mysql2/promise';

export default async function handler(req: VercelRequest, res: VercelResponse) {
  if (req.method === 'POST') {
    try {
      const connection = await mysql.createConnection({
        host: process.env.DB_HOST,
        user: process.env.DB_USER,
        password: process.env.DB_PASSWORD,
        database: process.env.DB_NAME
      });

      const { id, first_name, last_name, photo_100, photo_200, access_token } = req.body;

      // Проверяем существование пользователя
      const [existingUsers] = await connection.execute(
        'SELECT * FROM users WHERE vk_id = ?',
        [id]
      );

      let user;
      const usersArray = existingUsers as any[];

      if (usersArray.length > 0) {
        // Обновляем существующего пользователя
        await connection.execute(
          `UPDATE users 
           SET first_name = ?, last_name = ?, photo_100 = ?, photo_200 = ?, updated_at = NOW() 
           WHERE vk_id = ?`,
          [first_name, last_name, photo_100, photo_200, id]
        );
        user = usersArray[0];
      } else {
        // Создаем нового пользователя
        const [result] = await connection.execute(
          `INSERT INTO users (vk_id, first_name, last_name, photo_100, photo_200) 
           VALUES (?, ?, ?, ?, ?)`,
          [id, first_name, last_name, photo_100, photo_200]
        );
        
        const insertResult = result as any;
        user = {
          id: insertResult.insertId,
          vk_id: id,
          first_name,
          last_name,
          photo_100,
          photo_200
        };
      }

      await connection.end();

      res.status(200).json({
        success: true,
        data: user
      });

    } catch (error: any) {
      res.status(500).json({
        success: false,
        error: error.message
      });
    }
  } else {
    res.status(405).json({ error: 'Method not allowed' });
  }
}