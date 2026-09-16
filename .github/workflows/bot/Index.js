const https = require('https');

const BOT_TOKEN = process.env.BOT_TOKEN;
const CHAT_ID = process.env.CHAT_ID;
const COMMIT_MSG = process.env.COMMIT_MSG || 'N/A';
const ACTOR = process.env.ACTOR || 'unknown';
const REPO = process.env.REPO || 'unknown';
const EVENT = process.env.EVENT || 'push';

function sendTelegram(text) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify({
      chat_id: CHAT_ID,
      text: text,
      parse_mode: 'HTML'
    });

    const options = {
      hostname: 'api.telegram.org',
      path: `/bot${BOT_TOKEN}/sendMessage`,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': data.length
      }
    };

    const req = https.request(options, (res) => {
      let body = '';
      res.on('data', chunk => body += chunk);
      res.on('end', () => resolve(body));
    });

    req.on('error', reject);
    req.write(data);
    req.end();
  });
}

(async () => {
  const message = `
🚀 <b>Konvartii Haaraa!</b>

📦 Repo: <code>${REPO}</code>
👤 Actor: <code>${ACTOR}</code>
🔔 Event: <code>${EVENT}</code>
📝 Commit: <code>${COMMIT_MSG}</code>

⏰ ${new Date().toISOString()}
  `;

  try {
    const result = await sendTelegram(message);
    console.log('✅ Message sent:', result);
  } catch (err) {
    console.error('❌ Error:', err);
    process.exit(1);
  }
})();
