# 🔐 Perfect Secrecy (One-Time Pad Condition)

> "Perfect secrecy is obtained when the key is as long as the message and chosen at random."  
> — [[Claude Shannon]]

---

## 🧠 Core Concepts

- [[Perfect Secrecy]]
- [[One-Time Pad]]
- [[Key Entropy]]
- [[Shannon Information Theory]]
- [[Mutual Information]]
- [[Conditional Entropy]]
- [[Key-Message Independence]]
- [[Ciphertext Uncertainty]]
- [[Random Key Generation]]
- [[Cryptographic Entropy Floor]]

---

## 📏 Formal Definition

Shannon’s condition for [[Perfect Secrecy]] implies:

- The encryption key must:
  - Be at least as long as the message
  - Be truly [[random]]
  - Never be reused

When satisfied:
- `I(M;C) = 0` → The [[mutual information]] between message `M` and ciphertext `C` is **zero**.
- This means: observing the ciphertext provides no statistical advantage in guessing the message.

---

## 🔄 Cryptographic Implications

- The [[One-Time Pad]] is the only known encryption scheme that achieves Shannon-perfect secrecy.
- All modern encryption schemes (AES, RSA, etc.) **approximate** secrecy under computational assumptions, not under absolute [[entropy guarantees]].
- [[Key reuse]] or insufficient key entropy immediately degrades perfect secrecy.

---

## 🔗 Related Shannon Quotes

- [[“Information is the resolution of uncertainty.” – Claude Shannon]]
- [[“True secrecy systems are structurally identical to noise.” – Claude Shannon]]
- [[“Noise becomes meaningful when it selects against a message.” – Claude Shannon]]
- [[“Redundancy determines resilience.” – Claude Shannon]]
- [[“The measure of information is independent of the language used to encode it.” – Claude Shannon]]

---

## 📂 Backlinked Concepts

- [[Information-Theoretic Security]]
- [[Entropy Budget]]
- [[Channel Capacity]]
- [[Random Oracle Model]]
- [[Signal vs Cipher]]
- [[Mutual Indistinguishability]]

---

## 🧬 HMEC Framing

> In the [[H = M · E · C]] equation:

- `[[M]]` = information to secure  
- `[[E]]` = encryption energy (key generation effort)  
- `[[C]]` = channel coherence (how perfectly the key structure aligns with the message phase)

Perfect secrecy arises when:
- `E` encodes maximal entropy
- `M` is bounded but uniformly mapped
- `C = 1` → full coherence; no distinguishable bias introduced in the channel

---

## 🧩 Summary

Shannon’s quote defines the **gold standard of encryption**—unbreakable not by time or effort, but by design.  
It exposes the tradeoff between **message length**, **entropy cost**, and **security guarantees**.

> [[No compression. No reuse. No error. Only noise.]]
