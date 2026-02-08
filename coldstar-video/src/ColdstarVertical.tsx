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
            ellipse at ${50 + Math.sin(frame / 50) * 20}% ${30 + Math.cos(frame / 40) * 15}%,
            ${colors.primary}22 0%, transparent 50%
          ),
          radial-gradient(
            ellipse at ${50 - Math.sin(frame / 60) * 25}% ${70 - Math.cos(frame / 50) * 15}%,
            ${colors.secondary}15 0%, transparent 40%
          ),
          ${colors.bg}
        `,
      }}
    />
  );
};

// Hook/Intro (0-60 = 2s)
const HookScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const scale = spring({ frame, fps, config: { damping: 12 } });
  const textOpacity = interpolate(frame, [15, 30], [0, 1], { extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", flexDirection: "column", padding: 40 }}>
      <img
        src={staticFile("coldstar-logo.png")}
        alt="Coldstar"
        style={{ height: 100, transform: `scale(${scale})`, marginBottom: 30 }}
      />
      <p style={{
        fontSize: 36, color: colors.secondary, opacity: textOpacity,
        fontFamily: "SF Mono, monospace", textAlign: "center",
      }}>
        Air-Gapped Wallet
      </p>
    </AbsoluteFill>
  );
};

// Problem: $200 (60-120 = 2s)
const ProblemScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const priceScale = spring({ frame: frame - 10, fps, config: { damping: 10 } });

  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", flexDirection: "column", padding: 40 }}>
      <p style={{ fontSize: 28, color: colors.muted, fontFamily: "SF Pro Display, sans-serif", marginBottom: 20 }}>
        Hardware wallets cost
      </p>
      <div style={{
        fontSize: 120, fontWeight: 800, color: colors.danger,
        fontFamily: "SF Pro Display, sans-serif",
        transform: `scale(${Math.min(priceScale, 1)})`,
      }}>
        $200
      </div>
    </AbsoluteFill>
  );
};

// Solution: $10 (120-180 = 2s)
const SolutionScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const priceScale = spring({ frame: frame - 10, fps, config: { damping: 10 } });

  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", flexDirection: "column", padding: 40 }}>
      <p style={{ fontSize: 28, color: colors.muted, fontFamily: "SF Pro Display, sans-serif", marginBottom: 20 }}>
        Coldstar costs
      </p>
      <div style={{
        fontSize: 140, fontWeight: 800, color: colors.secondary,
        fontFamily: "SF Pro Display, sans-serif",
        transform: `scale(${Math.min(priceScale, 1)})`,
      }}>
        $10
      </div>
    </AbsoluteFill>
  );
};

// USB = Cold Wallet (180-270 = 3s)
const USBScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const iconScale = spring({ frame, fps, config: { damping: 12 } });
  const textOpacity = interpolate(frame, [20, 40], [0, 1], { extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", flexDirection: "column", padding: 40 }}>
      <div style={{ fontSize: 120, transform: `scale(${iconScale})`, marginBottom: 30 }}>
        💾
      </div>
      <p style={{
        fontSize: 32, color: colors.text, fontFamily: "SF Pro Display, sans-serif",
        textAlign: "center", opacity: textOpacity, lineHeight: 1.4,
      }}>
        Any USB drive
        <br />
        <span style={{ color: colors.primary, fontWeight: 700 }}>= Cold Wallet</span>
      </p>
    </AbsoluteFill>
  );
};

// Flow: Store → Sign → Swap → Confirm (270-420 = 5s)
const FlowScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const steps = [
    { icon: "💾", label: "Store Keys", delay: 0 },
    { icon: "🔐", label: "Sign Offline", delay: 20 },
    { icon: "💱", label: "Jupiter Swap", delay: 40 },
    { icon: "✓", label: "Confirmed", delay: 60 },
  ];

  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", flexDirection: "column", gap: 35, padding: 40 }}>
      {steps.map((step, i) => {
        const scale = spring({ frame: frame - step.delay, fps, config: { damping: 12 } });
        return (
          <div key={i} style={{
            display: "flex", alignItems: "center", gap: 20,
            transform: `scale(${Math.min(Math.max(scale, 0), 1)})`,
            opacity: scale > 0 ? 1 : 0,
          }}>
            <span style={{ fontSize: 52 }}>{step.icon}</span>
            <span style={{ fontSize: 32, color: colors.text, fontFamily: "SF Pro Display, sans-serif" }}>
              {step.label}
            </span>
          </div>
        );
      })}
    </AbsoluteFill>
  );
};

// Security (420-480 = 2s)
const SecurityScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const scale = spring({ frame, fps, config: { damping: 12 } });
  const textOpacity = interpolate(frame, [15, 30], [0, 1], { extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", flexDirection: "column", padding: 40 }}>
      <div style={{ fontSize: 100, transform: `scale(${scale})`, marginBottom: 30 }}>
        🔐
      </div>
      <p style={{
        fontSize: 28, color: colors.text, fontFamily: "SF Pro Display, sans-serif",
        textAlign: "center", opacity: textOpacity, lineHeight: 1.6,
      }}>
        Private key
        <br />
        <span style={{ color: colors.secondary, fontWeight: 700, fontSize: 36 }}>NEVER</span>
        <br />
        touches network
      </p>
    </AbsoluteFill>
  );
};

// CTA (480-540 = 2s)
const CTAScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const scale = spring({ frame, fps, config: { damping: 12 } });

  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", flexDirection: "column", padding: 40 }}>
      <div style={{ transform: `scale(${scale})`, textAlign: "center" }}>
        <img src={staticFile("coldstar-logo.png")} alt="Coldstar" style={{ height: 90, marginBottom: 20 }} />
        <p style={{ fontSize: 18, color: colors.secondary, fontFamily: "SF Mono, monospace", marginTop: 15 }}>
          coldstar.dev/colosseum
        </p>
        <div style={{
          marginTop: 30, padding: "14px 36px",
          background: `linear-gradient(135deg, ${colors.primary}, ${colors.secondary})`,
          borderRadius: 50, fontSize: 20, color: colors.bg, fontWeight: 700,
          fontFamily: "SF Pro Display, sans-serif",
        }}>
          Upvote on Colosseum
        </div>
      </div>
    </AbsoluteFill>
  );
};

// Main Vertical Video — 18s at 30fps = 540 frames
export const ColdstarVertical: React.FC = () => {
  return (
    <AbsoluteFill style={{ background: colors.bg }}>
      <AnimatedBackground />
      <Sequence from={0} durationInFrames={60}><HookScene /></Sequence>
      <Sequence from={60} durationInFrames={60}><ProblemScene /></Sequence>
      <Sequence from={120} durationInFrames={60}><SolutionScene /></Sequence>
      <Sequence from={180} durationInFrames={90}><USBScene /></Sequence>
      <Sequence from={270} durationInFrames={150}><FlowScene /></Sequence>
      <Sequence from={420} durationInFrames={60}><SecurityScene /></Sequence>
      <Sequence from={480} durationInFrames={60}><CTAScene /></Sequence>
    </AbsoluteFill>
  );
};
