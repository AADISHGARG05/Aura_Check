from flask import Flask, render_template, request
from flask_cors import CORS
import os
import script

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

DASS_QUESTIONS = [
    "I found myself getting upset by quite trivial things.",
    "I was aware of dryness of my mouth.",
    "I couldn't seem to experience any positive feeling at all.",
    "I experienced breathing difficulty, such as excessively rapid breathing or breathlessness in the absence of physical exertion.",
    "I just couldn't seem to get going.",
    "I tended to over-react to situations.",
    "I had a feeling of shakiness, such as my legs feeling like they were going to give way.",
    "I found it difficult to relax.",
    "I found myself in situations that made me so anxious that I was most relieved when they ended.",
    "I felt that I had nothing to look forward to.",
    "I found myself getting upset rather easily.",
    "I felt that I was using a lot of nervous energy.",
    "I felt sad and depressed.",
    "I found myself getting impatient when I was delayed in any way, such as at elevators, traffic lights, or while being kept waiting.",
    "I had a feeling of faintness.",
    "I felt that I had lost interest in just about everything.",
    "I felt that I wasn't worth much as a person.",
    "I felt that I was rather touchy.",
    "I perspired noticeably, such as having sweaty hands, in the absence of high temperatures or physical exertion.",
    "I felt scared without any good reason.",
    "I felt that life wasn't worthwhile.",
    "I found it hard to wind down.",
    "I had difficulty swallowing.",
    "I couldn't seem to get any enjoyment out of the things I did.",
    "I was aware of the action of my heart in the absence of physical exertion, such as an increased heart rate or a missed beat.",
    "I felt down-hearted and blue.",
    "I found that I was very irritable.",
    "I felt I was close to panic.",
    "I found it hard to calm down after something upset me.",
    "I feared that I would be thrown by some trivial but unfamiliar task.",
    "I was unable to become enthusiastic about anything.",
    "I found it difficult to tolerate interruptions to what I was doing.",
    "I was in a state of nervous tension.",
    "I felt I was pretty worthless.",
    "I was intolerant of anything that kept me from getting on with what I was doing.",
    "I felt terrified.",
    "I could see nothing in the future to be hopeful about.",
    "I felt that life was meaningless.",
    "I found myself getting agitated.",
    "I was worried about situations in which I might panic and make a fool of myself.",
    "I experienced trembling, such as trembling in my hands.",
    "I found it difficult to work up the initiative to do things."
]
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
