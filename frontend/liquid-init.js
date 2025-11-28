import React, { useEffect, useState } from 'https://esm.sh/react@18.3.1';
import { createRoot } from 'https://esm.sh/react-dom@18.3.1/client';
import LiquidGlass from 'https://esm.sh/liquid-glass-react@1.1.1?deps=react@18.3.1,react-dom@18.3.1';

function mountAfter(el) {
  const m = document.createElement('div');
  el.insertAdjacentElement('afterend', m);
  return m;
}

function GlassButton({ html, onClick }) {
  const [pos, setPos] = useState({ x: 0, y: 0 });
  useEffect(() => {
    const onMove = (e) => setPos({ x: e.clientX, y: e.clientY });
    window.addEventListener('mousemove', onMove);
    return () => window.removeEventListener('mousemove', onMove);
  }, []);
  return React.createElement(
    LiquidGlass,
    {
      displacementScale: 64,
      blurAmount: 0.1,
      saturation: 130,
      aberrationIntensity: 2,
      elasticity: 0.35,
      cornerRadius: 100,
      padding: '8px 16px',
      mode: 'shader',
      globalMousePos: pos,
      onClick,
      style: { display: 'inline-block' }
    },
    React.createElement('span', { className: 'text-white fw-medium', dangerouslySetInnerHTML: { __html: html } })
  );
}

function wrapButton(el) {
  const isSubmit = el.type === 'submit';
  const handler = el.onclick;
  const mount = mountAfter(el);
  const root = createRoot(mount);
  el.style.display = 'none';
  const onClick = () => {
    if (isSubmit) {
      const form = el.closest('form');
      if (form) form.requestSubmit();
    } else if (typeof handler === 'function') {
      handler.call(el);
    } else {
      el.dispatchEvent(new MouseEvent('click', { bubbles: true }));
    }
  };
  root.render(React.createElement(GlassButton, { html: el.innerHTML, onClick }));
}

function GlassNavLink({ html, onClick }) {
  const [pos, setPos] = useState({ x: 0, y: 0 });
  useEffect(() => {
    const onMove = (e) => setPos({ x: e.clientX, y: e.clientY });
    window.addEventListener('mousemove', onMove);
    return () => window.removeEventListener('mousemove', onMove);
  }, []);
  return React.createElement(
    LiquidGlass,
    {
      displacementScale: 56,
      blurAmount: 0.09,
      saturation: 140,
      aberrationIntensity: 1.8,
      elasticity: 0.28,
      cornerRadius: 16,
      padding: '8px 12px',
      mode: 'prominent',
      globalMousePos: pos,
      className: 'nav-glass d-block w-100',
      onClick
    },
    React.createElement('span', { className: 'text-white', dangerouslySetInnerHTML: { __html: html } })
  );
}

function wrapNavLink(el) {
  const href = el.getAttribute('href');
  const mount = mountAfter(el);
  const root = createRoot(mount);
  el.style.display = 'none';
  const onClick = () => {
    if (href && href !== '#') {
      window.location.href = href;
    } else {
      const handler = el.onclick;
      if (typeof handler === 'function') handler.call(el);
    }
  };
  const isActive = el.classList.contains('active');
  root.render(
    React.createElement(
      GlassNavLink,
      { html: el.innerHTML + (isActive ? '<span class="visually-hidden"> (current)</span>' : ''), onClick },
      null
    )
  );
}

function GlassSection({ headerHtml, bodyHtml, className }) {
  const [pos, setPos] = useState({ x: 0, y: 0 });
  const [offset, setOffset] = useState({ x: 0, y: 0 });
  const [hover, setHover] = useState(false);
  const wrapRef = React.useRef(null);
  useEffect(() => {
    const onMove = (e) => setPos({ x: e.clientX, y: e.clientY });
    window.addEventListener('mousemove', onMove);
    return () => window.removeEventListener('mousemove', onMove);
  }, []);
  useEffect(() => {
    const update = () => {
      if (wrapRef.current) {
        const r = wrapRef.current.getBoundingClientRect();
        setOffset({ x: -r.left, y: -r.top });
      }
    };
    update();
    window.addEventListener('resize', update);
    return () => window.removeEventListener('resize', update);
  }, []);
  return React.createElement(
    'div',
    { ref: wrapRef, className, onMouseEnter: () => setHover(true), onMouseLeave: () => setHover(false) },
    headerHtml ? React.createElement('div', { className: 'glass-header', dangerouslySetInnerHTML: { __html: headerHtml } }) : null,
    React.createElement(
      LiquidGlass,
      {
        displacementScale: hover ? 82 : 62,
        blurAmount: hover ? 0.09 : 0.065,
        saturation: 140,
        aberrationIntensity: hover ? 2.2 : 1.6,
        elasticity: 0.25,
        cornerRadius: 20,
        padding: '0',
        mode: 'prominent',
        globalMousePos: pos,
        mouseOffset: offset,
        className: 'w-100'
      },
      React.createElement('div', { className: 'glass-body', dangerouslySetInnerHTML: { __html: bodyHtml || '' } })
    )
  );
}

function wrapSection(el) {
  const headerEl = el.querySelector('.glass-header');
  const bodyEl = el.querySelector('.glass-body');
  const headerHtml = headerEl ? headerEl.innerHTML : null;
  const bodyHtml = bodyEl ? bodyEl.innerHTML : el.innerHTML;
  const mount = document.createElement('div');
  mount.style.width = '100%';
  el.replaceWith(mount);
  const root = createRoot(mount);
  root.render(React.createElement(GlassSection, { headerHtml, bodyHtml, className: el.className }));
}

