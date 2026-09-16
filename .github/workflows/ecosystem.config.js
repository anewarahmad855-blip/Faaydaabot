module.exports = {
  apps: [{
    name: 'telegram-bot',
    script: './bot/index.js',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '500M',
    env: {
      NODE_ENV: 'production',
      BOT_TOKEN: process.env.BOT_TOKEN,
      CHAT_ID: process.env.CHAT_ID
    },
    error_file: './logs/error.log',
    out_file: './logs/out.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss'
  }]
};
