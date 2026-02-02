from manim import *

# Solana-inspired colors
SOLANA_PURPLE = "#9945FF"
SOLANA_GREEN = "#14F195"
DARK_BG = "#0f0f0f"

class ColdstarExplainer(Scene):
    def construct(self):
        self.camera.background_color = DARK_BG

        # Title
        title = Text("COLDSTAR", font_size=72, weight=BOLD, color=WHITE)
        subtitle = Text("How Air-Gapped Signing Works", font_size=32, color=SOLANA_GREEN)
        subtitle.next_to(title, DOWN, buff=0.3)

        self.play(Write(title), run_time=1)
        self.play(FadeIn(subtitle), run_time=0.5)
        self.wait(0.5)
        self.play(FadeOut(title), FadeOut(subtitle))

        # Step 1: Key Generation
        step1_title = Text("Step 1: Generate Keypair (Offline)", font_size=28, color=SOLANA_PURPLE)
        step1_title.to_edge(UP, buff=0.5)
        self.play(Write(step1_title))

        # Show private and public key
        private_key = VGroup(
            RoundedRectangle(corner_radius=0.2, width=4, height=1.5, color=SOLANA_PURPLE, fill_opacity=0.2),
            Text("Private Key", font_size=20, color=WHITE),
            Text("🔐", font_size=40),
        )
        private_key[1].move_to(private_key[0].get_top() + DOWN * 0.3)
        private_key[2].move_to(private_key[0].get_center() + DOWN * 0.2)
        private_key.move_to(LEFT * 3)

        public_key = VGroup(
            RoundedRectangle(corner_radius=0.2, width=4, height=1.5, color=SOLANA_GREEN, fill_opacity=0.2),
            Text("Public Key", font_size=20, color=WHITE),
            Text("📢", font_size=40),
        )
        public_key[1].move_to(public_key[0].get_top() + DOWN * 0.3)
        public_key[2].move_to(public_key[0].get_center() + DOWN * 0.2)
        public_key.move_to(RIGHT * 3)

        arrow = Arrow(private_key.get_right(), public_key.get_left(), color=WHITE, buff=0.3)
        arrow_label = Text("derives", font_size=16, color=GRAY).next_to(arrow, UP, buff=0.1)

        self.play(FadeIn(private_key, shift=UP))
        self.wait(0.3)
        self.play(GrowArrow(arrow), Write(arrow_label))
        self.play(FadeIn(public_key, shift=UP))

        # USB drive
        usb = VGroup(
            RoundedRectangle(corner_radius=0.1, width=2, height=1, color=WHITE, fill_opacity=0.1),
            Text("USB", font_size=16, color=WHITE),
        )
        usb[1].move_to(usb[0])
        usb.next_to(private_key, DOWN, buff=0.5)

        self.play(FadeIn(usb))
        self.play(private_key.animate.scale(0.8).move_to(usb.get_center()), run_time=0.5)

        note1 = Text("Private key stored on USB drive", font_size=18, color=GRAY)
        note1.to_edge(DOWN, buff=0.5)
        self.play(Write(note1))
        self.wait(1)

        # Clear for next step
        self.play(
            FadeOut(step1_title), FadeOut(private_key), FadeOut(public_key),
            FadeOut(arrow), FadeOut(arrow_label), FadeOut(usb), FadeOut(note1)
        )

        # Step 2: Create Transaction
        step2_title = Text("Step 2: Create Transaction (Online)", font_size=28, color=SOLANA_GREEN)
        step2_title.to_edge(UP, buff=0.5)
        self.play(Write(step2_title))

        # Transaction data
        tx = VGroup(
            RoundedRectangle(corner_radius=0.2, width=5, height=2.5, color=WHITE, fill_opacity=0.1),
            Text("Transaction", font_size=24, color=WHITE),
            Text("To: ABC...XYZ", font_size=16, color=GRAY),
            Text("Amount: 1 SOL", font_size=16, color=GRAY),
            Text("Status: UNSIGNED", font_size=16, color=SOLANA_PURPLE),
        )
        tx[1].move_to(tx[0].get_top() + DOWN * 0.4)
        tx[2].next_to(tx[1], DOWN, buff=0.3)
        tx[3].next_to(tx[2], DOWN, buff=0.2)
        tx[4].next_to(tx[3], DOWN, buff=0.2)

        self.play(FadeIn(tx, shift=UP))
        self.wait(1)

        # Save to USB
        inbox = Text("→ /inbox/unsigned_tx.json", font_size=18, color=SOLANA_GREEN)
        inbox.next_to(tx, DOWN, buff=0.5)
        self.play(Write(inbox))
        self.wait(1)

        self.play(FadeOut(step2_title), FadeOut(tx), FadeOut(inbox))

        # Step 3: Sign Offline
        step3_title = Text("Step 3: Sign Transaction (OFFLINE)", font_size=28, color=SOLANA_PURPLE)
        step3_title.to_edge(UP, buff=0.5)
        self.play(Write(step3_title))

        # Air gap visualization
        online_zone = VGroup(
            RoundedRectangle(corner_radius=0.3, width=4, height=5, color=RED, fill_opacity=0.05),
            Text("ONLINE", font_size=16, color=RED),
        )
        online_zone[1].move_to(online_zone[0].get_top() + DOWN * 0.3)
        online_zone.move_to(LEFT * 3.5)

        offline_zone = VGroup(
            RoundedRectangle(corner_radius=0.3, width=4, height=5, color=SOLANA_GREEN, fill_opacity=0.1),
            Text("OFFLINE", font_size=16, color=SOLANA_GREEN),
        )
        offline_zone[1].move_to(offline_zone[0].get_top() + DOWN * 0.3)
        offline_zone.move_to(RIGHT * 3.5)

        air_gap = DashedLine(UP * 2, DOWN * 2, color=WHITE, dash_length=0.2)
        gap_label = Text("AIR GAP", font_size=14, color=WHITE).rotate(PI/2)
        gap_label.next_to(air_gap, RIGHT, buff=0.1)

        self.play(FadeIn(online_zone), FadeIn(offline_zone))
        self.play(Create(air_gap), Write(gap_label))

        # USB moves across
        usb2 = VGroup(
            RoundedRectangle(corner_radius=0.1, width=1.5, height=0.8, color=WHITE, fill_opacity=0.2),
            Text("💾", font_size=24),
        )
        usb2[1].move_to(usb2[0])
        usb2.move_to(online_zone.get_center())

        self.play(FadeIn(usb2))
        self.play(usb2.animate.move_to(offline_zone.get_center()), run_time=1)

        # Signing animation
        key_icon = Text("🔐", font_size=40).move_to(offline_zone.get_center() + UP * 0.5)
        tx_icon = Text("📝", font_size=40).move_to(offline_zone.get_center() + DOWN * 0.5)

        self.play(FadeIn(key_icon), FadeIn(tx_icon))

        # Combine into signed tx
        signed = Text("✓ SIGNED", font_size=24, color=SOLANA_GREEN)
        signed.move_to(offline_zone.get_center())

        self.play(
            FadeOut(key_icon), FadeOut(tx_icon),
            FadeIn(signed, scale=1.5),
            Flash(signed, color=SOLANA_GREEN, line_length=0.3)
        )

        self.wait(1)

        # Move USB back
        self.play(usb2.animate.move_to(online_zone.get_center()), run_time=1)

        self.play(
            FadeOut(step3_title), FadeOut(online_zone), FadeOut(offline_zone),
            FadeOut(air_gap), FadeOut(gap_label), FadeOut(usb2), FadeOut(signed)
        )

        # Step 4: Broadcast
        step4_title = Text("Step 4: Broadcast (Online)", font_size=28, color=SOLANA_GREEN)
        step4_title.to_edge(UP, buff=0.5)
        self.play(Write(step4_title))

        # Network visualization
        network = VGroup(
            Circle(radius=1.5, color=SOLANA_GREEN, fill_opacity=0.1),
            Text("SOLANA", font_size=20, color=SOLANA_GREEN),
        )
        network[1].move_to(network[0])

        # Signed tx
        signed_tx = VGroup(
            RoundedRectangle(corner_radius=0.1, width=2, height=1, color=SOLANA_GREEN),
            Text("Signed TX", font_size=14, color=WHITE),
        )
        signed_tx[1].move_to(signed_tx[0])
        signed_tx.move_to(LEFT * 4)

        self.play(FadeIn(network), FadeIn(signed_tx))

        # Broadcast animation
        self.play(signed_tx.animate.move_to(network.get_center()), run_time=1)
        self.play(FadeOut(signed_tx))

        # Confirmation
        confirmed = Text("✓ CONFIRMED", font_size=36, color=SOLANA_GREEN)
        confirmed.next_to(network, DOWN, buff=0.5)

        self.play(
            network[0].animate.set_stroke(SOLANA_GREEN, width=8),
            Write(confirmed),
            Flash(network, color=SOLANA_GREEN, line_length=0.5)
        )

        self.wait(1)

        # Final message
        self.play(FadeOut(step4_title), FadeOut(network), FadeOut(confirmed))

        icon = ImageMobject("coldstar-icon.png").scale(0.4)
        title = Text("COLDSTAR", font_size=48, weight=BOLD, color=WHITE)
        tagline = Text("Private Key Never Touches Network", font_size=24, color=SOLANA_GREEN)
        github = Text("github.com/ChainLabs-Technologies/coldstar", font_size=18, color=GRAY)
        title.next_to(icon, DOWN, buff=0.3)
        tagline.next_to(title, DOWN, buff=0.3)
        github.next_to(tagline, DOWN, buff=0.3)
        final = Group(icon, title, tagline, github)

        self.play(FadeIn(final, shift=UP))
        self.wait(2)


