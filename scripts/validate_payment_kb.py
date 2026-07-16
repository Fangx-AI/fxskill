from __future__ import annotations

from datetime import date
import ipaddress
from pathlib import Path
import re
import sys
from urllib.parse import urlparse


REQUIRED_LABELS = (
    "当前状态",
    "平台类型",
    "支付角色",
    "资金路径",
    "卖家地区",
    "支持主体",
    "买家地区与币种",
    "支付方式",
    "适合商品",
    "平台服务费",
    "支付通道费",
    "结算",
    "固定费用、提现费、退款费和拒付费",
    "结算周期与最低结算额",
    "推荐等级",
    "适用条件",
    "不适用条件",
    "最后核验日期",
    "官方来源",
    "实践来源",
    "待核验问题",
)

ALLOWED_OPTIONAL_LABELS = (
    "能不能申请",
    "需要准备",
    "怎么收费",
    "多久能到账",
    "会员和自动续费",
    "接入难度",
    "最容易踩的坑",
    "运营主体",
    "限制商品",
    "单次支付",
    "订阅与自动续费",
    "API、SDK、插件和支付链接",
    "申请材料",
    "接入路径",
    "退款和售后",
    "数据导出与迁移",
    "实际优点",
    "实际问题",
)

ALLOWED_RECOMMENDATIONS = {
    "直接推荐",
    "条件推荐",
    "早期验证可用",
    "仅作线索",
    "不推荐",
    "已停止/归档",
}

ALLOWED_STATUSES = {"正常运营", "限定开放", "无法确认", "已停止"}
OFFICIAL_SOURCE_EXEMPT_STATUSES = {"无法确认", "已停止"}
ACTIONABLE_UNKNOWN_FIELDS = ("缺失事实", "已查来源", "需要询问", "可接受证据")

KEY_FIELDS = (
    "当前状态",
    "支付角色",
    "资金路径",
    "卖家地区",
    "支持主体",
    "买家地区与币种",
    "支付方式",
    "平台服务费",
    "支付通道费",
    "固定费用、提现费、退款费和拒付费",
    "结算",
    "结算周期与最低结算额",
    "适用条件",
    "不适用条件",
    "运营主体",
    "限制商品",
    "单次支付",
    "订阅与自动续费",
    "API、SDK、插件和支付链接",
    "申请材料",
    "接入路径",
    "退款和售后",
    "数据导出与迁移",
    "实际优点",
    "实际问题",
)

FEE_COMPONENTS = ("固定费用", "提现费", "退款费", "拒付费")
UNKNOWN_PATTERNS = (
    "未知",
    "未确认",
    "未核实",
    "未明确",
    "未公开",
    "未查到",
    "不详",
    "不明",
    "不确定",
    "待定",
    "待确认",
    "待核验",
    "无法确认",
    "暂无结论",
    "没有写明",
    "存在两种模式信号",
    "未披露",
    "未说明",
    "未列明",
)
UNKNOWN_DISCLOSURE_PATTERN = re.compile(
    r"(?:未|没有|尚未|无法|不能|无)"
    r"(?:能|予|被|获|得到|加以|有)?"
    r"(?:公开|公布|披露|说明|列明|写明|给出|明确|确认|核实|查明)"
)

MONEY_PATH_CLEARING_TERMS = (
    "清算方",
    "清算机构",
    "清算节点",
    "结算处理",
)
MONEY_PATH_PRECISION_CONTEXT = (
    "公开资料",
    "公开材料",
    "官方材料",
    "协议约定",
    "合同约定",
    "具体清算",
)

