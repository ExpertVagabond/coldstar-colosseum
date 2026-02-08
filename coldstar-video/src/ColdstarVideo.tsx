import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
  Sequence,
  staticFile,
} from "remotion";

const colors = {
  bg: "#0f0f0f",
  primary: "#9945FF",
  secondary: "#14F195",
  accent: "#00D1FF",
  text: "#ffffff",
  muted: "#888888",
  danger: "#ff4444",
};

const AnimatedBackground: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill
      style={{
        background: `
          radial-gradient(
            ellipse at ${50 + Math.sin(frame / 50) * 20}% ${50 + Math.cos(frame / 40) * 20}%,
            ${colors.primary}22 0%, transparent 50%
          ),
          radial-gradient(
            ellipse at ${50 - Math.sin(frame / 60) * 30}% ${50 - Math.cos(frame / 50) * 30}%,
            ${colors.secondary}15 0%, transparent 40%
          ),
          ${colors.bg}
        `,
      }}
    />
  );
};

// Scene 1: Intro (0-90 frames = 3s)
const IntroScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const logoScale = spring({ frame, fps, config: { damping: 12 } });
  const subtitleOpacity = interpolate(frame, [30, 50], [0, 1], { extrapolateRight: "clamp" });
  const badgeOpacity = interpolate(frame, [50, 70], [0, 1], { extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", flexDirection: "column" }}>
      <img
        src={staticFile("coldstar-logo.png")}
        alt="Coldstar"
        style={{ transform: `scale(${logoScale})`, height: 160, marginBottom: 20 }}
      />
      <p style={{
        fontSize: 30, color: colors.secondary, opacity: subtitleOpacity,
        fontFamily: "SF Mono, monospace", marginTop: 10,
      }}>
        Air-Gapped Solana Vault
      </p>
      <div style={{
        marginTop: 25, padding: "8px 24px", borderRadius: 20,
        border: `1px solid ${colors.primary}88`, opacity: badgeOpacity,
        fontSize: 16, color: colors.primary, fontFamily: "SF Pro Display, sans-serif",
      }}>
        Colosseum Agent Hackathon 2026
      </div>
    </AbsoluteFill>
  );
};

// Scene 2: Problem (90-240 = 5s)
const ProblemScene: React.FC = () => {
  const frame = useCurrentFrame();
  const items = [
    { text: "Agents managing $100K+ in crypto", icon: "⚠", delay: 0 },
    { text: "Hot wallets — one exploit from zero", icon: "✗", delay: 20 },
    { text: "Hardware wallets — $200, not programmable", icon: "✗", delay: 40 },
    { text: "No DAO governance, no agent API", icon: "✗", delay: 60 },
  ];

  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", flexDirection: "column", padding: 60 }}>
      <h2 style={{
        fontSize: 44, color: colors.muted, marginBottom: 45,
        fontFamily: "SF Pro Display, sans-serif",
        opacity: interpolate(frame, [0, 15], [0, 1], { extrapolateRight: "clamp" }),
      }}>
        The Problem
      </h2>
      {items.map((item, i) => {
        const opacity = interpolate(frame, [item.delay + 10, item.delay + 25], [0, 1], { extrapolateRight: "clamp" });
        const x = interpolate(frame, [item.delay + 10, item.delay + 25], [40, 0], { extrapolateRight: "clamp" });
        return (
          <div key={i} style={{
            fontSize: 30, color: i === 0 ? colors.accent : colors.danger,
            opacity, transform: `translateX(${x}px)`, marginBottom: 20,
            fontFamily: "SF Pro Display, sans-serif", display: "flex", alignItems: "center", gap: 15,
          }}>
            <span style={{ fontSize: 22 }}>{item.icon}</span>
            {item.text}
          </div>
        );
      })}
    </AbsoluteFill>
  );
};

