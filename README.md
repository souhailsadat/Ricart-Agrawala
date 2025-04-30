# Ricart & Agrawala's Algorithm Lab

## Overview
This lab implements a **distributed mutual exclusion algorithm** (Ricart & Agrawala, 1981) using Python and PyQt5. The simulation models how multiple processes coordinate to access a shared resource (critical section) without conflicts, using message-passing and logical clocks.

## Key Features
- **GUI Visualization**: Real-time display of process states (active, waiting, in critical section) via a PyQt5 interface.
- **Threaded Processes**: 10 simulated processes (`Node` class) communicate via TCP sockets.
- **Algorithm Logic**:
  - Processes send `REQUEST` messages with timestamps.
  - Defer or grant `REPLY` messages based on priority (timestamp + process ID).
  - Ensures fairness and deadlock-free access to the critical section.
- **Pause/Resume**: Interactive control to pause the simulation for analysis.

## Files
- `Main.py`: Launches the GUI and manages process threads.
- `Node.py`: Implements the Ricart & Agrawala algorithm for each process.
- `Gui.ui`: PyQt5 UI design file (loaded by `Main.py`).

## How It Works
1. **Initialization**:
   - Each process (`Node`) starts a TCP server and connects to others.
   - Processes synchronize using a `Barrier` before beginning.
2. **Critical Section Access**:
   - A process requests access by broadcasting `REQUEST` messages.
   - Waits for `REPLY` from all other processes before entering.
   - Defers replies if it has a pending request with higher priority.
3. **GUI Updates**:
   - Colors indicate process states:  
     - **White**: Normal  
     - **Purple**: Waiting (`sc_demande=True`)  
     - **Orange**: In critical section (`dedans=True`)  
   - Table shows timestamps, deferred replies, and pending requests.

## Usage
1. Run `Main.py` to start the simulation.
2. Click **Pause/Resume** to control execution.
3. Observe the table and console logs for algorithm steps.

## Dependencies
- Python 3.x
- PyQt5 (`pip install PyQt5`)

## Educational Purpose
This lab demonstrates:
- **Distributed mutual exclusion** principles.
- **Logical clocks** and timestamp-based ordering.
- **Message-passing** concurrency in a networked system.

---

*Developed for a networking/operating systems course.*  
