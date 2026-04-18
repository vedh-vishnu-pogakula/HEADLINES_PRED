"""
app.py
------
Gradio UI for Hindi Headline Prediction.
Dark editorial / newspaper aesthetic with floating Devanagari letters.
"""

import random
import gradio as gr
from inference import predict_headline

# ── Background floating elements ──────────────────────────────────────────────
DEVANAGARI_CHARS = list("अआइईउऊएऐओऔकखगघचछजझटठडढतथदधनपफबभमयरलवशषसह")

NEWSPAPER_PHRASES = [
    "ताज़ा समाचार", "विशेष रिपोर्ट", "आज की खबर",
    "मुख्य समाचार", "दैनिक समाचार", "ब्रेकिंग न्यूज़",
    "राष्ट्रीय खबर", "अंतरराष्ट्रीय", "खेल जगत",
    "अर्थव्यवस्था", "राजनीति", "विज्ञान और तकनीक",
    "सम्पादकीय", "विचार मंच", "शीर्ष कहानी",
]


def _make_background() -> str:
    rng = random.Random(99)
    parts = []

    # 55 floating Devanagari characters
    for _ in range(55):
        char     = rng.choice(DEVANAGARI_CHARS)
        left     = rng.randint(0, 98)
        top      = rng.randint(0, 97)
        size     = rng.randint(18, 72)
        opacity  = round(rng.uniform(0.028, 0.09), 3)
        duration = rng.randint(14, 42)
        delay    = rng.randint(0, 30)
        parts.append(
            f'<span class="bgc" style="left:{left}%;top:{top}%'
            f';font-size:{size}px;opacity:{opacity}'
            f';animation-duration:{duration}s;animation-delay:-{delay}s">{char}</span>'
        )

    # 14 floating newspaper phrases
    for _ in range(14):
        phrase   = rng.choice(NEWSPAPER_PHRASES)
        left     = rng.randint(0, 75)
        top      = rng.randint(1, 96)
        opacity  = round(rng.uniform(0.03, 0.07), 3)
        duration = rng.randint(22, 55)
        delay    = rng.randint(0, 35)
        rot      = rng.randint(-25, 25)
        parts.append(
            f'<span class="bgp" style="left:{left}%;top:{top}%'
            f';opacity:{opacity};animation-duration:{duration}s'
            f';animation-delay:-{delay}s;transform:rotate({rot}deg)">{phrase}</span>'
        )

    return '<div id="bglayer">' + "".join(parts) + "</div>"


BG_HTML = _make_background()

# ── CSS ───────────────────────────────────────────────────────────────────────
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;0,900;1,400&family=Noto+Sans+Devanagari:wght@300;400;500;600;700&family=EB+Garamond:ital,wght@0,400;0,600;1,400;1,600&display=swap');

/* ── Variables ── */
:root {
    --bg:       #07070f;
    --srf:      rgba(11,10,20,0.92);
    --srf2:     rgba(18,16,30,0.88);
    --gold:     #e9a832;
    --goldd:    rgba(233,168,50,0.22);
    --goldf:    rgba(233,168,50,0.12);
    --red:      #b03020;
    --txt:      #ede8df;
    --txtd:     rgba(237,232,223,0.55);
    --bdr:      rgba(233,168,50,0.20);
}

/* ── Reset ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body, .gradio-container {
    background: var(--bg) !important;
    color: var(--txt) !important;
    font-family: 'EB Garamond', serif !important;
    min-height: 100vh;
    position: relative;
}

/* ── Animated background ── */
#bglayer {
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 0;
    overflow: hidden;
}

.bgc {
    position: absolute;
    font-family: 'Noto Sans Devanagari', sans-serif;
    color: #e9a832;
    animation: drift linear infinite;
    user-select: none;
}

.bgp {
    position: absolute;
    font-family: 'Playfair Display', serif;
    font-size: 12px;
    letter-spacing: 3px;
    color: #ede8df;
    white-space: nowrap;
    animation: drift linear infinite;
    user-select: none;
}

