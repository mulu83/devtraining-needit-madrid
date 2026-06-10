import os
import json
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session
import anthropic
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-before-going-live")

DB = "cases.db"

SYSTEM_PROMPT = """You help EFTA staff document AI and automation use cases through friendly conversation.

Collect these five things — ask naturally, one or two at a time:
1. What problem or opportunity was addressed?
2. Which domain: Finance & Budget / Legal & Compliance / Trade & Statistics / HR & Workforce / IT & Infrastructure / Communications & Outreach / Policy & Analysis / Other
3. Which tool: Microsoft Copilot / Claude / Azure AI Services / Power Automate / Power BI / GitHub Copilot / Custom ML Model / Other
4. What was the outcome? (specific numbers help — time saved, volume, error rate, etc.)
5. What's the key learning for colleagues trying something similar?

Also ask: should this be visible to Internal only / Management / Public?

Once you have everything, show a brief summary and ask "Shall I save this?".
If they confirm, output ONLY this block (nothing after it):

<case>
{"title":"short title you write","domain":"...","problem":"...","tool":"...","outcome":"...","learning":"...","visibility":"Internal only"}
</case>

Keep it warm and brief. The whole thing should take under 3 minutes."""


def get_db():
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    return db


def init_db():
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS cases (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id     TEXT UNIQUE,
                title       TEXT,
                domain      TEXT,
                problem     TEXT,
                tool        TEXT,
                outcome     TEXT,
                learning    TEXT,
                visibility  TEXT DEFAULT 'Internal only',
                submitted_by TEXT,
                submitted_at TEXT,
                status      TEXT DEFAULT 'Pending Approval'
            )
        """)


client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))


@app.route("/")
def index():
    session.clear()
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "").strip()
    if not user_message:
        return jsonify({"error": "empty message"}), 400

    history = session.get("messages", [])
    history.append({"role": "user", "content": user_message})

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=history,
    )
    reply = response.content[0].text
    history.append({"role": "assistant", "content": reply})
    session["messages"] = history
    session.modified = True

    case_data = None
    if "<case>" in reply:
        try:
            raw = reply.split("<case>")[1].split("</case>")[0].strip()
            case_data = json.loads(raw)
        except Exception:
            pass

    return jsonify({"message": reply, "case_data": case_data})


@app.route("/submit", methods=["POST"])
def submit():
    data = request.json
    case = data.get("case", {})
    name = data.get("submitted_by", "").strip() or "Anonymous"

    with get_db() as db:
        n = db.execute("SELECT COUNT(*) FROM cases").fetchone()[0]
        case_id = f"EFTA-AI-{n + 1:05d}"
        db.execute(
            """INSERT INTO cases
               (case_id,title,domain,problem,tool,outcome,learning,visibility,submitted_by,submitted_at,status)
               VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (
                case_id, case.get("title"), case.get("domain"),
                case.get("problem"), case.get("tool"), case.get("outcome"),
                case.get("learning"), case.get("visibility", "Internal only"),
                name, datetime.utcnow().isoformat(), "Pending Approval",
            ),
        )

    session.clear()
    return jsonify({"case_id": case_id})


@app.route("/cases")
def cases():
    with get_db() as db:
        rows = db.execute("SELECT * FROM cases ORDER BY submitted_at DESC").fetchall()
    return render_template("cases.html", cases=[dict(r) for r in rows])


@app.route("/approve/<case_id>", methods=["POST"])
def approve(case_id):
    action = request.json.get("action")  # "approve" or "reject"
    notes = request.json.get("notes", "")
    status = "Published" if action == "approve" else "Rejected"
    with get_db() as db:
        db.execute(
            "UPDATE cases SET status=? WHERE case_id=?",
            (status, case_id),
        )
    return jsonify({"ok": True, "status": status})


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)
