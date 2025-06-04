// AI Health Report - Main JavaScript File

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initializeNavigation();
    initializeScrollEffects();
    initializeFormValidation();
    initializeAnimations();
    initializeTooltips();
});

// Navigation functionality
function initializeNavigation() {
    const navbar = document.querySelector('.navbar');
    
    // Change navbar appearance on scroll
    window.addEventListener('scroll', function() {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });
    
    // Mobile menu handling
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (navbarToggler && navbarCollapse) {
        navbarToggler.addEventListener('click', function() {
            navbarCollapse.classList.toggle('show');
        });
        
        // Close mobile menu when clicking on links
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                navbarCollapse.classList.remove('show');
            });
        });
    }
}

// Scroll effects and animations
function initializeScrollEffects() {
    // Smooth scrolling for anchor links
    const scrollLinks = document.querySelectorAll('a[href^="#"]');
    scrollLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Reveal animations on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    const animateElements = document.querySelectorAll('.feature-card, .pricing-card, .coach-feature');
    animateElements.forEach(el => {
        el.classList.add('animate-ready');
        observer.observe(el);
    });
}

// Form validation and enhancement
function initializeFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        // Custom validation styling
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
                
                // Highlight first invalid field
                const firstInvalid = form.querySelector(':invalid');
                if (firstInvalid) {
                    firstInvalid.focus();
                    firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            }
            
            form.classList.add('was-validated');
        });
        
        // Real-time validation feedback
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                if (this.checkValidity()) {
                    this.classList.remove('is-invalid');
                    this.classList.add('is-valid');
                } else {
                    this.classList.remove('is-valid');
                    this.classList.add('is-invalid');
                }
            });
            
            input.addEventListener('input', function() {
                if (this.classList.contains('is-invalid') && this.checkValidity()) {
                    this.classList.remove('is-invalid');
                    this.classList.add('is-valid');
                }
            });
        });
    });
    
    // Auto-resize textareas
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
        // Set initial height
        autoResizeTextarea(textarea);
        
        // Resize on input
        textarea.addEventListener('input', function() {
            autoResizeTextarea(this);
        });
    });
}

function autoResizeTextarea(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = Math.max(textarea.scrollHeight, 100) + 'px';
}

// Initialize animations
function initializeAnimations() {
    // Add CSS for animations
    const style = document.createElement('style');
    style.textContent = `
        .animate-ready {
            opacity: 0;
            transform: translateY(30px);
            transition: all 0.6s ease;
        }
        
        .animate-in {
            opacity: 1;
            transform: translateY(0);
        }
        
        .navbar.scrolled {
            background: rgba(59, 130, 246, 0.98) !important;
            backdrop-filter: blur(20px);
            box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
        }
        
        .btn {
            position: relative;
            overflow: hidden;
        }
        
        .btn::before {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 0;
            height: 0;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 50%;
            transform: translate(-50%, -50%);
            transition: width 0.6s, height 0.6s;
        }
        
        .btn:hover::before {
            width: 300px;
            height: 300px;
        }
        
        .health-card {
            animation: float 6s ease-in-out infinite;
        }
        
        @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-20px); }
        }
        
        .feature-card:hover .feature-icon {
            transform: scale(1.1) rotate(5deg);
        }
        
        .feature-icon {
            transition: all 0.3s ease;
        }
    `;
    document.head.appendChild(style);
}

// Initialize tooltips and popovers
function initializeTooltips() {
    // Initialize Bootstrap tooltips if available
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
}

// Utility functions
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show notification-toast`;
    notification.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
        animation: slideIn 0.3s ease;
    `;
    
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            showNotification('Ссылка скопирована в буфер обмена!', 'success');
        }).catch(() => {
            fallbackCopyToClipboard(text);
        });
    } else {
        fallbackCopyToClipboard(text);
    }
}

function fallbackCopyToClipboard(text) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.top = '0';
    textArea.style.left = '0';
    textArea.style.width = '2em';
    textArea.style.height = '2em';
    textArea.style.padding = '0';
    textArea.style.border = 'none';
    textArea.style.outline = 'none';
    textArea.style.boxShadow = 'none';
    textArea.style.background = 'transparent';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        const successful = document.execCommand('copy');
        if (successful) {
            showNotification('Ссылка скопирована в буфер обмена!', 'success');
        }
    } catch (err) {
        showNotification('Не удалось скопировать ссылку', 'error');
    }
    
    document.body.removeChild(textArea);
}

// Form progress tracking
function trackFormProgress() {
    const form = document.querySelector('.questionnaire-form');
    if (!form) return;
    
    const requiredFields = form.querySelectorAll('[required]');
    const progressBar = document.createElement('div');
    progressBar.className = 'progress mb-4';
    progressBar.innerHTML = '<div class="progress-bar bg-success" role="progressbar"></div>';
    
    const formHeader = document.querySelector('.questionnaire-header');
    if (formHeader) {
        formHeader.appendChild(progressBar);
    }
    
    function updateProgress() {
        const filledFields = Array.from(requiredFields).filter(field => {
            if (field.type === 'checkbox' || field.type === 'radio') {
                return field.checked;
            }
            return field.value.trim() !== '';
        });
        
        const progress = (filledFields.length / requiredFields.length) * 100;
        const progressBarFill = progressBar.querySelector('.progress-bar');
        progressBarFill.style.width = progress + '%';
        progressBarFill.textContent = Math.round(progress) + '%';
    }
    
    requiredFields.forEach(field => {
        field.addEventListener('input', updateProgress);
        field.addEventListener('change', updateProgress);
    });
    
    updateProgress(); // Initial call
}

// Initialize form progress tracking
document.addEventListener('DOMContentLoaded', trackFormProgress);

// Loading state management
function setLoadingState(element, isLoading = true) {
    if (isLoading) {
        element.disabled = true;
        const originalText = element.textContent;
        element.dataset.originalText = originalText;
        element.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Загрузка...';
    } else {
        element.disabled = false;
        element.textContent = element.dataset.originalText || 'Готово';
    }
}

// Error handling
window.addEventListener('error', function(e) {
    console.error('JavaScript Error:', e.error);
    // In production, you might want to send this to a logging service
});
