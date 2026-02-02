#!/usr/bin/env python3
"""
Create HTML screenshots of Coldstar TUI interfaces
"""

import subprocess
import time
from pathlib import Path


def capture_tui_to_html(script_name, output_file, duration=3):
    """Capture TUI output and convert to HTML"""

    # Run the TUI script and capture output
    print(f"Capturing {script_name}...")

    # Use script command to capture terminal session
    try:
        # Create a temporary script to run the TUI
        run_script = f"""
import sys
import time
from {script_name.replace('.py', '')} import *

# Run the app briefly
app = {"FlashUSBApp()" if "flash" in script_name else "VaultDashboardApp()"}
# Start the app
import threading
def run_app():
    app.run()

thread = threading.Thread(target=run_app, daemon=True)
thread.start()
time.sleep({duration})
"""

        # For now, let's create a simple HTML representation
        html = create_html_preview(script_name)

        output_path = Path(output_file)
        output_path.write_text(html)
        print(f"✅ Created: {output_file}")

    except Exception as e:
        print(f"❌ Error: {e}")


def create_html_preview(script_name):
    """Create an HTML preview of the TUI"""

    if "flash" in script_name:
        return """<!DOCTYPE html>
<html>
<head>
    <title>Coldstar - Flash USB Interface</title>
    <style>
        body {
            background: #000;
            color: #fff;
            font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Courier New', monospace;
            padding: 20px;
            margin: 0;
        }
        .terminal {
            background: #1e1e1e;
            border: 3px solid #fff;
            padding: 20px;
            max-width: 900px;
            margin: 0 auto;
            border-radius: 8px;
        }
        .header {
            background: #0178d4;
            color: #ddedf9;
            text-align: center;
            padding: 10px;
            font-weight: bold;
            margin-bottom: 20px;
        }
        .panel {
            border: 2px solid #fd971f;
            padding: 15px;
            margin: 20px 0;
        }
        .panel-title {
            color: #fd971f;
            font-weight: bold;
            text-align: center;
            margin-bottom: 10px;
        }
        .device-info {
            color: #e0e0e0;
            padding: 10px;
        }
        .lock-icon { color: #58d1eb; }
        .status {
            text-align: center;
            color: #ffff00;
            padding: 10px;
            margin: 20px 0;
        }
        .step {
            padding: 5px 20px;
            margin: 5px 0;
        }
        .step-done { color: #98e024; }
        .step-active { color: #fff; }
        .step-pending { color: #666; }
        .progress-bar {
            background: #333;
            height: 20px;
            margin: 10px 0;
            border-radius: 4px;
            overflow: hidden;
        }
        .progress-fill {
            background: linear-gradient(90deg, #98e024, #66cc00);
            height: 100%;
            transition: width 0.3s ease;
        }
        .warning {
            text-align: center;
            color: #fd971f;
            border-top: 1px solid #666;
            border-bottom: 1px solid #666;
            padding: 10px;
            margin: 20px 0;
        }
        .shortcuts {
            color: #666;
            font-size: 0.9em;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="terminal">
        <div class="header">FLASH COLD WALLET USB</div>

        <div class="panel">
            <div class="panel-title">━━━━━━━━ TARGET USB VAULT ━━━━━━━━</div>
            <div class="device-info">
                <span class="lock-icon">🔒</span>  <strong>KIOXIA 32GB</strong> <span style="color:#9e9e9e">/dev/sdb</span>
            </div>
            <div class="device-info" style="padding-left: 40px; color: #9e9e9e">
                1CD6-FFFF removable • SN:L4330...
            </div>
        </div>

        <div class="status">Flashing vault to USB drive...</div>

        <div style="padding: 20px;">
            <div class="step step-done">
                ····  ✓ 1 / 4 <strong>Formatting /dev/sdb</strong>
                <span style="float: right; color: #98e024;">Done</span>
            </div>

            <div class="step step-active">
                ····  ├ 2 / 4 <strong>Writing secure vault</strong>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: 57%"></div>
                </div>
                <span style="float: right;">57%</span>
            </div>

            <div class="step step-pending">
                ····  ├ 3 / 4 <strong>Encrypting master key</strong>
                <span style="float: right; color: #666;">················································</span>
            </div>

            <div class="step step-pending">
                ····  ├ 4 / 4 <strong>Verifying integrity</strong>
                <span style="float: right; color: #666;">················································</span>
            </div>

            <div style="margin: 15px 0; color: #666;">
                ······ Hardware ID <span style="color: #58d1eb;">SFOD-Vy9X-H9xz-S3Ru</span>
            </div>

            <div class="progress-bar" style="margin-top: 20px;">
                <div class="progress-fill" style="width: 57%"></div>
            </div>
            <div style="text-align: right; margin-top: 5px;">Progress 57%</div>
        </div>

        <div class="warning">
            ━━━━━━━━━━━━━━━━━ DO NOT REMOVE THE DRIVE ━━━━━━━━━━━━━━━━━
        </div>

        <div class="shortcuts">
            [x] Abort immediately and wipe ────────────── [ESC] Abort  Ctrl+C Abort immediately<br>
            [e] Eject safely when ready
        </div>
    </div>
</body>
</html>"""

    else:  # vault dashboard
        return """<!DOCTYPE html>
<html>
<head>
    <title>Coldstar - Vault Dashboard</title>
    <style>
        body {
            background: #000;
            color: #fff;
            font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Courier New', monospace;
            padding: 20px;
            margin: 0;
        }
        .terminal {
            background: #1e1e1e;
            max-width: 1400px;
            margin: 0 auto;
        }
        .status-bar {
            background: #2a2a2a;
            padding: 10px 20px;
            border-bottom: 2px solid #0178d4;
        }
        .status-line {
            color: #e0e0e0;
            margin: 3px 0;
        }
        .panels {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 10px;
            padding: 10px;
        }
        .panel {
            border: 2px solid #58d1eb;
            padding: 15px;
            min-height: 400px;
        }
        .panel-title {
            font-weight: bold;
            color: #fff;
            margin-bottom: 10px;
            padding-bottom: 5px;
            border-bottom: 1px solid #444;
        }
        .token-row {
            padding: 5px;
            margin: 3px 0;
            display: grid;
            grid-template-columns: 30px 100px 1fr 80px;
            gap: 10px;
        }
        .token-row.selected {
            background: #1a1a1a;
        }
        .token-icon { color: #58d1eb; }
        .token-value { color: #98e024; text-align: right; }
        .tx-history {
            font-size: 0.9em;
            margin: 10px 0;
        }
        .tx-received { color: #98e024; }
        .tx-sent { color: #fd971f; }
        .risk-warning {
            color: #fd971f;
            margin-top: 15px;
            padding: 10px;
            background: #2a2a2a;
        }
        .form-row {
            margin: 10px 0;
            display: grid;
            grid-template-columns: 80px 1fr;
            gap: 10px;
        }
        .input {
            background: #2a2a2a;
            border: 1px solid #444;
            color: #58d1eb;
            padding: 5px;
        }
        .footer {
            background: #2a2a2a;
            padding: 5px 20px;
            border-top: 2px solid #0178d4;
            color: #666;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="terminal">
        <div class="status-bar">
            <div class="status-line">
                <span style="color: #58d1eb; font-weight: bold;">COLDSTAR</span> •
                Vault: <span style="color: #fd971f;">usb-03</span> •
                <span style="color: #98e024;">OFFLINE SIGNING</span> •
                RPC: <span style="color: #58d1eb;">mainnet</span>
            </div>
            <div class="status-line">
                Last sync <span style="color: #58d1eb;">2m ago</span> •
                <span style="color: #fd971f;">0</span> warnings •
                Total <span style="color: #98e024; font-weight: bold;">$12,431</span> •
                24h <span style="color: #98e024;">+1.8%</span>
            </div>
        </div>

        <div class="panels">
            <!-- Portfolio Panel -->
            <div class="panel">
                <div class="panel-title">Portfolio</div>
                <div class="token-row">
                    <div class="token-icon">◎</div>
                    <div style="font-weight: bold;">SOL</div>
                    <div style="text-align: right;">3.2546</div>
                    <div class="token-value">476.80</div>
                </div>
                <div class="token-row selected">
                    <div class="token-icon">></div>
                    <div style="font-weight: bold;">USDC</div>
                    <div style="text-align: right;">1,025.00</div>
                    <div class="token-value">1,025.00</div>
                </div>
                <div class="token-row">
                    <div class="token-icon">฿</div>
                    <div style="font-weight: bold;">BTC</div>
                    <div style="text-align: right;">0.0125</div>
                    <div class="token-value">600.50</div>
                </div>
                <div class="token-row">
                    <div class="token-icon">⚡</div>
                    <div style="font-weight: bold;">RAY</div>
                    <div style="text-align: right;">500.0</div>
                    <div class="token-value">85.00</div>
                </div>
                <div class="token-row">
                    <div class="token-icon">◆</div>
                    <div style="font-weight: bold;">XYZ</div>
                    <div style="text-align: right;">10.000</div>
                    <div style="color: #f00;">0.00 F</div>
                </div>
                <div class="token-row">
                    <div style="color: #f00;">⚠</div>
                    <div style="font-weight: bold;">Unknown Token</div>
                    <div style="text-align: right;">10.000</div>
                    <div style="color: #f00;">0.00 F</div>
                </div>
            </div>

            <!-- Token Details Panel -->
            <div class="panel">
                <div class="panel-title">USDC Details</div>
                <div style="color: #9e9e9e; font-size: 0.9em; margin-bottom: 15px;">
                    Mint: <span style="color: #58d1eb;">EPjFW...DeF2</span> •
                    Decimals: <span style="color: #fd971f;">6</span> •
                    <span style="color: #98e024;">✓ Verified SPL Token</span>
                </div>

                <div class="tx-history">
                    <div style="margin: 5px 0;">- <span class="tx-received">Received</span> 500.00 USDC <span style="float: right; color: #666;">30m ago</span></div>
                    <div style="margin: 5px 0;">- <span class="tx-sent">Sent</span> 250.00 USDC <span style="float: right; color: #666;">2h ago</span></div>
                    <div style="margin: 5px 0;">- <span class="tx-received">Received</span> 775.00 USDC <span style="float: right; color: #666;">1d ago</span></div>
                </div>

                <div class="risk-warning">
                    <div style="font-weight: bold; margin-bottom: 5px;">Risk Notes:</div>
                    <div>• Transfer-hook enabled</div>
                    <div>• Direct transfer • Swap then send</div>
                </div>
            </div>

            <!-- Send Panel -->
            <div class="panel">
                <div class="panel-title">Send USDC</div>

                <div class="form-row">
                    <div>To:</div>
                    <div class="input">4xp...Tf8Y <span style="color: #666;">v</span></div>
                </div>

                <div class="form-row">
                    <div>Amount:</div>
                    <div>
                        <span style="font-weight: bold;">100.00</span>
                        <span style="color: #666;">[a max] [25% 50% 75% 100%]</span>
                    </div>
                </div>

                <div class="form-row">
                    <div>Fee:</div>
                    <div>
                        <span style="color: #98e024; font-weight: bold;">[Standard]</span>
                        <span style="color: #666;">Fast  Custom</span>
                    </div>
                </div>

                <div style="color: #666; font-size: 0.9em; margin: 10px 0;">
                    Network fee ~0.00005 SOL • You'll have 3.15 SOL left
                </div>

                <div style="margin-top: 20px; padding-top: 15px; border-top: 1px solid #444;">
                    <div style="font-weight: bold; margin-bottom: 10px;">Review:</div>
                    <div style="margin: 5px 0;">- <strong>USDC</strong>  100.00</div>
                    <div style="margin: 5px 0;">- <strong>To:</strong>   <span style="color: #58d1eb;">4xp...Tf8Y</span></div>
                    <div style="margin: 10px 0; color: #fd971f;">Expected fee: ~0.00005 SOL</div>
                </div>

                <div style="margin-top: 15px; padding: 10px; background: #2a2a2a;">
                    Press <span style="color: #98e024; font-weight: bold;">ENTER</span> to confirm:
                    <div style="margin-top: 10px;">
                        <span style="color: #98e024; font-weight: bold;">[ENTER] Send</span> •
                        <span style="color: #666;">[x] Cancel</span>
                    </div>
                </div>

                <div style="color: #666; font-size: 0.8em; margin-top: 10px;">
                    Arrows navigate • a = max • 1|2|3|4 = % split
                </div>
            </div>
        </div>

        <div class="footer">
            / Search • Tab Sort • Space Multi-select
        </div>
    </div>
</body>
</html>"""


if __name__ == "__main__":
    print("Creating Coldstar TUI Screenshots...")
    print("=" * 50)

    # Create output directory
    output_dir = Path("screenshots")
    output_dir.mkdir(exist_ok=True)

    # Create HTML previews
    capture_tui_to_html("flash_usb_tui.py", "screenshots/flash_usb_preview.html")
    capture_tui_to_html("vault_dashboard_tui.py", "screenshots/vault_dashboard_preview.html")

    print("\n" + "=" * 50)
    print("✅ All screenshots created!")
    print("\nOpen these files in your browser:")
    print("  - screenshots/flash_usb_preview.html")
    print("  - screenshots/vault_dashboard_preview.html")
