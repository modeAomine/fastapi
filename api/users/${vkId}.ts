import { VercelRequest, VercelResponse } from '@vercel/node';
import mysql from 'mysql2/promise';

export default async function handler(req: VercelRequest, res: VercelResponse) {
  const { vkId } = req.query;

  if (req.method === 'GET') {
    try {
      const connection = await mysql.createConnection({
        host: process.env.DB_HOST,
        user: process.env.DB_USER,
        password: process.env.DB_PASSWORD,
        database: process.env.DB_NAME
      });

      const [users] = await connection.execute(
        'SELECT * FROM users WHERE vk_id = ?',
        [vkId]
      );

      await connection.end();

      const usersArray = users as any[];

      if (usersArray.length > 0) {
        res.status(200).json({
          success: true,
          data: usersArray[0]
        });
      } else {
        res.status(404).json({
          success: false,
          error: 'User not found'
        });
      }

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