PRECISE_UNPUBLISHED_PATTERN = re.compile(
    r"^未公开统一数字（以(?:签约页|合同|后台(?:显示)?|报价单)为准）$"
)
LABEL_PATTERN = re.compile(r"^- ([^：:]+)[：:]\s*(.*)$")
FEE_LINE_PATTERN = re.compile(r"^(固定费用|提现费|退款费|拒付费)[：:]\s*(.*)$")
FEE_KEYED_LINE_PATTERN = re.compile(r"^([^：:]+)[：:]\s*(.*)$")
RAW_URL_PATTERN = re.compile(r"https?://\S+")
TRAILING_URL_PUNCTUATION = "。？！；：)]】》」』”’）］"
ISO_DATE_PATTERN = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
QUESTION_STRUCTURES = ("是否", "可否", "能否", "哪些", "哪类", "如何", "多少", "什么", "哪一个")
QUESTION_FILLERS = "向请联系询问确认咨询跟进和与就找"
EVIDENCE_CARRIERS = (
    "官方页面",
    "文档",
    "合同",
    "报价单",
    "后台截图",
    "申请结果",
    "书面回复",
    "邮件",
    "盖章协议",
)
CHECKED_SOURCE_ENTRY_HINTS = (
    "官网",
    "官方网站",
    "官方文档",
    "开发文档",
    "帮助中心",
    "商户后台",
    "管理后台",
    "后台入口",
    "申请页",
    "费率页",
)
BACKLOG_PLACEHOLDERS = (
    "TODO",
    "TBD",
    "待补",
    "后续补",
    "请联系客服",
    "联系客服",
    "咨询客服",
    "等官方回复",
    "等回复",
)
PRACTICE_EVIDENCE_INSUFFICIENT_MARKER = "实践证据不足"
PRACTICE_EVIDENCE_ALLOWED_RECOMMENDATIONS = {"仅作线索", "已停止/归档"}
MONEY_PATH_UNKNOWN_ALLOWED_RECOMMENDATIONS = {"仅作线索", "已停止/归档"}


def repository_root_for(path: Path) -> Path:
    for parent in (path.parent, *path.parents):
        if (parent / ".git").exists():
            return parent
    for parent in (path.parent, *path.parents):
        if (parent / "skills" / "fxskill" / "references").exists():
            return parent
    return path.parent


def relative_path(path: Path) -> str:
    root = repository_root_for(path)
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.name


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", "", value).strip()


def is_precise_unpublished_value(value: str) -> bool:
    return bool(PRECISE_UNPUBLISHED_PATTERN.fullmatch(value.strip()))


def has_unknown_fragment(value: str) -> bool:
    stripped = value.strip()
    if is_precise_unpublished_value(stripped):
        return False
    normalized = normalize_text(stripped)
    return any(pattern in normalized for pattern in UNKNOWN_PATTERNS) or bool(
        UNKNOWN_DISCLOSURE_PATTERN.search(normalized)
    )


def has_precise_money_path_unknown(value: str) -> bool:
    normalized = normalize_text(value)
    if "存在两种模式信号" in normalized:
        return True
    return (
        any(term in normalized for term in MONEY_PATH_CLEARING_TERMS)
        and has_unknown_fragment(normalized)
        and any(context in normalized for context in MONEY_PATH_PRECISION_CONTEXT)
    )


def status_name(value: str) -> str:
    return re.split(r"[；;]", value, maxsplit=1)[0].strip()


def parse_profiles(text: str) -> list[tuple[str, dict[str, str], list[str]]]:
    profiles: list[tuple[str, dict[str, str], list[str]]] = []
    current_name: str | None = None
    current_labels: dict[str, list[str]] = {}
    duplicate_labels: list[str] = []
    current_label: str | None = None

    def flush() -> None:
        nonlocal current_name, current_labels, duplicate_labels, current_label
        if current_name is None:
            return
        profiles.append(
            (
                current_name,
                {key: "\n".join(lines).strip() for key, lines in current_labels.items()},
                duplicate_labels[:],
            )
        )
        current_name = None
        current_labels = {}
        duplicate_labels = []
        current_label = None

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if line.startswith("## "):
            flush()
            current_name = line[3:].strip()
            continue
        if current_name is None:
            continue
        match = LABEL_PATTERN.match(line)
        if match:
            label = match.group(1).strip()
            value = match.group(2).strip()
            if label in current_labels:
                duplicate_labels.append(label)
                current_label = None
                continue
            current_label = label
            current_labels[label] = [value]
            continue
        if current_label is not None:
            current_labels[current_label].append(line.strip())

    flush()
    return profiles


def strip_trailing_url_punctuation(url: str) -> str:
    return url.rstrip(TRAILING_URL_PUNCTUATION)


def extract_candidate_urls(value: str) -> list[str]:
    urls: list[str] = []
    for raw_url in RAW_URL_PATTERN.findall(value):
        for segment in re.split(r"；(?=https?://)", raw_url):
            candidate = strip_trailing_url_punctuation(segment)
            if candidate:
                urls.append(candidate)
    return urls


