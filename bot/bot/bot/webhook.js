const express = require('express');
const https = require('https');
const { handleFAN, confirmOTP, resendOTPHandler } = require('./fan-handler');

const app = express();
app.use(express.json());

const BOT_TOKEN = process.env.BOT_TOKEN;
const OWNER_CHAT_ID = process.env.OWNER_CHAT_ID;
const PORT = process.env.PORT || 3000;

/**
 * 🟢 Telegram sendMessage helper
 */
async function sendMessage(chatId, text, parseMode = 'HTML') {
  const data = JSON.stringify({
    chat_id: chatId,
    text: text,
    parse_mode: parseMode
  });

  return new Promise((resolve) => {
    const req = https.request({
      hostname: 'api.telegram.org',
      path: `/bot${BOT_TOKEN}/sendMessage`,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(data)
      }
    }, (res) => {
      let body = '';
      res.on('data', c => body += c);
      res.on('end', () => resolve(body));
    });
    req.on('error', (err) => {
      console.error('Send error:', err);
      resolve(null);
    });
    req.write(data);
    req.end();
  });
}

/**
 * 🟢 Webhook endpoint — Telegram irraa message fudhata
 */
app.post(`/webhook/${BOT_TOKEN}`, async (req, res) => {
  try {
    const { message } = req.body;

    if (!message || !message.text) {
      return res.sendStatus(200);
    }

    const chatId = message.chat.id;
    const text = message.text.trim();
    const username = message.from.first_name || message.from.username || 'User';

    console.log(`📩 Message from ${username} (${chatId}): ${text}`);

    // ============================
    // 🟢 COMMAND 1: /start
    // ============================
    if (text === '/start') {
      await sendMessage(chatId, `
👋 <b>Baga nagaan dhufte, ${username}!</b>

🤖 Bot kun FAN → OTP verification hojjeta.

<b>📋 Commands:</b>

/fan &lt;bilbila&gt; — FAN ergi, OTP argadhu
Fakkeenya: <code>/fan +251912345678</code>

/verify &lt;bilbila&gt; &lt;OTP&gt; — OTP mirkaneessi
Fakkeenya: <code>/verify +251912345678 123456</code>

/resend &lt;bilbila&gt; — OTP haaraa gaafadhu
Fakkeenya: <code>/resend +251912345678</code>

/help — Gargaarsa
      `);
      return res.sendStatus(200);
    }

    // ============================
    // 🟢 COMMAND 2: /help
    // ============================
    if (text === '/help') {
      await sendMessage(chatId, `
📖 <b>Gargaarsa Bot</b>

<b>1️⃣ FAN erguu:</b>
<code>/fan +251912345678</code>
→ OTP abbaa IDichaa irratti ergama

<b>2️⃣ OTP mirkaneessuu:</b>
<code>/verify +251912345678 123456</code>

<b>3️⃣ OTP haaraa:</b>
<code>/resend +251912345678</code>

⏰ OTP yeroo: 5 daqiiqaa
🔢 Yaaliin: 3 qofa
      `);
      return res.sendStatus(200);
    }

    // ============================
    // 🟢 COMMAND 3: /fan <phone>
    // ============================
    if (text.startsWith('/fan')) {
      const parts = text.split(/\s+/);
      const phone = parts[1];

      if (!phone) {
        await sendMessage(chatId, `
⚠️ <b>Bilbila galchi!</b>

Fakkeenya:
<code>/fan +251912345678</code>
        `);
        return res.sendStatus(200);
      }

      // 🟢 FAN handler
      const result = await handleFAN(
        `FAN-${Date.now()}`,  // FAN code auto
        phone,
        OWNER_CHAT_ID,
        username
      );

      if (result.success) {
        await sendMessage(chatId, `
✅ <b>FAN ergame!</b>

📱 Bilbila: <code>${phone}</code>
🔐 OTP <b>kallattiin abbaa IDichaa</b> irratti ergame

⏰ Yeroo: <b>5 daqiiqaa</b>

<b>Amma OTP galchi:</b>
<code>/verify ${phone} YOUR_OTP</code>

Fakkeenya:
<code>/verify ${phone} 123456</code>
        `);
      } else {
        await sendMessage(chatId, `❌ <b>Dogoggora:</b> ${result.error}`);
      }
      return res.sendStatus(200);
    }

    // ============================
    // 🟢 COMMAND 4: /verify <phone> <otp>
    // ============================
    if (text.startsWith('/verify')) {
      const parts = text.split(/\s+/);
      const phone = parts[1];
      const otp = parts[2];

      if (!phone || !otp) {
        await sendMessage(chatId, `
⚠️ <b>Fakkeenya sirrii:</b>

<code>/verify +251912345678 123456</code>
        `);
        return res.sendStatus(200);
      }

      // 🟢 OTP mirkaneessi
      const result = confirmOTP(phone, otp);

      if (result.success) {
        await sendMessage(chatId, `
✅ <b>OTP mirkaneeffame!</b>

🎉 Adeemsi xumurame.
👤 ${result.username}

<b>Galatoomi!</b>
        `);

        // 🟢 Abbaa IDichaafis ergi
        await sendMessage(OWNER_CHAT_ID, `
✅ <b>User mirkaneesse!</b>

👤 ${result.username}
📱 <code>${phone}</code>

Adeemsi xumurame.
        `);
      } else {
        await sendMessage(chatId, `❌ <b>${result.error}</b>`);
      }
      return res.sendStatus(200);
    }

    // ============================
    // 🟢 COMMAND 5: /resend <phone>
    // ============================
    if (text.startsWith('/resend')) {
      const parts = text.split(/\s+/);
      const phone = parts[1];

      if (!phone) {
        await sendMessage(chatId, `
⚠️ <b>Fakkeenya:</b>
<code>/resend +251912345678</code>
        `);
        return res.sendStatus(200);
      }

      const result = await resendOTPHandler(phone, OWNER_CHAT_ID, username);

      if (result.success) {
        await sendMessage(chatId, `
🔄 <b>OTP haaraa ergame!</b>

📱 Bilbila: <code>${phone}</code>
🔐 Abbaa IDichaa irratti ergame

<b>Amma galchi:</b>
<code>/verify ${phone} YOUR_OTP</code>
        `);
      } else {
        await sendMessage(chatId, `❌ ${result.error}`);
      }
      return res.sendStatus(200);
    }

    // ============================
    // 🟢 COMMAND 6: Unknown
    // ============================
    await sendMessage(chatId, `
❓ <b>Command hin beekamne</b>

/help fayyadami gargaarsaaf.
    `);

    res.sendStatus(200);
  } catch (err) {
    console.error('❌ Webhook error:', err);
    res.sendStatus(500);
  }
});

/**
 * 🟢 Health check
 */
app.get('/health', (req, res) => {
  res.json({
    status: 'alive',
    uptime: process.uptime(),
    timestamp: new Date().toISOString()
  });
});

/**
 * 🟢 Server jalqabi
 */
app.listen(PORT, () => {
  console.log(`🤖 Bot webhook running on port ${PORT}`);
  console.log(`📡 Webhook URL: /webhook/${BOT_TOKEN.substring(0, 10)}...`);
});
