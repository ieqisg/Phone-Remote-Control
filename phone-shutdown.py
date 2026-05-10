from flask import Flask, request, render_template_string, abort
import os

app = Flask(__name__)

# 🔐 CHANGE THIS TOKEN
SECRET_TOKEN = "change-this-to-something-long-and-random"

HTML = """
<!doctype html>
<html>
<head>
    <title>Remote Power Control</title>
    <style>
        * { box-sizing: border-box; }
        body {
            font-family: sans-serif;
            text-align: center;
            margin: 0;
            padding: 40px 20px;
            background: #f4f4f4;
        }
        h2 { margin-bottom: 30px; }

        .panels {
            display: flex;
            justify-content: center;
            gap: 30px;
            flex-wrap: wrap;
        }

        .card {
            background: white;
            border-radius: 12px;
            padding: 28px 32px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            min-width: 260px;
        }
        .card h3 {
            margin: 0 0 20px 0;
            font-size: 16px;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: #555;
        }

        /* Instant controls */
        .instant-controls {
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        .instant-controls button {
            font-size: 17px;
            padding: 12px 20px;
            cursor: pointer;
            border: 1px solid #ddd;
            border-radius: 8px;
            background: #fff;
            transition: background 0.15s;
        }
        .instant-controls button:hover { background: #f0f0f0; }

        /* Scheduled shutdown */
        .scheduled-controls {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 14px;
        }
        .scheduled-controls input[type=number] {
            font-size: 22px;
            padding: 12px;
            width: 130px;
            text-align: center;
            border: 1px solid #aaa;
            border-radius: 8px;
        }
        .scheduled-controls .label {
            font-size: 13px;
            color: #888;
            margin-top: -8px;
        }
        .scheduled-controls button {
            font-size: 17px;
            padding: 12px 24px;
            cursor: pointer;
            border-radius: 8px;
            border: none;
            width: 100%;
        }
        #schedule-btn {
            background: #3498db;
            color: white;
        }
        #schedule-btn:hover { background: #2980b9; }
        #cancel-btn {
            background: #e74c3c;
            color: white;
            display: none;
        }
        #cancel-btn:hover { background: #c0392b; }

        /* Toast */
        #toast {
            visibility: hidden;
            min-width: 220px;
            background-color: #333;
            color: #fff;
            text-align: center;
            border-radius: 8px;
            padding: 14px 24px;
            position: fixed;
            bottom: 40px;
            left: 50%;
            transform: translateX(-50%);
            font-size: 16px;
            z-index: 999;
            opacity: 0;
            transition: opacity 0.4s ease;
        }
        #toast.show {
            visibility: visible;
            opacity: 1;
        }
    </style>
</head>
<body>
    <h2>PC Control Panel</h2>

    <div class="panels">

        <!-- Instant Controls -->
        <div class="card">
            <h3>⚡ Instant</h3>
            <div class="instant-controls">
                <button onclick="confirmAction('lock')">🔒 Lock</button>
                <button onclick="confirmAction('suspend')">💤 Suspend</button>
                <button onclick="confirmAction('reboot')">🔄 Reboot</button>
                <button onclick="confirmAction('shutdown')">⏻ Shutdown</button>
            </div>
        </div>

        <!-- Scheduled Shutdown -->
        <div class="card">
            <h3>⏱ Scheduled Shutdown</h3>
            <div class="scheduled-controls">
                <input
                    type="number"
                    id="minutes-input"
                    min="1"
                    max="1440"
                    placeholder="0"
                />
                <span class="label">minutes from now</span>
                <button id="schedule-btn" onclick="scheduleShutdown()">Schedule Shutdown</button>
                <button id="cancel-btn" onclick="cancelShutdown()">Cancel Scheduled Shutdown</button>
            </div>
        </div>

    </div>

    <div id="toast"></div>

    <script>
        const labels = {
            lock: "Lock the session",
            suspend: "Suspend the PC",
            reboot: "Reboot the PC",
            shutdown: "Shut down the PC"
        };

        function confirmAction(cmd) {
            const label = labels[cmd] || cmd;
            if (!confirm("Are you sure you want to: " + label + "?")) return;

            fetch("/action", {
                method: "POST",
                headers: { "Content-Type": "application/x-www-form-urlencoded" },
                body: "token={{ token }}&cmd=" + encodeURIComponent(cmd)
            })
            .then(res => {
                if (res.ok) showToast("✅ Command sent: " + label);
                else showToast("❌ Failed (status " + res.status + ")");
            })
            .catch(() => showToast("❌ Network error"));
        }

        function scheduleShutdown() {
            const input = document.getElementById("minutes-input");
            const minutes = parseInt(input.value);

            if (!minutes || minutes < 1) {
                showToast("⚠️ Enter a valid number of minutes");
                return;
            }

            if (!confirm("Schedule shutdown in " + minutes + " minute(s)?")) return;

            fetch("/action", {
                method: "POST",
                headers: { "Content-Type": "application/x-www-form-urlencoded" },
                body: "token={{ token }}&cmd=shutdown_timer&minutes=" + encodeURIComponent(minutes)
            })
            .then(res => {
                if (res.ok) {
                    showToast("⏱ Shutdown scheduled in " + minutes + " min");
                    document.getElementById("cancel-btn").style.display = "block";
                } else {
                    showToast("❌ Failed (status " + res.status + ")");
                }
            })
            .catch(() => showToast("❌ Network error"));
        }

        function cancelShutdown() {
            if (!confirm("Cancel the scheduled shutdown?")) return;

            fetch("/action", {
                method: "POST",
                headers: { "Content-Type": "application/x-www-form-urlencoded" },
                body: "token={{ token }}&cmd=cancel_shutdown"
            })
            .then(res => {
                if (res.ok) {
                    showToast("🚫 Scheduled shutdown cancelled");
                    document.getElementById("cancel-btn").style.display = "none";
                    document.getElementById("minutes-input").value = "";
                } else {
                    showToast("❌ Failed (status " + res.status + ")");
                }
            })
            .catch(() => showToast("❌ Network error"));
        }

        function showToast(msg) {
            const toast = document.getElementById("toast");
            toast.textContent = msg;
            toast.classList.add("show");
            setTimeout(() => toast.classList.remove("show"), 3000);
        }
    </script>
</body>
</html>
"""

def run_cmd(cmd, minutes=None):
    if cmd == "lock":
        os.system("loginctl lock-session")
    elif cmd == "suspend":
        os.system("systemctl suspend")
    elif cmd == "reboot":
        os.system("systemctl reboot")
    elif cmd == "shutdown":
        os.system("systemctl poweroff")
    elif cmd == "shutdown_timer" and minutes is not None:
        os.system(f"shutdown -h +{minutes}")
    elif cmd == "cancel_shutdown":
        os.system("shutdown -c")

@app.route("/", methods=["GET"])
def index():
    return render_template_string(HTML, token=SECRET_TOKEN)

@app.route("/action", methods=["POST"])
def action():
    token = request.form.get("token")
    cmd = request.form.get("cmd")
    if token != SECRET_TOKEN:
        abort(403)
    if cmd:
        minutes_raw = request.form.get("minutes")
        minutes = None
        if minutes_raw is not None:
            try:
                minutes = int(minutes_raw)
                if minutes < 1:
                    abort(400)
            except ValueError:
                abort(400)
        run_cmd(cmd, minutes)
    return "OK"

if __name__ == "__main__":
    # listen on LAN
    app.run(host="0.0.0.0", port=5050)
