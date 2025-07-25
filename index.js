const express = require('express');
const axios = require('axios');

const app = express();
app.use(express.json());

const BOT_TOKEN = '7652827630:AAFbzcW-lS75BHK14wBEdgRrrkAL5KHwFBo';
const API_TOKEN = '1948684102:TUovfesW';
const API_URL = 'https://leakosintapi.com/';

app.post('/webhook', async (req, res) => {
  const msg = req.body.message;
  if (!msg || !msg.text) return res.sendStatus(200);

  const chatId = msg.chat.id;
  const userQuery = msg.text;

  try {
    const response = await axios.post(API_URL, {
      token: API_TOKEN,
      request: userQuery,
      limit: 100,
      lang: 'en'
    });

    if (!response.data || response.data["Error code"]) {
      await axios.post(`https://api.telegram.org/bot${BOT_TOKEN}/sendMessage`, {
        chat_id: chatId,
        text: "❌ API Error: " + (response.data["Error code"] || "Unknown error")
      });
    } else {
      let reply = '';
      for (const db in response.data.List) {
        reply += `📁 *${db}*
`;
        reply += response.data.List[db].InfoLeak + '\n\n';
        if (response.data.List[db].Data) {
          response.data.List[db].Data.forEach(entry => {
            for (const key in entry) {
              reply += `• *${key}*: ${entry[key]}\n`;
            }
            reply += '\n';
          });
        }
      }

      if (reply.length > 4000) reply = reply.slice(0, 3900) + "\n\n⚠️ Too long. Truncated.";

      await axios.post(`https://api.telegram.org/bot${BOT_TOKEN}/sendMessage`, {
        chat_id: chatId,
        text: reply || "No data found.",
        parse_mode: "Markdown"
      });
    }

  } catch (err) {
    await axios.post(`https://api.telegram.org/bot${BOT_TOKEN}/sendMessage`, {
      chat_id: chatId,
      text: '⚠️ Failed to connect to the API.'
    });
  }

  res.sendStatus(200);
});

app.get('/', (req, res) => {
  res.send('✅ Bot is live');
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
