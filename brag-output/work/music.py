# Score and SFX on one grid: 96 BPM, 32 beats = 20.000s, A minor / C major.
import numpy as np, wave
SR=48000; B=.625; N=int(20*SR); rng=np.random.default_rng(7)
dry=np.zeros(N); send=np.zeros(N); pad_bus=np.zeros(N); tick_bus=np.zeros(N)
hz=lambda m:440*2**((m-69)/12)
def put(bus,x,beat,g=1):
    i=int(round(beat*B*SR)); x=x[:max(0,N-i)]; bus[i:i+len(x)]+=x*g
def T(d): return np.arange(int(d*SR))/SR
def keys(m,d=1.6):       # soft FM electric piano
    t=T(d); f=hz(m); idx=1.4*np.exp(-t*7)
    return np.sin(2*np.pi*f*t+idx*np.sin(2*np.pi*f*t))*np.exp(-t*3.2)*np.minimum(t/.004,1)
def bell(m,d=2.5):
    t=T(d); f=hz(m); return (np.sin(2*np.pi*f*t+.9*np.exp(-t*4)*np.sin(2*np.pi*3.5*f*t)))*np.exp(-t*2.6)*np.minimum(t/.003,1)
def pad(ms,d):
    t=T(d); x=np.zeros(len(t))
    for m in ms:
        for det in(-.05,.05):
            f=hz(m+det)
            for h,a in((1,1),(2,.35),(3,.14),(4,.06)): x+=a*np.sin(2*np.pi*f*h*t+rng.uniform(0,6))
    return x/len(ms)*np.minimum(t/.35,1)*np.minimum((d-t)/.35,1)
def bass(m,d):
    t=T(d); f=hz(m); return (np.sin(2*np.pi*f*t)+.2*np.sin(4*np.pi*f*t))*np.minimum(t/.008,1)*np.exp(-t*1.1)*np.minimum((d-t)/.05,1)
def kick():
    t=T(.35); return np.sin(2*np.pi*(46*t+(64/30)*(1-np.exp(-t*30))))*np.exp(-t*11)
def hat():
    t=T(.05); return np.diff(rng.normal(size=len(t)+1))*np.exp(-t*95)
def rim():
    t=T(.12); return (.5*np.sin(2*np.pi*1046.5*t)+.5*rng.normal(size=len(t))*np.exp(-t*30))*np.exp(-t*45)
def tick(m):
    t=T(.05); return np.sin(2*np.pi*hz(m)*t)*np.exp(-t*160)
def whoosh(d=.55):       # rises into the cut
    n=int(d*SR); F=np.fft.rfft(rng.normal(size=n)); fr=np.fft.rfftfreq(n,1/SR)
    x=np.fft.irfft(F*np.exp(-((fr-1500)/1400)**2),n); return x/np.abs(x).max()*np.linspace(0,1,n)**2.5
bars=[([57,60,64,67,71],33),([53,57,60,64,67],29),([48,55,60,64,67],36),([55,59,62,67,69],31),
      ([57,60,64,67,71],33),([53,57,60,64,69],29),([50,57,60,65,69],38),([48,55,60,64,71],36)]
arp=[0,2,3,4,3,2,4,3]
for b,(ch,ba) in enumerate(bars):
    start=b*4
    if b<7:
        put(pad_bus,pad(ch,4*B+.3),start,.05)
        for i,k in enumerate(arp):
            if start+i/2>=29: break
            put(send,keys(ch[k]+12,1.1),start+i/2,.055 if b<2 else .07)
    if 1<=b<7:
        put(dry,bass(ba,2*B),start,.24); put(dry,bass(ba+(7 if b%2 else 0),2*B-.02),start+2,.2)
# ending: C add9 rings out from the logo cut (beat 29)
put(pad_bus,pad([48,55,60,64,67,71],3*B+.35),28.5,.06)
put(dry,bass(36,3*B),29,.28)
for m,o in((72,0),(76,.5),(79,1),(83,1.5)): put(send,bell(m),29+o,.09)
# drums
for beat in range(32):
    if 4<=beat<22 and beat%2==0 or beat in(24,26,28,29):
        put(dry,kick(),beat,.36)
    if 12<=beat<22 and beat%2==1:
        put(send,rim(),beat,.05)
for e in range(16,58):
    put(dry,hat(),e/2,.018 if e%2 else .03)
# scene cuts: soft riser + a chord-tone bell, in the same space as the music
cuts={5:76,11:72,16:76,22:81,29:84}
for c,m in cuts.items():
    w=whoosh(); put(send,w,c-len(w)/SR/B,.035); put(send,bell(m),c,.06)
for i,m in enumerate((72,74,76,79,76,74)):          # six logos on 8ths
    put(send,bell(m+12,1.0),12+i/2,.035)
for i,m in enumerate((84,86,88,84,86,88,91)):        # typing, 16ths
    put(send,tick(m),18+i/4,.05)
# light sidechain on the pad from the kick
sc=np.ones(N)
for beat in list(range(4,22,2))+[24,26,28,29]:
    i=int(beat*B*SR); n=int(.28*SR); sc[i:i+n]=np.minimum(sc[i:i+n],1-.45*np.exp(-np.arange(n)/SR*9))
pad_bus*=sc
# plate-ish reverb
L=int(1.7*SR); ir=rng.normal(size=L)*np.exp(-np.arange(L)/SR*3.4)
sz=N+L; Fi=np.fft.rfft(ir,sz); fr=np.fft.rfftfreq(sz,1/SR); Fi*=1/(1+(fr/5000)**2)
wet_in=send+.5*pad_bus
wet=np.fft.irfft(np.fft.rfft(wet_in,sz)*Fi,sz)[:N]; wet/=np.sqrt(np.sum(ir**2))
mid=dry+pad_bus+send
# stereo: wet decorrelated by short offset, arps slightly wide
l=mid+.42*wet; r=mid+.42*np.roll(wet,311)
st=np.stack([l,r],1)
st=np.tanh(st*1.1)/np.tanh(1.1); st/=np.abs(st).max()/.84
fade=np.minimum((20-np.arange(N)/SR)/.45,1)[:,None]; st*=np.clip(fade,0,1)
with wave.open('music.wav','wb') as w:
    w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR);w.writeframes((st*32767).astype('<i2').tobytes())