@keyframes drift {
    0%   { transform: translateY(0)    rotate(0deg);  }
    30%  { transform: translateY(-14px) rotate(1.5deg); }
    70%  { transform: translateY(7px)  rotate(-1.5deg); }
    100% { transform: translateY(0)    rotate(0deg);  }
}

/* ── Main wrapper ── */
.gradio-container {
    max-width: 860px !important;
    margin: 0 auto !important;
    padding: 0 24px 60px !important;
    position: relative;
    z-index: 1;
}

/* ── Masthead ── */
#masthead {
    text-align: center;
    padding: 48px 0 28px;
    position: relative;
}

#masthead::after {
    content: '';
    display: block;
    margin: 22px auto 0;
    width: 100%;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--gold), transparent);
}

.mh-eyebrow {
    font-family: 'Noto Sans Devanagari', sans-serif;
    font-size: 10px;
    letter-spacing: 7px;
    color: var(--gold);
    text-transform: uppercase;
    margin-bottom: 10px;
}

.mh-title {
    font-family: 'Playfair Display', serif;
    font-size: clamp(38px, 7vw, 66px);
    font-weight: 900;
    color: var(--txt);
    line-height: 1;
    letter-spacing: -1px;
}

.mh-hindi {
    font-family: 'Noto Sans Devanagari', sans-serif;
    font-size: 20px;
    color: var(--gold);
    font-weight: 300;
    margin: 8px 0 4px;
}

.mh-sub {
    font-family: 'EB Garamond', serif;
    font-style: italic;
    font-size: 14px;
    color: var(--txtd);
    letter-spacing: 0.5px;
}

.mh-rule {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 14px;
    margin: 14px 0;
    color: var(--gold);
    font-size: 9px;
    opacity: 0.6;
}
.mh-rule::before, .mh-rule::after {
    content: '';
    width: 80px;
    height: 1px;
    background: var(--gold);
}

/* ── Section headers ── */
.sec-hd {
    font-family: 'Playfair Display', serif;
    font-size: 10px;
    letter-spacing: 5px;
    text-transform: uppercase;
    color: var(--gold);
    margin: 28px 0 12px;
    display: flex;
    align-items: center;
    gap: 12px;
}
.sec-hd::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--goldd);
}

/* ── Input overrides ── */
.svelte-1f354aw, .block { background: transparent !important; }

label span {
    font-family: 'EB Garamond', serif !important;
    font-size: 12px !important;
    letter-spacing: 2px !important;
    color: var(--txtd) !important;
    text-transform: uppercase !important;
}

textarea, input[type=text] {
    background: var(--srf) !important;
    border: 1px solid var(--bdr) !important;
    color: var(--txt) !important;
    font-family: 'Noto Sans Devanagari', sans-serif !important;
    font-size: 16px !important;
    line-height: 1.7 !important;
    border-radius: 3px !important;
    padding: 14px 16px !important;
    transition: border-color .25s, box-shadow .25s !important;
    resize: vertical !important;
}

textarea:focus, input[type=text]:focus {
    border-color: var(--gold) !important;
    box-shadow: 0 0 0 3px var(--goldf) !important;
    outline: none !important;
}

textarea::placeholder, input::placeholder {
    color: rgba(237,232,223,0.28) !important;
    font-style: italic;
}

/* ── Predict button ── */
#predict-btn {
    width: 100%;
    margin-top: 8px;
}

#predict-btn button, button#predict-btn {
    width: 100% !important;
    background: linear-gradient(135deg, #e9a832 0%, #c07a14 100%) !important;
    color: #0a0808 !important;
    font-family: 'Playfair Display', serif !important;
    font-size: 13px !important;
    font-weight: 700 !important;
    letter-spacing: 5px !important;
    text-transform: uppercase !important;
    border: none !important;
    border-radius: 2px !important;
    padding: 18px !important;
    cursor: pointer !important;
    transition: all .3s !important;
    box-shadow: 0 4px 24px rgba(233,168,50,0.28) !important;
}

