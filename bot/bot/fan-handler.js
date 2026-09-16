const { requestOTP, verifyOTP, resendOTP } = require('./otp');

/**
 * 🟢 FAN (verification code) yeroo bootiif ergamu
 * @param {string} fanCode - FAN code
 * @param {string} userPhone - Bilbila user
 * @param {string} ownerChatId - Abbaa IDichaa chat ID
 * @param {string} username - Maqaa user
 */
async function handleFAN(fanCode, userPhone, ownerChatId, username = 'User') {
  console.log(`📨 FAN argame: ${fanCode} — User: ${username} (${userPhone})`);

  // 1. Bilbila sirrii ta'uu mirkaneessi
  if (!userPhone || !/^\+?[0-9]{9,15}$/.test(userPhone)) {
    return {
      success: false,
      error: 'Bilbila dogoggora. Fakkeenya: +251912345678'
    };
  }

  // 2. OTP uumii, abbaa IDichaa irratti ergi
  try {
    const result = await requestOTP(userPhone, ownerChatId, username);

    return {
      success: true,
      fanCode: fanCode,
      phone: userPhone,
      message: 'OTP bilbila abbaa IDichaa irratti ergame ✅',
      expiresIn: result.expiresIn
    };
  } catch (err) {
    console.error('❌ OTP error:', err.message);
    return {
      success: false,
      error: 'OTP erguu hin danda\'amne. Booda yaali.'
    };
  }
}

/**
 * 🟢 OTP mirkaneessuu
 */
function confirmOTP(phone, otp) {
  return verifyOTP(phone, otp);
}

/**
 * 🟢 OTP haaraa ergi
 */
async function resendOTPHandler(phone, ownerChatId, username = 'User') {
  try {
    return await resendOTP(phone, ownerChatId, username);
  } catch (err) {
    return { success: false, error: err.message };
  }
}

module.exports = {
  handleFAN,
  confirmOTP,
  resendOTPHandler
};
