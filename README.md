# Chall - UIDentity Crises

> RFID challenge #1 - Participants have a USB reader, and an empty Mifare classic 1k card, with UID rewritable. They must change the UID of their card to impersonate the admin and get the flag.

## Type

- [X] **OFF**line
- [ ] **ON**line

## Designer(s)

- Hugo Kermabon-Bobinnec

## Description

Back in old days, some access card only used the UID of the card (hardcoded by the constructor) to authenticate someone. Nowadays, some cards have their UID writable, meaning that it's easy to bypass such authentications.

## Category(ies)

- `env`

---

# Project Structure

## 1. HACKME.md

- **[HACKME.md](HACKME.md)**: A teaser or description of the challenge to be shared with participants (in CTFd).

## 2. Source Code

- **[source/README.md](source/README.md)**: Sufficient instructions for building your offline artifacts from source
  code. If your project includes multiple subprojects, please consult us (Anis and Hugo).
- **[source/*](source/)**: Your source code.

## 3. Offline Artifacts

- **[offline-artifacts/*](offline-artifacts/)**: All files (properly named) intended for local download by
  participants (e.g., a binary executable for reverse engineering, a custom-encoded image, etc.). For large files (
  exceeding 100 MB), please consult us (Anis and Hugo).

## 4. Solution

- **[solution/README.md](solution/README.md)**: A detailed writeup of the working solution.
- **[solution/FLAGS.md](solution/FLAGS.md)**: A single markdown file listing all (up-to-date) flags.
- **[solution/*](solution/)**: Any additional files or code necessary for constructing a reproducible solution for the
  challenge (e.g., `PoC.py`, `requirement.txt`, etc.). 
