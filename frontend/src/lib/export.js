// src/lib/export.js
import React from 'react';
import { createRoot } from 'react-dom/client';
import { ExportView } from '../print/ExportView.jsx';

/**
 * Clean, structured print-to-PDF export for the current chat.
 * Renders a minimal print DOM, prints, then cleans up.
 */
export async function exportToPDF({ chatId, messages, title }) {
  if (!Array.isArray(messages) || messages.length === 0) {
    console.warn('[exportToPDF] No messages to export');
  }

  // Create / reuse print root
  let root = document.getElementById('print-root');
  if (!root) {
    root = document.createElement('div');
    root.id = 'print-root';
    document.body.appendChild(root);
  }
  root.setAttribute('data-print', '1');

  // Mount print tree (NO JSX here)
  const appRoot = createRoot(root);
  appRoot.render(
    React.createElement(ExportView, { chatId, title, messages })
  );

  await new Promise((r) => requestAnimationFrame(r));
  window.print();

  const cleanup = () => {
    try {
      appRoot.unmount();
      root.removeAttribute('data-print');
    } catch {}
    window.removeEventListener('afterprint', cleanup);
  };
  window.addEventListener('afterprint', cleanup);
  setTimeout(cleanup, 4000);
}
