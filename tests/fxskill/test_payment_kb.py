from pathlib import Path
import importlib.util
import re
import tempfile
import unittest
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "validate_payment_kb", ROOT / "scripts" / "validate_payment_kb.py"
)
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


PRECISE_UNPUBLISHED_PAGE = "未公开统一数字（以签约页为准）"
PRECISE_UNPUBLISHED_CONTRACT = "未公开统一数字（以合同为准）"
PRECISE_UNPUBLISHED_BACKEND = "未公开统一数字（以后台显示为准）"
PRECISE_UNPUBLISHED_QUOTE = "未公开统一数字（以报价单为准）"

VALID_BACKLOG = "\n".join(
    [
        "",
        "- 缺失事实：尚未确认个体工商户是否可销售 AI 图像额度包。",
        "- 已查来源：2026-07-15 已检查官网申请页、费率页和开发文档 https://example.com/help-center。",
        "- 需要询问：商务团队是否支持个体工商户销售 AI 图像额度包？",
        "- 可接受证据：官方页面、文档、合同、后台截图、申请结果、报价单、书面回复、邮件或盖章协议中明确写出适用主体、类目和结算路径。",
    ]
)
INSUFFICIENT_PRACTICE_EVIDENCE = (
    "实践证据不足：2026-07-15 未找到两条相互独立、当前、可复核的真实接入记录。"
)
BACKLOG_WITH_UNIFIED_UNPUBLISHED_RATE = "\n".join(
    [
        "",
        "- 缺失事实：尚未确认该平台面向中国大陆企业的统一平台服务费。",
        "- 已查来源：2026-07-15 已检查官网费率页 https://example.com/pricing ，该页面未公开统一费率。",
        "- 需要询问：商务团队是否可以提供面向中国大陆企业商户的平台服务费报价？",
        "- 可接受证据：官方页面、报价单、合同或书面回复中明确写出适用主体和费率。",
    ]
)
BACKLOG_WITH_UNCONFIRMED_FACT = "\n".join(
    [
        "",
        "- 缺失事实：无法确认个体工商户是否可销售 AI 图像额度包。",
        "- 已查来源：2026-07-15 已检查官网申请页和开发文档 https://example.com/help-center。",
        "- 需要询问：商务团队是否支持个体工商户销售 AI 图像额度包？",
        "- 可接受证据：官方书面回复明确写出适用主体、类目和结算路径。",
    ]
)
FEE_BREAKDOWN = "\n".join(
    [
        "固定费用：0",
        "提现费：无此项",
        "退款费：无此项",
        f"拒付费：{PRECISE_UNPUBLISHED_PAGE}",
    ]
)

BASE_PROFILE = {
    "当前状态": "正常运营",
    "平台类型": "服务商",
    "支付角色": "技术服务方",
    "资金路径": "买家 -> 收款方 -> 清算方 -> 卖家对公银行账户",
    "卖家地区": "中国大陆",
    "支持主体": "企业",
    "买家地区与币种": "中国大陆买家，人民币",
    "支付方式": "微信支付、支付宝",
    "适合商品": "数字服务",
    "平台服务费": "1%",
    "支付通道费": "0.6%",
    "结算": "结算到中国大陆企业对公银行账户。",
    "固定费用、提现费、退款费和拒付费": FEE_BREAKDOWN,
    "结算周期与最低结算额": "T+1，最低结算额 100 元。",
    "推荐等级": "直接推荐",
    "适用条件": "中国大陆企业，销售数字服务。",
    "不适用条件": "自然人直接收款。",
    "最后核验日期": "2026-07-15",
    "官方来源": "https://example.com/official",
    "实践来源": "https://example.com/practice-one\nhttps://example.com/practice-two",
    "待核验问题": "无",
}

