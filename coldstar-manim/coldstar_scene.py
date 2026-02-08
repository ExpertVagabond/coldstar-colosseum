from manim import *

SOLANA_PURPLE = "#9945FF"
SOLANA_GREEN = "#14F195"
ACCENT_BLUE = "#00D1FF"
DARK_BG = "#0f0f0f"


class ColdstarExplainer(Scene):
    """30-second air-gap signing explainer for Colosseum hackathon."""

    def construct(self):
        self.camera.background_color = DARK_BG

        # Title (0-3s)
        title = Text("COLDSTAR", font_size=72, weight=BOLD, color=WHITE)
        subtitle = Text("How Air-Gapped Signing Works", font_size=28, color=SOLANA_GREEN)
        badge = Text("Colosseum Agent Hackathon 2026", font_size=16, color=SOLANA_PURPLE)
        subtitle.next_to(title, DOWN, buff=0.3)
        badge.next_to(subtitle, DOWN, buff=0.3)

        self.play(Write(title), run_time=0.8)
        self.play(FadeIn(subtitle), FadeIn(badge), run_time=0.5)
        self.wait(0.7)
        self.play(FadeOut(title), FadeOut(subtitle), FadeOut(badge))

        # Step 1: Key Generation Offline (3-10s)
        step1 = Text("Step 1: Generate Keys (Offline)", font_size=26, color=SOLANA_PURPLE)
        step1.to_edge(UP, buff=0.5)
        self.play(Write(step1), run_time=0.4)

        usb = VGroup(
            RoundedRectangle(corner_radius=0.15, width=2.5, height=1.2, color=WHITE, fill_opacity=0.1),
            Text("USB Drive", font_size=14, color=WHITE),
            Text("AIR-GAPPED", font_size=10, color=SOLANA_GREEN),
        )
        usb[1].move_to(usb[0].get_center() + UP * 0.2)
        usb[2].move_to(usb[0].get_center() + DOWN * 0.2)
        usb.move_to(LEFT * 3)

        private_key = VGroup(
            RoundedRectangle(corner_radius=0.15, width=3, height=1.2, color=SOLANA_PURPLE, fill_opacity=0.2),
            Text("Private Key", font_size=18, color=WHITE),
        )
        private_key[1].move_to(private_key[0])
        private_key.move_to(ORIGIN)

        public_key = VGroup(
            RoundedRectangle(corner_radius=0.15, width=3, height=1.2, color=SOLANA_GREEN, fill_opacity=0.2),
            Text("Public Key", font_size=18, color=WHITE),
        )
        public_key[1].move_to(public_key[0])
        public_key.move_to(RIGHT * 3)

        self.play(FadeIn(usb, shift=UP))
        self.play(FadeIn(private_key, shift=UP))

        arrow = Arrow(private_key.get_right(), public_key.get_left(), color=WHITE, buff=0.2)
        self.play(GrowArrow(arrow), FadeIn(public_key, shift=UP))

        # Key stays on USB
        self.play(private_key.animate.scale(0.7).move_to(usb.get_center()), run_time=0.5)

        note = Text("Private key never leaves USB", font_size=16, color=GRAY)
        note.to_edge(DOWN, buff=0.5)
        self.play(Write(note), run_time=0.4)
        self.wait(0.8)

        self.play(FadeOut(step1), FadeOut(usb), FadeOut(private_key),
                  FadeOut(public_key), FadeOut(arrow), FadeOut(note))

        # Step 2: Create TX Online (10-17s)
        step2 = Text("Step 2: Create Transaction (Online)", font_size=26, color=ACCENT_BLUE)
        step2.to_edge(UP, buff=0.5)
        self.play(Write(step2), run_time=0.4)

        tx = VGroup(
            RoundedRectangle(corner_radius=0.2, width=5, height=2.2, color=WHITE, fill_opacity=0.08),
            Text("Jupiter Swap", font_size=22, color=ACCENT_BLUE),
            Text("1 SOL → USDC", font_size=16, color=GRAY),
            Text("Route: Raydium (best rate)", font_size=14, color=GRAY),
            Text("Status: UNSIGNED", font_size=16, color=SOLANA_PURPLE, weight=BOLD),
        )
        tx[1].move_to(tx[0].get_top() + DOWN * 0.4)
        tx[2].next_to(tx[1], DOWN, buff=0.2)
        tx[3].next_to(tx[2], DOWN, buff=0.15)
        tx[4].next_to(tx[3], DOWN, buff=0.2)

        self.play(FadeIn(tx, shift=UP))

        qr = VGroup(
            Square(side_length=1.2, color=WHITE, fill_opacity=0.1),
            Text("QR", font_size=20, color=WHITE),
        )
        qr[1].move_to(qr[0])
        qr.next_to(tx, DOWN, buff=0.4)

        transfer_label = Text("Transfer via QR code", font_size=14, color=SOLANA_GREEN)
        transfer_label.next_to(qr, DOWN, buff=0.15)

        self.play(FadeIn(qr), Write(transfer_label))
        self.wait(0.8)

        self.play(FadeOut(step2), FadeOut(tx), FadeOut(qr), FadeOut(transfer_label))

        # Step 3: Sign Offline (17-24s)
        step3 = Text("Step 3: Sign (OFFLINE)", font_size=26, color=SOLANA_PURPLE)
        step3.to_edge(UP, buff=0.5)
        self.play(Write(step3), run_time=0.4)

        # Air gap visualization
        online_zone = VGroup(
            RoundedRectangle(corner_radius=0.3, width=3.5, height=4, color=RED, fill_opacity=0.04),
            Text("ONLINE", font_size=14, color=RED),
        )
        online_zone[1].move_to(online_zone[0].get_top() + DOWN * 0.3)
        online_zone.move_to(LEFT * 3)

        offline_zone = VGroup(
            RoundedRectangle(corner_radius=0.3, width=3.5, height=4, color=SOLANA_GREEN, fill_opacity=0.08),
            Text("OFFLINE", font_size=14, color=SOLANA_GREEN),
        )
        offline_zone[1].move_to(offline_zone[0].get_top() + DOWN * 0.3)
        offline_zone.move_to(RIGHT * 3)

        air_gap = DashedLine(UP * 1.8, DOWN * 1.8, color=WHITE, dash_length=0.15)
        gap_label = Text("AIR GAP", font_size=12, color=WHITE).rotate(PI / 2)
        gap_label.next_to(air_gap, RIGHT, buff=0.08)

        self.play(FadeIn(online_zone), FadeIn(offline_zone))
        self.play(Create(air_gap), Write(gap_label))

        # USB crosses the gap
        usb2 = VGroup(
            RoundedRectangle(corner_radius=0.1, width=1.2, height=0.6, color=WHITE, fill_opacity=0.2),
            Text("USB", font_size=12, color=WHITE),
        )
        usb2[1].move_to(usb2[0])
        usb2.move_to(online_zone.get_center())

        self.play(FadeIn(usb2))
        self.play(usb2.animate.move_to(offline_zone.get_center()), run_time=0.8)

        signed = Text("SIGNED", font_size=22, color=SOLANA_GREEN, weight=BOLD)
        signed.move_to(offline_zone.get_center() + DOWN * 0.8)
        self.play(FadeIn(signed, scale=1.5), Flash(signed, color=SOLANA_GREEN, line_length=0.2))

        # USB back
        self.play(usb2.animate.move_to(online_zone.get_center()), run_time=0.8)
        self.wait(0.3)

        self.play(FadeOut(step3), FadeOut(online_zone), FadeOut(offline_zone),
                  FadeOut(air_gap), FadeOut(gap_label), FadeOut(usb2), FadeOut(signed))

        # Step 4: Broadcast (24-28s)
        step4 = Text("Step 4: Broadcast", font_size=26, color=SOLANA_GREEN)
        step4.to_edge(UP, buff=0.5)
        self.play(Write(step4), run_time=0.4)

        network = VGroup(
            Circle(radius=1.2, color=SOLANA_GREEN, fill_opacity=0.08),
            Text("SOLANA", font_size=18, color=SOLANA_GREEN),
        )
        network[1].move_to(network[0])

        signed_tx = VGroup(
            RoundedRectangle(corner_radius=0.1, width=1.8, height=0.8, color=SOLANA_GREEN),
            Text("Signed TX", font_size=12, color=WHITE),
        )
        signed_tx[1].move_to(signed_tx[0])
        signed_tx.move_to(LEFT * 4)

        self.play(FadeIn(network), FadeIn(signed_tx))
        self.play(signed_tx.animate.move_to(network.get_center()), run_time=0.6)
        self.play(FadeOut(signed_tx))

        confirmed = Text("CONFIRMED", font_size=32, color=SOLANA_GREEN, weight=BOLD)
        confirmed.next_to(network, DOWN, buff=0.4)
        self.play(
            network[0].animate.set_stroke(SOLANA_GREEN, width=6),
            Write(confirmed),
            Flash(network, color=SOLANA_GREEN, line_length=0.4),
        )
        self.wait(0.5)

        self.play(FadeOut(step4), FadeOut(network), FadeOut(confirmed))

        # CTA (28-30s)
        title_final = Text("COLDSTAR", font_size=48, weight=BOLD, color=WHITE)
        tagline = Text("$10 USB. Hardware-Grade Security.", font_size=22, color=SOLANA_GREEN)
        url1 = Text("coldstar.dev/colosseum", font_size=16, color=ACCENT_BLUE)
        url2 = Text("github.com/ExpertVagabond/coldstar-colosseum", font_size=14, color=GRAY)
        cta = Text("Upvote on Colosseum", font_size=18, color=SOLANA_PURPLE)

        tagline.next_to(title_final, DOWN, buff=0.3)
        url1.next_to(tagline, DOWN, buff=0.4)
        url2.next_to(url1, DOWN, buff=0.15)
        cta.next_to(url2, DOWN, buff=0.4)

        final = VGroup(title_final, tagline, url1, url2, cta)
        self.play(FadeIn(final, shift=UP))
        self.wait(2)


