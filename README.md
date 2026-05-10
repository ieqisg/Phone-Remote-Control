# Remote PC Control — Documentation

A guide for accessing your PC remotely over your local network (and optionally via Tailscale outside home) using three tools: the Power Control Panel, ttyd terminal, and SSH via Termux.

---

## Table of Contents
1. [Services Overview](#services-overview)
2. [Power Control Panel (phone-shutdown)](#1-power-control-panel)
3. [ttyd — Browser Terminal](#2-ttyd--browser-terminal)
4. [SSH via Termux](#3-ssh-via-termux)
5. [Turning Services On and Off](#4-turning-services-on-and-off)
6. [Accessing Outside Home (Tailscale)](#5-accessing-outside-home-tailscale)

---

## Services Overview

| Service | Port | Access |
|---|---|---|
| Power Control Panel | 5050 | `http://yourip:5050` |
| ttyd Terminal | 8080 | `http://yourip:8080` |
| SSH | 22 | via Termux SSH client |

To find your current local IP:
```bash
ip addr | grep "inet " | grep -v 127.0.0.1
```

---

## 1. Power Control Panel

A web UI to remotely lock, suspend, reboot, shutdown, or schedule a shutdown on your PC.

### Access
Open your phone browser and go to:
```
http://yourip:5050
```

### Features
- **Lock** — locks your session
- **Suspend** — puts PC to sleep
- **Reboot** — restarts the PC
- **Shutdown** — immediately powers off
- **Scheduled Shutdown** — input minutes, then press Schedule. A Cancel button appears to abort it

### Service
Managed by `remote-power.service`. It runs `phone-shutdown.py` using the venv Python automatically on boot.

---

## 2. ttyd — Browser Terminal

A full interactive terminal accessible from any browser on your network. Useful for running commands, Claude Code, starting servers, etc.

### Access
Open your phone or laptop browser and go to:
```
http://yourip:8080
```

It will prompt for a username and password (set in the service file).

### Typing on Mobile
Install **Hacker's Keyboard** from the Play Store. It adds arrow keys, Ctrl, Tab, and Esc to your mobile keyboard — essential for terminal use.

To switch to it: **Settings → General Management → Keyboard → Default keyboard**

### If You Can't Type
The terminal may be in readonly mode or the port is stuck. Fix it:
```bash
sudo fuser -k 8080/tcp
sudo systemctl restart ttyd
```

### Service
Managed by `ttyd.service`. Runs automatically on boot with the `--writable` flag enabled.

---

## 3. SSH via Termux

SSH gives you a native terminal experience on Android with full keyboard support including arrow keys and Ctrl.

### Setup (one time)

**On your PC**, make sure SSH is running:
```bash
sudo systemctl enable --now sshd
```

**On your phone**, install Termux from the Play Store or F-Droid, then:
```bash
pkg install openssh
```

### Connecting
```bash
ssh marc@yourip
```

Enter your Linux user password when prompted.

### Why SSH over ttyd on mobile
- Better keyboard support (arrow keys, Ctrl+C, Ctrl+\ all work natively)
- More stable for long sessions like Claude Code
- No browser needed

---

## 4. Turning Services On and Off

When leaving home or connecting to a public/untrusted network, stop all services to close open ports. These aliases are set up in `~/.zshrc`:

**Stop everything:**
```bash
serve-off
```

**Start everything:**
```bash
serve-on
```

These control `ttyd`, `remote-power`, and `sshd` all at once.

> Always run `serve-off` before leaving home or connecting to public WiFi.

---

## 5. Accessing Outside Home (Tailscale)

By default everything is LAN-only. To access your PC from outside your home network (mobile data, different WiFi), use Tailscale.

### Setup

**On your PC:**
```bash
sudo pacman -S tailscale
sudo systemctl enable --now tailscaled
sudo tailscale up
```
Open the link it provides and log in with your Google or GitHub account.

**On your phone:**
Install the Tailscale app and log in with the same account.

### Usage
Tailscale gives your PC a fixed IP starting with `100.x.x.x`. Use that IP the same way:
```
http://100.x.x.x:5050   → Power panel
http://100.x.x.x:8080   → ttyd terminal
ssh marc@100.x.x.x      → SSH via Termux
```

### Security Notes
- Enable 2FA on your Tailscale login account (Google/GitHub)
- Use a strong ttyd password
- Run `serve-off` when on untrusted networks even with Tailscale, as an extra precaution
