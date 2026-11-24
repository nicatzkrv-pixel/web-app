"""Keyword rules shared by the pre-filter (fetch.py) and the keyword fallback scorer.

They are deliberately conservative: the pre-filter only removes items that are
clearly on the drop list (section 2 of the brief), so Claude sees everything else.
"""
from __future__ import annotations

import re

# --- Drop list (funding, M&A, people, earnings, events, opinion) -----------------
DROP_RULES: list[tuple[str, re.Pattern]] = [
    ("funding", re.compile(
        r"\b(raises?|raised|secures?|secured|closes?|bags?|lands?)\b[^.]{0,40}"
        r"(\$|€|£|usd|eur|million|billion|\bm\b|\bbn\b|seed|series [a-f]|funding|round|investment)"
        r"|\b(seed|series [a-f]|pre-seed)\s+(round|funding)\b|\bfunding round\b|\bvaluation\b|\bunicorn\b"
        r"|привлек\w*\s+\$|раунд\w* инвестиц|yatırım turu|investisiya cəlb", re.I)),
    ("m&a / ipo", re.compile(
        r"\b(acquires?|acquired|acquisition of|to acquire|to buy|buys|merger|merges with|takeover|ipo|"
        r"goes public|listing on|stake in)\b|поглощ|приобрел\w* долю|satın al|birleşme", re.I)),
    ("people", re.compile(
        r"\b(appoints?|appointed|names? .{0,30}(ceo|cfo|cto|coo|chief|head|president|chair)|"
        r"hires?|joins as|steps down|resigns?|new ceo|promoted to)\b|назначен|atandı|təyin edil", re.I)),
    ("earnings", re.compile(
        r"\b(q[1-4]\s+(results|earnings|profit|revenue)|quarterly (results|earnings)|net profit|"
        r"earnings|revenue (rose|fell|grew|up|down)|profit (rose|fell|grew|jumps|up|down)|"
        r"half-year results|annual results|financial results|dividend)\b|"
        r"чистая прибыль|прибыль банк|net kâr|xalis mənfəət", re.I)),
    ("event", re.compile(
        r"\b(conference|summit|webinar|award|awards|wins .{0,20}award|shortlist|expo|forum|"
        r"hackathon|panel discussion|keynote|podcast|sponsor(s|ed)?)\b|форум|конференц|"
        r"zirvə|konfrans|ödül", re.I)),
    ("opinion", re.compile(
        r"\b(opinion|op-ed|comment:|column:|interview:|q&a:|why .{0,40} (must|should)|"
        r"what .{0,30} means for|the future of|predictions? for|trends? to watch|"
        r"latest opinions)\b", re.I)),
    ("market data", re.compile(
        r"\b(stock price|share price|shares (rose|fell|jump|slide)|exchange rates?|курс(ы)? валют|"
        r"valyuta məzənnələri|döviz kuru|bitcoin price)\b", re.I)),
]

# Signals that an item is about something concrete that launched or is being built.
LAUNCH_RE = re.compile(
    r"\b(launch(es|ed)?|rolls? out|rolled out|introduc(es|ed)|unveil(s|ed)?|debuts?|"
    r"now (available|lets|offers)|adds?|added|enables?|goes live|went live|pilot(s|ing)?|"
    r"trials?|new feature|new service|partners? with|integrat(es|ed|ion))\b|"
    r"запустил|запуск|представил|внедрил|новая функция|новый сервис|"
    r"başlattı|hizmete sundu|yeni özellik|kullanıma sundu|"
    r"istifadəyə verdi|təqdim etdi|yeni xidmət|başladı", re.I)
ANNOUNCE_RE = re.compile(r"\b(plans? to|will launch|to launch|set to|announces? plans|considering)\b|планирует|planlıyor|planlaşdırır", re.I)
PILOT_RE = re.compile(r"\b(pilot(s|ing)?|trial(s|ling)?|beta|test(s|ing))\b|пилот|тестир", re.I)

FINTECH_RE = re.compile(
    r"\b(fintech|bank\w*|payment\w*|pay\b|wallet|card\w*|transfer\w*|remittance\w*|lending|loan\w*|"
    r"bnpl|kyc|onboarding|open banking|api|qr|nfc|crypto|stablecoin|neobank|super.?app|"
    r"merchant\w*|acquiring|pos\b|insurtech|savings|deposit\w*|fraud|scam)\b|"
    r"банк|платеж|плат[её]ж|перевод|карт[аы]|кошел[её]к|финтех|"
    r"ödəniş|kart|köçürmə|fintex|tətbiq|"
    r"ödeme|banka|cüzdan|fintek|transfer", re.I)

CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "Transfers and remittances": ["remittance", "transfer", "p2p", "peer-to-peer", "cross-border", "western union",
                                   "перевод", "köçürmə", "para transferi", "send money", "phone number"],
    "Payments": ["payment", "qr", "nfc", "tap to pay", "softpos", "checkout", "pay by bank", "instant payment",
                 "real-time payment", "pix", "upi", "fednow", "bill pay", "merchant", "acquiring", "pos",
                 "платеж", "ödəniş", "ödeme", "karekod", "сбп", "fast"],
    "Cards": ["card", "visa", "mastercard", "virtual card", "debit", "credit card", "карта", "kart"],
    "Lending and BNPL": ["bnpl", "buy now pay later", "loan", "lending", "credit line", "installment", "instalment",
                         "кредит", "рассрочк", "kredit", "taksit"],
    "Savings and wealth": ["savings", "deposit", "invest", "wealth", "round-up", "goal", "brokerage",
                           "вклад", "депозит", "əmanət", "birikim"],
    "Open banking and APIs": ["open banking", "open finance", "api", "account aggregation", "psd2", "psd3",
                              "открытый банкинг", "açıq bankçılıq", "açık bankacılık"],
    "Identity and KYC": ["kyc", "onboarding", "digital id", "e-id", "biometric", "passkey", "identity",
                         "e-signature", "asan imza", "верификац", "kimlik"],
    "Security and fraud": ["fraud", "scam", "security", "authentication", "phishing", "mule", "мошен", "dolandırıcı"],
    "AI in banking": ["ai ", "artificial intelligence", "genai", "chatbot", "assistant", "agentic", "llm",
                      "искусственн", "süni intellekt", "yapay zeka"],
    "Super-app and lifestyle": ["super app", "super-app", "superapp", "lifestyle", "marketplace", "loyalty",
                                "cashback", "rewards", "travel", "ticket", "кэшбэк", "keşbek"],
    "SME banking": ["sme", "small business", "merchant", "invoic", "payroll", "business account", "мсб", "kobi"],
    "Regulation and infrastructure": ["regulat", "central bank", "license", "licence", "rule", "law",
                                      "framework", "sandbox", "cbdc", "digital manat", "цб", "mərkəzi bank",
                                      "регулятор", "tcmb", "bddk"],
}

# Which KPI a category most often moves (used by the keyword fallback only).
CATEGORY_KPI: dict[str, str] = {
    "Payments": "Non-cash transactions",
    "Transfers and remittances": "MTU",
    "Cards": "Non-cash transactions",
    "Lending and BNPL": "Net profit",
    "Savings and wealth": "Ecosystem growth",
    "Open banking and APIs": "Ecosystem growth",
    "Identity and KYC": "Ecosystem growth",
    "Security and fraud": "NPS",
    "AI in banking": "NPS",
    "Super-app and lifestyle": "MTU",
    "SME banking": "Net profit",
    "Regulation and infrastructure": "Non-cash transactions",
}

COUNTRY_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("Azerbaijan", re.compile(r"azerbaijan|azərbaycan|азербайджан|\bbaku\b|bakı|баку|birbank|kapital bank|"
                              r"leobank|yelo bank|pasha bank|\babb\b|\bm10\b|unibank|xalq bank|cbar|"
                              r"mərkəzi bank|\bцба\b", re.I)),
    ("Georgia", re.compile(r"\bgeorgia\b|tbilisi|bank of georgia|tbc bank|грузи", re.I)),
    ("Armenia", re.compile(r"armenia|yerevan|ameriabank|idram|армени", re.I)),
    ("Kazakhstan", re.compile(r"kazakhstan|almaty|astana|kaspi|halyk|казахстан", re.I)),
    ("Uzbekistan", re.compile(r"uzbekistan|tashkent|\bpayme\b|\buzum\b|узбекистан", re.I)),
    ("Kyrgyzstan", re.compile(r"kyrgyz|bishkek|кыргыз|киргиз", re.I)),
    ("Türkiye", re.compile(r"türkiye|turkey|turkish|istanbul|papara|garanti|akbank|ziraat|tcmb|bddk|"
                           r"türk", re.I)),
    ("United Arab Emirates", re.compile(r"\buae\b|emirates|dubai|abu dhabi|emirati", re.I)),
    ("Saudi Arabia", re.compile(r"saudi|riyadh|\bksa\b|sama\b", re.I)),
    ("Qatar", re.compile(r"qatar|doha", re.I)),
    ("Bahrain", re.compile(r"bahrain", re.I)),
    ("Russia", re.compile(r"russia|россия|российск|сбер|тинькофф|т-банк|\bсбп\b|банк росси", re.I)),
    ("Ukraine", re.compile(r"ukrain|украин|monobank|privatbank", re.I)),
    ("United Kingdom", re.compile(r"\buk\b|britain|british|london|monzo|revolut|starling|\bfca\b", re.I)),
    ("United States", re.compile(r"\bu\.?s\.?\b|united states|america|fednow|zelle|venmo|cash app|\bcfpb\b", re.I)),
    ("India", re.compile(r"india|\bupi\b|npci|paytm|phonepe|rbi\b", re.I)),
    ("Brazil", re.compile(r"brazil|\bpix\b|nubank", re.I)),
    ("European Union", re.compile(r"\beu\b|europe|sepa|ecb|psd3|digital euro", re.I)),
]


def drop_reason(text: str) -> str | None:
    for reason, pattern in DROP_RULES:
        if pattern.search(text):
            return reason
    return None


def is_fintech(text: str) -> bool:
    return bool(FINTECH_RE.search(text))


def detect_country(text: str) -> str | None:
    for country, pattern in COUNTRY_PATTERNS:
        if pattern.search(text):
            return country
    return None


def guess_category(text: str) -> str:
    low = text.lower()
    best, best_hits = "Payments", 0
    for category, words in CATEGORY_KEYWORDS.items():
        hits = sum(1 for w in words if w in low)
        if hits > best_hits:
            best, best_hits = category, hits
    return best


def launch_status(text: str) -> str:
    if ANNOUNCE_RE.search(text):
        return "announced"
    if PILOT_RE.search(text):
        return "piloting"
    if LAUNCH_RE.search(text):
        return "launched"
    return "unclear"
