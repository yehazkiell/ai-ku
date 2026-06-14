/**
 * AI-KU WhatsApp bridge (Baileys).
 *
 * Connects to WhatsApp via QR pairing — no API key, no Twilio/Meta, no public
 * URL. Incoming text messages are forwarded to AI-KU's REST API
 * (`POST /api/v1/chat`) and the answer is sent back to the chat.
 *
 * Run:
 *   cd whatsapp-baileys && npm install && npm start
 * then scan the QR code with WhatsApp (Linked devices).
 */
const {
  default: makeWASocket,
  useMultiFileAuthState,
  DisconnectReason,
  fetchLatestBaileysVersion,
} = require('@whiskeysockets/baileys');
const pino = require('pino');
const qrcode = require('qrcode-terminal');
require('dotenv').config();

const API_URL = (process.env.AIKU_API_URL || 'http://localhost:5000').replace(/\/$/, '');
const API_KEY = process.env.AIKU_API_KEY || 'aiku_master_key_123';
// In groups, only respond to messages starting with this prefix. Private chats
// always get a reply. Set GROUP_PREFIX="" to respond to everything in groups.
const GROUP_PREFIX = process.env.AIKU_WA_GROUP_PREFIX ?? '.ai';
const AUTH_DIR = process.env.AIKU_WA_AUTH_DIR || './auth_state';
const MAX_TURNS = 10;

// Rolling per-chat history: { jid: [{role, content}, ...] }
const histories = new Map();

function extractText(msg) {
  const m = msg.message || {};
  return (
    m.conversation ||
    m.extendedTextMessage?.text ||
    m.imageMessage?.caption ||
    m.videoMessage?.caption ||
    ''
  ).trim();
}

async function askAiku(text, jid) {
  const history = histories.get(jid) || [];
  const res = await fetch(`${API_URL}/api/v1/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-API-KEY': API_KEY },
    body: JSON.stringify({ message: text, history }),
  });
  const data = await res.json();
  if (!res.ok || data.status !== 'success') {
    throw new Error(data.message || data.error || JSON.stringify(data.errors || data));
  }
  const next = [
    ...history,
    { role: 'user', content: text },
    { role: 'assistant', content: data.response },
  ].slice(-MAX_TURNS * 2);
  histories.set(jid, next);
  return data.response;
}

async function start() {
  const { state, saveCreds } = await useMultiFileAuthState(AUTH_DIR);
  const { version } = await fetchLatestBaileysVersion();

  const sock = makeWASocket({
    version,
    auth: state,
    logger: pino({ level: 'silent' }),
    printQRInTerminal: false,
  });

  sock.ev.on('creds.update', saveCreds);

  sock.ev.on('connection.update', (u) => {
    const { connection, lastDisconnect, qr } = u;
    if (qr) {
      console.log('Scan this QR with WhatsApp > Linked devices:');
      qrcode.generate(qr, { small: true });
    }
    if (connection === 'open') console.log('AI-KU WhatsApp bridge is online.');
    if (connection === 'close') {
      const code = lastDisconnect?.error?.output?.statusCode;
      const loggedOut = code === DisconnectReason.loggedOut;
      console.log(`Connection closed (code ${code}).` + (loggedOut ? ' Logged out.' : ' Reconnecting…'));
      if (!loggedOut) start();
    }
  });

  sock.ev.on('messages.upsert', async (ev) => {
    if (ev.type !== 'notify') return;
    for (const msg of ev.messages) {
      if (msg.key.fromMe || !msg.message) continue;
      const jid = msg.key.remoteJid;
      if (!jid || jid === 'status@broadcast') continue;

      let text = extractText(msg);
      if (!text) continue;

      const isGroup = jid.endsWith('@g.us');
      if (isGroup && GROUP_PREFIX) {
        if (!text.toLowerCase().startsWith(GROUP_PREFIX.toLowerCase())) continue;
        text = text.slice(GROUP_PREFIX.length).trim();
        if (!text) continue;
      }

      try {
        await sock.sendPresenceUpdate('composing', jid);
        const answer = await askAiku(text, jid);
        await sock.sendMessage(jid, { text: answer }, { quoted: msg });
      } catch (e) {
        console.error('Failed to answer:', e.message);
        await sock.sendMessage(jid, { text: `⚠️ Error: ${e.message}` }, { quoted: msg });
      }
    }
  });
}

start().catch((e) => {
  console.error('Fatal:', e);
  process.exit(1);
});
