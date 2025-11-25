fetch('/api/hello')
  .then(r => r.json())
  .then(d => {
    const el = document.getElementById('message')
    if (el) el.textContent = d.message
  })
  .catch(() => {
    const el = document.getElementById('message')
    if (el) el.textContent = '请求失败'
  })
