const fetch = require('node-fetch');
const url = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key=AIzaSyDgHwzBGMFySfVJ0xe5AI6CGCZLHsiu3-w";
fetch(url, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ contents: [{ parts: [{ text: "hello" }] }] })
}).then(res => {
  console.log(res.status, res.statusText);
  return res.text();
}).then(console.log);
