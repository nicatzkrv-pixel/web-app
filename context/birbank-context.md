# Birbank context for the Fintech Radar scorer

This file goes into the scorer's system prompt (`radar/score.py`). Keep it factual and short.
**Keep out:** customer data, exact internal financials, anything confidential. Use ranges or high / medium / low.

Lines marked `TODO(team)` are placeholders. Until they are filled in, the scorer judges novelty from general knowledge of the Azerbaijani market, so novelty scores are less reliable.

## Who we are
- Birbank is the digital banking brand of Kapital Bank, Azerbaijan's largest retail bank. Mobile-first, with a super-app direction.
- This bulletin serves the **payments and transfers vertical**. Team scope includes P2P transfers: C2C card-to-card, Western Union, and transfers by phone number.

## Team KPIs (every kept item names the one it moves)
| KPI | What moves it | Example finds |
|---|---|---|
| Net profit (payments vertical) | New fee, interchange or partner revenue; lower cost per transaction | Premium transfers, merchant services, FX features, cheaper rails |
| NPS | Less friction, more delight | Faster or cheaper transfers, status tracking, fewer failed payments |
| MTU (users with at least 1 transfer or payment a month) | Reasons to transact monthly | Bill split, recurring payments, rewards, social payments |
| Non-cash transactions | Replacing cash, higher frequency | QR/NFC, small-merchant acceptance, bill pay, cash-to-digital |
| Ecosystem growth | Acquisition | Remote onboarding, super-app and partner integrations, referrals |
| System uptime | Reliability | Fallback routing, incident tooling, monitoring |

## What a good find looks like
Something Birbank could realistically bring to Azerbaijan or into the Birbank app within about a year: it works on local rails, fits CBA rules, and solves a problem Azerbaijani customers have. Local and nearby-market launches matter most, because they show what competitors or neighbours will copy next.

## Features Birbank already has (do not recommend these)
An item whose main feature is on this list is not a find: Birbank already offers it. Only keep such an item if it adds a clearly new capability on top (for example a new corridor, a new rail, a new segment or a new mechanism), and then the idea must name exactly what is new.

**Transfers:** card-to-card transfer; transfer by phone number; transfer between own accounts; card number scan by camera; saved and recent recipients; transfer to m10; transfer to local bank accounts; international money transfers; request money from friends; AniPay transfers; QR code to receive transfers; turn receiving Birbank transfers to a card on or off.

**Payments:** bill and service payments (23 categories, e.g. mobile, utilities, internet, government, education); check and pay traffic fines; Bir Pay QR payments; Click to Pay; Apple Pay; coupons and offers.

**Card management:** order a card or a physical version; activate a card (store-bought, salary or student); add another bank's card; reissue, close, block or hide a card; rename a card; view card details and requisites; 3D Secure; change PIN, reset PIN attempts; spending and income limits; SMS banking; linked services and subscriptions.

**Loans:** cash loan; "Böl-ödə" installment limit; apply for a credit limit on a card; loans and debts overview.

**Savings and accounts:** goal-based savings account; digital deposit; open a current account.

**Insurance:** life insurance; compulsory auto insurance; travel insurance; Kasko.

**Mobile:** SIM card activation; add Nar or Bakcell numbers.

**Documents and legal:** document delivery (account statement, letter to an embassy, loan closure certificate); contracts to sign at a branch; powers of attorney (given and received).

**Other:** open banking (other banks' cards and accounts); trips (flight tickets and bookings); currency exchange; branch, ATM and terminal locator; online queue booking; chat support; notifications; hide balance.

## Roadmap
TODO(team): themes on the roadmap (high priority).

## Local competitors
Known local players to watch: ABB, PASHA Bank, Leobank, Yelo Bank, Unibank, Xalq Bank, AccessBank, m10 (wallet), and the Central Bank of Azerbaijan (CBA) as regulator and operator of the instant payment system.

TODO(team): competitor × feature table (who already offers QR payments, phone-number transfers, BNPL, virtual cards, bill split, cashback and so on).

## Regulation and rails (CBA)
TODO(team): current rules and limits for instant payments, C2C limits, remote onboarding, e-signature, open banking, crypto, and data residency. Until this is filled in, the scorer should not assume a regulation exists or does not exist.

## Labelled example finds
TODO(team): add 10–20 examples in the form below. They calibrate the scorer.

| Example | Label | Why |
|---|---|---|
| TODO | great for us / not relevant / already have it | TODO |

## Strategy and constraints
TODO(team): strategic priorities for the next 12 months, and hard constraints (for example, technology or partner limits) at a high level.

## Customer pain points
TODO(team): top pain points from NPS comments and support (high level, no customer data).

## Extra local sources to add
TODO(team): AZ / RU / TR news sites, Telegram channels and regulator pages worth adding to `config/sources.yaml`.
