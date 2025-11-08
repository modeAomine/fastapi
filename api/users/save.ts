// import { VercelRequest, VercelResponse } from '@vercel/node';
// import mysql from 'mysql2/promise';

// export default async function handler(req: VercelRequest, res: VercelResponse) {
//   if (req.method === 'POST') {
//     try {
//       const connection = await mysql.createConnection({
//         host: process.env.DB_HOST,
//         user: process.env.DB_USER,
//         password: process.env.DB_PASSWORD,
//         database: process.env.DB_NAME
//       });

//       const { vk_id, first_name, last_name, photo_100, photo_200, phone, email } = req.body;

//       const [result] = await connection.execute(
//         `INSERT INTO users (vk_id, first_name, last_name, photo_100, photo_200, phone, email) 
//          VALUES (?, ?, ?, ?, ?, ?, ?) 
//          ON DUPLICATE KEY UPDATE 
//          first_name = VALUES(first_name), last_name = VALUES(last_name),
//          photo_100 = VALUES(photo_100), photo_200 = VALUES(photo_200),
//          phone = VALUES(phone), email = VALUES(email),
//          updated_at = NOW()`,
//         [vk_id, first_name, last_name, photo_100, photo_200, phone, email]
//       );

//       await connection.end();

//       const insertResult = result as any;
      
//       res.status(200).json({
//         success: true,
//         data: {
//           id: insertResult.insertId || vk_id,
//           vk_id,
//           first_name,
//           last_name,
//           photo_100,
//           photo_200,
//           phone,
//           email
//         }
//       });

//     } catch (error: any) {
//       res.status(500).json({
//         success: false,
//         error: error.message
//       });
//     }
//   } else {
//     res.status(405).json({ error: 'Method not allowed' });
//   }
// }