#predict-btn button:hover {
    box-shadow: 0 6px 36px rgba(233,168,50,0.50) !important;
    transform: translateY(-2px) !important;
}

/* ── Result output container ── */
#result-out { background: transparent !important; border: none !important; }
#result-out > div { background: transparent !important; }

/* ── Gradio footer ── */
footer { display: none !important; }
.built-with { display: none !important; }
"""

# ── Result HTML builder ────────────────────────────────────────────────────────
OPTION_LABELS = ["A", "B", "C", "D"]


def _confidence_bar(label: str, headline: str, score: float, winner: bool) -> str:
    lc  = "#e9a832" if winner else "rgba(237,232,223,0.45)"
    bg  = "linear-gradient(90deg,#e9a832,#f5c860)" if winner else "rgba(233,168,50,0.35)"
    sh  = "box-shadow:0 0 10px rgba(233,168,50,0.55);" if winner else ""
    star = " ✦" if winner else ""
    short = (headline[:58] + "…") if len(headline) > 58 else headline
    return f"""
    <div style="margin-bottom:16px">
      <div style="display:flex;justify-content:space-between;margin-bottom:6px;
                  font-family:'EB Garamond',serif;font-size:13px;letter-spacing:.5px">
        <span style="color:{lc}">Option {label}{star} &ensp;
          <span style="font-family:'Noto Sans Devanagari',sans-serif;font-size:14px">{short}</span>
        </span>
        <span style="color:{lc};font-weight:600;min-width:48px;text-align:right">{score}%</span>
      </div>
      <div style="height:5px;background:rgba(255,255,255,0.05);border-radius:3px;overflow:hidden">
        <div style="height:100%;width:{score}%;border-radius:3px;background:{bg};{sh}
                    transition:width 1.2s cubic-bezier(.4,0,.2,1)"></div>
      </div>
    </div>"""


def build_result_html(result: dict) -> str:
    pred    = result["predicted_index"]
    options = result["all_options"]
    scores  = result["confidence_scores"]
    winner  = options[pred]

    bars = "".join(
        _confidence_bar(OPTION_LABELS[i], options[i], scores[f"option_{i}"], i == pred)
        for i in range(4)
    )

    return f"""
