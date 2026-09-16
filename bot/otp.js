const crypto = require('crypto');
const https = require('https');

// 🟢 OTP store (production keessatti Redis fayyadami)
const otpStore = new Map();

/**
 * 🟢 OTP 6-digit uumi
 */
function generateOTP() {
  return crypto.randomInt(100000, 999999).toString();
}

/**
 * 🟢 OTP ergaa Telegram fayyadamuun
 * @param {string} chatId - Abbaa IDichaa chat ID
 * @param {string} otp - OTP 6-digit
 * @param {string} phone - Bilbila user
 * @param {string} username - Maqaa user
 */
function sendOTPviaTelegram(chatId, otp, phone, username = 'User') {
  const BOT_TOKEN = process.env.BOT_TOKEN;

  const text = `
🔐 <b>OTP Verification — FAN</b>

👤 User: <b>${username}</b>
📱 Bilbila: <code>${phone}</code>
🔢 Koodii: <code>${otp}</code>

⏰ Yeroo: <b>5 daqiiqaa</b>
⚠️ Namni biraa hin beeku!

  `;

  return new Promise((resolve, reject) => {
    const data = JSON.stringify({
      chat_id: chatId,
      text: text,
      parse_mode: 'HTML'
    });

    const options = {
      hostname: 'api.telegram.org',
      path: `/bot${BOT_TOKEN}/sendMessage`,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(data)
      }
    };

    const req = https.request(options, (res) => {
      let body = '';
      res.on('data', chunk => body += chunk);
      res.on('end', () => {
        try {
          resolve(JSON.parse(body));
        } catch (e) {
          reject(e);
        }
      });
    });

    req.on('error', reject);
    req.write(data);
    req.end();
  });
}

/**
 * 🟢 OTP uumii fi abbaa IDichaa irratti ergi
 * @param {string} phone - Bilbila user
 * @param {string} ownerChatId - Abbaa IDichaa chat ID
 * @param {string} username - Maqaa user
 */
async function requestOTP(phone, ownerChatId, username = 'User') {
  // 1. OTP uumi
  const otp = generateOTP();
  const expiresAt = Date.now() + 5 * 60 * 1000; // 5 daqiiqaa

  // 2. Store keessatti galchi
  otpStore.set(phone, {
    otp,
    expiresAt,
    attempts: 0,
    createdAt: Date.now(),
    username
  });

  // 3. Abbaa IDichaa irratti ergi
  const result = await sendOTPviaTelegram(ownerChatId, otp, phone, username);

  if (!result.ok) {
    otpStore.delete(phone);
    throw new Error('OTP erguu hin danda\'amne: ' + (result.description || 'Unknown'));
  }

  return {
    success: true,
    message: 'OTP ergame bilbila abbaa IDichaa irratti',
    expiresIn: 300
  };
}

/**
 * 🟢 OTP mirkaneessi
 * @param {string} phone - Bilbila user
 * @param {string} userOTP - OTP user galche
 */
function verifyOTP(phone, userOTP) {
  const record = otpStore.get(phone);

  // 1. OTP hin argamne
  if (!record) {
    return { success: false, error: 'OTP hin argamne. Dura /fan ergi.' };
  }

  // 2. Yeroo dabarse
  if (Date.now() > record.expiresAt) {
    otpStore.delete(phone);
    return { success: false, error: 'OTP yeroo dabarse. Dura /fan ergi.' };
  }

  // 3. Yaaliin 3 dabarse
  if (record.attempts >= 3) {
    otpStore.delete(phone);
    return { success: false, error: 'Yaaliin 3 dabarse. OTP dhaabbate.' };
  }

  // 4. OTP dogoggora
  if (record.otp !== userOTP) {
    record.attempts++;
    return {
      success: false,
      error: `OTP dogoggora. Yaalii ${3 - record.attempts} hafe.`
    };
  }

  // 5. OTP sirrii — dhaabi
  otpStore.delete(phone);
  return {
    success: true,
    message: 'OTP mirkaneeffame ✅',
    username: record.username
  };
}

/**
 * 🟢 OTP haaraa ergi (resend)
 */
async function resendOTP(phone, ownerChatId, username = 'User') {
  otpStore.delete(phone); // Isa dura dhaabi
  return requestOTP(phone, ownerChatId, username);
}

module.exports = {
  generateOTP,
  requestOTP,
  verifyOTP,
  resendOTP,
  otpStore
};
