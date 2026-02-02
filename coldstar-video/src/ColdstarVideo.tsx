import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
  Sequence,
  Audio,
  staticFile,
} from "remotion";

// Color scheme - Solana inspired
const colors = {
  bg: "#0f0f0f",
  primary: "#9945FF", // Solana purple
  secondary: "#14F195", // Solana green
  accent: "#00D1FF",
  text: "#ffffff",
  muted: "#888888",
};

// Animated background gradient
const AnimatedBackground: React.FC = () => {
  const frame = useCurrentFrame();
  const gradientRotation = interpolate(frame, [0, 300], [0, 360]);

  return (
    <AbsoluteFill
      style={{
        background: `
          radial-gradient(
            ellipse at ${50 + Math.sin(frame / 50) * 20}% ${50 + Math.cos(frame / 40) * 20}%,
            ${colors.primary}22 0%,
            transparent 50%
          ),
          radial-gradient(
            ellipse at ${50 - Math.sin(frame / 60) * 30}% ${50 - Math.cos(frame / 50) * 30}%,
            ${colors.secondary}15 0%,
            transparent 40%
          ),
          ${colors.bg}
        `,
      }}
    />
  );
};

// Intro Scene
const IntroScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const logoScale = spring({ frame, fps, config: { damping: 12 } });
  const titleOpacity = interpolate(frame, [20, 40], [0, 1], { extrapolateRight: "clamp" });
  const subtitleOpacity = interpolate(frame, [40, 60], [0, 1], { extrapolateRight: "clamp" });

  return (
    <AbsoluteFill
      style={{
        justifyContent: "center",
        alignItems: "center",
        flexDirection: "column",
      }}
    >
      {/* Coldstar Logo */}
      <img
        src={staticFile("coldstar-logo.png")}
        alt="Coldstar"
        style={{
          transform: `scale(${logoScale})`,
          height: 180,
          marginBottom: 30,
          opacity: titleOpacity,
        }}
      />

      {/* Subtitle */}
      <p
        style={{
          fontSize: 28,
          color: colors.secondary,
          opacity: subtitleOpacity,
          fontFamily: "SF Mono, monospace",
          marginTop: 15,
        }}
      >
        Air-Gapped Solana Cold Wallet
      </p>
    </AbsoluteFill>
  );
};

// Problem Scene
const ProblemScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const items = [
    { text: "Hardware wallets cost $100-200+", delay: 0 },
    { text: "Complex setup process", delay: 15 },
    { text: "Proprietary software", delay: 30 },
  ];

  return (
    <AbsoluteFill
      style={{
        justifyContent: "center",
        alignItems: "center",
        flexDirection: "column",
        padding: 60,
      }}
    >
      <h2
        style={{
          fontSize: 48,
          color: colors.muted,
          marginBottom: 50,
          fontFamily: "SF Pro Display, sans-serif",
          opacity: interpolate(frame, [0, 20], [0, 1], { extrapolateRight: "clamp" }),
        }}
      >
        The Problem
      </h2>

      {items.map((item, i) => {
        const itemOpacity = interpolate(
          frame,
          [item.delay + 10, item.delay + 30],
          [0, 1],
          { extrapolateRight: "clamp" }
        );
        const itemX = interpolate(
          frame,
          [item.delay + 10, item.delay + 30],
          [50, 0],
          { extrapolateRight: "clamp" }
        );

        return (
          <div
            key={i}
            style={{
              fontSize: 36,
              color: "#ff4444",
              opacity: itemOpacity,
              transform: `translateX(${itemX}px)`,
              marginBottom: 25,
              fontFamily: "SF Pro Display, sans-serif",
              display: "flex",
              alignItems: "center",
              gap: 15,
            }}
          >
            <span style={{ fontSize: 24 }}>✗</span>
            {item.text}
          </div>
        );
      })}
    </AbsoluteFill>
  );
};