class ColdstarShort(Scene):
    """15-second version for social media."""

    def construct(self):
        self.camera.background_color = DARK_BG

        title = Text("COLDSTAR", font_size=72, weight=BOLD, color=WHITE)
        self.play(Write(title), run_time=0.5)
        self.wait(0.3)

        subtitle = Text("$10 Air-Gapped Wallet", font_size=32, color=SOLANA_GREEN)
        subtitle.next_to(title, DOWN)
        self.play(FadeIn(subtitle))
        self.wait(0.5)

        self.play(FadeOut(title), FadeOut(subtitle))

        flow = VGroup(
            Text("USB", font_size=36),
            Text("→", font_size=36, color=GRAY),
            Text("Sign Offline", font_size=36),
            Text("→", font_size=36, color=GRAY),
            Text("Swap via Jupiter", font_size=36, color=ACCENT_BLUE),
            Text("→", font_size=36, color=GRAY),
            Text("Confirmed", font_size=36, color=SOLANA_GREEN),
        )
        flow.arrange(RIGHT, buff=0.3)
        flow.scale_to_fit_width(12)

        for item in flow:
            self.play(FadeIn(item, shift=RIGHT * 0.5), run_time=0.25)

        self.wait(0.5)
        self.play(FadeOut(flow))

        tagline = Text("Air-Gapped Security\nOn Any USB Drive", font_size=36, color=WHITE)
        url = Text("coldstar.dev/colosseum", font_size=20, color=ACCENT_BLUE)
        url.next_to(tagline, DOWN, buff=0.4)

        self.play(Write(tagline), run_time=0.5)
        self.play(FadeIn(url))
        self.wait(1)
