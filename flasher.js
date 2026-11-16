'use strict';
const yearSpan = document.getElementById('year');
if (yearSpan) yearSpan.textContent = new Date().getFullYear();

const select = document.getElementById('deviceSelect');
const flasherBtn = document.getElementById('flasherBtn');
// The release line shows the version only, read from the manifest the install button uses.
// Release notes are not shown on this page; they live in releases/<version>/ and the README.
const releaseLine = document.getElementById('releaseLine');
async function showRelease() {
  if (!releaseLine) return;
  try {
    const res = await fetch(select.value, { cache: 'no-cache' });
    const version = res.ok ? (await res.json()).version : null;
    if (typeof version === 'string' && /^\d+\.\d+\.\d+$/.test(version)) {
      releaseLine.textContent = 'Release: v' + version;
      releaseLine.hidden = false;
      return;
    }
  } catch (e) { /* leave the line hidden rather than show a wrong version */ }
  releaseLine.hidden = true;
}

select.addEventListener('change', () => {
  flasherBtn.setAttribute('manifest', select.value);
  showRelease();
});
showRelease();

// Phones, tablets and browsers without Web Serial: show the "open this on a computer" message with Copy link / Share.
(function showGateIfNeeded() {
  const gate = document.getElementById('flashGate');
  if (!gate || !window.FlashSupport) return;
  const kind = window.FlashSupport.flashSupport(navigator);
  if (kind === 'ok') return;
  const url = location.href.split('#')[0];
  window.FlashSupport.fillGate(gate, kind, url, navigator, document);
  // The install button cannot work here, so it is not offered; the gate is the page's one instruction.
  if (flasherBtn) flasherBtn.hidden = true;
  if (select) select.disabled = true;
})();
