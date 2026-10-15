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
          const intervalMs = el.hasAttribute('data-interval') ? +el.getAttribute('data-interval') : 10000;
          setInterval(() => {
            const currentVal = Math.floor(obj.val);
            gsap.to(obj, {
              val: currentVal + 1,
              duration: 0.5,
              ease: "power2.out",
              onUpdate: () => el.innerText = Math.floor(obj.val).toLocaleString('pt-BR')
            });
          }, intervalMs);
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

    // 6. Auto-highlight active navigation link
    const currentPath = window.location.pathname.split('/').pop() || 'index.html';
    
    document.querySelectorAll('.nav-link, .mobile-link').forEach(link => {
        const href = link.getAttribute('href');
        if (!href || href.startsWith('http')) return;
        
        const cleanHref = href.split('#')[0].split('?')[0];
        if (cleanHref === currentPath || (currentPath === '' && cleanHref === 'index.html')) {
            link.classList.add('active');
            link.classList.remove('text-white');
        } else {
            link.classList.remove('active', 'text-white');
        }
    });

    // 7. Hub Deck - Expanding cards interaction (Mobile touch support)
    const hubDeck = document.getElementById('hub-deck');
    if (hubDeck) {
        const cards = hubDeck.querySelectorAll('.hub-card');
        
        cards.forEach(card => {
            // On mobile / touch device: tap to expand first, second tap or button click navigates
            card.addEventListener('click', (e) => {
                if (window.innerWidth < 768) {
                    if (!card.classList.contains('active')) {
                        const clickedBtn = e.target.closest('.hub-btn');
                        if (!clickedBtn) {
                            e.preventDefault();
                            cards.forEach(c => c.classList.remove('active'));
                            card.classList.add('active');
                        }
                    }
                }
            });
        });
    }

    // 8. Privacy & Cookie Consent Card (LGPD + Data Product Storytelling)
    function initCookieConsent() {
        const CONSENT_KEY = 'mdp_cookie_consent';
        if (localStorage.getItem(CONSENT_KEY)) return;

        const banner = document.createElement('div');
        banner.id = 'cookie-consent-card';
        banner.className = 'fixed bottom-5 right-5 sm:right-6 max-w-md w-[calc(100%-2.5rem)] z-50 transition-all duration-500 transform translate-y-10 opacity-0 pointer-events-none';
        banner.style.fontFamily = "'Inter', -apple-system, BlinkMacSystemFont, sans-serif";

        banner.innerHTML = `
            <div class="bg-white/95 backdrop-blur-md rounded-2xl p-5 border border-[#d0d7de] shadow-2xl flex flex-col gap-3.5 relative">
                <div class="flex items-start justify-between gap-3">
                    <div class="flex items-center gap-2.5">
                        <span class="w-8 h-8 rounded-xl bg-[#11376e]/10 text-[#11376e] flex items-center justify-center flex-shrink-0">
                            <i data-lucide="cookie" class="w-4 h-4"></i>
                        </span>
                        <div>
                            <h4 class="text-xs font-bold text-[#1f2328] uppercase tracking-wider">
                                Dados & Transparência
                            </h4>
                            <p class="text-[11px] text-[#656d76]">Do dado à decisão • Marcos Data Product</p>
                        </div>
                    </div>
                    <button id="cookie-close-btn" class="p-1.5 rounded-lg text-[#8c959f] hover:text-[#1f2328] hover:bg-slate-100 transition-colors cursor-pointer" aria-label="Fechar aviso" title="Fechar">
                        <i data-lucide="x" class="w-4 h-4"></i>
                    </button>
                </div>

                <p class="text-xs text-[#57606a] leading-relaxed">
                    Utilizamos cookies e métricas de navegação anônimas para entender o engajamento e aprimorar sua experiência. Como este é um site sobre <strong>Business Analytics e Produtos de Dados</strong>, alguns desses insights agregados também servirão de <strong>exemplo real em futuros artigos e estudos de caso do blog</strong>!
                </p>

                <div class="flex items-center gap-2 pt-1 border-t border-[#d0d7de]/50">
                    <button id="cookie-accept-btn" class="flex-1 py-2.5 px-4 rounded-xl bg-[#11376e] hover:bg-[#184a91] text-white text-xs font-semibold shadow-xs hover:shadow transition-all btn-tactile cursor-pointer flex items-center justify-center gap-1.5">
                        <i data-lucide="check" class="w-3.5 h-3.5"></i>
                        <span>Aceitar e colaborar</span>
                    </button>
                    <button id="cookie-essential-btn" class="py-2.5 px-3.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-[#57606a] hover:text-[#1f2328] text-xs font-medium transition-all cursor-pointer">
                        <span>Apenas essenciais</span>
                    </button>
                </div>
            </div>
        `;

        document.body.appendChild(banner);
        if (window.lucide) {
            lucide.createIcons();
        }

        // Suave entrada após 800ms
        setTimeout(() => {
            banner.classList.remove('translate-y-10', 'opacity-0', 'pointer-events-none');
        }, 800);

        function dismissBanner(consentValue) {
            localStorage.setItem(CONSENT_KEY, consentValue);
            banner.classList.add('translate-y-10', 'opacity-0', 'pointer-events-none');
            
            // Disparar no dataLayer para futuro Google Tag Manager / GA4
            window.dataLayer = window.dataLayer || [];
            window.dataLayer.push({
                event: 'cookie_consent_update',
                consent_status: consentValue,
                timestamp: new Date().toISOString()
            });

            setTimeout(() => {
                banner.remove();
            }, 500);
        }

        const acceptBtn = document.getElementById('cookie-accept-btn');
        const essentialBtn = document.getElementById('cookie-essential-btn');
        const closeBtn = document.getElementById('cookie-close-btn');

        if (acceptBtn) acceptBtn.addEventListener('click', () => dismissBanner('granted'));
        if (essentialBtn) essentialBtn.addEventListener('click', () => dismissBanner('essential_only'));
        if (closeBtn) closeBtn.addEventListener('click', () => dismissBanner('dismissed'));
    }

    initCookieConsent();
});
