Here is a professional, beautifully structured `README.md` file tailored specifically for your project. It explains the architecture, features, and setup instructions, making it perfect to hand in to your professor alongside your source files.

```markdown
# Multi-Threaded TCP Chat Application

An extensible, multi-threaded terminal chat application implemented using standard Python socket primitives. The system features custom command parsing, robust asynchronous terminal I/O synchronization, dynamic thread management, thread-safe memory handling, and localized interactive color messaging.

---

## 🚀 Key Features

* **Asynchronous Multi-Threading:** Employs concurrent Python background worker threads (`daemon=True`) to split socket transmission and interface rendering, preventing terminal interface freezes.
* **Smart Prompt Synchronization:** Implements cross-thread tracking flags (`waiting_for_input`) alongside low-level ANSI escape characters (`\r\033[K`) to dynamically wipe and redraft the text cursor prompt (`> `), completely resolving asynchronous layout overlaps.
* **Thread-Safe Data Structures:** Leverages a `threading.Lock()` mutex primitive to wrap all dynamic mutations on the online arrays, preventing race conditions or indexing memory corruption when multiple clients scale concurrent actions.
* **Polished Application Protocol:**
  * `/help` — Generates a localized command manual.
  * `/list` — Displays a real-time list of all authenticated nicknames.
  * `/msg [username] [message]` — Routes targeted, non-broadcast isolated private messages.
* **Graceful Timeouts & Shutdowns:** The server manages an active `server.settimeout(1.0)` lifecycle loop. This allows the main process to check and catch a terminal `KeyboardInterrupt` (`Ctrl+C`) instantly, dropping sockets cleanly without creating lingering phantom background listening ports on the operating system.

---

## 🛠️ Architecture Overview

The system runs on an asynchronous Client-Server model operating strictly on the Transport layer via TCP sockets (`SOCK_STREAM`):

```text
       ┌───────────┐
       │ server.py │ (Main Port Listener, Port: 55555)
       └─────┬─────┘
             │
      ┌──────┴──────┐
      ▼             ▼
┌───────────┐ ┌───────────┐
│ Thread 1  │ │ Thread 2  │ (Isolated execution handlers per client)
└─────┬─────┘ └─────┬─────┘
      ▼             ▼
 ┌─────────┐   ┌─────────┐
 │ Client  │   │ Client  │  (Runs background receive/write loops)
 └─────────┘   └─────────┘

```

---

## 💻 Requirements

* **Python 3.x** (Tested extensively on Python 3.8+)
* **Dependencies:** None. Built entirely using standard, cross-platform modules (`socket`, `threading`, `sys`, `os`, `time`).

---

## ⚙️ Installation & Usage

Follow these steps to run the application locally on your machine:

### 1. Initialize the Server Instance

Open your preferred terminal console and spin up the central tracking server:

```bash
python server.py

```

*The terminal will display: `Server is running and listening on 127.0.0.1:55555...*`

### 2. Connect Client Nodes

Open a separate, dedicated terminal tab or window for each client node you want to launch (supports multiple clients simultaneously):

```bash
python client.py

```

### 3. Complete Handshake Authentication

1. Type in your desired unique profile username at the `Choose your nickname:` prompt.
2. If the user name is available, the node successfully handshakes with the system and accesses the active pool.
3. Start messaging inside the terminal framework!

### 4. How to Exit Cleanly

* **Client Side:** Press `Ctrl + C` at any time to kill the socket pipeline cleanly. The server will immediately recognize the disconnect and announce your departure to everyone else.
* **Server Side:** Press `Ctrl + C` to run the shutdown routine instantly.

---

## 🧩 Protocol Design & Command Structure

The application routes text streams using distinct color schemas via ANSI codes to provide a clean terminal user experience:

| Event/Command Type | Terminal Layout Sample | Target Audience |
| --- | --- | --- |
| **System Welcome** | `[SYSTEM] Type /help to see available commands.` | Newcomer Private Message |
| **Global Broadcast** | `[SYSTEM] Mark joined the chat!` | All Active Sockets |
| **Standard Text Chat** | `Eric: how are you` | Broadcast Group |
| **Private Message (PM)** | `[PM from Eric]: Hello` / `[PM to Mark]: Hi` | Direct Peer Sockets |
| **Active Roster Query** | `Server: Online users (2): Eric, Mark` | Requesting Client Socket |

```

```