// Solution Scene
const SolutionScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleOpacity = interpolate(frame, [0, 20], [0, 1], { extrapolateRight: "clamp" });

  const features = [
    { text: "Any USB drive = cold wallet", icon: "💾", delay: 20 },
    { text: "Offline transaction signing", icon: "🔐", delay: 40 },
    { text: "Open source & free", icon: "⚡", delay: 60 },
  ];

  return (
    <AbsoluteFill
      style={{
        justifyContent: "center",
        alignItems: "center",
        flexDirection: "column",
        padding: 60,
      }}
    >
      <h2
        style={{
          fontSize: 48,
          color: colors.secondary,
          marginBottom: 50,
          fontFamily: "SF Pro Display, sans-serif",
          opacity: titleOpacity,
        }}
      >
        The Solution: Coldstar
      </h2>

      {features.map((feature, i) => {
        const featureScale = spring({
          frame: frame - feature.delay,
          fps,
          config: { damping: 12 },
        });

        return (
          <div
            key={i}
            style={{
              fontSize: 32,
              color: colors.text,
              transform: `scale(${Math.min(featureScale, 1)})`,
              opacity: featureScale > 0 ? 1 : 0,
              marginBottom: 30,
              fontFamily: "SF Pro Display, sans-serif",
              display: "flex",
              alignItems: "center",
              gap: 20,
            }}
          >
            <span style={{ fontSize: 40 }}>{feature.icon}</span>
            {feature.text}
          </div>
        );
      })}
    </AbsoluteFill>
  );
};

// Terminal Demo Scene
const TerminalScene: React.FC = () => {
  const frame = useCurrentFrame();

  const lines = [
    { text: "$ python3 video_demo.py", delay: 0, color: colors.text },
    { text: "", delay: 10, color: colors.text },
    { text: "✓ Loaded keypair from external drive", delay: 20, color: colors.secondary },
    { text: "✓ Wallet: EY3wWQ7R...uAopD", delay: 35, color: colors.secondary },
    { text: "✓ Balance: 1.0 SOL", delay: 50, color: colors.secondary },
    { text: "", delay: 60, color: colors.text },
    { text: "→ Creating unsigned transaction...", delay: 65, color: colors.accent },
    { text: "✓ Transaction saved to /inbox", delay: 80, color: colors.secondary },
    { text: "", delay: 90, color: colors.text },
    { text: "⚠ SIGNING OFFLINE - KEY NEVER LEAVES DRIVE", delay: 95, color: colors.primary },
    { text: "✓ Transaction signed!", delay: 115, color: colors.secondary },
    { text: "", delay: 125, color: colors.text },
    { text: "→ Broadcasting to Solana Devnet...", delay: 130, color: colors.accent },
    { text: "✓ TRANSACTION CONFIRMED!", delay: 150, color: colors.secondary },
  ];

  return (
    <AbsoluteFill
      style={{
        justifyContent: "center",
        alignItems: "center",
        padding: 40,
      }}
    >
      <div
        style={{
          background: "#1a1a2e",
          borderRadius: 16,
          padding: 40,
          width: "90%",
          maxWidth: 900,
          boxShadow: `0 0 60px ${colors.primary}33`,
          border: `1px solid ${colors.primary}44`,
        }}
      >
        {/* Terminal header */}
        <div
          style={{
            display: "flex",
            gap: 8,
            marginBottom: 25,
          }}
        >
          <div style={{ width: 14, height: 14, borderRadius: "50%", background: "#ff5f57" }} />
          <div style={{ width: 14, height: 14, borderRadius: "50%", background: "#febc2e" }} />
          <div style={{ width: 14, height: 14, borderRadius: "50%", background: "#28c840" }} />
        </div>

        {/* Terminal content */}
        <div style={{ fontFamily: "SF Mono, Monaco, monospace", fontSize: 18, lineHeight: 1.8 }}>
          {lines.map((line, i) => {
            const lineOpacity = interpolate(
              frame,
              [line.delay, line.delay + 5],
              [0, 1],
              { extrapolateRight: "clamp" }
            );

            return (
              <div
                key={i}
                style={{
                  color: line.color,
                  opacity: lineOpacity,
                  minHeight: 28,
                }}
              >
                {line.text}
              </div>
            );
          })}
        </div>
      </div>
    </AbsoluteFill>
  );
};

