'use strict';
const yearSpan = document.getElementById('year');
if (yearSpan) yearSpan.textContent = new Date().getFullYear();

const select = document.getElementById('deviceSelect');
const flasherBtn = document.getElementById('flasherBtn');
select.addEventListener('change', () => {
  flasherBtn.setAttribute('manifest', select.value);
});

const enc = new TextEncoder();
const statusBox = document.getElementById('statusBox');
const statusIcon = document.getElementById('statusIcon');
const statusText = document.getElementById('statusText');
const btnUsbBridge = document.getElementById('btnUsbBridge');
const btnPushWifi = document.getElementById('btnPushWifi');
const wifiSsidInput = document.getElementById('wifiSsid');
const wifiPassInput = document.getElementById('wifiPass');
const wifiShowPass = document.getElementById('wifiShowPass');

if (wifiShowPass && wifiPassInput) {
  wifiShowPass.addEventListener('change', () => {
    wifiPassInput.type = wifiShowPass.checked ? 'text' : 'password';
  });
}

function setStatus(message, type = 'normal') {
  statusBox.className = 'status-box p-3 small mt-3';
  if (type === 'success') {
    statusBox.classList.add('success');
    statusIcon.textContent = '🎉';
  } else if (type === 'warning') {
    statusBox.classList.add('warning');
    statusIcon.textContent = '⚠️';
  } else if (type === 'error') {
    statusBox.classList.add('error');
    statusIcon.textContent = '❌';
  } else if (type === 'busy') {
    statusIcon.textContent = '⏳';
  } else {
    statusIcon.textContent = '💡';
  }
  statusText.innerHTML = message;
}

// --- Option 1: Push Wi-Fi & Activate Bipkin over USB ---
btnPushWifi.addEventListener('click', async () => {
  const ssid = wifiSsidInput.value.trim();
  const pass = wifiPassInput.value;

  if (!ssid) {
    setStatus('Please enter your 2.4 GHz Wi-Fi network name (SSID).', 'warning');
    wifiSsidInput.focus();
    return;
  }
  if (pass.length > 0 && pass.length < 8) {
    setStatus('WPA2 Wi-Fi passwords must be at least 8 characters (or empty for open networks).', 'warning');
    wifiPassInput.focus();
    return;
  }

  if (!('serial' in navigator)) {
    setStatus('Web Serial is not supported in this browser. Please use Chrome, Edge, or Opera on desktop.', 'error');
    return;
  }

  btnPushWifi.disabled = true;
  setStatus('Please select your CYD device port (CH340 / CP2102) in the browser popup...', 'busy');

  let port = null, writer = null, reader = null;
  try {
    port = await navigator.serial.requestPort();
    await port.open({ baudRate: 115200 });

    setStatus('Connected! Sending Wi-Fi credentials & synchronizing clock...', 'busy');
    writer = port.writable.getWriter();
    reader = port.readable.getReader();

    // 1. Send SET_WIFI command
    const setWifiCmd = `SET_WIFI ${ssid} ${pass}\n`;
    await writer.write(enc.encode(setWifiCmd));

    // 2. Also send BRIDGE_TIME for instant UTC time synchronization
    const epoch = Math.floor(Date.now() / 1000);
    const bridgeCmd = `BRIDGE_TIME ${epoch}\n`;
    await writer.write(enc.encode(bridgeCmd));

    writer.releaseLock();
    writer = null;

    let buffer = '';
    const startTime = Date.now();
    let wifiSaved = false;
    let clockVerified = false;

    while (Date.now() - startTime < 8000) {
      const readPromise = reader.read();
      const timeoutPromise = new Promise((_, reject) => setTimeout(() => reject(new Error('timeout')), 1500));
      let result;
      try {
        result = await Promise.race([readPromise, timeoutPromise]);
      } catch (e) {
        if (e.message === 'timeout') continue;
        throw e;
      }
      if (result.done) break;
      buffer += new TextDecoder().decode(result.value);

      if (buffer.includes('[NETWORK] Saved')) wifiSaved = true;
      if (buffer.includes('[CLOCK] USB bridge verified') || buffer.includes('[CLOCK] verified=1')) clockVerified = true;

      if (wifiSaved && clockVerified) break;
    }

    if (wifiSaved || clockVerified) {
      setStatus(`<strong>Success!</strong> Wi-Fi credentials for <b>${ssid}</b> saved, UTC internet clock verified, and incubation started!`, 'success');
    } else {
      setStatus('Credentials sent. Ensure the Bipkin is booted up to the egg screen.', 'warning');
    }

  } catch (err) {
    if (err.name === 'NotFoundError') {
      setStatus('Port selection was cancelled.', 'normal');
    } else {
      setStatus('Connection error: ' + (err.message || 'Port unavailable') + '. Ensure other serial apps or monitors are closed.', 'error');
    }
  } finally {
    if (writer) { try { writer.releaseLock(); } catch {} }
    if (reader) { try { await reader.cancel(); } catch {} try { reader.releaseLock(); } catch {} }
    if (port) { try { await port.close(); } catch {} }
    btnPushWifi.disabled = false;
  }
});

// --- USB Internet Bridge (1-Click Time Sync over USB without Wi-Fi) ---
btnUsbBridge.addEventListener('click', async () => {
  if (!('serial' in navigator)) {
    setStatus('Web Serial is not supported in this browser. Please use Chrome, Edge, or Opera on desktop.', 'error');
    return;
  }

  btnUsbBridge.disabled = true;
  setStatus('Please select your device port (CH340 / CP2102) in the browser popup...', 'busy');

  let port = null, writer = null, reader = null;
  try {
    port = await navigator.serial.requestPort();
    await port.open({ baudRate: 115200 });

    setStatus('Connected! Syncing UTC internet time to your Bipkin...', 'busy');
    writer = port.writable.getWriter();
    reader = port.readable.getReader();

    const epoch = Math.floor(Date.now() / 1000);
    const command = `BRIDGE_TIME ${epoch}\n`;
    await writer.write(enc.encode(command));
    writer.releaseLock();
    writer = null;

    let buffer = '';
    const startTime = Date.now();
    let verified = false;

    while (Date.now() - startTime < 6000) {
      const readPromise = reader.read();
      const timeoutPromise = new Promise((_, reject) => setTimeout(() => reject(new Error('timeout')), 1500));
      let result;
      try {
        result = await Promise.race([readPromise, timeoutPromise]);
      } catch (e) {
        if (e.message === 'timeout') continue;
        throw e;
      }
      if (result.done) break;
      buffer += new TextDecoder().decode(result.value);

      if (buffer.includes('[CLOCK] USB bridge verified')) {
        verified = true;
        break;
      }
    }

    if (verified) {
      setStatus('<strong>Internet time verified via USB!</strong> Your Bipkin clock is synced, care and hatching are unlocked, and incubation has started!', 'success');
    } else {
      setStatus('Connected, but device response timed out. Ensure the Bipkin is booted up to the egg screen.', 'warning');
    }

  } catch (err) {
    if (err.name === 'NotFoundError') {
      setStatus('Port selection was cancelled.', 'normal');
    } else {
      setStatus('Connection error: ' + (err.message || 'Port unavailable') + '. Ensure other serial apps or monitors are closed.', 'error');
    }
  } finally {
    if (writer) { try { writer.releaseLock(); } catch {} }
    if (reader) { try { await reader.cancel(); } catch {} try { reader.releaseLock(); } catch {} }
    if (port) { try { await port.close(); } catch {} }
    btnUsbBridge.disabled = false;
  }
});
