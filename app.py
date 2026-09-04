from flask import Flask, render_template, request
from flask_cors import CORS
import os
import script

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

DASS_QUESTIONS = [f"Question {i}" for i in range(1, 43)]
TIPI_QUESTIONS = [
    "I see myself as extraverted and enthusiastic.",
    "I see myself as critical and quarrelsome.",
    "I see myself as dependable and self-disciplined.",
    "I see myself as anxious and easily upset.",
    "I see myself as open to new experiences and complex.",
    "I see myself as reserved and quiet.",
    "I see myself as sympathetic and warm.",
    "I see myself as disorganized and careless.",
    "I see myself as calm and emotionally stable.",
    "I see myself as conventional and uncreative.",
]
VCL_WORDS = [
    "boat", "incoherent", "pallid", "robot", "audible", "cuivocal",
    "paucity", "epistemology", "florted", "decide", "pastiche",
    "verdid", "abysmal", "lucid", "betray", "funny"
]

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/test", methods=["GET", "POST"])
def test():
    if request.method == "GET":
        return render_template(
            "test.html",
            dass_questions=DASS_QUESTIONS,
            tipi_questions=TIPI_QUESTIONS,
            vcl_words=VCL_WORDS,
        )

    try:
        form_data = request.form.to_dict()
        results = script.predict_all(form_data)
        return render_template(
            "result.html",
            stress=results["stress"],
            anxiety=results["anxiety"],
            depression=results["depression"],
            severity_class=results["severity_class"],
            error=None,
        )
    except (ValueError, KeyError) as exc:
        return render_template(
            "test.html",
            dass_questions=DASS_QUESTIONS,
            tipi_questions=TIPI_QUESTIONS,
            vcl_words=VCL_WORDS,
            error=str(exc),
            submitted=request.form,
        ), 400
    except Exception as exc:
        import traceback
        traceback.print_exc()

        return render_template(
            "result.html",
            stress=None,
            anxiety=None,
            depression=None,
            severity_class="",
            error=f"Analysis failed: {exc}"
        ), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5500))
    app.run(host="0.0.0.0", port=port, debug=False)
