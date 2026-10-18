"""Generate content/13-lesson4.html (高频词速查) from the term counts in data/term_freq.json."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FREQ = json.loads((ROOT / "data" / "term_freq.json").read_text())

# (count key, English, 中文译法, 一句大白话, detail anchor or "", extra citation id or "")
GROUPS = [
    ("怎么做：方法与工作方式", [
        ("research", "research", "研究", "不只是查资料写论文；在 RCA，做作品本身就可以是研究，能产生新的认识。", "lesson1-teaching", "frayling-1993"),
        ("practice", "practice", "实践", "你长期在做的创作和工作方式。「你的实践」大致等于「你是一个什么样的创作者」。", "", ""),
        ("experiment", "experiment / experimental", "实验、实验性的", "不按既定答案做，先试再说，允许失败。", "l3-process", ""),
        ("process", "process", "过程", "从想法到成品的整个经过。RCA 看重过程，常常不亚于成品。", "l3-process", ""),
        ("method(ology)", "method / methodology", "方法、方法论", "你用什么办法研究和创作，以及为什么用这个办法。", "", ""),
        ("making", "making / thinking through making", "动手做、通过动手做来思考", "动手做本身就是思考的一种方式，不是想好了再做。", "l3-process", ""),
        ("reflexive/reflective", "reflective / reflexive", "反思的", "回头审视自己做了什么、为什么这样做、哪里可以更好。", "", ""),
        ("iterative/prototyping", "iterative / prototyping", "迭代、原型", "先做一个粗糙版本，测试，再改，循环多次。", "", ""),
        ("studio", "studio", "工作室", "既指学生的创作空间，也指以项目为中心的上课方式。", "", ""),
        ("crit/tutorial", "crit / tutorial", "评图、导师辅导", "评图：把作品摆出来，大家一起讨论；辅导：和导师一对一聊进展。", "lesson1-teaching", ""),
        ("workshop", "workshop", "工作坊", "短时间、动手为主的集中课程，也指学校的技术车间。", "", ""),
        ("independent research project", "Independent Research Project (IRP)", "独立研究项目", "大多数硕士第三学期的毕业项目，一个人从头做到展出。", "", ""),
    ]),
    ("怎么想：态度与立场", [
        ("critical", "critical / criticality", "批判性的", "不是挑毛病，而是不把任何事当成理所当然：为什么是这样？谁受益，谁受伤？", "l3-criteria", ""),
        ("context", "context / contextualise", "语境、放到语境里", "作品在什么社会、历史、文化环境里产生和被观看。", "", ""),
        ("positionality/position", "position / positionality", "立场、位置", "你是谁、从哪里来，决定了你怎么看问题。", "l3-situated", ""),
        ("situated", "situated", "情境化的", "知识和作品都来自具体的位置，没有「站在外面」的客观视角。", "l3-situated", "haraway-1988"),
        ("dialogue", "dialogue", "对话", "作品和观众、和别的作品、和理论之间的来回交流。", "", ""),
        ("discourse", "discourse", "话语", "一个领域里大家怎么谈论某件事的方式和语言。「进入当代艺术话语」就是能参与这个圈子的讨论。", "", ""),
        ("future(s)", "future / futures", "未来（复数）", "不是一个注定的未来，而是多种可能的未来，可以讨论和选择。", "l3-futures", ""),
        ("speculative", "speculative", "思辨的", "从真实研究出发虚构一个未来，用来讨论今天的选择。", "l3-futures", "dunne-raby-bio"),
        ("intervention", "intervention", "介入", "主动打断一个习以为常的过程，而不只是旁观、记录。", "", ""),
        ("agency", "agency", "能动性", "人（或物）主动行动、改变处境的能力。", "", ""),
        ("urgent", "urgent", "紧迫的", "官网常说「紧迫的问题」，通常指气候、不平等、技术带来的冲击。", "", ""),
        ("provocation", "provocation", "激发、挑衅", "故意提出一个让人不舒服的问题，引发思考。", "", ""),
    ]),
    ("跨界：打破专业边界", [
        ("interdisciplinary", "interdisciplinary", "跨学科的", "把两个以上学科的方法放在一起用。31 个页面全部出现。", "", ""),
        ("transdisciplinary", "transdisciplinary", "超学科的", "围绕一个真实问题组织知识，不以学科划界。", "", ""),
        ("expanded", "expanded", "扩展的", "作品不受媒介边界限制，比如摄影不一定是照片。", "photo-q1", "krauss-1979"),
        ("hybrid", "hybrid", "混合的", "把不同媒介、方法、传统混在一起用。", "", ""),
    ]),
    ("关心什么：议题", [
        ("material(ity)", "material / materiality", "材料、物质性", "东西是用什么做的、材料本身带着什么意义。", "", ""),
        ("environment", "environment / environmental", "环境", "既指自然环境，也指人所处的空间和条件。", "l2-climate", ""),
        ("community", "community", "社群", "一群有共同处境或关系的人；很多项目和他们一起做。", "", ""),
        ("social(ly engaged)", "social / socially engaged", "社会的、社会参与的", "作品主动回应社会问题，常常和真实人群一起完成。", "", ""),
        ("collaboration", "collaboration", "协作", "和其他专业、机构、社群一起做。RCA 几乎所有专业都强调。", "", ""),
        ("public", "public", "公众、公共的", "作品最终要面对公众，常说「making public」（公开展示）。", "", ""),
        ("participatory/co-", "participatory / co-design", "参与式、共同设计", "让观众或使用者参与创作本身。", "l3-participation", ""),
        ("audience", "audience", "观众", "作品为谁而做、在哪里被看到、对他们有什么作用。", "l3-participation", ""),
        ("technology", "technology / emerging technologies", "技术、新兴技术", "讨论技术对人做了什么，而不只是怎么用。", "l2-tech", ""),
        ("AI", "AI / artificial intelligence", "人工智能", "2027 年新开了专门的 AI 与数字艺术专业。", "l2-tech", ""),
        ("immersive", "immersive", "沉浸式的", "让观众置身其中的体验，比如 VR、装置。", "", ""),
        ("system(s)", "system / systems", "系统", "把问题看成相互关联的整体，而不是孤立的一件事。", "ied-q1", ""),
        ("sustainab", "sustainable / sustainability", "可持续的", "考虑资源、环境和长远影响。", "", ""),
        ("ecology/ecological", "ecology / ecological", "生态", "生物与环境的关系网；也常比喻任何相互依存的关系。", "l2-climate", ""),
        ("climate", "climate", "气候", "气候危机是建筑、时装、影像等多个专业共同的话题。", "l2-climate", ""),
        ("planet", "planet / planetary", "地球的、全球尺度的", "把问题放到整个地球的尺度上看。", "", ""),
        ("more-than-human/other species", "more-than-human / other species", "超越人类、其他物种", "把动物、植物、生态也当成参与者。", "ied-q3", "book-spell-sensuous"),
        ("identity", "identity", "身份", "你是谁：文化、性别、国籍、阶层等交织在一起。", "l2-identity", ""),
        ("representation", "representation", "再现、代表", "图像和叙事怎样呈现某些人和事，谁有权呈现谁。", "photo-q2", ""),
        ("visibility", "visibility", "可见性", "谁被看见、谁被忽略。", "photo-q2", ""),
        ("archive", "archive", "档案", "被保存下来的记录：照片、信件、物件；重新整理它们也是创作。", "l2-memory", ""),
        ("narrative", "narrative / storytelling", "叙事、讲故事", "用作品讲一个故事，也追问谁有权讲故事。", "", ""),
        ("embodied", "embodied", "具身的", "通过身体去感受和理解，而不只是用脑子想。", "", ""),
        ("craft", "craft", "手艺", "传统技艺和手工知识，在 RCA 常和新技术结合。", "", ""),
        ("ethic", "ethics / ethical", "伦理", "做作品时对人、对环境的责任。", "", ""),
        ("inclusive/equitable", "inclusive / equitable", "包容的、公平的", "让更多人、尤其是被忽视的人，被考虑进来。", "", ""),
        ("justice", "justice", "正义", "常见搭配：社会正义、环境正义、气候正义。", "", ""),
        ("care", "care", "照护、关怀", "关注照顾他人、照顾环境这类常被忽视的劳动。", "", ""),
        ("decolonial", "decolonial / decolonising", "去殖民的", "反思殖民历史留下的权力关系和知识偏见。", "", ""),
        ("performance", "performance / performative", "表演、表演性的", "用身体和时间完成的作品；也指图像「在做什么」。", "", ""),
        ("installation", "installation", "装置", "在一个空间里布置的作品，观众走进去体验。", "", ""),
        ("spatial", "spatial", "空间的", "和空间有关的，不只建筑，也包括展览、城市、声音的空间。", "", ""),
        ("worldbuilding", "worldbuilding", "世界构建", "虚构一个完整的世界（规则、社会、物件），用来讨论现实。", "", ""),
    ]),
]

SPECIAL = [
    ("warm data", "暖数据", "关于相互关系的数据，和可以量化的「冷数据」相对。信息体验设计的核心概念。", "ied-q1", "ibi-warm-data"),
    ("post-digital", "后数字", "数字技术已经像空气一样无处不在之后的状态。", "ied-q2", "cascone-2000"),
    ("deep listening", "深度聆听", "有意识地、全身心地去听。声音实践专业的关键词。", "", "deep-listening"),
    ("field collective / practice group", "场域小组、实践小组", "信息体验设计和摄影专业的小组教学单位，约 10 到 14 人跟一位老师。", "lesson1-teaching", ""),
]


def ref(anchor):
    return f"[[ref:{anchor}]]" if anchor else ""


def main():
    rows = []
    for gi, (title, terms) in enumerate(GROUPS, 1):
        rows.append(f'<h2 id="l4-group{gi}">{title}</h2>')
        rows.append("<table><tr><th>英文</th><th>中文</th><th>一句话</th><th class=\"nw\">页面数</th><th>详见</th></tr>")
        for key, en, zh, plain, anchor, cite in terms:
            df = FREQ.get(key, {}).get("df", 0)
            c = f"[[c:{cite}]]" if cite else ""
            rows.append(f'<tr><td class="en">{en}</td><td>{zh}</td><td>{plain}{c}</td><td>{df}</td><td>{ref(anchor)}</td></tr>')
        rows.append("</table>")
    special = ["<table><tr><th>英文</th><th>中文</th><th>一句话</th><th>详见</th></tr>"]
    for en, zh, plain, anchor, cite in SPECIAL:
        c = f"[[c:{cite}]]" if cite else ""
        special.append(f'<tr><td class="en">{en}</td><td>{zh}</td><td>{plain}{c}</td><td>{ref(anchor)}</td></tr>')
    special.append("</table>")
    html = f"""<section class="chapter" id="lesson4">
