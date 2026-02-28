/* ========================================
   MEDICAL AI PLATFORM - BASE JAVASCRIPT
   Interactive features and animations
   ======================================== */

// ========================================
// COUNTER ANIMATIONS
// ========================================

/**
 * Animate numbers from 0 to target value
 * Used for statistics cards
 */
function animateCounter(element, start, end, duration) {
    if (!element) return;
    
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        const value = Math.floor(progress * (end - start) + start);
        element.textContent = value;
        
        if (progress < 1) {
            window.requestAnimationFrame(step);
        } else {
            element.textContent = end;
        }
    };
    window.requestAnimationFrame(step);
}

/**
 * Initialize all counters on page
 */
function initCounters() {
    const counters = document.querySelectorAll('[data-counter]');
    counters.forEach(counter => {
        const target = parseInt(counter.getAttribute('data-counter'));
        const duration = parseInt(counter.getAttribute('data-duration')) || 2000;
        animateCounter(counter, 0, target, duration);
    });
}

// ========================================
// PROGRESS BARS
// ========================================

/**
 * Animate progress bar to target percentage
 */
function animateProgressBar(bar, targetPercent, duration = 1500) {
    if (!bar) return;
    
    bar.style.transition = `width ${duration}ms cubic-bezier(0.4, 0, 0.2, 1)`;
    setTimeout(() => {
        bar.style.width = targetPercent + '%';
    }, 50);
}

// ========================================
// CARD ANIMATIONS
// ========================================

/**
 * Fade in cards with staggered animation
 */