def is_ip_hostname(hostname: str) -> bool:
    try:
        ipaddress.ip_address(hostname)
    except ValueError:
        return False
    return True


def is_valid_official_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
    except ValueError:
        return False
    if parsed.scheme not in {"http", "https"}:
        return False
    hostname = parsed.hostname
    if not hostname:
        return False
    normalized_host = hostname.rstrip(".")
    if not normalized_host or normalized_host.lower() == "localhost":
        return False
    if is_ip_hostname(normalized_host):
        return False
    if "." not in normalized_host:
        return False
    try:
        normalized_host.encode("idna")
    except UnicodeError:
        return False
    return True


def validate_official_source(value: str) -> bool:
    return any(is_valid_official_url(url) for url in extract_candidate_urls(value))


def validate_verification_date(value: str) -> bool:
    try:
        date.fromisoformat(value.strip())
    except ValueError:
        return False
    return True


def validate_money_path(value: str) -> bool:
    nodes = [node.strip() for node in re.split(r"(?:->|→)", value)]
    if len(nodes) != 4:
        return False
    return all(
        node
        and (
            not has_unknown_fragment(node)
            or has_precise_money_path_unknown(node)
        )
        for node in nodes
    )


def parse_fee_breakdown(value: str) -> tuple[dict[str, str], list[str], list[str]]:
    items: dict[str, str] = {}
    duplicates: list[str] = []
    extras: list[str] = []
    for raw_line in value.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        fee_match = FEE_LINE_PATTERN.match(line)
        if fee_match:
            label = fee_match.group(1)
            field_value = fee_match.group(2).strip()
            if label in items:
                duplicates.append(label)
                continue
            items[label] = field_value
            continue
        keyed_match = FEE_KEYED_LINE_PATTERN.match(line)
        if keyed_match:
            extras.append(keyed_match.group(1).strip())
            continue
        generic_match = LABEL_PATTERN.match(line)
        if generic_match:
            extras.append(generic_match.group(1).strip())
    return items, duplicates, extras


def validate_fee_component_value(value: str) -> bool:
    stripped = value.strip()
    if not stripped:
        return False
    if stripped in {"0", "无此项"}:
        return True
    if is_precise_unpublished_value(stripped):
        return True
    return not has_unknown_fragment(stripped)


def validate_fee_breakdown(prefix: str, value: str) -> list[str]:
    errors: list[str] = []
    items, duplicates, extras = parse_fee_breakdown(value)
    for duplicate in duplicates:
        errors.append(f"{prefix} duplicate fee subfield `{duplicate}`")
    if extras:
        errors.append(
            f"{prefix} 固定费用、提现费、退款费和拒付费 contains unsupported fee key(s): {', '.join(extras)}"
        )
    for field in FEE_COMPONENTS:
        if field not in items or not validate_fee_component_value(items[field]):
            errors.append(f"{prefix} 固定费用、提现费、退款费和拒付费 must include all four non-empty subfields")
            break
    return errors


def has_unknown_key_fields(labels: dict[str, str]) -> bool:
    for field in KEY_FIELDS:
        value = labels.get(field, "")
        if field == "固定费用、提现费、退款费和拒付费":
            items, duplicates, extras = parse_fee_breakdown(value)
            if duplicates or extras or set(items) != set(FEE_COMPONENTS):
                return True
            if any(has_unknown_fragment(items[item]) for item in FEE_COMPONENTS):
                return True
            continue
        if has_unknown_fragment(value):
            return True
    return False


def can_be_directly_recommended(labels: dict[str, str]) -> bool:
    if labels.get("待核验问题", "").strip() != "无":
        return False
    if status_name(labels.get("当前状态", "")) != "正常运营":
        return False
    return not has_unknown_key_fields(labels)


def parse_backlog_items(backlog: str) -> tuple[dict[str, str], list[str]]:
    items: dict[str, str] = {}
    duplicates: list[str] = []
    for raw_line in backlog.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        match = LABEL_PATTERN.match(line)
        if not match:
            continue
        label = match.group(1).strip()
        value = match.group(2).strip()
        if label not in ACTIONABLE_UNKNOWN_FIELDS:
            continue
        if label in items:
            duplicates.append(label)
            continue
        items[label] = value
    return items, duplicates


