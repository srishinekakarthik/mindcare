// Sample notifications data
        let notifications = [
            {
                id: 1,
                type: 'info',
                title: 'Welcome to MindCare!',
                message: 'Your mental health platform is ready to support you.',
                time: '5 minutes ago',
                read: false
            },
            {
                id: 2,
                type: 'success',
                title: 'Session Scheduled',
                message: 'Your counseling session is confirmed for tomorrow at 2:00 PM.',
                time: '1 hour ago',
                read: false
            },
            {
                id: 3,
                type: 'warning',
                title: 'Daily Check-in Reminder',
                message: 'Don\'t forget to complete your daily wellness check-in.',
                time: '3 hours ago',
                read: false
            },
            {
                id: 4,
                type: 'info',
                title: 'New Resource Available',
                message: 'Check out our new meditation guide in the Resources section.',
                time: '1 day ago',
                read: true
            }
        ];

        // Check user role and show/hide admin features
        function checkUserRole() {
            try {
                const userData = localStorage.getItem('user');
                if (userData) {
                    const user = JSON.parse(userData);
                    const analyticsMenuItem = document.getElementById('analyticsMenuItem');
                    
                    if (user.role === 'admin' && analyticsMenuItem) {
                        analyticsMenuItem.style.display = 'block';
                        console.log('Admin user detected - Analytics menu item shown');
                    } else if (analyticsMenuItem) {
                        analyticsMenuItem.style.display = 'none';
                        console.log('Student user detected - Analytics menu item hidden');
                    }
                } else {
                    // No user data found, hide analytics
                    const analyticsMenuItem = document.getElementById('analyticsMenuItem');
                    if (analyticsMenuItem) {
                        analyticsMenuItem.style.display = 'none';
                        console.log('No user data found - Analytics menu item hidden');
                    }
                }
            } catch (error) {
                console.error('Error checking user role:', error);
                // Hide analytics on error
                const analyticsMenuItem = document.getElementById('analyticsMenuItem');
                if (analyticsMenuItem) {
                    analyticsMenuItem.style.display = 'none';
                }
            }
        }

        // Navigation functionality
        document.addEventListener('DOMContentLoaded', function() {
            // Initialize notifications
            initializeNotifications();
            
            // Check user role and show/hide admin features
            checkUserRole();
            
            // Add click event listeners to navigation links
            const navLinks = document.querySelectorAll('.nav-link');
            navLinks.forEach(link => {
                link.addEventListener('click', function(e) {
                    const href = this.getAttribute('href');
                    const page = this.getAttribute('data-page');
                    
                    // Allow direct navigation for analytics and other direct links
                    if (href && href !== '#' && (href.startsWith('/') || href.startsWith('http'))) {
                        // Let the browser handle the navigation
                        return;
                    }
                    
                    // Prevent default for data-page navigation
                    e.preventDefault();
                    if (page) {
                        navigateToPage(page);
                    }
                });
            });

            // Add smooth scrolling to emergency cards
            const emergencyCards = document.querySelectorAll('.emergency-card');
            emergencyCards.forEach(card => {
                card.addEventListener('mouseenter', function() {
                    this.style.transform = 'translateY(-5px) scale(1.02)';
                });
                
                card.addEventListener('mouseleave', function() {
                    this.style.transform = 'translateY(0) scale(1)';
                });
            });

            // Close notification dropdown when clicking outside
            document.addEventListener('click', function(e) {
                if (!e.target.closest('.notification-container')) {
                    closeNotifications();
                }
            });
        });

        // Navigation function
        function navigateToPage(page) {
            // Add visual feedback
            const currentLink = document.querySelector(`[data-page="${page}"]`);
            if (currentLink) {
                // Remove active class from all links
                document.querySelectorAll('.nav-link').forEach(link => {
                    link.style.backgroundColor = '';
                });
                
                // Add active class to current link
                currentLink.style.backgroundColor = 'rgba(255,255,255,0.3)';
            }

            // Navigate to different pages
            switch(page) {
                case 'home':
                    showNotification('Welcome to the Home page!', 'info');
                    break;
                case 'chatbot':
                    showNotification('Redirecting to AI Support...', 'info');
                    addNotification('info', 'AI Chatbot Access', 'You are being redirected to the AI Support page.');
                    setTimeout(() => {
                        window.location.href = '/ai-support/';
                    }, 1000);
                    break;
                case 'sessions':
                    showNotification('Redirecting to Book Session...', 'info');
                    addNotification('info', 'Session Booking', 'You are being redirected to the booking page.');
                    setTimeout(() => {
                        window.location.href = '/book-session/';
                    }, 1000);
                    break;
                case 'assessment':
                    showNotification('Redirecting to Self Assessment...', 'info');
                    addNotification('info', 'Self Assessment', 'You are being redirected to the assessment page.');
                    setTimeout(() => {
                        window.location.href = '/self-assessment/';
                    }, 1000);
                    break;
                case 'mood':
                    showNotification('Redirecting to Mood Tracker...', 'info');
                    setTimeout(() => {
                        window.location.href = '/mood-tracker/';
                    }, 1000);
                    break;
                case 'resources':
                    showNotification('Redirecting to Resources...', 'info');
                    setTimeout(() => {
                        window.location.href = '/resources/';
                    }, 1000);
                    break;
                case 'support':
                    showNotification('Redirecting to Peer Support...', 'info');
                    setTimeout(() => {
                        window.location.href = '/peer-support/';
                    }, 1000);
                    break;
            }
        }

        // Toggle sidebar
        function toggleSidebar() {
            const sidebar = document.querySelector('.sidebar');
            const overlay = document.querySelector('.sidebar-overlay');
            const isMobile = window.innerWidth <= 768;
            
            sidebar.classList.toggle('expanded');
            
            if (isMobile) {
                overlay.classList.toggle('active');
                // Prevent body scroll when sidebar is open on mobile
                document.body.style.overflow = sidebar.classList.contains('expanded') ? 'hidden' : '';
            }
        }

        // Close sidebar when clicking outside on mobile
        function closeSidebar() {
            const sidebar = document.querySelector('.sidebar');
            const overlay = document.querySelector('.sidebar-overlay');
            
            if (sidebar.classList.contains('expanded')) {
                sidebar.classList.remove('expanded');
                overlay.classList.remove('active');
                document.body.style.overflow = '';
            }
        }

        // Handle window resize
        window.addEventListener('resize', function() {
            const sidebar = document.querySelector('.sidebar');
            const overlay = document.querySelector('.sidebar-overlay');
            
            if (window.innerWidth > 768) {
                // Desktop: remove mobile-specific classes and styles
                overlay.classList.remove('active');
                document.body.style.overflow = '';
            }
        });

        // Notification functions
        function initializeNotifications() {
            updateNotificationBadge();
            renderNotifications();
        }

        function toggleNotifications() {
            const dropdown = document.getElementById('notificationDropdown');
            dropdown.classList.toggle('show');
            
            if (dropdown.classList.contains('show')) {
                // Mark notifications as read when dropdown is opened
                setTimeout(() => {
                    markAllAsRead();
                }, 1000);
            }
        }

        function closeNotifications() {
            const dropdown = document.getElementById('notificationDropdown');
            dropdown.classList.remove('show');
        }

        function updateNotificationBadge() {
            const badge = document.getElementById('notificationBadge');
            const unreadCount = notifications.filter(n => !n.read).length;
            
            if (unreadCount > 0) {
                badge.textContent = unreadCount > 9 ? '9+' : unreadCount;
                badge.style.display = 'flex';
            } else {
                badge.style.display = 'none';
            }
        }

        function renderNotifications() {
            const notificationList = document.getElementById('notificationList');
            
            if (notifications.length === 0) {
                notificationList.innerHTML = `
                    <div class="notification-empty">
                        <svg viewBox="0 0 24 24">
                            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                        </svg>
                        <p>No notifications yet</p>
                    </div>
                `;
                return;
            }

            const notificationHTML = notifications.map(notification => {
                const iconSVG = getNotificationIcon(notification.type);
                return `
                    <div class="notification-item ${notification.read ? 'read' : ''}" onclick="markAsRead(${notification.id})">
                        <div class="notification-icon ${notification.type}">
                            ${iconSVG}
                        </div>
                        <div class="notification-content">
                            <h4 class="notification-title">${notification.title}</h4>
                            <p class="notification-message">${notification.message}</p>
                            <p class="notification-time">${notification.time}</p>
                        </div>
                        ${!notification.read ? '<div class="notification-dot"></div>' : ''}
                    </div>
                `;
            }).join('');

            notificationList.innerHTML = notificationHTML;
        }

        function getNotificationIcon(type) {
            const icons = {
                info: '<svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/></svg>',
                success: '<svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>',
                warning: '<svg viewBox="0 0 24 24"><path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"/></svg>'
            };
            return icons[type] || icons.info;
        }

        function markAsRead(notificationId) {
            const notification = notifications.find(n => n.id === notificationId);
            if (notification) {
                notification.read = true;
                updateNotificationBadge();
                renderNotifications();
            }
        }

        function markAllAsRead() {
            notifications.forEach(n => n.read = true);
            updateNotificationBadge();
            renderNotifications();
        }

        function clearAllNotifications() {
            if (confirm('Are you sure you want to clear all notifications?')) {
                notifications = [];
                updateNotificationBadge();
                renderNotifications();
                showNotification('All notifications cleared!', 'success');
            }
        }

        function addNotification(type, title, message) {
            const newNotification = {
                id: Date.now(),
                type: type,
                title: title,
                message: message,
                time: 'Just now',
                read: false
            };
            notifications.unshift(newNotification);
            updateNotificationBadge();
            renderNotifications();
            
            // Show a brief animation on the bell
            const bell = document.querySelector('.notification-bell');
            bell.style.animation = 'bounce 0.6s ease';
            setTimeout(() => {
                bell.style.animation = '';
            }, 600);
        }


        // Logout functionality
        async function handleLogout() {
            if (confirm('Are you sure you want to logout?')) {
                try {
                    // Clear local storage
                    localStorage.removeItem('user');
                    localStorage.removeItem('access_token');
                    
                    // Show logout notification
                    showNotification('Logging out...', 'info');
                    
                    // Call logout API if available
                    try {
                        await fetch('/api/logout/', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'X-CSRFToken': getCookie('csrftoken')
                            }
                        });
                    } catch (error) {
                        console.log('Logout API call failed, but continuing with client-side logout');
                    }
                    
                    // Redirect to login page after 1 second
                    setTimeout(() => {
                        window.location.href = '/login/';
                    }, 1000);
                    
                } catch (error) {
                    console.error('Logout error:', error);
                    showNotification('Logout failed. Redirecting anyway...', 'error');
                    setTimeout(() => {
                        window.location.href = '/login/';
                    }, 2000);
                }
            }
        }

        // Helper function to get CSRF cookie
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

        // Emergency contact functions
        function callCrisisHelpline() {
            if (confirm('Are you in immediate danger? If yes, please call 911 or your local emergency number immediately.')) {
                showNotification('Crisis Helpline: 1800-XXX-XXXX', 'emergency');
                // In a real application, this would initiate a phone call
                // window.location.href = 'tel:1800-XXX-XXXX';
            }
        }

        function contactCampusCounselling() {
            showNotification('Campus Counselling: Mon-Fri 9AM-5PM, Student Center 2nd Floor', 'info');
        }

        function callEmergencyServices() {
            if (confirm('This will connect you to emergency services. Continue?')) {
                showNotification('Emergency Services: Campus Security XXX-XXXX or Call 911', 'emergency');
                // In a real application, this would initiate a phone call
                // window.location.href = 'tel:911';
            }
        }

        // Notification system
        function showNotification(message, type = 'info') {
            // Remove existing notifications
            const existingNotification = document.querySelector('.notification');
            if (existingNotification) {
                existingNotification.remove();
            }

            // Create notification element
            const notification = document.createElement('div');
            notification.className = `notification notification-${type}`;
            notification.innerHTML = `
                <div style="
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    background: ${type === 'emergency' ? '#ff6b6b' : '#667eea'};
                    color: white;
                    padding: 15px 20px;
                    border-radius: 8px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
                    z-index: 1000;
                    font-size: 14px;
                    max-width: 300px;
                    animation: slideIn 0.3s ease-out;
                ">
                    ${message}
                </div>
            `;

            // Add CSS animation
            const style = document.createElement('style');
            style.textContent = `
                @keyframes slideIn {
                    from {
                        transform: translateX(100%);
                        opacity: 0;
                    }
                    to {
                        transform: translateX(0);
                        opacity: 1;
                    }
                }
            `;
            document.head.appendChild(style);

            // Add to page
            document.body.appendChild(notification);

            // Auto remove after 4 seconds
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.remove();
                }
            }, 4000);
        }

        // Set active navigation item
        function setActiveNavItem(page) {
            // Remove active class from all nav items
            const navItems = document.querySelectorAll('.nav-item');
            navItems.forEach(item => item.classList.remove('active'));
            
            // Add active class to current page
            const currentNavItem = document.querySelector(`[data-page="${page}"]`);
            if (currentNavItem) {
                currentNavItem.closest('.nav-item').classList.add('active');
            }
        }

        // Add some interactive features
        document.addEventListener('DOMContentLoaded', function() {
            // Set home as active by default
            setActiveNavItem('home');
            
            // Add hover effects to feature badges
            const badges = document.querySelectorAll('.badge');
            badges.forEach(badge => {
                badge.addEventListener('mouseenter', function() {
                    this.style.transform = 'scale(1.05)';
                    this.style.transition = 'transform 0.2s ease';
                });
                
                badge.addEventListener('mouseleave', function() {
                    this.style.transform = 'scale(1)';
                });
            });

            // Add click effect to feature list items
            const featureItems = document.querySelectorAll('.features-list li');
            featureItems.forEach(item => {
                item.addEventListener('click', function() {
                    this.style.backgroundColor = 'rgba(102, 126, 234, 0.1)';
                    setTimeout(() => {
                        this.style.backgroundColor = '';
                    }, 200);
                });
            });
        });

        // Keyboard navigation support
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                // Close any open modals or notifications
                const notification = document.querySelector('.notification');
                if (notification) {
                    notification.remove();
                }
            }
        });

        // Welcome message on page load
        window.addEventListener('load', function() {
            setTimeout(() => {
                showNotification('Welcome to MindCare! Your mental health journey starts here.', 'info');
            }, 1000);
        });