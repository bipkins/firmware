'use strict';
// Can this browser flash a board? Web Serial exists only in desktop Chrome, Edge and Opera. Everyone else (phones,
// tablets, Firefox and Safari) gets a message and a link to copy or share, never a button that cannot work.
// Plain script with no imports so the CSP stays `script-src 'self'`; Node can load it for tests.
(function (root) {
  function isMobileLike(nav) {
    if (!nav) return false;
    if (nav.userAgentData && nav.userAgentData.mobile === true) return true;
    if (/Android|iPhone|iPad|iPod|Mobile|Tablet|Silk|Kindle/i.test(String(nav.userAgent || ''))) return true;
    // iPadOS asks for the desktop site and calls itself a Mac, but a Mac has no touch points.
    return nav.platform === 'MacIntel' && Number(nav.maxTouchPoints) > 1;
  }

  // 'ok' = Web Serial is there; 'phone' = phone or tablet without it; 'browser' = a computer whose browser lacks it.
  function flashSupport(nav) {
    if (nav && 'serial' in nav) return 'ok';
    return isMobileLike(nav) ? 'phone' : 'browser';
  }

  var TEXT = {
    phone: {
      title: 'Open this page on a computer with Chrome or Edge',
      body: 'Flashing a board needs a computer with a USB port and Chrome or Edge. Phones and tablets cannot do it. Copy the link, or send it to yourself, and open it there.'
    },
    browser: {
      title: 'Use Chrome or Edge to flash your board',
      body: 'This browser cannot talk to a USB device. Open this page in Chrome or Edge on this computer. Copy the link to paste it there.'
    }
  };

  async function copyText(text, nav, doc) {
    try {
      if (nav && nav.clipboard && nav.clipboard.writeText) { await nav.clipboard.writeText(text); return true; }
    } catch (e) { /* fall through to the older way */ }
    try {
      var box = doc.createElement('textarea');
      box.value = text; box.setAttribute('readonly', ''); box.style.position = 'fixed'; box.style.opacity = '0';
      doc.body.appendChild(box); box.select();
      var done = doc.execCommand('copy');
      box.remove();
      return Boolean(done);
    } catch (e) { return false; }
  }

  // Fills the (initially hidden) container with the message, the link, Copy link and, where it exists, Share.
  function fillGate(container, kind, url, nav, doc) {
    var text = TEXT[kind];
    container.setAttribute('data-flash-gate', kind);
    var heading = doc.createElement('strong'); heading.textContent = text.title;
    var body = doc.createElement('p'); body.textContent = text.body;
    var field = doc.createElement('code'); field.className = 'flash-gate-url'; field.textContent = url;
    var row = doc.createElement('div'); row.className = 'flash-gate-actions';
    var status = doc.createElement('span'); status.className = 'flash-gate-status'; status.setAttribute('role', 'status');
    var copy = doc.createElement('button'); copy.type = 'button'; copy.className = 'btn btn-outline-secondary btn-sm'; copy.textContent = 'Copy link';
    copy.addEventListener('click', async function () {
      status.textContent = (await copyText(url, nav, doc)) ? 'Link copied.' : 'Could not copy. Select the link above and copy it.';
    });
    row.appendChild(copy);
    if (nav && typeof nav.share === 'function') {
      var share = doc.createElement('button'); share.type = 'button'; share.className = 'btn btn-outline-secondary btn-sm'; share.textContent = 'Share';
      share.addEventListener('click', async function () {
        try { await nav.share({ title: 'Bipkins web flasher', text: 'Open this on a computer with Chrome or Edge to set up your Bipkin.', url: url }); }
        catch (e) { if (!e || e.name !== 'AbortError') status.textContent = 'Sharing is not available here. Use Copy link.'; }
      });
      row.appendChild(share);
    }
    container.append(heading, body, field, row, status);
    container.hidden = false;
    return container;
  }

  var api = { isMobileLike: isMobileLike, flashSupport: flashSupport, copyText: copyText, fillGate: fillGate, TEXT: TEXT };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.FlashSupport = api;
})(typeof window !== 'undefined' ? window : this);