// Scene 3: Solution (240-480 = 8s)
const SolutionScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const titleOpacity = interpolate(frame, [0, 20], [0, 1], { extrapolateRight: "clamp" });
  const priceScale = spring({ frame: frame - 20, fps, config: { damping: 10 } });

  const features = [
    { text: "Air-gapped signing via QR code", icon: "🔐", delay: 60 },
    { text: "Jupiter DEX + Pyth price feeds", icon: "💱", delay: 80 },
    { text: "DAO governance with multi-sig", icon: "🏛", delay: 100 },
  ];

  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", flexDirection: "column", padding: 60 }}>
      <h2 style={{
        fontSize: 44, color: colors.secondary, marginBottom: 15,
        fontFamily: "SF Pro Display, sans-serif", opacity: titleOpacity,
      }}>
        The Solution
      </h2>
      <div style={{
        fontSize: 72, fontWeight: 800, color: colors.secondary,
        fontFamily: "SF Pro Display, sans-serif",
        transform: `scale(${Math.min(priceScale, 1)})`,
        marginBottom: 40,
      }}>
        $10 USB = Hardware Wallet
      </div>
      {features.map((feature, i) => {
        const scale = spring({ frame: frame - feature.delay, fps, config: { damping: 12 } });
        return (
          <div key={i} style={{
            fontSize: 28, color: colors.text,
            transform: `scale(${Math.min(scale, 1)})`, opacity: scale > 0 ? 1 : 0,
            marginBottom: 22, fontFamily: "SF Pro Display, sans-serif",
            display: "flex", alignItems: "center", gap: 18,
          }}>
            <span style={{ fontSize: 34 }}>{feature.icon}</span>
            {feature.text}
          </div>
        );
      })}
    </AbsoluteFill>
  );
};

// Scene 4: Terminal Demo (480-780 = 10s)
const TerminalScene: React.FC = () => {
  const frame = useCurrentFrame();
  const lines = [
    { text: "$ coldstar", delay: 0, color: colors.text },
    { text: "", delay: 8, color: colors.text },
    { text: "✓ Loaded keypair from air-gapped USB", delay: 12, color: colors.secondary },
    { text: "✓ Wallet: Cds7wQ...uAopD", delay: 22, color: colors.secondary },
    { text: "✓ Balance: 5.23 SOL ($523.41 via Pyth)", delay: 32, color: colors.secondary },
    { text: "", delay: 42, color: colors.text },
    { text: "→ Jupiter swap: 1 SOL → USDC", delay: 48, color: colors.accent },
    { text: "  Route: SOL → USDC via Raydium (best rate)", delay: 58, color: colors.muted },
    { text: "  Price impact: 0.01%", delay: 66, color: colors.muted },
    { text: "✓ Unsigned swap TX saved to /inbox", delay: 78, color: colors.secondary },
    { text: "", delay: 88, color: colors.text },
    { text: "⚠ SIGNING OFFLINE — KEY NEVER LEAVES USB", delay: 94, color: colors.primary },
    { text: "✓ Transaction signed on air-gapped device", delay: 114, color: colors.secondary },
    { text: "", delay: 124, color: colors.text },
    { text: "→ Broadcasting to Solana...", delay: 130, color: colors.accent },
    { text: "✓ SWAP CONFIRMED! Sig: 5j7s8K...mN2x", delay: 148, color: colors.secondary },
  ];

  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", padding: 40 }}>
      <div style={{
        background: "#1a1a2e", borderRadius: 16, padding: 35, width: "92%", maxWidth: 950,
        boxShadow: `0 0 60px ${colors.primary}33`, border: `1px solid ${colors.primary}44`,
      }}>
        <div style={{ display: "flex", gap: 8, marginBottom: 20 }}>
          <div style={{ width: 14, height: 14, borderRadius: "50%", background: "#ff5f57" }} />
          <div style={{ width: 14, height: 14, borderRadius: "50%", background: "#febc2e" }} />
          <div style={{ width: 14, height: 14, borderRadius: "50%", background: "#28c840" }} />
        </div>
        <div style={{ fontFamily: "SF Mono, Monaco, monospace", fontSize: 16, lineHeight: 1.7 }}>
          {lines.map((line, i) => {
            const opacity = interpolate(frame, [line.delay, line.delay + 4], [0, 1], { extrapolateRight: "clamp" });
            return (
              <div key={i} style={{ color: line.color, opacity, minHeight: 24 }}>
                {line.text}
              </div>
            );
          })}
        </div>
      </div>
    </AbsoluteFill>
  );
};