function init() {
  document.querySelectorAll('button.btn, a.btn').forEach(wrapButton);
  document.querySelectorAll('a.nav-link').forEach(wrapNavLink);
  document.querySelectorAll('.glass-card, .glass-section').forEach(wrapSection);
  setupStudentRowGlass();
  document.querySelectorAll('.glass-header .form-select, .glass-body .form-select, .glass-card .form-select, .glass-section .form-select').forEach(wrapSelect);
}

window.addEventListener('DOMContentLoaded', init);

function RowGlass({ visible, width, height, pos, cornerRadius = 12 }) {
  const [mouse, setMouse] = useState({ x: 0, y: 0 });
  useEffect(() => {
    const onMove = (e) => setMouse({ x: e.clientX, y: e.clientY });
    window.addEventListener('mousemove', onMove);
    return () => window.removeEventListener('mousemove', onMove);
  }, []);
  return React.createElement(
    'div',
    { style: { width: width + 'px', height: height + 'px', pointerEvents: 'none' } },
    visible && React.createElement(
      LiquidGlass,
      {
        displacementScale: 68,
        blurAmount: 0.08,
        saturation: 140,
        aberrationIntensity: 1.9,
        elasticity: 0.22,
        cornerRadius,
        padding: '0',
        mode: 'prominent',
        globalMousePos: mouse,
        mouseOffset: pos,
        className: 'w-100',
        overLight: false
      },
      React.createElement('div', { style: { width: '100%', height: '100%' } })
    )
  );
}

function setupStudentRowGlass() {
  const tbody = document.getElementById('student-tbody');
  if (!tbody) return;
  const wrap = tbody.closest('.table-responsive') || tbody.parentElement;
  if (!wrap) return;
  wrap.style.position = 'relative';

  let overlayContainer = wrap.querySelector('.row-glass-overlay');
  if (!overlayContainer) {
    overlayContainer = document.createElement('div');
    overlayContainer.className = 'row-glass-overlay';
    overlayContainer.style.position = 'absolute';
    overlayContainer.style.left = '0';
    overlayContainer.style.top = '0';
    overlayContainer.style.width = '100%';
    overlayContainer.style.height = wrap.offsetHeight + 'px';
    overlayContainer.style.pointerEvents = 'none';
    overlayContainer.style.zIndex = '3';
    wrap.appendChild(overlayContainer);
  }

  const roots = [];
  const rows = Array.from(tbody.querySelectorAll('tr'));
  const wrapRect = wrap.getBoundingClientRect();
  overlayContainer.innerHTML = '';
  rows.forEach((tr) => {
    const r = tr.getBoundingClientRect();
    const holder = document.createElement('div');
    holder.style.position = 'absolute';
    holder.style.left = (r.left - wrapRect.left) + 'px';
    holder.style.top = (r.top - wrapRect.top) + 'px';
    holder.style.width = r.width + 'px';
    holder.style.height = r.height + 'px';
    overlayContainer.appendChild(holder);
    const root = createRoot(holder);
    const pos = { x: -(r.left), y: -(r.top) };
    let visible = false;
    root.render(React.createElement(RowGlass, { visible, width: r.width, height: r.height, pos }));
    roots.push({ tr, root, holder, getRect: () => tr.getBoundingClientRect() });
    tr.addEventListener('mouseenter', () => {
      const rect = tr.getBoundingClientRect();
      holder.style.left = (rect.left - wrapRect.left) + 'px';
      holder.style.top = (rect.top - wrapRect.top) + 'px';
      holder.style.width = rect.width + 'px';
      holder.style.height = rect.height + 'px';
      const posNow = { x: -rect.left, y: -rect.top };
      root.render(React.createElement(RowGlass, { visible: true, width: rect.width, height: rect.height, pos: posNow }));
    });
    tr.addEventListener('mouseleave', () => {
      const rect = tr.getBoundingClientRect();
      const posNow = { x: -rect.left, y: -rect.top };
      root.render(React.createElement(RowGlass, { visible: false, width: rect.width, height: rect.height, pos: posNow }));
    });
  });

  const rebuild = () => setupStudentRowGlass();
  const mo = new MutationObserver(rebuild);
  mo.observe(tbody, { childList: true, subtree: true });
  window.addEventListener('resize', rebuild);
}

function wrapSelect(el) {
  const mount = mountAfter(el);
  const root = createRoot(mount);
  const SelectGlass = () => {
    const [pos, setPos] = useState({ x: 0, y: 0 });
    const [offset, setOffset] = useState({ x: 0, y: 0 });
    const hostRef = React.useRef(null);
    useEffect(() => {
      const onMove = (e) => setPos({ x: e.clientX, y: e.clientY });
      window.addEventListener('mousemove', onMove);
      return () => window.removeEventListener('mousemove', onMove);
    }, []);
    useEffect(() => {
      if (hostRef.current) {
        const r = hostRef.current.getBoundingClientRect();
        setOffset({ x: -r.left, y: -r.top });
      }
    });
    useEffect(() => {
      if (hostRef.current) {
        hostRef.current.appendChild(el);
        el.style.display = '';
        el.style.width = '100%';
      }
    }, []);
    return React.createElement(
      LiquidGlass,
      {
        displacementScale: 56,
        blurAmount: 0.085,
        saturation: 140,
        aberrationIntensity: 1.8,
        elasticity: 0.26,
        cornerRadius: 12,
        padding: '4px 8px',
        mode: 'prominent',
        globalMousePos: pos,
        mouseOffset: offset,
        className: 'd-block w-100'
      },
      React.createElement('div', { ref: hostRef })
    );
  };
  root.render(React.createElement(SelectGlass));
}
