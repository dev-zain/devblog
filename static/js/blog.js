/**
 * Blog JavaScript - Interactions and Enhancements
 */

(function() {
    'use strict';

    // ============================================
    // Like Button Toggle
    // ============================================
    function initLikeButton() {
        // Only select like buttons that have the like URL pattern
        const likeButtons = document.querySelectorAll('a.like-button[href*="/like/"]');
        
        likeButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                
                const url = this.getAttribute('href') || this.dataset.url;
                if (!url || !url.includes('/like/')) return;
                
                // Disable button during request
                const originalHTML = this.innerHTML;
                this.disabled = true;
                this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
                
                // Get CSRF token from cookie or meta tag
                let csrftoken = getCookie('csrftoken');
                if (!csrftoken) {
                    // Try to get from meta tag
                    const metaTag = document.querySelector('meta[name="csrf-token"]');
                    if (metaTag) {
                        csrftoken = metaTag.getAttribute('content');
                    }
                }
                if (!csrftoken) {
                    // Try to get from form
                    const form = document.querySelector('form');
                    if (form) {
                        const csrfInput = form.querySelector('input[name="csrfmiddlewaretoken"]');
                        if (csrfInput) {
                            csrftoken = csrfInput.value;
                        }
                    }
                }
                
                if (!csrftoken) {
                    console.error('CSRF token not found');
                    this.innerHTML = originalHTML;
                    this.disabled = false;
                    alert('Security token missing. Please refresh the page.');
                    return;
                }
                
                // Send AJAX request
                fetch(url + '?ajax=1', {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrftoken,
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    credentials: 'same-origin'
                })
                .then(response => {
                    // Check if response is JSON
                    const contentType = response.headers.get('content-type');
                    if (!contentType || !contentType.includes('application/json')) {
                        // If not JSON, it's probably an HTML error page (e.g., login redirect)
                        if (response.status === 401 || response.status === 403) {
                            throw new Error('Please log in to like posts.');
                        }
                        throw new Error('Server returned an error page. Please refresh and try again.');
                    }
                    if (!response.ok) {
                        return response.json().then(data => {
                            throw new Error(data.error || 'Server error');
                        });
                    }
                    return response.json();
                })
                .then(data => {
                    // Update button state
                    if (data.liked) {
                        this.classList.add('liked');
                        this.innerHTML = '<i class="fas fa-heart"></i> Liked (' + data.like_count + ')';
                    } else {
                        this.classList.remove('liked');
                        this.innerHTML = '<i class="far fa-heart"></i> Like (' + data.like_count + ')';
                    }
                    
                    // Update like count in other places
                    const likeCountElements = document.querySelectorAll('.like-count');
                    likeCountElements.forEach(el => {
                        el.textContent = '(' + data.like_count + ')';
                    });
                })
                .catch(error => {
                    console.error('Error:', error);
                    this.innerHTML = originalHTML;
                    alert('Failed to update like: ' + error.message);
                })
                .finally(() => {
                    this.disabled = false;
                });
            });
        });
    }

    // ============================================
    // Scroll Reveal Animation
    // ============================================
    function initScrollReveal() {
        if (!('IntersectionObserver' in window)) {
            // Fallback: show all elements
            document.querySelectorAll('.reveal').forEach(el => {
                el.classList.add('visible');
            });
            return;
        }

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    observer.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        });

        document.querySelectorAll('.reveal').forEach(el => {
            observer.observe(el);
        });
    }

    // ============================================
    // Search Highlight
    // ============================================
    function highlightSearchTerms() {
        const urlParams = new URLSearchParams(window.location.search);
        const query = urlParams.get('q');
        
        if (!query) return;
        
        const searchResults = document.querySelector('.search-results');
        if (!searchResults) return;
        
        const terms = query.trim().split(/\s+/);
        const walker = document.createTreeWalker(
            searchResults,
            NodeFilter.SHOW_TEXT,
            null,
            false
        );
        
        const textNodes = [];
        let node;
        while (node = walker.nextNode()) {
            if (node.parentElement.tagName !== 'SCRIPT' && 
                node.parentElement.tagName !== 'STYLE') {
                textNodes.push(node);
            }
        }
        
        textNodes.forEach(textNode => {
            let text = textNode.textContent;
            let highlighted = false;
            
            terms.forEach(term => {
                const regex = new RegExp(`(${term})`, 'gi');
                if (regex.test(text)) {
                    text = text.replace(regex, '<span class="search-highlight">$1</span>');
                    highlighted = true;
                }
            });
            
            if (highlighted) {
                const wrapper = document.createElement('span');
                wrapper.innerHTML = text;
                textNode.parentNode.replaceChild(wrapper, textNode);
            }
        });
    }

    // ============================================
    // Quill Editor Initialization
    // ============================================
    function initQuillEditor() {
        const quillEditor = document.querySelector('.quill-editor');
        if (!quillEditor) return;
        
        // Check if Quill is loaded
        if (typeof Quill === 'undefined') {
            console.warn('Quill.js not loaded. Rich text editor will not be available.');
            return;
        }
        
        // Initialize Quill
        const quill = new Quill('.quill-editor', {
            theme: 'snow',
            modules: {
                toolbar: [
                    [{ 'header': [1, 2, 3, false] }],
                    ['bold', 'italic', 'underline', 'strike'],
                    ['blockquote', 'code-block'],
                    [{ 'list': 'ordered'}, { 'list': 'bullet' }],
                    ['link', 'image'],
                    ['clean']
                ]
            },
            placeholder: 'Write your post content here...'
        });
        
        // Sync Quill content with textarea
        const textarea = quillEditor;
        if (textarea.value) {
            quill.root.innerHTML = textarea.value;
        }
        
        // Update textarea on content change
        quill.on('text-change', function() {
            textarea.value = quill.root.innerHTML;
        });
        
        // Store quill instance for form submission
        window.quillInstance = quill;
    }

    // ============================================
    // Tag Selector Enhancement
    // ============================================
    function initTagSelector() {
        const tagSelect = document.querySelector('select[name="tags"]');
        if (!tagSelect) return;
        
        // Add max selection limit
        tagSelect.addEventListener('change', function() {
            if (this.selectedOptions.length > 4) {
                alert('You can select a maximum of 4 tags.');
                // Remove the last selected option
                this.selectedOptions[this.selectedOptions.length - 1].selected = false;
            }
        });
    }

    // ============================================
    // Utility Functions
    // ============================================
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // ============================================
    // Initialize Everything
    // ============================================
    function init() {
        initLikeButton();
        initScrollReveal();
        highlightSearchTerms();
        initQuillEditor();
        initTagSelector();
    }

    // Run when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();

