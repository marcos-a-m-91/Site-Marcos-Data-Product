/* 
   MARCOS DATA PRODUCT — MAIN SCRIPTS
   Utility functions and shared animation logic
*/

/**
 * Helper to animate counters - Global to ensure availability for inline scripts
 * @param {HTMLElement} el 
 */
window.initCounter = function(el) {
    if (!window.gsap) return;
    const target = +el.getAttribute('data-target');
    const dur = el.getAttribute('data-duration') ? +el.getAttribute('data-duration') : 3.5;
    const autoIncrement = el.hasAttribute('data-increment');
    const obj = { val: 0 };
    
    gsap.to(obj, {
      val: target,
      duration: dur,
      ease: "power3.out",
      scrollTrigger: {
          trigger: el,
          start: "top 90%"
      },
      onUpdate: () => {
        el.innerText = Math.floor(obj.val).toLocaleString('pt-BR');
      },
      onComplete: () => {
        if (autoIncrement) {
          setInterval(() => {
            const currentVal = Math.floor(obj.val);
            gsap.to(obj, {
              val: currentVal + 1,
              duration: 0.5,
              ease: "power2.out",
              onUpdate: () => el.innerText = Math.floor(obj.val).toLocaleString('pt-BR')
            });
          }, 10000);
        }
      }
    });
};

document.addEventListener('DOMContentLoaded', () => {
    // 1. Init Lucide icons
    if (window.lucide) {
        lucide.createIcons();
    }

    // 2. Ripple effect
    window.createRipple = function(event) {
        const btn = event.currentTarget;
        const rect = btn.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = event.clientX - rect.left - size / 2;
        const y = event.clientY - rect.top - size / 2;
        
        const ripple = document.createElement('span');
        ripple.className = 'ripple-effect';
        ripple.style.width = ripple.style.height = `${size}px`;
        ripple.style.left = `${x}px`;
        ripple.style.top = `${y}px`;
        
        btn.appendChild(ripple);
        setTimeout(() => ripple.remove(), 600);
    };

    // 3. Mobile menu toggle
    const mobileBtn = document.getElementById('mobile-btn');
    const mobileClose = document.getElementById('mobile-close');
    const mobileMenu = document.getElementById('mobile-menu');

    if (mobileBtn && mobileMenu) {
        mobileBtn.addEventListener('click', () => {
            mobileMenu.classList.add('active');
            document.body.style.overflow = 'hidden';
        });
        
        const closeMenu = () => {
            mobileMenu.classList.remove('active');
            document.body.style.overflow = '';
        };

        if (mobileClose) mobileClose.addEventListener('click', closeMenu);
        
        // Close mobile menu on link click
        mobileMenu.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', closeMenu);
        });
    }

    // 4. Navbar scroll effect
    const navbar = document.getElementById('navbar');
    if (navbar) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 50) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        });
    }

    // 5. Shared ScrollTrigger base config (if gsap exists)
    if (window.gsap && window.ScrollTrigger) {
        gsap.registerPlugin(ScrollTrigger);

        // Common reveal animation
        gsap.utils.toArray('.reveal').forEach((el) => {
            gsap.to(el, {
                opacity: 1,
                y: 0,
                duration: 1,
                ease: "power3.out",
                scrollTrigger: {
                    trigger: el,
                    start: "top 85%",
                    toggleActions: "play none none none"
                }
            });
        });
    }
});
