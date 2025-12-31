/**
 * DevBlog - Main JavaScript File
 * Handles navigation, UI interactions, and user experience enhancements
 */

(function() {
  'use strict';

    // ============================================
    // DOM Elements
    // ============================================
    const navbar = document.getElementById('mainNavbar');
    const navbarToggle = document.getElementById('navbarToggle');
    const navbarMenu = document.getElementById('navbarMenu');
    const backToTopBtn = document.getElementById('backToTop');
    const dropdowns = document.querySelectorAll('.dropdown');
    const alerts = document.querySelectorAll('.alert');
    const messagesContainer = document.querySelector('.messages-container');

    // ============================================
    // Navbar Scroll Effect (Disabled - navbar is no longer sticky)
    // ============================================
    // Removed - navbar now scrolls normally with the page

    // ============================================
    // Mobile Menu Toggle
    // ============================================
    function initMobileMenu() {
        if (!navbarToggle || !navbarMenu) return;

        navbarToggle.addEventListener('click', function() {
            navbarToggle.classList.toggle('active');
            navbarMenu.classList.toggle('active');
            
            // Prevent body scroll when menu is open
            if (navbarMenu.classList.contains('active')) {
                document.body.style.overflow = 'hidden';
            } else {
                document.body.style.overflow = '';
            }
        });

        // Close menu when clicking outside
        document.addEventListener('click', function(event) {
            if (navbarMenu && navbarToggle) {
                const isClickInsideMenu = navbarMenu.contains(event.target);
                const isClickOnToggle = navbarToggle.contains(event.target);
                
                if (!isClickInsideMenu && !isClickOnToggle && navbarMenu.classList.contains('active')) {
                    navbarMenu.classList.remove('active');
                    navbarToggle.classList.remove('active');
                    document.body.style.overflow = '';
                }
            }
        });

        // Close menu when clicking on a nav link
        const navLinks = navbarMenu.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                // If this is a dropdown-toggle, do NOT close menu
                if (link.classList.contains('dropdown-toggle')) return;
                if (window.innerWidth <= 768) {
                    navbarMenu.classList.remove('active');
                    navbarToggle.classList.remove('active');
                    document.body.style.overflow = '';
                }
            });
        });
    }

    // ============================================
    // Dropdown Menu Handling
    // ============================================
    function initDropdowns() {
        dropdowns.forEach(dropdown => {
            const toggle = dropdown.querySelector('.dropdown-toggle');
            const menu = dropdown.querySelector('.dropdown-menu');
            
            if (!toggle || !menu) return;

            // Desktop: hover
            if (window.innerWidth > 768) {
                dropdown.addEventListener('mouseenter', function() {
                    menu.classList.add('show');
                });
                
                dropdown.addEventListener('mouseleave', function() {
                    menu.classList.remove('show');
                });
            } else {
                // Mobile: click
                toggle.addEventListener('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    
                    // Close other dropdowns
                    dropdowns.forEach(otherDropdown => {
                        if (otherDropdown !== dropdown) {
                            const otherMenu = otherDropdown.querySelector('.dropdown-menu');
                            if (otherMenu) {
                                otherMenu.classList.remove('show');
                            }
                        }
                    });
                    
                    menu.classList.toggle('show');
                });
            }
        });

        // Close dropdowns when clicking outside
        document.addEventListener('click', function(event) {
            dropdowns.forEach(dropdown => {
                const menu = dropdown.querySelector('.dropdown-menu');
                if (menu && !dropdown.contains(event.target)) {
                    menu.classList.remove('show');
                }
            });
        });
    }

    // ============================================
    // Back to Top Button
    // ============================================
    function initBackToTop() {
        if (!backToTopBtn) return;

        function toggleBackToTop() {
            if (window.scrollY > 300) {
                backToTopBtn.classList.add('visible');
            } else {
                backToTopBtn.classList.remove('visible');
            }
        }

        backToTopBtn.addEventListener('click', function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });

        window.addEventListener('scroll', toggleBackToTop, { passive: true });
        toggleBackToTop(); // Check on load
    }

    // ============================================
    // Alert Dismissal
    // ============================================
    function initAlerts() {
        alerts.forEach(alert => {
            const closeBtn = alert.querySelector('.btn-close');
            if (closeBtn) {
                closeBtn.addEventListener('click', function() {
                    alert.style.animation = 'fadeOut 0.3s ease';
                    setTimeout(() => {
                        alert.remove();
                        
                        // Remove messages container if empty
                        if (messagesContainer && messagesContainer.querySelectorAll('.alert').length === 0) {
                            messagesContainer.remove();
                        }
                    }, 300);
                });
            }

            // Auto-dismiss after 5 seconds
            setTimeout(() => {
                if (alert && alert.parentNode) {
                    alert.style.animation = 'fadeOut 0.3s ease';
                    setTimeout(() => {
                        alert.remove();
                        
                        if (messagesContainer && messagesContainer.querySelectorAll('.alert').length === 0) {
                            messagesContainer.remove();
                        }
                    }, 300);
                }
            }, 5000);
        });
    }

    // ============================================
    // Smooth Scroll for Anchor Links
    // ============================================
    function initSmoothScroll() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function(e) {
                const href = this.getAttribute('href');
                if (href === '#' || href === '') return;
                
                const target = document.querySelector(href);
                if (target) {
                    e.preventDefault();
                    const offsetTop = target.offsetTop - (navbar ? navbar.offsetHeight : 0);
                    window.scrollTo({
                        top: offsetTop,
                        behavior: 'smooth'
                    });
                }
            });
        });
    }

    // ============================================
    // Keyboard Shortcuts
    // ============================================
    function initKeyboardShortcuts() {
        // Focus search input with '/' key
        document.addEventListener('keydown', function(e) {
            // Don't trigger if user is typing in an input/textarea
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
                return;
            }

            // Press '/' to focus search
            if (e.key === '/' && !e.ctrlKey && !e.metaKey && !e.altKey) {
                const searchInput = document.querySelector('input[type="search"], input[name="q"]');
                if (searchInput) {
                    e.preventDefault();
                    searchInput.focus();
                    searchInput.select();
                }
            }

            // Press 'Escape' to close mobile menu
            if (e.key === 'Escape') {
                if (navbarMenu && navbarMenu.classList.contains('active')) {
                    navbarMenu.classList.remove('active');
                    if (navbarToggle) {
                        navbarToggle.classList.remove('active');
                    }
                    document.body.style.overflow = '';
                }
            }
        });
    }

    // ============================================
    // Form Enhancements
    // ============================================
    function initFormEnhancements() {
        // Add focus effects to form inputs
        const inputs = document.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('focus', function() {
                this.parentElement?.classList.add('focused');
            });
            
            input.addEventListener('blur', function() {
                this.parentElement?.classList.remove('focused');
            });
        });
    }

    // ============================================
    // Lazy Loading Images
    // ============================================
    function initLazyLoading() {
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        if (img.dataset.src) {
                            img.src = img.dataset.src;
                            img.removeAttribute('data-src');
                            img.classList.add('loaded');
                            observer.unobserve(img);
                        }
                    }
                });
            });

            document.querySelectorAll('img[data-src]').forEach(img => {
                imageObserver.observe(img);
            });
        }
    }

    // ============================================
    // Reveal Animation on Scroll
    // ============================================
    function initRevealAnimation() {
        if ('IntersectionObserver' in window) {
            const revealObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('revealed');
                        revealObserver.unobserve(entry.target);
                    }
                });
            }, {
                threshold: 0.1,
                rootMargin: '0px 0px -50px 0px'
            });

            document.querySelectorAll('.reveal').forEach(el => {
                revealObserver.observe(el);
            });
        }
    }

    // ============================================
    // Window Resize Handler
    // ============================================
    function handleResize() {
        // Close mobile menu on resize to desktop
        if (window.innerWidth > 768) {
            if (navbarMenu) {
                navbarMenu.classList.remove('active');
            }
            if (navbarToggle) {
                navbarToggle.classList.remove('active');
            }
            document.body.style.overflow = '';
        }
    }

    // ============================================
    // Initialize Everything
    // ============================================
    function init() {
        // Core functionality
        initMobileMenu();
        initDropdowns();
        initBackToTop();
        initAlerts();
        initSmoothScroll();
        initKeyboardShortcuts();
        initFormEnhancements();
        initLazyLoading();
        initRevealAnimation();

        // Event listeners
        window.addEventListener('resize', handleResize, { passive: true });

        // Add loaded class to body
        document.body.classList.add('loaded');
    }

    // Run when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Add fade out animation for alerts
    const style = document.createElement('style');
    style.textContent = `
        @keyframes fadeOut {
            from {
                opacity: 1;
                transform: translateX(0);
            }
            to {
                opacity: 0;
                transform: translateX(100%);
            }
        }
        .reveal {
            opacity: 0;
            transform: translateY(20px);
            transition: opacity 0.6s ease, transform 0.6s ease;
        }
        .reveal.revealed {
            opacity: 1;
            transform: translateY(0);
        }
        img.loaded {
            opacity: 1;
            transition: opacity 0.3s ease;
        }
        img[data-src] {
            opacity: 0;
        }
    `;
    document.head.appendChild(style);

})();