import express from 'express';
import qrcode from 'qrcode';
import { connect, sendMessage, disconnectSession, getStatus, getQr } from './whatsapp.js';

const app = express();
const PORT = 3001;
const HOST = '127.0.0.1';

app.use(express.json({ limit: '20mb' }));

// Restricción: solo llamadas desde localhost
app.use((req, res, next) => {
  const ip = req.ip || req.socket?.remoteAddress || '';
  const allowed = ['127.0.0.1', '::1', '::ffff:127.0.0.1'];
  if (!allowed.includes(ip)) {
    return res.status(403).json({ error: 'Acceso solo desde localhost.' });
  }
  next();
});

// GET /status — estado de la conexión
app.get('/status', (req, res) => {
  res.json({ status: getStatus() });
});

// GET /qr — QR como data URL base64
app.get('/qr', async (req, res) => {
  const qr = getQr();
  if (!qr) {
    return res.json({ qr: null, status: getStatus() });
  }
  try {
    const qrDataUrl = await qrcode.toDataURL(qr);
    res.json({ qr: qrDataUrl, status: getStatus() });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// POST /send — enviar mensaje al grupo
app.post('/send', async (req, res) => {
  const { groupJid, text, imageBase64 } = req.body;
  if (!groupJid || !text) {
    return res.status(400).json({ error: 'groupJid y text son requeridos.' });
  }
  try {
    const imageBuffer = imageBase64 ? Buffer.from(imageBase64, 'base64') : null;
    await sendMessage(groupJid, text, imageBuffer);
    res.json({ ok: true, enviado_en: new Date().toISOString() });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// DELETE /logout — cerrar sesión y limpiar auth_info
app.delete('/logout', async (req, res) => {
  try {
    await disconnectSession();
    res.json({ ok: true, message: 'Sesión cerrada.' });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Iniciar servidor y conectar WhatsApp
app.listen(PORT, HOST, async () => {
  console.log(`[Servidor] WhatsApp service corriendo en http://${HOST}:${PORT}`);
  console.log('[WhatsApp] Iniciando conexión...');
  try {
    await connect();
  } catch (err) {
    console.error('[WhatsApp] Error al conectar:', err.message);
  }
});
