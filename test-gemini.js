const url1 = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key=invalid";
fetch(url1, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ contents: [{ parts: [{ text: "hello" }] }] })
}).then(res => {
  console.log('v1', res.status, res.statusText);
});

const url2 = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=invalid";
fetch(url2, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ contents: [{ parts: [{ text: "hello" }] }] })
}).then(res => {
  console.log('v1beta', res.status, res.statusText);
});
