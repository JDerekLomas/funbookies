/**
 * Simple toast notification system
 * Usage: Toast.show('Message') or Toast.error('Error message')
 */
const Toast = (function() {
  let container = null;

  function ensureContainer() {
    if (!container) {
      container = document.createElement('div');
      container.id = 'toast-container';
      container.setAttribute('aria-live', 'polite');
      container.setAttribute('aria-atomic', 'true');
      document.body.appendChild(container);
    }
    return container;
  }

  function show(message, type = 'info', duration = 3000) {
    const container = ensureContainer();

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.setAttribute('role', 'alert');

    const icon = type === 'error' ? '!' :
                 type === 'success' ? '✓' :
                 type === 'warning' ? '⚠' : 'i';

    toast.innerHTML = `
      <span class="toast-icon">${icon}</span>
      <span class="toast-message">${message}</span>
      <button class="toast-close" aria-label="Dismiss">&times;</button>
    `;

    // Close button handler
    toast.querySelector('.toast-close').addEventListener('click', () => {
      dismiss(toast);
    });

    container.appendChild(toast);

    // Trigger animation
    requestAnimationFrame(() => {
      toast.classList.add('toast-visible');
    });

    // Auto-dismiss
    if (duration > 0) {
      setTimeout(() => dismiss(toast), duration);
    }

    return toast;
  }

  function dismiss(toast) {
    toast.classList.remove('toast-visible');
    toast.classList.add('toast-hiding');
    setTimeout(() => toast.remove(), 300);
  }

  return {
    show: (message, duration) => show(message, 'info', duration),
    success: (message, duration) => show(message, 'success', duration),
    warning: (message, duration) => show(message, 'warning', duration),
    error: (message, duration = 5000) => show(message, 'error', duration),
  };
})();

// Export for module systems if needed
if (typeof module !== 'undefined' && module.exports) {
  module.exports = Toast;
}