<p class="kicker">第一部分 · 第 4 课</p>
<h1 id="lesson4-title">RCA 高频词速查</h1>
<p class="lede">RCA 各专业的介绍反复使用同一批词。我们把 31 个项目（29 个授课型硕士和 2 个研究生文凭）的官网页面全部读了一遍，统计每个词出现在多少个页面里。下面按「怎么做、怎么想、跨界、关心什么」分成四组，每个词配一句大白话。</p>
<div class="box">
<h4>统计方法</h4>
<p>{{{{官网}}}} 页面范围：RCA 官网专业搜索页列出的 29 个授课型硕士和 2 个研究生文凭[[c:finder-taught]][[c:finder-pre-masters]]，读取日期 2026 年 10 月 18 日。统计范围是页面正文，不含学费、奖学金、教师名单和图片说明。「页面数」表示这个词（含同根词）出现在多少个页面里，满分 31。各页面共用的段落也计算在内，所以数字只用来看「常不常见」，不是精确的学术统计。</p>
</div>
{chr(10).join(rows)}
<h2 id="l4-special">只在个别专业出现、但很关键的词</h2>
{chr(10).join(special)}
<div class="box">
<h4>{{{{经验}}}} 怎么用这张表</h4>
<p>读专业介绍时，遇到表里的词，先看一句话解释，再去「详见」那一页看例子。写个人陈述时，只用你真的理解、能举出例子的词；堆砌术语，老师一眼就能看出来。</p>
</div>
<!--SOURCES-->
</section>
"""
    (ROOT / "content" / "13-lesson4.html").write_text(html)
    print("written")


if __name__ == "__main__":
    main()