class ColdstarShort(Scene):
    """15 second version for social media"""
    def construct(self):
        self.camera.background_color = DARK_BG

        # Quick intro
        title = Text("COLDSTAR", font_size=72, weight=BOLD, color=WHITE)
        self.play(Write(title), run_time=0.5)
        self.wait(0.3)

        subtitle = Text("$0 Cold Wallet", font_size=36, color=SOLANA_GREEN)
        subtitle.next_to(title, DOWN)
        self.play(FadeIn(subtitle))
        self.wait(0.5)

        # Quick flow
        self.play(FadeOut(title), FadeOut(subtitle))

        flow = VGroup(
            Text("USB 💾", font_size=40),
            Text("→", font_size=40, color=GRAY),
            Text("Sign 🔐", font_size=40),
            Text("→", font_size=40, color=GRAY),
            Text("✓", font_size=50, color=SOLANA_GREEN),
        )
        flow.arrange(RIGHT, buff=0.5)

        for item in flow:
            self.play(FadeIn(item, shift=RIGHT * 0.5), run_time=0.3)

        self.wait(0.5)

        # Tagline
        self.play(FadeOut(flow))

        tagline = Text("Air-Gapped Security\nOn Any USB Drive", font_size=36, color=WHITE)
        self.play(Write(tagline))
        self.wait(1)