// Scene 5: Air-Gap Flow (780-960 = 6s)
const AirGapScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const steps = [
    { label: "Create TX\nOnline", icon: "📝", color: colors.accent },
    { label: "Transfer\nvia QR", icon: "📱", color: colors.text },
    { label: "Sign\nOffline", icon: "🔐", color: colors.primary },
    { label: "Broadcast\nConfirm", icon: "📡", color: colors.secondary },
  ];

  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", flexDirection: "column", padding: 40 }}>
      <h2 style={{
        fontSize: 36, color: colors.text, marginBottom: 60,
        fontFamily: "SF Pro Display, sans-serif",
        opacity: interpolate(frame, [0, 15], [0, 1], { extrapolateRight: "clamp" }),
      }}>
        Air-Gapped Signing Flow
      </h2>
      <div style={{ display: "flex", alignItems: "center", gap: 20 }}>
        {steps.map((step, i) => {
          const scale = spring({ frame: frame - i * 20 - 15, fps, config: { damping: 12 } });
          const arrowOpacity = interpolate(frame, [i * 20 + 25, i * 20 + 35], [0, 1], { extrapolateRight: "clamp" });
          return (
            <div key={i} style={{ display: "flex", alignItems: "center", gap: 20 }}>
              <div style={{
                textAlign: "center", transform: `scale(${Math.min(Math.max(scale, 0), 1)})`,
                opacity: scale > 0 ? 1 : 0,
              }}>
                <div style={{
                  width: 100, height: 100, borderRadius: 20,
                  background: `${step.color}22`, border: `2px solid ${step.color}66`,
                  display: "flex", justifyContent: "center", alignItems: "center",
                  fontSize: 44, marginBottom: 12,
                }}>
                  {step.icon}
                </div>
                <div style={{
                  fontSize: 14, color: step.color, fontFamily: "SF Pro Display, sans-serif",
                  whiteSpace: "pre-line", lineHeight: 1.3,
                }}>
                  {step.label}
                </div>
              </div>
              {i < steps.length - 1 && (
                <div style={{
                  fontSize: 28, color: colors.muted, opacity: arrowOpacity,
                  fontFamily: "SF Mono, monospace",
                }}>
                  →
                </div>
              )}
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

// Scene 6: Feature Grid (960-1200 = 8s)
const FeatureGridScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const features = [
    { title: "Jupiter DEX", desc: "Best swap routes across all Solana DEXes", icon: "💱", color: colors.accent },
    { title: "Pyth Network", desc: "Real-time price feeds & USD valuation", icon: "📊", color: colors.secondary },
    { title: "DAO Governance", desc: "Multi-sig vaults with on-chain voting", icon: "🏛", color: colors.primary },
    { title: "Agent API", desc: "Built for AI treasury management", icon: "🤖", color: "#ff9900" },
  ];

  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", flexDirection: "column", padding: 60 }}>
      <h2 style={{
        fontSize: 40, color: colors.text, marginBottom: 50,
        fontFamily: "SF Pro Display, sans-serif",
        opacity: interpolate(frame, [0, 15], [0, 1], { extrapolateRight: "clamp" }),
      }}>
        Built for the Agent Economy
      </h2>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 30, justifyContent: "center", maxWidth: 900 }}>
        {features.map((f, i) => {
          const scale = spring({ frame: frame - i * 15 - 15, fps, config: { damping: 12 } });
          return (
            <div key={i} style={{
              width: 400, padding: 28, borderRadius: 16,
              background: `${f.color}11`, border: `1px solid ${f.color}44`,
              transform: `scale(${Math.min(Math.max(scale, 0), 1)})`,
              opacity: scale > 0 ? 1 : 0,
            }}>
              <div style={{ fontSize: 36, marginBottom: 10 }}>{f.icon}</div>
              <div style={{ fontSize: 22, fontWeight: 700, color: f.color, marginBottom: 6, fontFamily: "SF Pro Display, sans-serif" }}>
                {f.title}
              </div>
              <div style={{ fontSize: 16, color: colors.muted, fontFamily: "SF Pro Display, sans-serif" }}>
                {f.desc}
              </div>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

// Scene 7: Comparison (1200-1440 = 8s)
const ComparisonScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const rows = [
    { feature: "Air-Gap Security", cold: true, hw: true, hot: false },
    { feature: "Cost", coldVal: "$10", hwVal: "$200+", hotVal: "Free" },
    { feature: "Open Source", cold: true, hw: false, hot: "varies" },
    { feature: "DAO Governance", cold: true, hw: false, hot: false },
    { feature: "Jupiter Swaps", cold: true, hw: false, hot: true },
    { feature: "Agent-Friendly", cold: true, hw: false, hot: "risky" },
  ];

  const headerOpacity = interpolate(frame, [0, 15], [0, 1], { extrapolateRight: "clamp" });

  const renderCell = (val: boolean | string | undefined) => {
    if (val === true) return <span style={{ color: colors.secondary, fontSize: 22 }}>✓</span>;
    if (val === false) return <span style={{ color: colors.danger, fontSize: 22 }}>✗</span>;
    return <span style={{ color: colors.muted, fontSize: 16 }}>{val}</span>;
  };

  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", padding: 60 }}>
      <div style={{
        background: "#1a1a2e", borderRadius: 16, padding: 40, width: "85%", maxWidth: 900,
        border: `1px solid ${colors.primary}33`,
      }}>
        <div style={{
          display: "grid", gridTemplateColumns: "1.5fr 1fr 1fr 1fr",
          gap: "16px 24px", opacity: headerOpacity,
        }}>
          <div style={{ fontSize: 16, color: colors.muted, fontFamily: "SF Pro Display, sans-serif" }} />
          <div style={{ fontSize: 18, fontWeight: 700, color: colors.secondary, textAlign: "center", fontFamily: "SF Pro Display, sans-serif" }}>Coldstar</div>
          <div style={{ fontSize: 18, fontWeight: 700, color: colors.muted, textAlign: "center", fontFamily: "SF Pro Display, sans-serif" }}>Hardware</div>
          <div style={{ fontSize: 18, fontWeight: 700, color: colors.muted, textAlign: "center", fontFamily: "SF Pro Display, sans-serif" }}>Hot Wallet</div>
          {rows.map((row, i) => {
            const rowOpacity = interpolate(frame, [i * 12 + 15, i * 12 + 25], [0, 1], { extrapolateRight: "clamp" });
            return (
              <React.Fragment key={i}>
                <div style={{ fontSize: 17, color: colors.text, opacity: rowOpacity, fontFamily: "SF Pro Display, sans-serif" }}>{row.feature}</div>
                <div style={{ textAlign: "center", opacity: rowOpacity }}>{row.coldVal ? <span style={{ color: colors.secondary, fontSize: 17, fontWeight: 700 }}>{row.coldVal}</span> : renderCell(row.cold)}</div>
                <div style={{ textAlign: "center", opacity: rowOpacity }}>{row.hwVal ? <span style={{ color: colors.danger, fontSize: 17 }}>{row.hwVal}</span> : renderCell(row.hw)}</div>
                <div style={{ textAlign: "center", opacity: rowOpacity }}>{row.hotVal ? <span style={{ color: colors.muted, fontSize: 17 }}>{row.hotVal}</span> : renderCell(row.hot)}</div>
              </React.Fragment>
            );
          })}
        </div>
      </div>
    </AbsoluteFill>
  );
};

// Scene 8: CTA (1440-1800 = 12s)
const CTAScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const scale = spring({ frame, fps, config: { damping: 12 } });
  const urlOpacity = interpolate(frame, [30, 50], [0, 1], { extrapolateRight: "clamp" });
  const buttonOpacity = interpolate(frame, [50, 70], [0, 1], { extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", flexDirection: "column" }}>
      <div style={{ transform: `scale(${scale})`, textAlign: "center" }}>
        <img src={staticFile("coldstar-logo.png")} alt="Coldstar" style={{ height: 120, marginBottom: 20 }} />
        <p style={{
          fontSize: 22, color: colors.secondary, fontFamily: "SF Mono, monospace",
          marginTop: 15, opacity: urlOpacity,
        }}>
          coldstar.dev/colosseum
        </p>
        <p style={{
          fontSize: 16, color: colors.muted, fontFamily: "SF Mono, monospace",
          marginTop: 8, opacity: urlOpacity,
        }}>
          github.com/ExpertVagabond/coldstar-colosseum
        </p>
        <div style={{
          marginTop: 40, padding: "16px 48px",
          background: `linear-gradient(135deg, ${colors.primary}, ${colors.secondary})`,
          borderRadius: 50, fontSize: 22, color: colors.bg, fontWeight: 700,
          fontFamily: "SF Pro Display, sans-serif", opacity: buttonOpacity,
        }}>
          Upvote on Colosseum
        </div>
        <p style={{
          fontSize: 14, color: colors.muted, fontFamily: "SF Pro Display, sans-serif",
          marginTop: 20, opacity: buttonOpacity,
        }}>
          Open Source • $10 USB • Hardware-Grade Security
        </p>
      </div>
    </AbsoluteFill>
  );
};

// Main Video — 60s at 30fps = 1800 frames
export const ColdstarVideo: React.FC = () => {
  return (
    <AbsoluteFill style={{ background: colors.bg }}>
      <AnimatedBackground />
      <Sequence from={0} durationInFrames={90}><IntroScene /></Sequence>
      <Sequence from={90} durationInFrames={150}><ProblemScene /></Sequence>
      <Sequence from={240} durationInFrames={240}><SolutionScene /></Sequence>
      <Sequence from={480} durationInFrames={300}><TerminalScene /></Sequence>
      <Sequence from={780} durationInFrames={180}><AirGapScene /></Sequence>
      <Sequence from={960} durationInFrames={240}><FeatureGridScene /></Sequence>
      <Sequence from={1200} durationInFrames={240}><ComparisonScene /></Sequence>
      <Sequence from={1440} durationInFrames={360}><CTAScene /></Sequence>
    </AbsoluteFill>
  );
};
