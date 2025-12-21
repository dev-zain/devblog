/**
 * Post List Page JavaScript
 * Handles search functionality, filtering, and animations
 */

(function() {
    'use strict';

    // ============================================
    // DOM Elements
    // ============================================
    const searchForm = document.getElementById('searchForm');
    const searchInput = document.getElementById('searchInput');
    const postsGrid = document.getElementById('postsGrid');
    const noResults = document.getElementById('noResults');
    const postCards = document.querySelectorAll('.post-card');

    // ============================================
    // Search Functionality
    // ============================================
    function initSearch() {
        if (!searchInput || !postsGrid) return;

        let searchTimeout;

        // Real-time search as user types
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const query = this.value.trim().toLowerCase();

            searchTimeout = setTimeout(() => {
                filterPosts(query);
            }, 300); // Debounce for 300ms
        });

        // Handle form submission
        if (searchForm) {
            searchForm.addEventListener('submit', function(e) {
                e.preventDefault();
                const query = searchInput.value.trim().toLowerCase();
                filterPosts(query);
            });
        }
    }

    // ============================================
    // Filter Posts
    // ============================================
    function filterPosts(query) {
        if (!postsGrid || !postCards.length) return;

        let visibleCount = 0;

        postCards.forEach(card => {
            const title = card.getAttribute('data-post-title') || '';
            const content = card.getAttribute('data-post-content') || '';
            
            const matches = !query || 
                title.includes(query) || 
                content.includes(query);

            if (matches) {
                card.classList.remove('hidden');
                visibleCount++;
                
                // Add animation
                card.style.animation = 'fadeInUp 0.4s ease';
            } else {
                card.classList.add('hidden');
            }
        });

        // Show/hide no results message
        if (noResults) {
            if (visibleCount === 0 && query) {
                noResults.style.display = 'block';
                noResults.style.animation = 'fadeIn 0.4s ease';
            } else {
                noResults.style.display = 'none';
            }
        }

        // Update URL without reload (optional)
        if (query) {
            const url = new URL(window.location);
            url.searchParams.set('q', query);
            window.history.pushState({}, '', url);
        } else {
            const url = new URL(window.location);
            url.searchParams.delete('q');
            window.history.pushState({}, '', url);
        }
    }

    // ============================================
    // Clear Search
    // ============================================
    window.clearSearch = function() {
        if (searchInput) {
            searchInput.value = '';
            searchInput.focus();
            filterPosts('');
        }
    };

    // ============================================
    // Load Search Query from URL
    // ============================================
    function loadSearchFromURL() {
        if (!searchInput) return;

        const urlParams = new URLSearchParams(window.location.search);
        const query = urlParams.get('q');

        if (query) {
            searchInput.value = query;
            filterPosts(query);
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
        } else {
            // Fallback for browsers without IntersectionObserver
            document.querySelectorAll('.reveal').forEach(el => {
                el.classList.add('revealed');
            });
        }
    }

    // ============================================
    // Image Lazy Loading
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
            }, {
                rootMargin: '50px'
            });

            document.querySelectorAll('img[data-src]').forEach(img => {
                imageObserver.observe(img);
            });
        }
    }

    // ============================================
    // Card Hover Effects
    // ============================================
    function initCardEffects() {
        postCards.forEach(card => {
            card.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-8px)';
            });

            card.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0)';
            });
        });
    }

    // ============================================
    // Keyboard Shortcuts
    // ============================================
    function initKeyboardShortcuts() {
        document.addEventListener('keydown', function(e) {
            // Don't trigger if user is typing in an input
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
                // Allow '/' to focus search even when in input
                if (e.key === '/' && e.target !== searchInput) {
                    e.preventDefault();
                    if (searchInput) {
                        searchInput.focus();
                        searchInput.select();
                    }
                }
                return;
            }

            // Press 'Escape' to clear search
            if (e.key === 'Escape' && searchInput && searchInput.value) {
                clearSearch();
            }
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
                    const navbar = document.getElementById('mainNavbar');
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
    // Initialize Everything
    // ============================================
    function init() {
        initSearch();
        loadSearchFromURL();
        initRevealAnimation();
        initLazyLoading();
        initCardEffects();
        initKeyboardShortcuts();
        initSmoothScroll();
    }

    // Run when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Add CSS animations
    const style = document.createElement('style');
    style.textContent = `
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes fadeIn {
            from {
                opacity: 0;
            }
            to {
                opacity: 1;
            }
        }

        .post-card {
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
    `;
    document.head.appendChild(style);

})();