// Stats Scene
const StatsScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const stats = [
    { label: "Hardware Wallet", value: "$200", color: "#ff4444" },
    { label: "Coldstar", value: "$0", color: colors.secondary },
  ];

  return (
    <AbsoluteFill
      style={{
        justifyContent: "center",
        alignItems: "center",
        gap: 80,
        flexDirection: "row",
      }}
    >
      {stats.map((stat, i) => {
        const scale = spring({
          frame: frame - i * 20,
          fps,
          config: { damping: 10 },
        });

        return (
          <div
            key={i}
            style={{
              textAlign: "center",
              transform: `scale(${Math.min(scale, 1)})`,
              opacity: scale > 0 ? 1 : 0,
            }}
          >
            <div
              style={{
                fontSize: 80,
                fontWeight: 800,
                color: stat.color,
                fontFamily: "SF Pro Display, sans-serif",
              }}
            >
              {stat.value}
            </div>
            <div
              style={{
                fontSize: 24,
                color: colors.muted,
                marginTop: 10,
                fontFamily: "SF Pro Display, sans-serif",
              }}
            >
              {stat.label}
            </div>
          </div>
        );
      })}
    </AbsoluteFill>
  );
};

// Call to Action Scene
const CTAScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const scale = spring({ frame, fps, config: { damping: 12 } });
  const urlOpacity = interpolate(frame, [30, 50], [0, 1], { extrapolateRight: "clamp" });

  return (
    <AbsoluteFill
      style={{
        justifyContent: "center",
        alignItems: "center",
        flexDirection: "column",
      }}
    >
      <div
        style={{
          transform: `scale(${scale})`,
          textAlign: "center",
        }}
      >
        <img src={staticFile("coldstar-logo.png")} alt="Coldstar" style={{ height: 120, marginBottom: 20 }} />
        <p
          style={{
            fontSize: 24,
            color: colors.secondary,
            fontFamily: "SF Mono, monospace",
            marginTop: 15,
            opacity: urlOpacity,
          }}
        >
          github.com/ChainLabs-Technologies/coldstar
        </p>

        <div
          style={{
            marginTop: 50,
            padding: "15px 40px",
            background: `linear-gradient(135deg, ${colors.primary}, ${colors.secondary})`,
            borderRadius: 50,
            fontSize: 22,
            color: colors.bg,
            fontWeight: 700,
            fontFamily: "SF Pro Display, sans-serif",
            opacity: urlOpacity,
          }}
        >
          Open Source • Free • Secure
        </div>
      </div>
    </AbsoluteFill>
  );
};

// Main Video Composition
export const ColdstarVideo: React.FC = () => {
  return (
    <AbsoluteFill style={{ background: colors.bg }}>
      <AnimatedBackground />

      {/* Intro - 0 to 90 frames (3s) */}
      <Sequence from={0} durationInFrames={90}>
        <IntroScene />
      </Sequence>

      {/* Problem - 90 to 180 frames (3s) */}
      <Sequence from={90} durationInFrames={90}>
        <ProblemScene />
      </Sequence>

      {/* Solution - 180 to 300 frames (4s) */}
      <Sequence from={180} durationInFrames={120}>
        <SolutionScene />
      </Sequence>

      {/* Terminal Demo - 300 to 510 frames (7s) */}
      <Sequence from={300} durationInFrames={210}>
        <TerminalScene />
      </Sequence>

      {/* Stats - 510 to 600 frames (3s) */}
      <Sequence from={510} durationInFrames={90}>
        <StatsScene />
      </Sequence>

      {/* CTA - 600 to 720 frames (4s) */}
      <Sequence from={600} durationInFrames={120}>
        <CTAScene />
      </Sequence>
    </AbsoluteFill>
  );
};
