import makeWASocket, {
  useMultiFileAuthState,
  DisconnectReason,
  fetchLatestBaileysVersion,
} from '@whiskeysockets/baileys';
import pino from 'pino';

const logger = pino({ level: 'silent' });

let sock = null;
let _qrCode = null;
let _status = 'disconnected';
let _reconnecting = false;

export function getStatus() {
  return _status;
}

export function getQr() {
  return _qrCode;
}

export async function connect() {
  const { state, saveCreds } = await useMultiFileAuthState('./auth_info');
  const { version } = await fetchLatestBaileysVersion();

  sock = makeWASocket({
    version,
    auth: state,
    logger,
    printQRInTerminal: false,
    browser: ['Gestor Iglesia', 'Chrome', '1.0.0'],
  });

  sock.ev.on('creds.update', saveCreds);

  sock.ev.on('connection.update', ({ connection, lastDisconnect, qr }) => {
    if (qr) {
      _qrCode = qr;
      _status = 'qr_pending';
      console.log('[WhatsApp] QR listo para escanear.');
    }

    if (connection === 'open') {
      _status = 'connected';
      _qrCode = null;
      _reconnecting = false;
      console.log('[WhatsApp] Conectado.');
    }

    if (connection === 'close') {
      _status = 'disconnected';
      const code = lastDisconnect?.error?.output?.statusCode;
      const shouldReconnect = code !== DisconnectReason.loggedOut;
      console.log(`[WhatsApp] Desconectado (código ${code}). Reconectar: ${shouldReconnect}`);
      if (shouldReconnect && !_reconnecting) {
        _reconnecting = true;
        setTimeout(() => {
          _reconnecting = false;
          connect();
        }, 5000);
      }
    }
  });
}

export async function sendMessage(groupJid, text, imageBuffer = null) {
  if (!sock || _status !== 'connected') {
    throw new Error('WhatsApp no conectado. Escanea el QR primero.');
  }
  if (imageBuffer) {
    await sock.sendMessage(groupJid, { image: imageBuffer, caption: text });
  } else {
    await sock.sendMessage(groupJid, { text });
  }
}

export async function disconnectSession() {
  if (sock) {
    await sock.logout();
    sock = null;
  }
  _status = 'disconnected';
  _qrCode = null;

  const { rm } = await import('fs/promises');
  await rm('./auth_info', { recursive: true, force: true });
  console.log('[WhatsApp] Sesión cerrada y auth_info eliminada.');
}
