#!/usr/bin/env python3
import argparse
import json
import re


INSULTS = {
    "B": ["不负责任", "很差劲", "不靠谱", "渣男", "渣女"],
    "C": ["人渣", "不要脸", "无耻", "下三滥", "烂人", "骗子"],
    "D": ["傻逼", "傻X", "婊子", "畜生", "去死", "狗东西"],
}
ALLEGATIONS = ["骗子", "诈骗", "诈骗犯", "偷钱", "吸毒", "强奸", "犯罪分子", "出轨", "家暴"]
PUBLIC_PLATFORMS = {"微博", "小红书", "抖音", "贴吧", "知乎", "公开平台"}


def hits(text, words):
    return [word for word in words if word.lower() in text.lower()]


def analyze(args):
    insult_hits = {level: hits(args.text, words) for level, words in INSULTS.items()}
    insult_level = "D" if insult_hits["D"] else "C" if insult_hits["C"] else "B" if insult_hits["B"] else "A"
    allegations = hits(args.text, ALLEGATIONS)
    privacy = re.findall(r"(?<!\d)1[3-9]\d{9}(?!\d)|(?<!\d)\d{17}[\dXx](?!\d)", args.text)
    tier = "T5" if args.audience >= 10000 else "T4" if args.platform in PUBLIC_PLATFORMS or args.audience >= 500 else "T3" if args.audience >= 100 else "T2"
    criminal_threshold = args.views >= 5000 or args.shares >= 500
    score = {"A": 0, "B": 1, "C": 3, "D": 5}[insult_level]
    score += {"T2": 1, "T3": 2, "T4": 3, "T5": 5}[tier]
    score += 3 if allegations and args.evidence in ("无", "弱") else 0
    score += 3 if privacy else 0
    score += 4 if criminal_threshold else 0
    level = "RED" if score >= 10 or insult_level == "D" or criminal_threshold else "YELLOW" if score >= 5 else "GREEN"
    return {
        "risk_level": level,
        "score": score,
        "platform_tier": tier,
        "insult_level": insult_level,
        "insult_hits": insult_hits,
        "factual_allegations": allegations,
        "privacy_identifiers": privacy,
        "criminal_threshold_flag": criminal_threshold,
        "scene": args.scene,
        "note": "Deterministic first pass only; apply the skill workflow and case context before finalizing.",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--text", required=True)
    parser.add_argument("--platform", default="公开平台")
    parser.add_argument("--scene", default="其他")
    parser.add_argument("--audience", type=int, default=0)
    parser.add_argument("--views", type=int, default=0)
    parser.add_argument("--shares", type=int, default=0)
    parser.add_argument("--evidence", choices=["无", "弱", "中", "强"], default="无")
    args = parser.parse_args()
    print(json.dumps(analyze(args), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