function animateCards() {
    const cards = document.querySelectorAll('.card, .stat-card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        
        setTimeout(() => {
            card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
}

// ========================================
// MEDICAL NOTIFICATIONS
// ========================================

/**
 * Show toast notification
 */
function showToast(message, type = 'info', duration = 5000) {
    const toast = document.createElement('div');
    toast.className = `medical-toast toast-${type}`;
    
    const icons = {
        success: '✓',
        error: '⚠',
        warning: '⚡',
        info: 'ℹ️'
    };
    
    toast.innerHTML = `
        <span class="toast-icon">${icons[type]}</span>
        <span class="toast-message">${message}</span>
        <button class="toast-close" onclick="this.parentElement.remove()">×</button>
    `;
    
    // Add toast styles if not already present
    if (!document.getElementById('toast-styles')) {
        const style = document.createElement('style');
        style.id = 'toast-styles';
        style.textContent = `
            .medical-toast {
                position: fixed;
                top: 90px;
                right: 20px;
                background: white;
                padding: 16px 20px;
                border-radius: 12px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
                display: flex;
                align-items: center;
                gap: 12px;
                z-index: 10000;
                animation: slideInRight 0.3s ease;
                max-width: 400px;
                border-left: 4px solid;
            }
            
            .toast-success { border-color: #10b981; }
            .toast-error { border-color: #ef4444; }
            .toast-warning { border-color: #f59e0b; }
            .toast-info { border-color: #3b82f6; }
            
            .toast-icon {
                font-size: 20px;
                flex-shrink: 0;
            }
            
            .toast-message {
                flex: 1;
                font-size: 14px;
                font-weight: 600;
                color: #1e293b;
            }
            
            .toast-close {
                background: none;
                border: none;
                font-size: 24px;
                cursor: pointer;
                color: #64748b;
                padding: 0;
                width: 24px;
                height: 24px;
                display: flex;
                align-items: center;
                justify-content: center;
                border-radius: 4px;
            }
            
            .toast-close:hover {
                background: #f1f5f9;
            }
            
            @keyframes slideInRight {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
            
            @keyframes slideOutRight {
                from {
                    transform: translateX(0);
                    opacity: 1;
                }
                to {
                    transform: translateX(100%);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(style);
    }
    
    document.body.appendChild(toast);
    
    // Auto dismiss
    if (duration > 0) {
        setTimeout(() => {
            toast.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }, duration);
    }
}

// ========================================
// MEDICAL LOADING OVERLAY
// ========================================

/**
 * Show full-screen loading overlay
 */
function showLoadingOverlay(message = 'Analyzing...') {
    let overlay = document.getElementById('medical-loading-overlay');
    
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.id = 'medical-loading-overlay';
        overlay.innerHTML = `
            <div class="loading-content">
                <div class="spinner"></div>
                <div class="loading-text">${message}</div>
                <div class="ekg-line">
                    <svg viewBox="0 0 200 60">
                        <polyline class="ekg-path" 
                            points="0,30 20,30 25,10 30,50 35,30 50,30 55,20 60,40 65,30 200,30" />
                    </svg>
                </div>
            </div>
        `;
        document.body.appendChild(overlay);
    }
    
    overlay.style.display = 'flex';
}

/**
 * Hide loading overlay
 */
function hideLoadingOverlay() {
    const overlay = document.getElementById('medical-loading-overlay');
    if (overlay) {
        overlay.style.display = 'none';
    }
}

// ========================================
// IMAGE ZOOM VIEWER
// ========================================

/**
 * Create zoomable image viewer
 */
function createImageZoomViewer(imageUrl, altText = 'Medical Image') {
    const viewer = document.createElement('div');
    viewer.className = 'image-zoom-viewer';
    viewer.innerHTML = `
        <div class="zoom-overlay" onclick="this.parentElement.remove()"></div>
        <div class="zoom-container">
            <button class="zoom-close" onclick="this.parentElement.parentElement.remove()">×</button>
            <img src="${imageUrl}" alt="${altText}" class="zoom-image">
            <div class="zoom-controls">
                <button class="zoom-btn" onclick="zoomIn(this)">+</button>
                <button class="zoom-btn" onclick="zoomOut(this)">−</button>
                <button class="zoom-btn" onclick="resetZoom(this)">⟲</button>
            </div>
        </div>
    `;
    
    // Add viewer styles
    if (!document.getElementById('zoom-viewer-styles')) {
        const style = document.createElement('style');
        style.id = 'zoom-viewer-styles';
        style.textContent = `
            .image-zoom-viewer {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                z-index: 10000;
                display: flex;
                align-items: center;
                justify-content: center;
                animation: fadeIn 0.3s ease;
            }
            
            .zoom-overlay {
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0, 0, 0, 0.95);
                backdrop-filter: blur(10px);
            }
            
            .zoom-container {
                position: relative;
                max-width: 90vw;
                max-height: 90vh;
                z-index: 1;
            }
            
            .zoom-image {
                max-width: 100%;
                max-height: 90vh;
                object-fit: contain;
                border-radius: 16px;
                transition: transform 0.3s ease;
                cursor: move;
            }
            
            .zoom-close {
                position: absolute;
                top: -50px;
                right: 0;
                background: white;
                border: none;
                width: 40px;
                height: 40px;
                border-radius: 50%;
                font-size: 24px;
                cursor: pointer;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            }
            
            .zoom-controls {
                position: absolute;
                bottom: -60px;
                left: 50%;
                transform: translateX(-50%);
                display: flex;
                gap: 10px;
            }
            
            .zoom-btn {
                background: white;
                border: none;
                width: 40px;
                height: 40px;
                border-radius: 50%;
                font-size: 20px;
                cursor: pointer;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
                font-weight: bold;
            }
        `;
        document.head.appendChild(style);
    }
    
    document.body.appendChild(viewer);
    
    // Add zoom functionality
    let scale = 1;
    const img = viewer.querySelector('.zoom-image');
    
    window.zoomIn = (btn) => {
        scale = Math.min(scale + 0.2, 3);
        img.style.transform = `scale(${scale})`;
    };
    
    window.zoomOut = (btn) => {
        scale = Math.max(scale - 0.2, 0.5);
        img.style.transform = `scale(${scale})`;
    };
    
    window.resetZoom = (btn) => {
        scale = 1;
        img.style.transform = `scale(${scale})`;
    };
}

// ========================================
// SMOOTH SCROLLING
// ========================================

/**
 * Enable smooth scrolling for anchor links
 */
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href === '#') return;
            
            e.preventDefault();
            const target = document.querySelector(href);
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// ========================================
// AUTO-DISMISS MESSAGES
// ========================================

/**
 * Auto-dismiss alert messages
 */
function initAutoDismissMessages() {
    const messages = document.querySelectorAll('.message.active, .alert-box');
    messages.forEach(message => {
        setTimeout(() => {
            message.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
            message.style.opacity = '0';
            message.style.transform = 'translateX(100%)';
            setTimeout(() => message.remove(), 300);
        }, 5000);
    });
}

// ========================================
// COPY TO CLIPBOARD
// ========================================

/**
 * Copy text to clipboard with feedback
 */
function copyToClipboard(text, button) {
    navigator.clipboard.writeText(text).then(() => {
        const originalText = button.textContent;
        button.textContent = '✓ Copied!';
        button.style.background = '#10b981';
        button.style.color = 'white';
        
        setTimeout(() => {
            button.textContent = originalText;
            button.style.background = '';
            button.style.color = '';
        }, 2000);
    }).catch(err => {
        showToast('Failed to copy to clipboard', 'error');
    });
}

// ========================================
// CONFIRM DIALOG
// ========================================

/**
 * Show styled confirmation dialog
 */
function confirmDialog(message, onConfirm, onCancel) {
    const dialog = document.createElement('div');
    dialog.className = 'medical-confirm-dialog';
    dialog.innerHTML = `
        <div class="confirm-overlay"></div>
        <div class="confirm-box">
            <div class="confirm-icon">⚠️</div>
            <div class="confirm-message">${message}</div>
            <div class="confirm-buttons">
                <button class="btn btn-secondary confirm-cancel">Cancel</button>
                <button class="btn btn-danger confirm-ok">Confirm</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(dialog);
    
    const removeDialog = () => {
        dialog.style.opacity = '0';
        setTimeout(() => dialog.remove(), 300);
    };
    
    dialog.querySelector('.confirm-cancel').onclick = () => {
        removeDialog();
        if (onCancel) onCancel();
    };
    
    dialog.querySelector('.confirm-ok').onclick = () => {
        removeDialog();
        if (onConfirm) onConfirm();
    };
    
    dialog.querySelector('.confirm-overlay').onclick = () => {
        removeDialog();
        if (onCancel) onCancel();
    };
}

// ========================================
// INITIALIZATION
// ========================================

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize counters
    initCounters();
    
    // Animate cards
    animateCards();
    
    // Initialize smooth scrolling
    initSmoothScroll();
    
    // Auto-dismiss messages
    initAutoDismissMessages();
    
    console.log('🫁 PneumoAI Medical Platform Loaded');
});

// Log initialization
console.log('Medical Base JavaScript loaded');