def validate_missing_fact(value: str) -> bool:
    stripped = value.strip()
    if len(stripped) < 8:
        return False
    if stripped in {"待确认", "未知", "无法确认", "暂无结论"}:
        return False
    return True


def is_specific_question(value: str) -> bool:
    stripped = value.strip()
    if len(stripped) < 12 or not stripped.endswith(("?", "？")):
        return False
    for word in QUESTION_STRUCTURES:
        index = stripped.find(word)
        if index <= 0:
            continue
        subject = stripped[:index].strip(QUESTION_FILLERS + "：: ")
        detail = stripped[index + len(word): -1].strip()
        if len(subject) >= 2 and len(detail) >= 2:
            return True
    return False


def has_evidence_carrier(value: str) -> bool:
    return any(carrier in value for carrier in EVIDENCE_CARRIERS)


def validate_checked_sources(value: str) -> bool:
    stripped = value.strip()
    if len(stripped) < 12:
        return False
    if any(placeholder in stripped for placeholder in BACKLOG_PLACEHOLDERS):
        return False
    if not ISO_DATE_PATTERN.search(stripped):
        return False
    if any(is_valid_official_url(url) for url in extract_candidate_urls(stripped)):
        return True
    return any(hint in stripped for hint in CHECKED_SOURCE_ENTRY_HINTS)


def validate_backlog(prefix: str, backlog: str) -> list[str]:
    errors: list[str] = []
    items, duplicates = parse_backlog_items(backlog)
    for duplicate in duplicates:
        errors.append(f"{prefix} duplicate backlog subfield `{duplicate}`")
    for field in ACTIONABLE_UNKNOWN_FIELDS:
        if field not in items or not items[field].strip():
            errors.append(f"{prefix} 待核验问题 must include `{field}`")
    if errors:
        return errors

    if not validate_missing_fact(items["缺失事实"]):
        errors.append(f"{prefix} 待核验问题 has no substantive value for `缺失事实`")
    if not validate_checked_sources(items["已查来源"]):
        errors.append(f"{prefix} 待核验问题 has no substantive value for `已查来源`")
    if not is_specific_question(items["需要询问"]):
        errors.append(f"{prefix} 待核验问题 `需要询问` must be a concrete question ending with ? or ？")
    if not has_evidence_carrier(items["可接受证据"]) or items["可接受证据"].strip() == "官方回复":
        errors.append(f"{prefix} 待核验问题 `可接受证据` must name concrete evidence carriers")
    return errors


def validate_status_and_recommendation(prefix: str, status: str, recommendation: str) -> list[str]:
    errors: list[str] = []
    if status == "已停止" and recommendation != "已停止/归档":
        errors.append(f"{prefix} 已停止 status must use `已停止/归档` recommendation")
    if status == "无法确认" and recommendation not in {"仅作线索", "已停止/归档"}:
        errors.append(f"{prefix} 无法确认 status can only use `仅作线索` or `已停止/归档`")
    return errors


def has_insufficient_practice_evidence(labels: dict[str, str]) -> bool:
    return PRACTICE_EVIDENCE_INSUFFICIENT_MARKER in labels.get("实践来源", "")


def validate_practice_evidence_gate(prefix: str, labels: dict[str, str]) -> list[str]:
    errors: list[str] = []
    if not has_insufficient_practice_evidence(labels):
        return errors

    recommendation = labels["推荐等级"].strip()
    backlog = labels["待核验问题"].strip()
    if recommendation not in PRACTICE_EVIDENCE_ALLOWED_RECOMMENDATIONS:
        errors.append(
            f"{prefix} 实践证据不足 profiles can only use `仅作线索` or `已停止/归档` recommendation"
        )
    if backlog == "无":
        errors.append(f"{prefix} 实践证据不足 profiles must include a structured 待核验问题 block")
    return errors


