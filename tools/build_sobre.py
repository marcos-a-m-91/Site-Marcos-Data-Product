import os

script_dir = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(script_dir, '../')

with open(path + 'index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

split_idx = 0
for i, l in enumerate(lines):
    if '<!-- HERO SECTION -->' in l:
        split_idx = i - 2
        break
    if 'HERO' in lines[i+1] and '═════════════════' in l:
        split_idx = i
        break

head_lines = lines[:split_idx]

sobre_body = """
  <!-- ═══════════════════════════════════════════════════════
     SOBRE HERO (1ª Dobra)
  ═══════════════════════════════════════════════════════ -->
  <section id="sobre-hero" class="min-h-[100vh] flex flex-col justify-center px-5 sm:px-8 pt-32 pb-16 relative overflow-hidden">
    <div class="max-w-7xl mx-auto w-full grid lg:grid-cols-2 gap-12 lg:gap-8 items-center z-10">
      
      <!-- Content Side -->
      <div class="flex flex-col items-center lg:items-start text-center lg:text-left">
        <span class="badge badge-blue mb-6">Senior Business Analytics</span>
        <h1 class="text-4xl sm:text-5xl md:text-6xl lg:text-[4rem] font-bold text-white mb-6 tracking-tight leading-[1.1] reveal">
          Conectando <span class="gradient-text">dados</span> a <span class="gradient-text">decisões estratégicas</span>
        </h1>
        <p class="text-base sm:text-lg text-white/50 max-w-xl mb-10 leading-relaxed reveal" style="font-family:'Manrope',sans-serif">
          Eu ajudo a transformar dados brutos em respostas claras para negócios que não tem tempo a perder.
        </p>
        
        <div class="flex flex-wrap gap-4 justify-center lg:justify-start reveal">
          <a href="#" class="btn-primary" onclick="createRipple(event)">
            <i data-lucide="linkedin" class="w-5 h-5 text-[#0A66C2]"></i>
            LinkedIn
          </a>
          <a href="#" class="btn-secondary">
            <i data-lucide="github" class="w-5 h-5"></i>
            GitHub
          </a>
        </div>
      </div>
      
      <!-- Visual Side (Foto) -->
      <div class="relative flex justify-center lg:justify-end reveal">
        <div class="relative w-full max-w-md aspect-[4/5] rounded-[2rem] sm:rounded-[3rem] overflow-hidden glass border-white/20 shadow-[0_0_80px_rgba(96,165,250,0.15)] group animate-float-slow">
          <div class="absolute inset-0 bg-gradient-to-t from-[#080810] via-[#080810]/40 to-transparent z-10 opacity-70"></div>
          <img src="assets/img/Foto Marcos Aurélio.png" alt="Marcos Aurélio" class="w-full h-full object-cover object-center group-hover:scale-105 transition-transform duration-700 ease-out" />
        </div>
      </div>
    </div>
  </section>

  <div class="section-divider"></div>

  <!-- ═══════════════════════════════════════════════════════
     TIMELINE (2ª Dobra)
  ═══════════════════════════════════════════════════════ -->
  <section id="timeline" class="py-24 sm:py-32 px-5 sm:px-8 relative overflow-hidden">
    <div class="section-glow w-[500px] h-[500px] bg-blue-500/20 pointer-events-none" style="top:20%;left:-10%;"></div>
    <div class="section-glow w-[500px] h-[500px] bg-amber-500/10 pointer-events-none" style="bottom:20%;right:-10%;"></div>
    
    <div class="max-w-4xl mx-auto relative z-10">
      
      <div class="text-center mb-28 reveal">
        <h2 class="text-3xl sm:text-4xl md:text-5xl font-bold text-white tracking-tight leading-tight max-w-3xl mx-auto pb-2">
          De números a estratégia: uma <span class="text-blue-400">trajetória</span> construída com grandes empresas.
        </h2>
      </div>

      <!-- GSAP Animated Timeline Container -->
      <div class="relative pl-8 md:pl-0 mt-12">
        
        <!-- Center/Left Vertical Line -->
        <div class="absolute left-8 md:left-[50%] top-4 bottom-0 w-px bg-white/10 md:-translate-x-1/2 timeline-line"></div>

        <!-- TIMELINE ITEMS -->
        <div class="space-y-24">
          
          <!-- Item: 2020 Nubank -->
          <div class="timeline-item relative flex flex-col md:flex-row items-start md:items-center justify-between group">
            
            <!-- Mobile Year (hidden on desktop) -->
            <div class="md:hidden absolute -left-8 top-[28px] -translate-y-1/2 -ml-[4px] mt-0.5">
               <div class="w-3 h-3 rounded-full border-2 border-[#080810] bg-blue-400 shadow-[0_0_10px_rgba(96,165,250,0.6)] tl-dot"></div>
            </div>
            <div class="md:hidden text-blue-400 font-bold mb-4 pl-4 text-2xl tl-year">2020</div>

            <!-- Desktop Year (Left side) -->
            <div class="hidden md:flex w-1/2 justify-end pr-16 tl-year">
              <span class="text-5xl lg:text-7xl font-bold text-white/10 group-hover:text-blue-400/40 transition-colors duration-500 tracking-tighter">2020</span>
            </div>
            
            <!-- Desktop Node/Dot -->
            <div class="hidden md:block absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-5 h-5 rounded-full border-[5px] border-[#080810] bg-white/20 group-hover:bg-blue-400 transition-all duration-500 z-10 tl-dot shadow-[0_0_15px_rgba(96,165,250,0)] group-hover:shadow-[0_0_15px_rgba(96,165,250,0.8)]"></div>

            <!-- Card (Right side) -->
            <div class="w-full md:w-1/2 md:pl-16 tl-card">
              <div class="glass hover:bg-white/[0.04] transition-colors duration-300 p-8 sm:p-10 rounded-[2rem] border border-white/10 relative overflow-hidden">
                <div class="absolute inset-0 bg-gradient-to-br from-blue-500/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-700 pointer-events-none"></div>
                <h3 class="text-2xl sm:text-3xl font-bold text-white mb-4 relative z-10">Nubank</h3>
                <p class="text-white/50 leading-relaxed text-base sm:text-lg style="font-family:'Manrope',sans-serif" relative z-10">
                  Analista de dados no time de crédito. Primeiro contato com dados em escala: milhões de transações, decisões em tempo real, cultura orientada a evidência.
                </p>
              </div>
            </div>
          </div>

          <!-- Item: 2022 Google -->
          <div class="timeline-item relative flex flex-col md:flex-row-reverse items-start md:items-center justify-between group">
            
            <div class="md:hidden absolute -left-8 top-[28px] -translate-y-1/2 -ml-[4px] mt-0.5">
               <div class="w-3 h-3 rounded-full border-2 border-[#080810] bg-amber-400 shadow-[0_0_10px_rgba(251,191,36,0.6)] tl-dot"></div>
            </div>
            <div class="md:hidden text-amber-400 font-bold mb-4 pl-4 text-2xl tl-year">2022</div>

            <!-- Desktop Year (Right side) -->
            <div class="hidden md:flex w-1/2 justify-start pl-16 tl-year">
              <span class="text-5xl lg:text-7xl font-bold text-white/10 group-hover:text-amber-400/40 transition-colors duration-500 tracking-tighter">2022</span>
            </div>
            
            <div class="hidden md:block absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-5 h-5 rounded-full border-[5px] border-[#080810] bg-white/20 group-hover:bg-amber-400 transition-all duration-500 z-10 tl-dot shadow-[0_0_15px_rgba(251,191,36,0)] group-hover:shadow-[0_0_15px_rgba(251,191,36,0.8)]"></div>

            <!-- Card (Left side) -->
            <div class="w-full md:w-1/2 md:pr-16 text-left md:text-right tl-card">
              <div class="glass hover:bg-white/[0.04] transition-colors duration-300 p-8 sm:p-10 rounded-[2rem] border border-white/10 relative overflow-hidden">
                <div class="absolute inset-0 bg-gradient-to-bl from-amber-500/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-700 pointer-events-none"></div>
                <h3 class="text-2xl sm:text-3xl font-bold text-white mb-4 relative z-10">Google</h3>
                <p class="text-white/50 leading-relaxed text-base sm:text-lg style="font-family:'Manrope',sans-serif" relative z-10">
                  Integrou o time de analytics de produto. Trabalhou com métricas de engajamento e retenção, desenvolvendo modelos preditivos usados por squads de produto globais.
                </p>
              </div>
            </div>
          </div>

          <!-- Item: 2024 Asimov Academy -->
          <div class="timeline-item relative flex flex-col md:flex-row items-start md:items-center justify-between group">
            
            <div class="md:hidden absolute -left-8 top-[28px] -translate-y-1/2 -ml-[4px] mt-0.5">
               <div class="w-3 h-3 rounded-full border-2 border-[#080810] bg-emerald-400 shadow-[0_0_10px_rgba(52,211,153,0.6)] tl-dot"></div>
            </div>
            <div class="md:hidden text-emerald-400 font-bold mb-4 pl-4 text-2xl tl-year">2024</div>

            <!-- Desktop Year (Left side) -->
            <div class="hidden md:flex w-1/2 justify-end pr-16 tl-year">
              <span class="text-5xl lg:text-7xl font-bold text-white/10 group-hover:text-emerald-400/40 transition-colors duration-500 tracking-tighter">2024</span>
            </div>
            
            <div class="hidden md:block absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-5 h-5 rounded-full border-[5px] border-[#080810] bg-white/20 group-hover:bg-emerald-400 transition-all duration-500 z-10 tl-dot shadow-[0_0_15px_rgba(52,211,153,0)] group-hover:shadow-[0_0_15px_rgba(52,211,153,0.8)]"></div>

            <!-- Card (Right side) -->
            <div class="w-full md:w-1/2 md:pl-16 tl-card">
              <div class="glass hover:bg-white/[0.04] transition-colors duration-300 p-8 sm:p-10 rounded-[2rem] border border-white/10 relative overflow-hidden">
                 <div class="absolute inset-0 bg-gradient-to-br from-emerald-500/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-700 pointer-events-none"></div>
                <h3 class="text-2xl sm:text-3xl font-bold text-white mb-4 relative z-10">Asimov Academy</h3>
                <p class="text-white/50 leading-relaxed text-base sm:text-lg style="font-family:'Manrope',sans-serif" relative z-10">
                  Lidera projeto de análise e automação para uma das principais edtechs de tecnologia do Brasil. Foco em performance de campanhas, comportamento de alunos e decisões de negócio baseadas em dados.
                </p>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  </section>

  <!-- ═══════════════════════════════════════════════════════
     FOOTER
  ═══════════════════════════════════════════════════════ -->
  <footer class="relative z-10 border-t border-white/5 px-5 sm:px-8 py-8 mt-12">
    <div class="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-white/25">
      <div class="flex items-center gap-3">
        <img src="assets/img/Logo.png" alt="" class="w-5 h-5 object-contain opacity-50" />
        <span>© 2026 Marcos Data Product</span>
      </div>
      <span>Feito com dados, café e IA</span>
    </div>
  </footer>

  <!-- ═══════════════════════════════════════════════════════
     SCRIPTS
  ═══════════════════════════════════════════════════════ -->
  <script>
    // Ripple effect script
    function createRipple(event) {
      const button = event.currentTarget;
      const circle = document.createElement('span');
      const diameter = Math.max(button.clientWidth, button.clientHeight);
      const radius = diameter / 2;
      circle.style.width = circle.style.height = `${diameter}px`;
      circle.style.left = `${event.clientX - button.getBoundingClientRect().left - radius}px`;
      circle.style.top = `${event.clientY - button.getBoundingClientRect().top - radius}px`;
      circle.classList.add('ripple-effect');
      const existingRipple = button.querySelector('.ripple-effect');
      if (existingRipple) {
        existingRipple.remove();
      }
      button.appendChild(circle);
    }

    lucide.createIcons();

    // Setup GSAP
    gsap.registerPlugin(ScrollTrigger);

    // Initial Reveal for Base Elements
    gsap.utils.toArray('.reveal').forEach((elem) => {
      gsap.fromTo(elem, 
        { y: 30, opacity: 0 }, 
        { 
          y: 0, 
          opacity: 1, 
          duration: 1, 
          ease: 'power3.out',
          scrollTrigger: {
            trigger: elem,
            start: 'top 85%',
          }
        }
      );
    });

    // Timeline Animation
    gsap.utils.toArray('.timeline-item').forEach((item, index) => {
      const card = item.querySelector('.tl-card');
      const dot = item.querySelectorAll('.tl-dot');
      const year = item.querySelectorAll('.tl-year');

      // Expand line up to the element
      const timelineLine = document.querySelector('.timeline-line');

      // Card enters
      gsap.fromTo(card,
        { opacity: 0, x: index % 2 === 0 ? 30 : -30 },
        { 
          opacity: 1, 
          x: 0, 
          duration: 1, 
          ease: "power3.out",
          scrollTrigger: {
            trigger: item,
            start: "top 80%",
          }
        }
      );

      // Dot flashes
      gsap.fromTo(dot,
        { scale: 0, opacity: 0 },
        { 
          scale: 1, 
          opacity: 1, 
          duration: 0.5, 
          ease: "back.out(1.7)",
          scrollTrigger: {
            trigger: item,
            start: "top 80%",
          }
        }
      );

      // Year slides in slightly
      gsap.fromTo(year,
        { opacity: 0, x: index % 2 === 0 ? -15 : 15 },
        { 
          opacity: 1, 
          x: 0, 
          duration: 0.8, 
          ease: "power2.out",
          scrollTrigger: {
            trigger: item,
            start: "top 80%",
          }
        }
      );
    });

    // Mobile menu toggle
    const mobileBtn = document.getElementById('mobile-btn');
    const mobileClose = document.getElementById('mobile-close');
    const mobileMenu = document.getElementById('mobile-menu');
    const mobileLinks = document.querySelectorAll('.mobile-link');

    mobileBtn?.addEventListener('click', () => {
      mobileMenu.classList.add('active');
      document.body.style.overflow = 'hidden';
    });

    const closeMenu = () => {
      mobileMenu.classList.remove('active');
      document.body.style.overflow = '';
    };

    if (mobileClose && mobileMenu && mobileBtn) {
      mobileClose.addEventListener('click', closeMenu);
      mobileLinks.forEach(link => link.addEventListener('click', closeMenu));
    }

    // Nav blur on scroll
    const navbar = document.getElementById('navbar');
    window.addEventListener('scroll', () => {
      if (window.scrollY > 50) {
        navbar.classList.add('scrolled');
      } else {
        navbar.classList.remove('scrolled');
      }
    });
  </script>
</body>
</html>
"""

final_text = "".join(head_lines) + sobre_body

with open(path + 'sobre.html', 'w', encoding='utf-8') as f:
    f.write(final_text)

print(f"File written successfully. Length: {len(final_text)}")