OPTIONAL_LABELS = (
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
DOMESTIC_SCENARIOS = (
    "中国大陆自然人验证首批订单",
    "中国大陆个体户 AI 生图额度包",
    "中国大陆个体户 30 天会员",
    "中国大陆企业 SaaS 单次支付",
    "数字资料或课程快速销售",
    "平台型网站代收与分账",
)
DOMESTIC_SCENARIO_FIELDS = (
    "主路线",
    "当前成本",
    "成立条件",
    "执行路径",
    "最容易卡住",
    "备选",
    "引用档案",
)
DOMESTIC_SCENARIO_COST_LABELS = (
    "平台服务费",
    "通道费",
    "固定费",
    "提现费",
    "退款费",
    "拒付费",
    "结算周期",
)
DOMESTIC_SCENARIO_MINIMUM_OR_RETAINED_LABELS = (
    "最低结算额",
    "留存额",
    "最低转出额",
    "可提现余额",
)
DOMESTIC_SCENARIO_CONDITION_LABELS = (
    "主体",
    "类目",
    "结算",
)
DOMESTIC_SCENARIO_PAYMENT_MODEL_LABELS = (
    "支付模式",
    "支付模型",
)
TASK_6_SCENARIO_MARKERS = (
    "R7 大陆自然人最低可用收款路线",
    "R8 个体户比较虎皮椒与 XorPay",
    "R9 小报童不是网站支付 API",
    "R10 当前平台费用组成",
)
USER_DECISION_FIELDS = (
    "能不能申请",
    "需要准备",
    "怎么收费",
    "多久能到账",
    "会员和自动续费",
    "接入难度",
    "最容易踩的坑",
)
USER_DECISION_PROFILES = (
    ("payment-platform-cn-direct.md", "微信支付"),
    ("payment-platform-cn-direct.md", "支付宝"),
    ("payment-platform-cn-services.md", "虎皮椒"),
    ("payment-platform-cn-services.md", "XorPay"),
)
PAYMENT_USER_ACCEPTANCE_CASE_IDS = tuple(f"P{index:02d}" for index in range(1, 21))
PAYMENT_USER_ACCEPTANCE_TOPICS = (
    "自然人",
    "个体工商户",
    "自动续费",
    "H5",
    "JSAPI",
    "XorPay",
    "虎皮椒",
    "费用",
    "到账",
    "ICP",
    "回调",
    "退款",
    "Vibe Coding",
)


class PaymentKnowledgeBaseTests(unittest.TestCase):
    def render_profile(self, name: str = "测试平台", **overrides: str) -> str:
        fields = dict(BASE_PROFILE)
        fields.update(overrides)
        lines = [f"## {name}", ""]
        for label, value in fields.items():
            value_lines = value.splitlines() or [""]
            lines.append(f"- {label}：{value_lines[0]}")
            for extra_line in value_lines[1:]:
                lines.append(f"  {extra_line}")
        lines.append("")
        return "\n".join(lines)

    def write_profile_file(self, root: Path, content: str, filename: str = "payment-platform-test.md") -> Path:
        path = root / "skills" / "fxskill" / "references" / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, "utf-8")
        return path

    def remove_label(self, profile_text: str, label: str) -> str:
        prefix = f"- {label}："
        return "\n".join(
            line for line in profile_text.splitlines() if not line.startswith(prefix)
        )

    def parse_domestic_scenario_sections(self):
        text = (ROOT / "skills/fxskill/references/payment-scenarios.md").read_text("utf-8")
        sections = {}
        matches = list(re.finditer(r"^## (.+)$", text, re.MULTILINE))
        for index, match in enumerate(matches):
            start = match.end()
            end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
            sections[match.group(1).strip()] = text[start:end]
        return sections

    def parse_domestic_scenario_actions(self, heading):
        section = self.parse_domestic_scenario_sections()[heading]
        action_match = re.search(
            r"^- 执行路径：\s*\n(?P<actions>(?:  \d+\.[^\n]*(?:\n|$))+)",
            section,
            re.MULTILINE,
        )
        self.assertIsNotNone(action_match, f"{heading} must keep one to three listed actions")
        actions = [
            re.sub(r"^  \d+\.\s*", "", line).strip()
            for line in action_match.group("actions").splitlines()
        ]
        self.assertGreaterEqual(len(actions), 1, f"{heading} must keep at least one listed action")
        self.assertLessEqual(len(actions), 3, f"{heading} must keep at most three listed actions")
        return actions

    def test_core_payment_profiles_put_user_decisions_before_audit_fields(self):
        references = ROOT / "skills/fxskill/references"

        for filename, platform in USER_DECISION_PROFILES:
            text = (references / filename).read_text("utf-8")
            match = re.search(
                rf"^## {re.escape(platform)}\s*$\n(?P<section>.*?)(?=^## |\Z)",
                text,
                re.MULTILINE | re.DOTALL,
            )
            self.assertIsNotNone(match, f"missing profile for {platform}")
            section = match.group("section")
            audit_start = section.find("- 当前状态：")
            self.assertGreaterEqual(audit_start, 0, f"{platform} missing audit profile")
            decision_card = section[:audit_start]
            self.assertIn("### 用户先看", decision_card, f"{platform} missing user decision card")

            positions = []
            for field in USER_DECISION_FIELDS:
                marker = f"- {field}："
                self.assertIn(marker, decision_card, f"{platform} missing `{field}`")
                positions.append(decision_card.index(marker))
            self.assertEqual(sorted(positions), positions, f"{platform} decision fields are out of order")

    def test_payment_recipe_keeps_audit_identity_out_of_default_answers(self):
        text = (ROOT / "skills/fxskill/SKILL.md").read_text("utf-8")

        expected = "能不能申请 -> 需要准备 -> 怎么收费 -> 多久能到账 -> 会员和自动续费 -> 接入难度 -> 最容易踩的坑"
        self.assertIn(expected, text)
        self.assertIn("运营主体、合同主体和资金路径只作为内部核验字段", text)
        self.assertIn("影响申请、收款、结算或售后追责", text)

    def test_twenty_beginner_payment_answers_are_concrete_and_short(self):
        path = ROOT / "tests/fxskill/payment-user-acceptance.md"
        self.assertTrue(path.exists(), "missing payment user acceptance results")
        text = path.read_text("utf-8")
        matches = list(
            re.finditer(
                r"^## (?P<id>P\d{2}) .+?\n(?P<section>.*?)(?=^## P\d{2} |\Z)",
                text,
                re.MULTILINE | re.DOTALL,
            )
        )
        self.assertEqual(PAYMENT_USER_ACCEPTANCE_CASE_IDS, tuple(match.group("id") for match in matches))

        for topic in PAYMENT_USER_ACCEPTANCE_TOPICS:
            self.assertIn(topic, text)

        for match in matches:
            case_id = match.group("id")
            section = match.group("section")
            answer_match = re.search(r"\*\*参考短答\*\*\s*\n\n```text\n(?P<answer>.*?)\n```", section, re.DOTALL)
            self.assertIsNotNone(answer_match, f"{case_id} missing reference answer")
            answer = answer_match.group("answer").strip()
            self.assertTrue(answer.startswith("结论："), f"{case_id} must lead with a conclusion")
            self.assertLessEqual(len(answer), 450, f"{case_id} answer is too long")
            self.assertLessEqual(
                len(re.findall(r"^\d+\. ", answer, re.MULTILINE)),
                3,
                f"{case_id} has more than three actions",
            )
            self.assertNotIn("请联系客服", answer, f"{case_id} falls back to customer-service language")
            self.assertNotIn("合同主体", answer, f"{case_id} exposes an internal audit field")

            status_match = re.search(r"^- 状态：(PASS|GAP)$", section, re.MULTILINE)
            self.assertIsNotNone(status_match, f"{case_id} missing PASS/GAP status")
            gap_match = re.search(r"^- 资料缺口：(.+)$", section, re.MULTILINE)
            self.assertIsNotNone(gap_match, f"{case_id} missing gap assessment")
            if status_match.group(1) == "GAP":
                self.assertNotEqual("无", gap_match.group(1).strip(), f"{case_id} GAP needs a concrete gap")

    def test_domestic_scenario_action_parser_rejects_fourth_action(self):
        original_parser = self.parse_domestic_scenario_sections
        try:
            self.parse_domestic_scenario_sections = lambda: {
                "四条行动场景": "\n".join(
                    [
                        "",
                        "- 执行路径：",
                        "  1. 第一条行动。",
                        "  2. 第二条行动。",
                        "  3. 第三条行动。",
                        "  4. 第四条行动。",
                        "- 最容易卡住：第四条行动不应被解析器漏掉。",
                    ]
                )
            }

            with self.assertRaises(AssertionError):
                self.parse_domestic_scenario_actions("四条行动场景")
        finally:
            self.parse_domestic_scenario_sections = original_parser

    def test_domestic_scenario_action_parser_accepts_one_to_three_actions(self):
        original_parser = self.parse_domestic_scenario_sections
        try:
            for count in (1, 2, 3):
                with self.subTest(count=count):
                    lines = ["", "- 执行路径："]
                    lines.extend(f"  {index}. 第 {index} 条行动。" for index in range(1, count + 1))
                    self.parse_domestic_scenario_sections = lambda lines=lines: {
                        "合法行动场景": "\n".join(lines)
                    }
                    self.assertEqual(count, len(self.parse_domestic_scenario_actions("合法行动场景")))
        finally:
            self.parse_domestic_scenario_sections = original_parser

    def test_task_6_behavior_prompts_are_present_and_specific(self):
        text = (ROOT / "tests/fxskill/scenarios.md").read_text("utf-8")

        for marker in TASK_6_SCENARIO_MARKERS:
            self.assertIn(marker, text)

        expected_fragments = (
            "中国大陆自然人",
            "没有营业执照",
            "只面向国内买家",
            "原创 Notion 模板和 PDF 下载包",
            "中国大陆个体工商户",
            "AI 生图网站",
            "虎皮椒和 XorPay 哪个更适合",
            "小报童能不能替代网站支付 API",
            "XorPay 的费用怎么算",
        )
        for fragment in expected_fragments:
            self.assertIn(fragment, text)

    def test_task_6_rubric_hard_gates_are_present(self):
        text = (ROOT / "tests/fxskill/rubric.md").read_text("utf-8")

        required_phrases = (
            "只说需要核验",
            "没有给出路线",
            "平台清单或平台比较",
            "没有推荐或明确不作为主路线的结论",
            "费用回答不得把一个标题百分比当作总成本",
            "会改变决定的已知费用层",
            "其余未公开费用可以合并一句说明",
            "用户明确要求完整费用拆解或严谨对比时",
        )
        for phrase in required_phrases:
            self.assertIn(phrase, text)

    def test_skill_topic_table_splits_payment_from_general_compliance(self):
        text = (ROOT / "skills/fxskill/SKILL.md").read_text("utf-8")
        table_lines = [line.strip() for line in text.splitlines() if line.startswith("|")]

        payment_rows = [line for line in table_lines if "payment-index.md" in line]
        self.assertEqual(1, len(payment_rows), "payment topic must route to payment-index.md")
        self.assertIn("支付", payment_rows[0])
        for compliance_term in ("备案", "隐私", "Cookie", "版权", "无障碍"):
            self.assertNotIn(compliance_term, payment_rows[0])

        compliance_rows = [line for line in table_lines if "payment-compliance.md" in line]
        self.assertEqual(1, len(compliance_rows), "general compliance topic must route to payment-compliance.md")
        for compliance_term in ("备案", "隐私", "Cookie", "条款", "版权", "无障碍"):
            self.assertIn(compliance_term, compliance_rows[0])
        self.assertNotIn("国内外支付", compliance_rows[0])

    def test_skill_payment_runtime_uses_index_then_one_scenario_and_one_profile(self):
        text = (ROOT / "skills/fxskill/SKILL.md").read_text("utf-8")

        required_phrases = (
            "支付问题先读 `references/payment-index.md`",
            "只读一个相关场景",
            "只读一个相关类别或平台档案",
            "不得一次倾倒全部支付档案",
            "缺失的海外档案不存在时",
        )
        for phrase in required_phrases:
            self.assertIn(phrase, text)

    def test_skill_payment_answer_contract_is_clear_by_default(self):
        text = (ROOT / "skills/fxskill/SKILL.md").read_text("utf-8")

        required_phrases = (
            "资料库深、回答浅",
            "先给一句明确结论",
            "再给 2-4 条真正影响选择的信息",
            "优先能否申请、所需材料、费用、到账、续费能力、接入难度或最大坑",
            "最后给最多三个按顺序的原子步骤",
            "不强制固定标题",
            "不默认输出完整成本卡或条件卡",
        )
        for phrase in required_phrases:
            self.assertIn(phrase, text)

        obsolete_phrases = (
            "一律使用固定标题",
            "`依据` 恰好两个项目符号",
            "每个候选都填写全部标签",
            "从规范档案对应字段原样摘取",
        )
        for phrase in obsolete_phrases:
            self.assertNotIn(phrase, text)

    def test_skill_payment_contract_preserves_decision_boundaries(self):
        text = (ROOT / "skills/fxskill/SKILL.md").read_text("utf-8")

        required_phrases = (
            "不得把 `仅作线索` 平台写成稳定主支付、最便宜或最好",
            "价格证据不足时不得判定最便宜",
            "未公开的费用合并为一句说明",
            "不能为了完整把所有未知标签念一遍",
            "保留来源边界",
        )
        for phrase in required_phrases:
            self.assertIn(phrase, text)

    def test_skill_payment_recipe_selects_subject_and_model_scenario_first(self):
        text = (ROOT / "skills/fxskill/SKILL.md").read_text("utf-8")

        required_phrases = (
            "先按卖家主体 + 支付模式匹配场景标题",
            "主体与支付模式场景优先于产品形式场景",
            "自然人首单问题固定使用 `中国大陆自然人验证首批订单`",
            "内容托管场景至多进入一个有条件备选槽",
        )
        for phrase in required_phrases:
            self.assertIn(phrase, text)

    def test_skill_payment_recipe_only_expands_on_explicit_request(self):
        text = (ROOT / "skills/fxskill/SKILL.md").read_text("utf-8")

        required_phrases = (
            "只有用户明确要求完整费用拆解或严谨对比时才展开",
            "不得用缺项拼总价",
            "同类候选按相同且会改变决定的维度比较",
        )
        for phrase in required_phrases:
            self.assertIn(phrase, text)

    def test_skill_payment_recipe_keeps_actions_atomic(self):
        text = (ROOT / "skills/fxskill/SKILL.md").read_text("utf-8")

        required_phrases = (
            "每一步只放一个主要动作",
            "按依赖顺序排列",
            "总步骤不超过三条",
            "结论不要塞进行动项",
        )
        for phrase in required_phrases:
            self.assertIn(phrase, text)

    def test_payment_recipe_overrides_global_semantic_contract(self):
        skill = (ROOT / "skills/fxskill/SKILL.md").read_text("utf-8")
        rubric = (ROOT / "tests/fxskill/rubric.md").read_text("utf-8")

        for text in (skill, rubric):
            self.assertIn("支付答案配方优先于全局语义输出契约", text)
            self.assertIn("主路线或不选某个平台", text)
            self.assertIn("描述性结论不计入行动", text)
            self.assertIn("真正命令用户执行的操作只放在最后步骤区", text)

    def test_skill_payment_recipe_refuses_unproven_price_rankings(self):
        text = (ROOT / "skills/fxskill/SKILL.md").read_text("utf-8")

        required_phrases = (
            "成本未知或比较维度不一致时",
            "明确说明价格排名尚未成立",
            "固定费用或关键费用未公开时，不得使用“低固定成本”“最省固定成本”",
            "固定费用未知时，只能称为“当前可行的官方核验入口”，不得称“低成本候选”",
            "当前费率、资格或状态必须简短标明核验日期",
        )
        for phrase in required_phrases:
            self.assertIn(phrase, text)

    def test_skill_explicit_fee_answers_keep_source_settlement_and_unknown_boundaries(self):
        text = (ROOT / "skills/fxskill/SKILL.md").read_text("utf-8")

        for phrase in (
            "平台页面声称的通道费不得写成支付机构官方统一费率",
            "平台费与平台自述通道费分开写",
            "结算周期或到账口径",
            "已公开的结算口径不得省略",
            "最低结算额或提现费是否公开",
            "未知项最多点名两项，其余统一写“其他费用未公开”",
            "平台费率已按套餐列出时，不再逐档换算单笔金额",
            "用户点名某一套餐时才换算该档",
            "不得计算套餐销量分界或总成本",
        ):
            self.assertIn(phrase, text)

    def test_skill_natural_person_route_keeps_subject_branch_ahead_of_integration(self):
        text = (ROOT / "skills/fxskill/SKILL.md").read_text("utf-8")

        for phrase in (
            "提交资料 → 支持且费用、结算可接受时签约 → 后台明确不支持且允许个体工商户时登记个体工商户",
            "支付回调、验签等技术接入留到下一轮",
        ):
            self.assertIn(phrase, text)

    def test_skill_payment_recipe_keeps_lead_only_comparisons_on_official_route(self):
        text = (ROOT / "skills/fxskill/SKILL.md").read_text("utf-8")

        required_phrases = (
            "被比较候选全部是 `仅作线索` 时，明确它们不作为主支付",
            "不得再挑其中一个作备选或排序",
            "回到规范场景的可防守路线",
            "回到规范场景时称为官方核验入口，不得称为已成立主支付",
            "四条关键信息依次为：当前可注册性、主体或类目、主要费用、资金或结算路径",
            "比较答案必须按四条短信息输出，四项都出现，不合并省略",
            "候选都不作为主支付；当前先走规范场景的官方核验入口",
            "比较事实只描述当前证据，不写需要用户核验或确认的操作",
            "真实订单验证只保留一个验收动作，不展开回调、查单、验签或幂等子动作",
            "平台比较必须用“截至 YYYY-MM-DD”标明核验日期",
            "真实订单验证写明“仅当上一项配置完成时”",
        )
        for phrase in required_phrases:
            self.assertIn(phrase, text)

    def test_skill_creator_platform_answer_keeps_api_and_business_boundaries(self):
        text = (ROOT / "skills/fxskill/SKILL.md").read_text("utf-8")

        self.assertIn("托管内容平台能否替代网站支付 API", text)
        self.assertIn("API 能力、主要费用、主体与内容边界、结算或退款限制", text)

    def test_skill_distinguishes_stable_main_payment_from_verification_entry(self):
        text = (ROOT / "skills/fxskill/SKILL.md").read_text("utf-8")

        self.assertIn("不得把 `仅作线索` 平台写成稳定主支付", text)
        self.assertIn("可以作为第一个官方核验入口", text)
        self.assertIn("正式使用仍以后台或签约结果为条件", text)

    def test_skill_payment_recipe_stays_within_requested_length(self):
        text = (ROOT / "skills/fxskill/SKILL.md").read_text("utf-8")
        section = text.split("### 支付答案配方", 1)[1].split("SEO/GEO 共用", 1)[0]
        nonblank_lines = [line for line in section.splitlines() if line.strip()]

        self.assertGreaterEqual(len(nonblank_lines), 15)
        self.assertLessEqual(len(nonblank_lines), 25)

    def test_payment_rubric_rewards_clear_answers_instead_of_full_cards(self):
        text = (ROOT / "tests/fxskill/rubric.md").read_text("utf-8")

        self.assertIn("支付直达专题清晰度是独立硬门槛", text)
        self.assertIn("不强制固定标题", text)
        self.assertIn("其余未公开费用可以合并一句说明", text)
        self.assertNotIn("支付直达专题固定标题", text)
        self.assertNotIn("支付路线与费用完整性", text)

    def test_natural_person_scenario_enforces_official_evidence_dependencies(self):
        section = self.parse_domestic_scenario_sections()["中国大陆自然人验证首批订单"]
        actions = self.parse_domestic_scenario_actions("中国大陆自然人验证首批订单")

        self.assertIn("一站式接入", actions[0])
        for term in ("当前账号", "商品类目", "网站资料"):
            self.assertIn(term, actions[0])
        self.assertIn("仅当后台结果显示可开通", actions[1])
        self.assertIn("费用和结算可接受", actions[1])
        self.assertIn("完成签约", actions[1])
        self.assertIn("仅当后台明确当前主体不支持且允许个体工商户时", actions[2])
        self.assertIn("登记个体工商户", actions[2])
        self.assertIn("个人收款场景", section)
        self.assertIn("后台申请结果", section)
        self.assertNotIn("最便宜", section)
        self.assertNotIn("申请前先取得", section)
        self.assertNotIn("面包多", "\n".join(actions))

        alternative_match = re.search(r"^- 备选[：:](.+)$", section, re.MULTILINE)
        self.assertIsNotNone(alternative_match)
        self.assertIn("明确允许个体工商户", alternative_match.group(1))
        self.assertIn("不替代官方主路线", alternative_match.group(1))

    def test_alipay_ai_web_profile_keeps_personal_product_boundary(self):
        text = (ROOT / "skills/fxskill/references/payment-platform-cn-direct.md").read_text("utf-8")
        profiles = {name: labels for name, labels, _ in module.parse_profiles(text)}
        alipay = profiles["支付宝"]

        self.assertIn("AI 网页应用收款明确支持个人收款场景和个人开发者", alipay["支持主体"])
        self.assertIn("不能扩大为所有支付宝网站支付", alipay["支持主体"])
        self.assertIn("一站式接入", alipay["接入路径"])
        self.assertIn("提交当前账号、商品类目和网站资料", alipay["接入路径"])
        self.assertIn("AI 订阅 SaaS 联系销售", alipay["接入路径"])
        self.assertIn("AI 按量付费", alipay["接入路径"])
        self.assertIn("402", alipay["接入路径"])
        for phrase in ("中国大陆商家", "网页一次性支付", "订阅", "席位", "API/Skill/MCP 按量计费"):
            self.assertIn(phrase, alipay["适用条件"])
        self.assertIn("自然人使用 AI 网页应用收款", alipay["适用条件"])
        self.assertIn("后台申请结果", alipay["适用条件"])
        self.assertIn("后台申请结果", alipay["待核验问题"])
        self.assertIn("费率", alipay["待核验问题"])
        self.assertIn("结算", alipay["待核验问题"])

    def test_hupijiao_profile_marks_conflicting_mode_signals(self):
        text = (ROOT / "skills/fxskill/references/payment-platform-cn-services.md").read_text("utf-8")
        profiles = {name: labels for name, labels, _ in module.parse_profiles(text)}
        hupijiao = profiles["虎皮椒"]

        for field in ("支付角色", "资金路径"):
            self.assertIn("两种模式信号", hupijiao[field])
            self.assertIn("不能写成统一已确认路径", hupijiao[field])
        self.assertIn("实际账户采用哪一模式", hupijiao["待核验问题"])
        self.assertIn("合同和结算路径", hupijiao["待核验问题"])

    def test_ai_credit_scenario_gates_configuration_and_real_order(self):
        actions = self.parse_domestic_scenario_actions("中国大陆个体户 AI 生图额度包")

        self.assertEqual(
            [
                "取得支付宝 AI 支付或商家平台对个体工商户主体、AI 生图额度包类目、费率和结算的书面结果。",
                "仅当上一项结果支持时，配置支付宝 AI 网页应用收款链路。",
                "仅当上一项结果支持时，完成一笔小额真实订单。",
            ],
            actions,
        )

    def test_enterprise_saas_scenario_requires_written_native_dependencies(self):
        section = self.parse_domestic_scenario_sections()["中国大陆企业 SaaS 单次支付"]
        actions = self.parse_domestic_scenario_actions("中国大陆企业 SaaS 单次支付")

        self.assertIn("作为第一个官方核验入口", section)
        self.assertNotIn("主路线走微信支付 Native", section)
        self.assertEqual(
            [
                "取得微信支付对企业主体、目标 AI/数字类目、费率和结算的官方书面结果。",
                "仅当上一项结果支持时，申请企业商户号的 Native 权限。",
                "仅当上一项结果支持时，接入 Native 支付链路。",
            ],
            actions,
        )

    def test_membership_scenario_requires_written_native_dependencies(self):
        actions = self.parse_domestic_scenario_actions("中国大陆个体户 30 天会员")

        self.assertEqual(
            [
                "取得微信支付对个体工商户或小微商户主体、30 天会员权益类目、费率和结算的官方书面结果。",
                "仅当上一项结果支持时，申请微信支付 Native 产品权限。",
                "仅当上一项结果支持时，接入 Native 支付链路。",
            ],
            actions,
        )

    def test_payment_compliance_defers_answer_shape_to_skill(self):
        text = (ROOT / "skills/fxskill/references/payment-compliance.md").read_text("utf-8")

        self.assertIn("直接支付专题复用 `SKILL.md` 的“支付答案配方”", text)
        self.assertNotIn("不用“并、和、再、同时、以及、；”连接额外操作", text)

    def test_payment_compliance_points_to_index_without_cn_platform_fact_duplicates(self):
        text = (ROOT / "skills/fxskill/references/payment-compliance.md").read_text("utf-8")

        self.assertIn("payment-index.md", text)
        forbidden_cn_platform_fact_labels = (
            "微信支付小微商户进件产品介绍",
            "微信支付普通商户主体资料",
            "支付宝开放平台入口",
        )
        for label in forbidden_cn_platform_fact_labels:
            self.assertNotIn(label, text)

        retained_shared_rules = (
            "拒绝伪造主体",
            "借用账户",
            "登记后每年还要报年报",
            "路线 | 适合与责任边界",
            "直接支付专题复用 `SKILL.md` 的“支付答案配方”",
        )
        for phrase in retained_shared_rules:
            self.assertIn(phrase, text)

        for obsolete_phrase in ("成品固定为", "成本卡", "条件卡", "**现状**", "**依据**", "**风险**"):
            self.assertNotIn(obsolete_phrase, text)

    def test_repository_profiles_are_valid(self):
        errors = module.validate_repository(ROOT)
        self.assertEqual([], errors, "\n".join(errors))

    def test_index_routes_every_domestic_category(self):
        text = (ROOT / "skills/fxskill/references/payment-index.md").read_text("utf-8")
        for path in (
            "payment-platform-cn-direct.md",
            "payment-platform-cn-services.md",
            "payment-platform-cn-creators.md",
            "payment-scenarios.md",
        ):
            self.assertIn(path, text)

    def test_cn_direct_profiles_have_official_organization_sources(self):
        path = ROOT / "skills/fxskill/references/payment-platform-cn-direct.md"
        text = path.read_text("utf-8") if path.exists() else ""
        profiles = {
            name: labels
            for name, labels, _ in module.parse_profiles(text)
        }
        expected_hosts = {
            "微信支付": ("wechatpay.cn", "qq.com"),
            "支付宝": ("alipay.com",),
            "银联": ("unionpay.com",),
        }

        missing = [name for name in expected_hosts if name not in profiles]
        self.assertEqual([], missing, f"missing direct profile heading(s): {', '.join(missing)}")

        bad_sources = []
        for name, host_suffixes in expected_hosts.items():
            urls = module.extract_candidate_urls(profiles[name].get("官方来源", ""))
            hosts = [
                urlparse(url).hostname or ""
                for url in urls
                if module.is_valid_official_url(url)
            ]
            if not any(
                host == suffix or host.endswith(f".{suffix}")
                for host in hosts
                for suffix in host_suffixes
            ):
                bad_sources.append(f"{name}: {profiles[name].get('官方来源', '')}")

        self.assertEqual([], bad_sources, "missing official organization source host(s)")

    def test_cn_service_profiles_cover_task_3_platforms_and_roles(self):
        path = ROOT / "skills/fxskill/references/payment-platform-cn-services.md"
        text = path.read_text("utf-8") if path.exists() else ""
        profiles = {
            name: labels
            for name, labels, _ in module.parse_profiles(text)
        }
        expected_names = ("虎皮椒", "XorPay", "PAYJS", "面包多 Pay", "BufPay")

        missing = [name for name in expected_names if name not in profiles]
        self.assertEqual([], missing, f"missing service profile heading(s): {', '.join(missing)}")

        bad_fields = []
        for name in expected_names:
            labels = profiles[name]
            for label in ("运营主体", "支付角色", "资金路径"):
                if not labels.get(label, "").strip():
                    bad_fields.append(f"{name}: {label}")
            if not module.validate_money_path(labels.get("资金路径", "")):
                bad_fields.append(f"{name}: 资金路径 must use four explicit segments")

        self.assertEqual([], bad_fields, "service profile role and money-path contract failures")

    def test_cn_creator_profiles_cover_task_4_platforms_and_boundaries(self):
        path = ROOT / "skills/fxskill/references/payment-platform-cn-creators.md"
        text = path.read_text("utf-8") if path.exists() else ""
        profiles = {
            name: labels
            for name, labels, _ in module.parse_profiles(text)
        }
        expected_names = ("面包多内容交易", "爱发电", "小报童")

        missing = [name for name in expected_names if name not in profiles]
        self.assertEqual([], missing, f"missing creator profile heading(s): {', '.join(missing)}")

        bad_platform_types = []
        for name in expected_names:
            platform_type = profiles[name].get("平台类型", "")
            if "官方直连" in platform_type:
                bad_platform_types.append(f"{name}: must not be 官方直连")
            if "内容平台" not in platform_type and "代售" not in platform_type:
                bad_platform_types.append(f"{name}: 平台类型 must include 内容平台 or 代售")

        self.assertEqual([], bad_platform_types, "creator profiles must be hosted-content or resale platforms")

    def test_domestic_scenarios_cover_task_5_decision_paths(self):
        sections = self.parse_domestic_scenario_sections()

        missing_headings = [heading for heading in DOMESTIC_SCENARIOS if heading not in sections]
        self.assertEqual([], missing_headings, f"missing scenario heading(s): {', '.join(missing_headings)}")

        missing_fields = []
        for heading in DOMESTIC_SCENARIOS:
            section = sections[heading]
            for field in DOMESTIC_SCENARIO_FIELDS:
                if not re.search(rf"^- {re.escape(field)}[：:]", section, re.MULTILINE):
                    missing_fields.append(f"{heading}: {field}")

        self.assertEqual([], missing_fields, f"missing scenario field(s): {', '.join(missing_fields)}")

    def test_domestic_scenarios_cost_and_condition_blocks_cover_contract_labels(self):
        sections = self.parse_domestic_scenario_sections()
        missing_cost_labels = []
        missing_condition_labels = []

        for heading in DOMESTIC_SCENARIOS:
            section = sections.get(heading, "")

            cost_match = re.search(r"^- 当前成本[：:](.+)$", section, re.MULTILINE)
            cost_line = cost_match.group(1) if cost_match else ""
            for label in DOMESTIC_SCENARIO_COST_LABELS:
                if label not in cost_line:
                    missing_cost_labels.append(f"{heading}: {label}")
            if not any(label in cost_line for label in DOMESTIC_SCENARIO_MINIMUM_OR_RETAINED_LABELS):
                missing_cost_labels.append(f"{heading}: 最低结算额/留存额")

            condition_match = re.search(r"^- 成立条件[：:](.+)$", section, re.MULTILINE)
            condition_line = condition_match.group(1) if condition_match else ""
            for label in DOMESTIC_SCENARIO_CONDITION_LABELS:
                if label not in condition_line:
                    missing_condition_labels.append(f"{heading}: {label}")
            if not any(label in condition_line for label in DOMESTIC_SCENARIO_PAYMENT_MODEL_LABELS):
                missing_condition_labels.append(f"{heading}: 支付模式/model")

        self.assertEqual([], missing_cost_labels, f"missing cost labels: {', '.join(missing_cost_labels)}")
        self.assertEqual(
            [],
            missing_condition_labels,
            f"missing condition labels: {', '.join(missing_condition_labels)}",
        )

    def test_mianbaoduo_creator_profile_uses_public_content_trade_fee_lines(self):
        path = ROOT / "skills/fxskill/references/payment-platform-cn-creators.md"
        text = path.read_text("utf-8") if path.exists() else ""
        profiles = {
            name: labels
            for name, labels, _ in module.parse_profiles(text)
        }

        platform_fee = profiles["面包多内容交易"].get("平台服务费", "")
        payment_fee = profiles["面包多内容交易"].get("支付通道费", "")

        self.assertEqual("普通模式 5% 平台费；闪电结算总服务费 5.7%；服务单 3%。", platform_fee)
        self.assertEqual(
            "普通模式 1% 第三方支付费；闪电结算总服务费已含通道成本；服务单未单独公开通道费。",
            payment_fee,
        )
        self.assertNotIn("面包多 Pay", platform_fee)

    def test_cn_service_numeric_rates_have_same_section_official_source(self):
        path = ROOT / "skills/fxskill/references/payment-platform-cn-services.md"
        text = path.read_text("utf-8") if path.exists() else ""
        bad_sources = []
        for name, labels, _ in module.parse_profiles(text):
            section_text = "\n".join(labels.values())
            if not re.search(r"\d+(?:\.\d+)?\s*%", section_text):
                continue
            official_source = labels.get("官方来源", "")
            if not any(
                module.is_valid_official_url(url)
                for url in module.extract_candidate_urls(official_source)
            ):
                bad_sources.append(name)

        self.assertEqual([], bad_sources, "numeric service rates need official source URLs in the same profile")

    def test_hupijiao_profile_tracks_public_entry_fee_conflicts_and_backup_boundary(self):
        path = ROOT / "skills/fxskill/references/payment-platform-cn-services.md"
        text = path.read_text("utf-8") if path.exists() else ""
        profiles = {
            name: labels
            for name, labels, _ in module.parse_profiles(text)
        }
        hupijiao = profiles["虎皮椒"]

        entry_path = hupijiao["接入路径"]
        self.assertIn("https://admin.xunhupay.com/sign-up.html", entry_path)
        self.assertIn("通道临时关闭", entry_path)
        self.assertIn("https://admin.dpweixin.com/sign-up.html", entry_path)
        self.assertIn("不能直接完成正式新注册", entry_path)
        self.assertIn("书面复核后才使用备用平台", entry_path)

        platform_fee = hupijiao["平台服务费"]
        self.assertIn("2%+", platform_fee)
        self.assertIn("3%+", platform_fee)
        self.assertIn("5%+", platform_fee)
        self.assertIn("后台签约页、合同或报价单", platform_fee)
        self.assertNotIn("以公开申请页展示为准", platform_fee)

        settlement = hupijiao["结算周期与最低结算额"]
        self.assertIn("未公开统一数字（以后台显示或通道规则为准）", settlement)

        official_sources = hupijiao["官方来源"]
        self.assertIn("https://www.xunhupay.com/258.html", official_sources)
        self.assertIn("https://admin.dpweixin.com/sign-up.html", official_sources)

        practical_issues = hupijiao["实际问题"]
        self.assertIn("app/mimu.html", practical_issues)
        self.assertIn("历史/不同 App 通知机制", practical_issues)

        backlog = (ROOT / "skills/fxskill/references/payment-research-backlog.md").read_text("utf-8")
        self.assertIn("### 虎皮椒备用平台主体与资金路径", backlog)
        self.assertIn("书面复核后才使用备用平台", backlog)

    def test_xorpay_profile_tracks_unverified_subject_fee_and_entry_boundaries(self):
        path = ROOT / "skills/fxskill/references/payment-platform-cn-services.md"
        text = path.read_text("utf-8") if path.exists() else ""
        profiles = {
            name: labels
            for name, labels, _ in module.parse_profiles(text)
        }
        xorpay = profiles["XorPay"]

        operator = xorpay["运营主体"]
        self.assertIn("无法确认", operator)
        self.assertIn("XorPay.com", operator)
        self.assertIn("粤ICP备18047748号", operator)
        self.assertIn("工信部查询、合同、签约页或书面回复", operator)

        self.assertIn("未公开统一边界", xorpay["卖家地区"])
        self.assertIn("未公开统一边界", xorpay["买家地区与币种"])

        product_fit = xorpay["适合商品"]
        self.assertIn("官网自述面向独立开发者、个体户和小微企业", product_fit)
        self.assertIn("AI 生图额度、数字会员或虚拟权益", product_fit)
        self.assertIn("进件结果", product_fit)

        fees = xorpay["固定费用、提现费、退款费和拒付费"]
        self.assertIn("任一渠道资料进件成功视为开通成功", fees)
        self.assertIn("开通成功不能退款", fees)
        self.assertIn("提现费：未公开统一数字", fees)
        self.assertIn("退款费：未公开统一数字", fees)
        self.assertIn("拒付费：未公开统一数字", fees)
        self.assertNotIn("提现费：无此项", fees)
        self.assertNotIn("退款费：无此项", fees)
        self.assertNotIn("拒付费：无此项", fees)

        settlement = xorpay["结算周期与最低结算额"]
        self.assertIn("微信 T+1", settlement)
        self.assertIn("支付宝即时到账", settlement)
        self.assertIn("最低结算额未公开统一数字", settlement)
        self.assertIn("30 天无交易可能被通道回收权限", settlement)
        self.assertIn("重新开通需重新收费 100 元", settlement)

        entry_path = xorpay["接入路径"]
        self.assertIn("https://xorpay.com/main", entry_path)
        self.assertIn("/login", entry_path)
        self.assertIn("登录页可勾选注册", entry_path)
        self.assertIn("/register 404", entry_path)
        self.assertIn("只有后台结果支持时才配置支付接口", entry_path)

        backlog = (ROOT / "skills/fxskill/references/payment-research-backlog.md").read_text("utf-8")
        self.assertIn("### XorPay 主体、地区、费用与进件边界", backlog)
        for phrase in (
            "合同主体、备案主体",
            "卖家地区",
            "买家地区与币种",
            "最低结算额",
            "提现费、退款费、拒付费",
            "后台申请/进件页",
            "公告页",
            "AI 生图额度、数字会员、虚拟权益包",
            "书面费率",
        ):
            self.assertIn(phrase, backlog)

    def test_payjs_profile_tracks_public_conflicts_and_unverified_boundaries(self):
        path = ROOT / "skills/fxskill/references/payment-platform-cn-services.md"
        text = path.read_text("utf-8") if path.exists() else ""
        profiles = {
            name: labels
            for name, labels, _ in module.parse_profiles(text)
        }
        payjs = profiles["PAYJS"]

        operator = payjs["运营主体"]
        self.assertIn("北京顶风科技有限公司", operator)
        self.assertIn("agreement", operator)
        self.assertIn("404", operator)
        self.assertIn("合同主体以签约合同或后台协议为准", operator)

        self.assertIn("未公开统一边界", payjs["卖家地区"])
        self.assertIn("未公开统一边界", payjs["买家地区与币种"])

        payment_methods = payjs["支付方式"]
        self.assertIn("账号 FAQ 明确不支持 H5、APP 支付，也不支持支付宝", payment_methods)
        self.assertIn("H5 接口处于测试阶段", payment_methods)
        self.assertIn("域名需工单备案、一级域名需 ICP 备案", payment_methods)
        self.assertIn("支付与清算 FAQ、规则 FAQ 和收银台 API 仍出现支付宝口径", payment_methods)
        self.assertIn("公开文档存在冲突", payment_methods)
        self.assertIn("未确认前不作为已确认能力", payment_methods)

        platform_fee = payjs["平台服务费"]
        self.assertIn("H5 使用页写 PAYJS 服务费 2%", platform_fee)
        self.assertIn("不能当作统一总价", platform_fee)

        channel_fee = payjs["支付通道费"]
        for phrase in (
            "价格页写微信支付手续费 0.6%",
            "支付与清算 FAQ 写 0.38%",
            "费率表按主体和行业列 0%、0.1%、0.2%、0.3%、0.38%、1%",
            "contrast 页写 0.38%-0.6%",
            "少部分用户可能额外收取服务费",
            "不视为微信或支付宝官方统一费率",
            "交易 100 元到银行卡仍 100 元",
            "2% PAYJS 服务费另行计收",
            "不能据此拼总价",
            "签约页、合同、后台、报价单或微信支付终审为准",
        ):
            self.assertIn(phrase, channel_fee)

        settlement = payjs["结算周期与最低结算额"]
        self.assertIn("结算周期按费率表规则 ID 可能为 T+1、T+3、T+7", settlement)
        self.assertIn("单笔限额按费率表规则可能出现 3K", settlement)
        self.assertIn("最低结算额未公开统一数字（以签约页、合同或后台显示为准）", settlement)

        official_sources = payjs["官方来源"]
        self.assertIn("https://payjs.cn/dashboard/auth/login", official_sources)
        self.assertIn("https://payjs.cn/view/9vw7", official_sources)

        practical_issues = payjs["实际问题"]
        self.assertIn("H5 页面与账号 FAQ 冲突", practical_issues)
        self.assertIn("支付宝相关页面口径也冲突", practical_issues)
        self.assertIn("后台、工单或合同", practical_issues)
        self.assertIn("公开协议/公告入口未找到统一边界说明", practical_issues)

        self.assertIn("需要稳定 H5", payjs["不适用条件"])
        self.assertIn("后台、工单或合同尚未确认", payjs["不适用条件"])

        backlog = (ROOT / "skills/fxskill/references/payment-research-backlog.md").read_text("utf-8")
        self.assertIn("### PAYJS 地区、协议主体、最低结算额与支付宝口径冲突", backlog)
        for phrase in (
            "卖家地区、买家地区与币种统一边界",
            "合同主体或后台协议主体",
            "最低结算额",
            "支付宝能力冲突",
            "H5 能力与 2% 服务费冲突",
            "AI 生图额度、软件 SaaS、数字会员、虚拟权益包",
            "主体、费率、结算规则",
        ):
            self.assertIn(phrase, backlog)

    def test_mianbaoduo_pay_profile_tracks_unverified_subject_region_and_settlement_boundaries(self):
        path = ROOT / "skills/fxskill/references/payment-platform-cn-services.md"
        text = path.read_text("utf-8") if path.exists() else ""
        profiles = {
            name: labels
            for name, labels, _ in module.parse_profiles(text)
        }
        mianbaoduo_pay = profiles["面包多 Pay"]

        operator = mianbaoduo_pay["运营主体"]
        self.assertIn("毛线球科技", operator)
        self.assertIn("京ICP备16062428号-8", operator)
        self.assertIn("京ICP备16062428号-2", operator)
        self.assertIn("签约主体、合同主体和备案主体全称仍无法确认", operator)

        settlement = mianbaoduo_pay["结算周期与最低结算额"]
        self.assertIn("支付宝约 5 分钟内到账", settlement)
        self.assertIn("微信次日自动汇总提现", settlement)
        self.assertIn("settle_time", settlement)
        self.assertIn("最低结算额未公开统一数字", settlement)
        self.assertIn("留存额未公开统一数字", settlement)
        self.assertIn("权限回收规则未公开统一数字", settlement)

        backlog = (ROOT / "skills/fxskill/references/payment-research-backlog.md").read_text("utf-8")
        self.assertIn("### 面包多 Pay 主体、开放与结算边界", backlog)
        for phrase in (
            "签约主体、合同主体和备案主体全称",
            "最低结算额",
            "留存额",
            "权限回收规则",
            "新注册个人开发者稳定开放",
        ):
            self.assertIn(phrase, backlog)

    def test_mianbaoduo_content_trade_profile_locks_decision_fields(self):
        path = ROOT / "skills/fxskill/references/payment-platform-cn-creators.md"
        text = path.read_text("utf-8") if path.exists() else ""
        profiles = {
            name: labels
            for name, labels, _ in module.parse_profiles(text)
        }
        profile = profiles["面包多内容交易"]

        self.assertEqual(
            "普通模式：买家微信或支付宝账户 -> 面包多平台收款账户 -> 面包多公司账户结算链路 -> 创作者可提现余额或提现账户；闪电结算和服务单的具体清算方公开资料没有写明。",
            profile["资金路径"],
        )
        self.assertEqual(
            "普通模式 5% 平台费；闪电结算总服务费 5.7%；服务单 3%。",
            profile["平台服务费"],
        )
        self.assertEqual(
            "普通模式 1% 第三方支付费；闪电结算总服务费已含通道成本；服务单未单独公开通道费。",
            profile["支付通道费"],
        )

        backlog = (ROOT / "skills/fxskill/references/payment-research-backlog.md").read_text("utf-8")
        self.assertIn("### 面包多内容交易费率嵌入和迁移边界", backlog)
        self.assertIn("highfee 模式", backlog)
        self.assertIn("企业账号与个人账号差异", backlog)
        self.assertIn("拒付费", backlog)
        self.assertIn("迁移路径", backlog)
        self.assertIn("能否说明闪电结算和服务单的具体清算方", profile["待核验问题"])
        self.assertNotIn("面包多内容交易当前各结算模式的正式适用费率", backlog)

    def test_quick_sale_scenario_uses_creator_profile_fee_modes_without_adding_them(self):
        scenarios = self.parse_domestic_scenario_sections()
        scenario = scenarios["数字资料或课程快速销售"]
        text = (ROOT / "skills/fxskill/references/payment-platform-cn-creators.md").read_text("utf-8")
        profiles = {name: labels for name, labels, _ in module.parse_profiles(text)}
        profile = profiles["面包多内容交易"]

        for phrase in (
            "普通模式 5% 平台费 + 1% 第三方支付手续费",
            "闪电结算总服务费 5.7%",
            "服务单 3%",
            "三种模式不能相加",
        ):
            self.assertIn(phrase, scenario)
        self.assertIn("普通模式 5% 平台费", profile["平台服务费"])
        self.assertIn("普通模式 1% 第三方支付费", profile["支付通道费"])

    def test_afdian_profile_locks_operator_funds_and_refund_role(self):
        path = ROOT / "skills/fxskill/references/payment-platform-cn-creators.md"
        text = path.read_text("utf-8") if path.exists() else ""
        profiles = {
            name: labels
            for name, labels, _ in module.parse_profiles(text)
        }
        profile = profiles["爱发电"]

        self.assertIn("电羊科技（北京）有限公司", profile["运营主体"])
        self.assertEqual(
            "买家微信或支付宝账户 -> 爱发电统一收款账户 -> 协议约定的结算处理（公开资料没有写明具体清算方） -> 创作者余额或提现账户",
            profile["资金路径"],
        )
        self.assertIn("平台协调售后和争议", profile["退款和售后"])
        self.assertIn("可冻结款项", profile["退款和售后"])
        self.assertIn("全额或部分退款", profile["退款和售后"])
        self.assertIn("决定继续结算", profile["退款和售后"])

        backlog = (ROOT / "skills/fxskill/references/payment-research-backlog.md").read_text("utf-8")
        self.assertIn("### 爱发电提现退款导出和独立站边界", backlog)
        self.assertIn("具体清算方", backlog)
        self.assertIn("能否说明具体清算方", profile["待核验问题"])
        self.assertNotIn("退款责任规则", backlog)

    def test_xiaobot_profile_locks_settlement_nodes_and_backlog_focus(self):
        path = ROOT / "skills/fxskill/references/payment-platform-cn-creators.md"
        text = path.read_text("utf-8") if path.exists() else ""
        profiles = {
            name: labels
            for name, labels, _ in module.parse_profiles(text)
        }
        profile = profiles["小报童"]

        self.assertEqual(
            "读者支付账户 -> 小报童平台收款账户 -> 协议约定的结算处理（公开资料没有写明具体清算方） -> 创作者个人云账户或企业对公账户",
            profile["资金路径"],
        )

        backlog = (ROOT / "skills/fxskill/references/payment-research-backlog.md").read_text("utf-8")
        self.assertIn("### 小报童支付接口导出和买断退款细则", backlog)
        self.assertIn("具体支付商户主体", backlog)
        self.assertIn("具体清算方", backlog)
        self.assertIn("具体支付商户主体和具体清算方分别是谁", profile["待核验问题"])

    def test_payment_behavior_scenarios_keep_conclusions_descriptive_and_costs_bounded(self):
        text = (ROOT / "tests/fxskill/scenarios.md").read_text("utf-8")

        self.assertIn("R7 的固定费用未知时不得称为低固定成本候选", text)
        self.assertIn("R7 必须注明费用与资格的核验日期", text)
        self.assertIn("R8 和 R9 的结论可描述路线或平台定位", text)
        self.assertIn("这种描述不计为命令动作", text)
        self.assertIn("R10 必须给出结算边界", text)
        self.assertIn("0.38% 是 XorPay 页面口径", text)

    def test_bufpay_profile_tracks_split_costs_and_operational_unknowns(self):
        path = ROOT / "skills/fxskill/references/payment-platform-cn-services.md"
        text = path.read_text("utf-8") if path.exists() else ""
        profiles = {
            name: labels
            for name, labels, _ in module.parse_profiles(text)
        }
        bufpay = profiles["BufPay"]

        platform_fee = bufpay["平台服务费"]
        for phrase in ("免费版 0", "基础版 0.4%", "标准版 0.3%", "高级版 0.2%"):
            self.assertIn(phrase, platform_fee)
        for forbidden in ("25 元/月", "50 元/月", "99 元/月"):
            self.assertNotIn(forbidden, platform_fee)

        fees = bufpay["固定费用、提现费、退款费和拒付费"]
        self.assertIn("固定费用：套餐月费 0 元、25 元、50 元或 99 元", fees)
        self.assertIn("手续费余额需预充值", fees)
        self.assertIn("未用完余额不支持提现或退款", fees)

        practical_issues = bufpay["实际问题"]
        self.assertIn("实践证据不足", practical_issues)
        self.assertIn("通知漏单率", practical_issues)
        self.assertIn("回调失败或过期后付款", practical_issues)
        self.assertIn("客服响应", practical_issues)
        self.assertIn("退款和人工确认", practical_issues)

        backlog = (ROOT / "skills/fxskill/references/payment-research-backlog.md").read_text("utf-8")
        self.assertIn("### BufPay 2026 接入稳定性与异常处理体验", backlog)
        for phrase in (
            "真实接入稳定性",
            "通知漏单率",
            "回调失败或过期后付款",
            "客服响应",
            "退款处理",
            "人工确认",
        ):
            self.assertIn(phrase, backlog)

    def test_alipay_refund_fee_discloses_nonrefundable_transaction_fee(self):
        path = ROOT / "skills/fxskill/references/payment-platform-cn-direct.md"
        text = path.read_text("utf-8") if path.exists() else ""
        profiles = {
            name: labels
            for name, labels, _ in module.parse_profiles(text)
        }
        alipay = profiles["\u652f\u4ed8\u5b9d"]
        fee_label = "\u56fa\u5b9a\u8d39\u7528\u3001\u63d0\u73b0\u8d39\u3001\u9000\u6b3e\u8d39\u548c\u62d2\u4ed8\u8d39"
        refund_label = "\u9000\u6b3e\u8d39"
        source_label = "\u5b98\u65b9\u6765\u6e90"
        items, duplicates, extras = module.parse_fee_breakdown(alipay[fee_label])

        self.assertEqual([], duplicates)
        self.assertEqual([], extras)
        self.assertIn(refund_label, items)
        self.assertNotEqual("\u65e0\u6b64\u9879", items[refund_label])
        self.assertIn("\u624b\u7eed\u8d39\u4e0d\u9000\u56de", items[refund_label])
        self.assertIn("AI \u7f51\u9875\u5e94\u7528\u6536\u6b3e", items[refund_label])
        self.assertIn(
            "https://aipay.alipay.com/docs/ai-web-app-payment-qianyi/ai-web-app-payment-integration-guide.html",
            alipay[source_label],
        )

    def test_backlog_has_actionable_unknowns(self):
        text = (ROOT / "skills/fxskill/references/payment-research-backlog.md").read_text("utf-8")
        for field in ("缺失事实", "已查来源", "需要询问", "可接受证据"):
            self.assertIn(field, text)

    def test_validate_file_rejects_unknown_recommendation_level(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_profile_file(Path(tmp), self.render_profile(推荐等级="随便推荐"))
            errors = module.validate_file(path)
        self.assertTrue(any("推荐等级" in error for error in errors), errors)

    def test_validate_file_requires_real_iso_verification_date(self):
        for value in ("2026/07/15", "2026-02-31"):
            with self.subTest(value=value):
                with tempfile.TemporaryDirectory() as tmp:
                    path = self.write_profile_file(Path(tmp), self.render_profile(最后核验日期=value))
                    errors = module.validate_file(path)
                self.assertTrue(any("最后核验日期" in error for error in errors), errors)

    def test_validate_file_requires_valid_official_link_for_active_platforms(self):
        for value in (
            "无",
            "https://。",
            "https://localhost/admin",
            "https://localhost./admin",
            "https://127.0.0.1/admin",
            "https://10.0.0.1/admin",
        ):
            with self.subTest(value=value):
                with tempfile.TemporaryDirectory() as tmp:
                    path = self.write_profile_file(Path(tmp), self.render_profile(官方来源=value))
                    errors = module.validate_file(path)
                self.assertTrue(any("官方来源" in error for error in errors), errors)

    def test_validate_file_accepts_official_link_with_trailing_punctuation(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_profile_file(
                Path(tmp),
                self.render_profile(官方来源="https://example.com。"),
            )
            errors = module.validate_file(path)
        self.assertEqual([], errors, errors)

    def test_extract_candidate_urls_splits_chinese_semicolon_lists(self):
        self.assertEqual(
            ["https://example.com/one", "https://example.com/two"],
            module.extract_candidate_urls("https://example.com/one；https://example.com/two。"),
        )

    def test_extract_candidate_urls_keeps_single_url_with_fullwidth_semicolon(self):
        self.assertEqual(
            ["https://example.com/path；detail"],
            module.extract_candidate_urls("https://example.com/path；detail"),
        )

    def test_validate_file_requires_extended_contract_fields(self):
        profile = self.render_profile()
        for label in (
            "卖家地区",
            "买家地区与币种",
            "支付方式",
            "固定费用、提现费、退款费和拒付费",
            "结算周期与最低结算额",
        ):
            with self.subTest(label=label):
                with tempfile.TemporaryDirectory() as tmp:
                    path = self.write_profile_file(Path(tmp), self.remove_label(profile, label))
                    errors = module.validate_file(path)
                self.assertTrue(any(label in error for error in errors), errors)

    def test_validate_file_requires_four_segment_money_path(self):
        for value in (
            "未知",
            "买家 -> 收款方 -> 卖家账户",
            "买家 -> 收款方 ->  -> 卖家账户",
            "买家 -> 待确认收款方 -> 清算方 -> 卖家账户",
            "买家 -> 收款方 -> 未公开清算方 -> 卖家账户",
            "买家 -> 收款方 -> 清算方 -> 不明账户",
        ):
            with self.subTest(value=value):
                with tempfile.TemporaryDirectory() as tmp:
                    path = self.write_profile_file(Path(tmp), self.render_profile(资金路径=value))
                    errors = module.validate_file(path)
                self.assertTrue(any("资金路径" in error for error in errors), errors)

    def test_validate_file_accepts_four_segment_money_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_profile_file(
                Path(tmp),
                self.render_profile(资金路径="买家 -> 收款方 -> 清算方 -> 卖家企业银行账户"),
            )
            errors = module.validate_file(path)
        self.assertEqual([], errors, errors)

    def test_validate_file_treats_precise_money_path_gap_as_unknown(self):
        value = (
            "买家 -> 平台收款账户 -> 协议约定的结算处理"
            "（公开资料没有写明具体清算方） -> 卖家提现账户"
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_profile_file(Path(tmp), self.render_profile(资金路径=value))
            errors = module.validate_file(path)

        self.assertTrue(
            any("unknown key fields" in error or "pending verification" in error for error in errors),
            errors,
        )

    def test_validate_file_accepts_precise_money_path_gap_as_lead_with_backlog(self):
        value = (
            "买家 -> 平台收款账户 -> 协议约定的结算处理"
            "（公开资料没有写明具体清算方） -> 卖家提现账户"
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_profile_file(
                Path(tmp),
                self.render_profile(
                    资金路径=value,
                    推荐等级="仅作线索",
                    待核验问题=VALID_BACKLOG,
                ),
            )
            errors = module.validate_file(path)

        self.assertEqual([], errors, errors)

    def test_validate_file_rejects_precise_money_path_gap_with_stronger_recommendation(self):
        values = (
            "买家 -> 平台收款账户 -> 协议约定的结算处理（公开资料没有写明具体清算方） -> 卖家提现账户",
            "买家 -> 平台收款账户 -> 平台结算处理（具体清算机构未披露） -> 卖家提现账户",
            "买家 -> 平台收款账户 -> 合同约定的清算节点（官方材料未说明具体机构） -> 卖家提现账户",
            "买家 -> 平台收款账户 -> 平台结算处理（具体清算机构未公布） -> 卖家提现账户",
            "买家 -> 平台收款账户 -> 协议约定的清算节点（具体机构未给出） -> 卖家提现账户",
            "买家 -> 平台收款账户 -> 平台结算处理（具体清算机构未能确认） -> 卖家提现账户",
            "买家 -> 平台收款账户 -> 协议约定的清算节点（具体机构未予披露） -> 卖家提现账户",
        )
        for value in values:
            for recommendation in ("条件推荐", "不推荐"):
                with self.subTest(value=value, recommendation=recommendation):
                    with tempfile.TemporaryDirectory() as tmp:
                        path = self.write_profile_file(
                            Path(tmp),
                            self.render_profile(
                                资金路径=value,
                                推荐等级=recommendation,
                                待核验问题=VALID_BACKLOG,
                            ),
                        )
                        errors = module.validate_file(path)

                    self.assertTrue(
                        any("unknown clearing node" in error for error in errors),
                        errors,
                    )

    def test_validate_file_rejects_unknown_current_status(self):
        for status in ("运营中", "正常营业", "待观察"):
            with self.subTest(status=status):
                with tempfile.TemporaryDirectory() as tmp:
                    path = self.write_profile_file(
                        Path(tmp),
                        self.render_profile(
                            当前状态=status,
                        ),
                    )
                    errors = module.validate_file(path)

                self.assertTrue(
                    any("当前状态" in error and "must be one of" in error for error in errors),
                    errors,
                )

    def test_source_policy_requires_precise_money_path_gaps_to_stay_lead_only(self):
        text = (ROOT / "skills/fxskill/references/payment-source-policy.md").read_text("utf-8")

        self.assertIn("精确指出缺失的清算节点", text)
        self.assertIn("只能配 `仅作线索` 或 `已停止/归档`", text)
        self.assertIn("结构化 `待核验问题`", text)

    def test_validate_file_rejects_ambiguous_payment_role(self):
        for value in ("待确认", "未知", "未公开", "不确定"):
            with self.subTest(value=value):
                with tempfile.TemporaryDirectory() as tmp:
                    path = self.write_profile_file(
                        Path(tmp),
                        self.render_profile(推荐等级="仅作线索", 支付角色=value, 待核验问题="无"),
                    )
                    errors = module.validate_file(path)
                self.assertTrue(any("支付角色" in error or "待核验问题" in error for error in errors), errors)

    def test_has_unknown_key_fields_treats_precise_unpublished_as_known(self):
        labels = dict(BASE_PROFILE)
        labels["平台服务费"] = PRECISE_UNPUBLISHED_PAGE
        labels["支付通道费"] = PRECISE_UNPUBLISHED_CONTRACT
        labels["固定费用、提现费、退款费和拒付费"] = "\n".join(
            [
                f"固定费用：{PRECISE_UNPUBLISHED_BACKEND}",
                "提现费：0",
                "退款费：无此项",
                f"拒付费：{PRECISE_UNPUBLISHED_QUOTE}",
            ]
        )
        self.assertFalse(module.has_unknown_key_fields(labels))

    def test_has_unknown_key_fields_treats_plain_unpublished_as_unknown(self):
        for value in ("未公开", "未核实", "暂无结论", "待定", "不详", "不明", "不确定"):
            with self.subTest(value=value):
                labels = dict(BASE_PROFILE)
                labels["平台服务费"] = value
                self.assertTrue(module.has_unknown_key_fields(labels))

    def test_validate_file_requires_backlog_for_unknown_key_fields_at_any_recommendation(self):
        for value in ("未公开", "未核实", "暂无结论"):
            with self.subTest(value=value):
                with tempfile.TemporaryDirectory() as tmp:
                    path = self.write_profile_file(
                        Path(tmp),
                        self.render_profile(推荐等级="条件推荐", 平台服务费=value, 待核验问题="无"),
                    )
                    errors = module.validate_file(path)
                self.assertTrue(any("待核验问题" in error for error in errors), errors)

    def test_validate_file_rejects_stronger_recommendation_when_practice_evidence_is_insufficient(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_profile_file(
                Path(tmp),
                self.render_profile(推荐等级="条件推荐", 实践来源=INSUFFICIENT_PRACTICE_EVIDENCE, 待核验问题=VALID_BACKLOG),
            )
            errors = module.validate_file(path)
        self.assertTrue(any("实践证据不足" in error and "仅作线索" in error for error in errors), errors)

    def test_validate_file_requires_actionable_backlog_when_practice_evidence_is_insufficient(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_profile_file(
                Path(tmp),
                self.render_profile(推荐等级="仅作线索", 实践来源=INSUFFICIENT_PRACTICE_EVIDENCE, 待核验问题="无"),
            )
            errors = module.validate_file(path)
        self.assertTrue(any("实践证据不足" in error and "待核验问题" in error for error in errors), errors)

    def test_validate_file_accepts_unknown_key_fields_when_backlog_exists(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_profile_file(
                Path(tmp),
                self.render_profile(推荐等级="条件推荐", 平台服务费="未公开", 待核验问题=VALID_BACKLOG),
            )
            errors = module.validate_file(path)
        self.assertEqual([], errors, errors)

    def test_validate_file_rejects_direct_recommendation_with_backlog(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_profile_file(Path(tmp), self.render_profile(待核验问题=VALID_BACKLOG))
            errors = module.validate_file(path)
        self.assertTrue(any("直接推荐" in error for error in errors), errors)

    def test_validate_file_requires_split_fee_breakdown(self):
        for value in (
            "固定费用：0\n提现费：无此项\n退款费：无此项",
            "其他费用：以签约页为准",
            "固定费用：0\n提现费：无此项\n退款费：无此项\n拒付费：无此项\n其他费：以合同为准",
        ):
            with self.subTest(value=value):
                with tempfile.TemporaryDirectory() as tmp:
                    path = self.write_profile_file(
                        Path(tmp),
                        self.render_profile(
                            推荐等级="条件推荐",
                            **{"固定费用、提现费、退款费和拒付费": value},
                        ),
                    )
                    errors = module.validate_file(path)
                self.assertTrue(any("固定费用、提现费、退款费和拒付费" in error for error in errors), errors)

    def test_validate_file_rejects_duplicate_fee_subfields(self):
        value = "\n".join(
            [
                "固定费用：0",
                "固定费用：无此项",
                "提现费：无此项",
                "退款费：无此项",
                "拒付费：无此项",
            ]
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_profile_file(
                Path(tmp),
                self.render_profile(推荐等级="条件推荐", **{"固定费用、提现费、退款费和拒付费": value}),
            )
            errors = module.validate_file(path)
        self.assertTrue(any("duplicate fee subfield `固定费用`" in error for error in errors), errors)

    def test_validate_file_rejects_empty_duplicate_fee_subfield(self):
        value = "\n".join(
            [
                "固定费用：0",
                "固定费用：",
                "提现费：无此项",
                "退款费：无此项",
                "拒付费：无此项",
            ]
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_profile_file(
                Path(tmp),
                self.render_profile(推荐等级="条件推荐", **{"固定费用、提现费、退款费和拒付费": value}),
            )
            errors = module.validate_file(path)
        self.assertTrue(any("duplicate fee subfield `固定费用`" in error for error in errors), errors)

    def test_validate_file_rejects_empty_extra_fee_key(self):
        value = "\n".join(
            [
                "固定费用：0",
                "提现费：无此项",
                "退款费：无此项",
                "拒付费：无此项",
                "其他费用：",
            ]
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_profile_file(
                Path(tmp),
                self.render_profile(推荐等级="条件推荐", **{"固定费用、提现费、退款费和拒付费": value}),
            )
            errors = module.validate_file(path)
        self.assertTrue(any("unsupported fee key" in error and "其他费用" in error for error in errors), errors)

    def test_validate_file_accepts_explicit_fee_breakdown_values(self):
        value = "\n".join(
            [
                f"固定费用：{PRECISE_UNPUBLISHED_BACKEND}",
                "提现费：无此项",
                "退款费：0",
                f"拒付费：{PRECISE_UNPUBLISHED_CONTRACT}",
            ]
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_profile_file(
                Path(tmp),
                self.render_profile(
                    平台服务费=PRECISE_UNPUBLISHED_PAGE,
                    支付通道费="0",
                    **{"固定费用、提现费、退款费和拒付费": value},
                ),
            )
            errors = module.validate_file(path)
        self.assertEqual([], errors, errors)

    def test_validate_file_rejects_unknown_top_level_label(self):
        profile = self.render_profile().replace(
            "- 官方来源：https://example.com/official",
            "- 官方来源：https://example.com/official\n- 其他费用：未公开",
            1,
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_profile_file(Path(tmp), profile)
            errors = module.validate_file(path)
        self.assertTrue(any("unknown label `其他费用`" in error for error in errors), errors)

    def test_validate_file_accepts_optional_export_label(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_profile_file(
                Path(tmp),
                self.render_profile(**{"数据导出与迁移": "支持 CSV 导出"}),
            )
            errors = module.validate_file(path)
        self.assertEqual([], errors, errors)

    def test_validate_file_accepts_all_allowed_optional_labels(self):
        overrides = {label: f"{label}示例" for label in OPTIONAL_LABELS}
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_profile_file(Path(tmp), self.render_profile(**overrides))
            errors = module.validate_file(path)
        self.assertEqual([], errors, errors)

    def test_validate_file_requires_non_empty_optional_label_value(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_profile_file(Path(tmp), self.render_profile(**{"运营主体": ""}))
            errors = module.validate_file(path)
        self.assertTrue(any("运营主体" in error for error in errors), errors)

    def test_validate_file_requires_backlog_for_unknown_optional_label(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_profile_file(
                Path(tmp),
                self.render_profile(**{"限制商品": "未知"}),
            )
            errors = module.validate_file(path)
        self.assertTrue(any("待核验问题" in error for error in errors), errors)

    def test_validate_file_accepts_explicit_optional_label_value(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_profile_file(
                Path(tmp),
                self.render_profile(**{"限制商品": "无额外限制，以官方禁售清单为准"}),
            )
            errors = module.validate_file(path)
        self.assertEqual([], errors, errors)

    def test_validate_file_rejects_placeholder_unknown_values(self):
        backlog = "\n".join(
            [
                "",
                "- 缺失事实：待确认",
                "- 已查来源：TODO，等官方回复。",
                "- 需要询问：请联系客服。",
                "- 可接受证据：官方回复。",
            ]
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_profile_file(
                Path(tmp),
                self.render_profile(推荐等级="条件推荐", 待核验问题=backlog),
            )
            errors = module.validate_file(path)
        self.assertTrue(any("待核验问题" in error for error in errors), errors)

    def test_validate_file_accepts_review_false_positive_backlog_examples(self):
        cases = (
            BACKLOG_WITH_UNCONFIRMED_FACT,
            "\n".join(
                [
                    "",
                    "- 缺失事实：无法确认该平台是否向中国大陆个体工商户开放申请。",
                    "- 已查来源：2026-07-15 已检查官网申请页 https://example.com/help-center。",
                    "- 需要询问：商务团队可否确认中国大陆个体工商户是否能申请该产品？",
                    "- 可接受证据：官方书面回复明确写出适用主体、类目和结算路径。",
                ]
            ),
            "\n".join(
                [
                    "",
                    "- 缺失事实：尚未确认该平台向中国大陆个体工商户开放的具体类目。",
                    "- 已查来源：2026-07-15 已检查官网帮助中心 https://example.com/docs。",
                    "- 需要询问：商务团队哪些类目支持中国大陆个体工商户申请该产品？",
                    "- 可接受证据：官方页面、文档、合同、报价单、后台截图或书面回复中明确写出可申请类目。",
                ]
            ),
        )
        for backlog in cases:
            with self.subTest(backlog=backlog.splitlines()[1]):
                with tempfile.TemporaryDirectory() as tmp:
                    path = self.write_profile_file(
                        Path(tmp),
                        self.render_profile(推荐等级="条件推荐", 平台服务费="未公开", 待核验问题=backlog),
                    )
                    errors = module.validate_file(path)
                self.assertEqual([], errors, errors)

    def test_validate_file_accepts_checked_sources_with_unified_unpublished_rate(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_profile_file(
                Path(tmp),
                self.render_profile(推荐等级="条件推荐", 平台服务费="未公开", 待核验问题=BACKLOG_WITH_UNIFIED_UNPUBLISHED_RATE),
            )
            errors = module.validate_file(path)
        self.assertEqual([], errors, errors)

    def test_validate_file_requires_specific_question_in_need_to_ask_field(self):
        for question in ("请确认是否支持？", "商务团队？"):
            backlog = "\n".join(
                [
                    "",
                    "- 缺失事实：尚未确认个体工商户是否可销售 AI 图像额度包。",
                    "- 已查来源：2026-07-15 已检查官网申请页 https://example.com/help-center。",
                    f"- 需要询问：{question}",
                    "- 可接受证据：官方页面或书面回复。",
                ]
            )
            with self.subTest(question=question):
                with tempfile.TemporaryDirectory() as tmp:
                    path = self.write_profile_file(
                        Path(tmp),
                        self.render_profile(推荐等级="条件推荐", 待核验问题=backlog),
                    )
                    errors = module.validate_file(path)
                self.assertTrue(any("需要询问" in error for error in errors), errors)

    def test_validate_file_requires_evidence_carrier_in_acceptance_field(self):
        backlog = "\n".join(
            [
                "",
                "- 缺失事实：尚未确认个体工商户是否可销售 AI 图像额度包。",
                "- 已查来源：2026-07-15 已检查官网申请页 https://example.com/help-center。",
                "- 需要询问：商务团队是否支持个体工商户销售 AI 图像额度包？",
                "- 可接受证据：官方回复。",
            ]
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_profile_file(
                Path(tmp),
                self.render_profile(推荐等级="条件推荐", 待核验问题=backlog),
            )
            errors = module.validate_file(path)
        self.assertTrue(any("可接受证据" in error for error in errors), errors)

    def test_validate_file_rejects_duplicate_backlog_subfields(self):
        backlog = "\n".join(
            [
                "",
                "- 缺失事实：尚未确认个体工商户是否可销售 AI 图像额度包。",
                "- 已查来源：2026-07-15 已检查官网申请页 https://example.com/help-center。",
                "- 已查来源：2026-07-16 已检查帮助中心 https://example.com/docs。",
                "- 需要询问：商务团队是否支持个体工商户销售 AI 图像额度包？",
                "- 可接受证据：官方页面或书面回复。",
            ]
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_profile_file(
                Path(tmp),
                self.render_profile(推荐等级="条件推荐", 待核验问题=backlog),
            )
            errors = module.validate_file(path)
        self.assertTrue(any("duplicate backlog subfield `已查来源`" in error for error in errors), errors)

    def test_validate_file_accepts_substantive_unknown_values(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_profile_file(
                Path(tmp),
                self.render_profile(推荐等级="条件推荐", 平台服务费="未公开", 待核验问题=VALID_BACKLOG),
            )
            errors = module.validate_file(path)
        self.assertEqual([], errors, errors)

    def test_validate_file_rejects_duplicate_labels_in_profile(self):
        profile = self.render_profile().replace(
            "- 官方来源：https://example.com/official",
            "- 官方来源：https://example.com/official\n- 官方来源：https://example.com/duplicate",
            1,
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_profile_file(Path(tmp), profile)
            errors = module.validate_file(path)
        self.assertTrue(any("duplicate label `官方来源`" in error for error in errors), errors)

    def test_validate_file_parses_and_validates_multiple_profiles_in_one_file(self):
        content = "\n".join(
            [
                self.render_profile(name="平台甲").rstrip(),
                self.render_profile(name="平台乙", 官方来源="无").rstrip(),
                "",
            ]
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_profile_file(Path(tmp), content)
            errors = module.validate_file(path)
        self.assertEqual(1, len(errors), errors)
        self.assertIn("平台乙", errors[0])
        self.assertIn("官方来源", errors[0])

    def test_validate_repository_rejects_cross_file_duplicate_platform_names(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".git").write_text("", "utf-8")
            self.write_profile_file(root, self.render_profile(name="同名平台"), "payment-platform-one.md")
            self.write_profile_file(root, self.render_profile(name="同名平台"), "payment-platform-two.md")
            errors = module.validate_repository(root)
        self.assertTrue(any("duplicate platform `同名平台`" in error for error in errors), errors)

    def test_validate_file_reports_non_empty_file_without_profiles(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_profile_file(Path(tmp), "# 平台草稿\n\n暂未整理字段。")
            errors = module.validate_file(path)
        self.assertTrue(any("contains content but no `##` profiles" in error for error in errors), errors)

    def test_validate_file_allows_whitespace_only_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_profile_file(Path(tmp), " \n\t\n")
            errors = module.validate_file(path)
        self.assertEqual([], errors, errors)

    def test_validate_file_requires_archived_recommendation_for_stopped_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_profile_file(
                Path(tmp),
                self.render_profile(当前状态="已停止", 推荐等级="仅作线索"),
            )
            errors = module.validate_file(path)
        self.assertTrue(any("已停止/归档" in error for error in errors), errors)

    def test_validate_file_rejects_recommendation_for_unconfirmed_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_profile_file(
                Path(tmp),
                self.render_profile(当前状态="无法确认", 推荐等级="条件推荐"),
            )
            errors = module.validate_file(path)
        self.assertTrue(any("无法确认" in error for error in errors), errors)

    def test_validate_file_accepts_lead_only_for_unconfirmed_status(self):
        for recommendation in ("仅作线索", "已停止/归档"):
            with self.subTest(recommendation=recommendation):
                with tempfile.TemporaryDirectory() as tmp:
                    path = self.write_profile_file(
                        Path(tmp),
                        self.render_profile(当前状态="无法确认", 推荐等级=recommendation, 待核验问题=VALID_BACKLOG),
                    )
                    errors = module.validate_file(path)
                self.assertEqual([], errors, errors)


if __name__ == "__main__":
    unittest.main()
