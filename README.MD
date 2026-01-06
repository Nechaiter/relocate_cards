# Relocate Cards on Import (Experimental)

**This is a personal project released "as-is" for educational and learning purposes.** I built this addon to solve a specific personal use case: moving existing cards to a new deck when importing. I am sharing the code for anyone interested in how it works or who wants to fork it, but **I do not expect to maintain it actively.**

**Hopefully the devs could add this as a Built-in feature.**

## ⚠️ Core Architecture & Warnings

**Please read this before looking at the code:**

This addon relies heavily on **Monkey Patching** internal Anki methods that are not part of the public API. Specifically, it overrides:

- `RustBackend.import_anki_package_raw` (to intercept Protobuf messages).
- Frontend injection using `MutationObserver` on Anki's Svelte components.

### 🛑 Known Risks
1.  **High Breakage Potential:** Since this patches internal methods, **any update to Anki (especially to the Rust backend or the Import Dialog UI)** will likely break this addon immediately.
2.  **Limited Testing:** This code has **only been tested on the Import workflow**. I have not tested if patching `RustBackend` causes side effects in other parts of Anki (e.g., syncing, exporting, or daily review).
3.  **"Works on my Machine":** It works for my specific workflow. I cannot guarantee it handles edge cases, different OS environments, or massive collection sizes gracefully.

## 🛠 Technical Implementation

If you are reviewing the code, here is the flow:

1.  **Backend Patching:** The addon wraps `import_anki_package_raw`. It lets the original method run, intercepts the `ImportResponse` (Protobuf), calculates which cards need moving, and modifies the deck IDs directly in the database logic.
2.  **Frontend Injection:** Since the Import Dialog uses Svelte, standard Qt hooks don't work for UI modification. The addon uses a `MutationObserver` to detect when the DOM is ready and injects the "Relocate" checkbox and the final status counter directly into the HTML.

## 🤖 AI Declaration

This project was developed with the assistance of Artificial Intelligence (LLMs). The AI was utilized for:
* Generating boilerplate code for the Anki UI injection.
* Educated me about how do some stuff and the anki source code, since its my first time reading and investigating any opensource code.

While AI assisted with the code generation, all logic was verified and tested manually for this specific use case.

## ✅ Compatibility

* **Verified Version:** Anki 25.09.2
* **OS:** Windows (Code uses `os.path`, so it *should* be cross-platform, but untested).

## 🤝 Contributing / Issues

Since this was a personal fix:
* **Issues:** You can open them to document bugs, but please don't expect immediate fixes.
* **Pull Requests:** If you know how to fix a bug, refactor my horrible code (lol) or make the patch safer, feel free to submit a PR.

**Use at your own risk.**

## License

AGPL v3