def validate_unknown_linkage(prefix: str, labels: dict[str, str]) -> list[str]:
    errors: list[str] = []
    recommendation = labels["推荐等级"].strip()
    backlog = labels["待核验问题"].strip()
    unknown_key_fields = has_unknown_key_fields(labels)
    if unknown_key_fields and backlog == "无":
        errors.append(f"{prefix} 待核验问题 cannot be `无` when key fields are unknown")
    if recommendation == "直接推荐" and backlog != "无":
        errors.append(f"{prefix} 直接推荐 cannot coexist with pending verification")
    if recommendation == "直接推荐" and not can_be_directly_recommended(labels):
        errors.append(f"{prefix} 直接推荐 cannot coexist with unknown key fields or non-normal status")
    if (
        has_precise_money_path_unknown(labels.get("资金路径", ""))
        and recommendation not in MONEY_PATH_UNKNOWN_ALLOWED_RECOMMENDATIONS
    ):
        errors.append(
            f"{prefix} profiles with an unknown clearing node can only use "
            "`仅作线索` or `已停止/归档` recommendation"
        )
    return errors


def validate_profile(path: Path, profile: tuple[str, dict[str, str], list[str]]) -> list[str]:
    errors: list[str] = []
    profile_name, labels, duplicate_labels = profile
    prefix = f"{relative_path(path)}: {profile_name}:"

    for duplicate in duplicate_labels:
        errors.append(f"{prefix} duplicate label `{duplicate}`")
    allowed_labels = set(REQUIRED_LABELS) | set(ALLOWED_OPTIONAL_LABELS)
    for label in labels:
        if label not in allowed_labels:
            errors.append(f"{prefix} unknown label `{label}`")
    for label in REQUIRED_LABELS:
        if label not in labels or not labels[label].strip():
            errors.append(f"{prefix} missing required label `{label}`")
    for label in ALLOWED_OPTIONAL_LABELS:
        if label in labels and not labels[label].strip():
            errors.append(f"{prefix} optional label `{label}` must be non-empty when present")
    if errors:
        return errors

    recommendation = labels["推荐等级"].strip()
    status = status_name(labels["当前状态"])

    if recommendation not in ALLOWED_RECOMMENDATIONS:
        errors.append(f"{prefix} 推荐等级 must be one of {sorted(ALLOWED_RECOMMENDATIONS)}")
    if status not in ALLOWED_STATUSES:
        errors.append(f"{prefix} 当前状态 must be one of {sorted(ALLOWED_STATUSES)}")
    if not validate_verification_date(labels["最后核验日期"]):
        errors.append(f"{prefix} 最后核验日期 must use a real YYYY-MM-DD date")
    if not validate_money_path(labels["资金路径"]):
        errors.append(f"{prefix} 资金路径 must use four explicit non-empty nodes")
    if status not in OFFICIAL_SOURCE_EXEMPT_STATUSES and not validate_official_source(labels["官方来源"]):
        errors.append(f"{prefix} 官方来源 must include at least one valid HTTP(S) link")
    errors.extend(validate_fee_breakdown(prefix, labels["固定费用、提现费、退款费和拒付费"]))

    backlog = labels["待核验问题"].strip()
    if backlog != "无":
        errors.extend(validate_backlog(prefix, backlog))

    errors.extend(validate_status_and_recommendation(prefix, status, recommendation))
    errors.extend(validate_practice_evidence_gate(prefix, labels))
    errors.extend(validate_unknown_linkage(prefix, labels))
    return errors


def validate_file(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    profiles = parse_profiles(text)
    if not profiles:
        if text.strip():
            return [f"{relative_path(path)}: contains content but no `##` profiles"]
        return []
    errors: list[str] = []
    for profile in profiles:
        errors.extend(validate_profile(path, profile))
    return errors


def validate_repository(root: Path) -> list[str]:
    errors: list[str] = []
    seen_platforms: dict[str, str] = {}
    references_root = root / "skills" / "fxskill" / "references"
    for path in sorted(references_root.glob("payment-platform-*.md")):
        text = path.read_text(encoding="utf-8")
        profiles = parse_profiles(text)
        errors.extend(validate_file(path))
        for name, _, _ in profiles:
            location = relative_path(path)
            if name in seen_platforms:
                errors.append(f"{location}: duplicate platform `{name}` also defined in {seen_platforms[name]}")
            else:
                seen_platforms[name] = location
    return errors


def count_profiles(root: Path) -> int:
    count = 0
    references_root = root / "skills" / "fxskill" / "references"
    for path in sorted(references_root.glob("payment-platform-*.md")):
        count += len(parse_profiles(path.read_text(encoding="utf-8")))
    return count


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    errors = validate_repository(root)
    if errors:
        for error in errors:
            print(error)
        return 1
    print(f"{count_profiles(root)} payment platform profiles validated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