<div style="background:var(--srf);border:1px solid var(--bdr);border-radius:4px;
            padding:30px 32px;margin-top:20px;position:relative;overflow:hidden">

  <!-- left accent bar -->
  <div style="position:absolute;top:0;left:0;width:4px;height:100%;
              background:linear-gradient(180deg,#e9a832,#c07a14)"></div>

  <!-- winner label -->
  <div style="font-family:'Playfair Display',serif;font-size:10px;letter-spacing:5px;
              color:var(--gold);text-transform:uppercase;margin-bottom:10px">
    ✦ &nbsp; Predicted Headline
  </div>

  <!-- winner text -->
  <div style="font-family:'Noto Sans Devanagari',sans-serif;font-size:19px;
              color:var(--txt);line-height:1.65;margin-bottom:28px;padding:16px 20px;
              background:rgba(233,168,50,0.07);border-left:3px solid #e9a832;
              border-radius:2px">
    {winner}
  </div>

  <!-- divider -->
  <div style="height:1px;background:var(--goldd);margin-bottom:20px"></div>

  <!-- section label -->
  <div style="font-family:'Playfair Display',serif;font-size:10px;letter-spacing:4px;
              color:var(--txtd);text-transform:uppercase;margin-bottom:18px">
    Confidence Distribution
  </div>

  {bars}
</div>"""


# ── Predict handler ───────────────────────────────────────────────────────────
def predict(article: str, opt_a: str, opt_b: str, opt_c: str, opt_d: str) -> str:
    opts   = [opt_a, opt_b, opt_c, opt_d]
    labels = OPTION_LABELS

    if not article.strip():
        return _info_box("कृपया लेख दर्ज करें — Please enter a Hindi article.")

    for i, opt in enumerate(opts):
        if not opt.strip():
            return _info_box(f"Option {labels[i]} is empty. Please fill in all 4 candidate headlines.")

    try:
        result = predict_headline(article, opts)
        return build_result_html(result)
    except FileNotFoundError as e:
        return _err_box(str(e))
    except Exception as e:
        return _err_box(f"Prediction error: {e}")


def _info_box(msg: str) -> str:
    return (
        f'<div style="padding:22px 28px;border:1px solid var(--goldd);border-radius:4px;'
        f'color:var(--gold);font-family:EB Garamond,serif;font-style:italic;'
        f'font-size:16px;margin-top:16px">{msg}</div>'
    )


def _err_box(msg: str) -> str:
    return (
        f'<div style="padding:22px 28px;border:1px solid rgba(176,48,32,.5);border-radius:4px;'
        f'color:#e06050;font-family:EB Garamond,serif;font-size:15px;margin-top:16px">'
        f'⚠ {msg}</div>'
    )


# ── Layout ────────────────────────────────────────────────────────────────────
with gr.Blocks(css=CSS, title="Hindi Headline Oracle") as demo:

    # Floating background
    gr.HTML(BG_HTML)

    # ── Masthead ──────────────────────────────────────────────────────────────
    gr.HTML("""
    <div id="masthead">
      <div class="mh-eyebrow">AI · NLP · Hindi Language Intelligence</div>
      <div class="mh-title">Headline Oracle</div>
      <div class="mh-hindi">शीर्षक भविष्यवक्ता</div>
      <div class="mh-rule">◆</div>
      <div class="mh-sub">
        MuRIL &nbsp;·&nbsp; 86% Accuracy &nbsp;·&nbsp;
        IndicGLUE WSTP &nbsp;·&nbsp; 4-Way Multiple Choice
      </div>
    </div>
    """)

    # ── Article input ─────────────────────────────────────────────────────────
    gr.HTML('<div class="sec-hd">Article &nbsp;·&nbsp; लेख</div>')
    article_in = gr.Textbox(
        label="",
        placeholder="यहाँ हिंदी समाचार लेख दर्ज करें…  (Paste your Hindi news article here)",
        lines=6,
    )

    # ── Options ───────────────────────────────────────────────────────────────
    gr.HTML('<div class="sec-hd">Candidate Headlines &nbsp;·&nbsp; शीर्षक विकल्प</div>')

    with gr.Row():
        opt_a = gr.Textbox(label="Option A", placeholder="पहला शीर्षक…", lines=2)
        opt_b = gr.Textbox(label="Option B", placeholder="दूसरा शीर्षक…", lines=2)

    with gr.Row():
        opt_c = gr.Textbox(label="Option C", placeholder="तीसरा शीर्षक…", lines=2)
        opt_d = gr.Textbox(label="Option D", placeholder="चौथा शीर्षक…", lines=2)

    # ── Predict button ────────────────────────────────────────────────────────
    predict_btn = gr.Button(
        "✦   Predict Headline   ✦",
        variant="primary",
        elem_id="predict-btn",
    )

    # ── Result ────────────────────────────────────────────────────────────────
    result_out = gr.HTML(elem_id="result-out")

    predict_btn.click(
        fn=predict,
        inputs=[article_in, opt_a, opt_b, opt_c, opt_d],
        outputs=result_out,
    )

    # ── Footer ────────────────────────────────────────────────────────────────
    gr.HTML("""
    <div style="text-align:center;padding:40px 0 0;font-size:12px;
                color:rgba(237,232,223,0.35);letter-spacing:2px;
                border-top:1px solid rgba(233,168,50,0.12);margin-top:48px;
                font-family:'EB Garamond',serif;font-style:italic">
      MuRIL &nbsp;·&nbsp; Multilingual Representations for Indian Languages &nbsp;·&nbsp; Google Research
      <br><br>
      IndicGLUE &nbsp;·&nbsp; Wikipedia Section Title Prediction &nbsp;·&nbsp; Hindi
    </div>
    """)


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    demo.launch(share=False)
