# 🤖 AI Assistance & Engineering Log

## Project: CodeSentinel AI
**Event:** Mycrobo Hackathon - AntiSlop  
**Track:** AI Triage (`ai-triage`)  
**Repository:** [navyagowthami/CodeSentinel-AI](https://github.com/navyagowthami/CodeSentinel-AI)  
**Date:** November 2026

---

## 1. Executive Summary & AI Utilization Overview
CodeSentinel AI was engineered as an architecture-agnostic AI code security, slop detection, and quality review agent. Throughout development, AI was utilized as an augmented pair-programmer for architectural design, scanner rule synthesis, prompt calibration, and multi-stack AST pattern mapping, while humans maintained strict oversight over logic verification, security constraints, and deterministic scanning guarantees.

---

## 2. AI Tools & Models Leveraged
- **Claude 3.5 Sonnet / Gemini 2.5 Flash:** Used for drafting AST visitors, heuristic regular expressions for vulnerability detection, and designing unified diff patch templates.
- **Antigravity AI Agent:** Used for development workflow orchestration, dependency management, unit test creation, and continuous integration validation.
- **Local Heuristic Fallback Engine:** Engineered to guarantee zero-API-key functionality, allowing local offline scans and deterministic rule matching.

---

## 3. Engineering Phases & AI Collaboration

### Phase 1: Architecture & System Decomposition
- **AI Task:** Propose a modular FastAPI + React pipeline capable of processing local and remote Git repositories with streaming Server-Sent Events (SSE).
- **Human Review / Decision:** Enforced strict separation between deterministic AST scanners (OWASP Top 10, CVE checks) and generative LLM reasoning layers to avoid hallucinated vulnerabilities and false positives.

### Phase 2: Anti-Slop & Quality Scanner Rules
- **AI Task:** Synthesize heuristic patterns for detecting AI-generated code bloat ("slop"), conversational prompt leaks (`As an AI model...`), tautological comments, and swallowed exceptions (`except: pass`).
- **Human Refinement:** Filtered out false alarms in standard library wrappers and test mock files to ensure a low false-positive rate.

### Phase 3: Automated Unified Diff Patching
- **AI Task:** Design patch generation templates conforming to GNU `unified diff` standards (`--- a/file` / `+++ b/file`).
- **Human Verification:** Added the 1-Click direct file patching engine with dry-run validation to ensure syntax errors are never written to source repositories.

### Phase 4: Production Readiness & Arena Contract
- **AI Task:** Implement contract compliance for Mycrobo Arena (`GET /health` and `POST /classify` triage API) alongside the full CodeSentinel platform.
- **Human Verification:** Verified standalone test suites (`pytest`), zero external network dependencies for baseline mode, and verified that all 11 unit tests pass.

---

## 4. Key Lessons & Self-Correction
1. **Deterministic + Heuristic Superiority:** Relying entirely on LLMs for code audits introduces latency and hallucinations. Combining deterministic AST parsing with contextual AI verification achieved 10x faster scan times and higher precision.
2. **Offline Resilience:** Designing a heuristic reasoning engine enabled the system to function completely offline without leaking repository contents or requiring third-party API keys.
