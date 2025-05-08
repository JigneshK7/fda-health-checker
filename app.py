
from flask import Flask, request, render_template_string
import os
import re

app = Flask(__name__)

def load_keywords(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return set(line.strip().lower() for line in f if line.strip())

red_flag_keywords = load_keywords("redflag.txt")
disease_keywords = load_keywords("diseases.txt")
symptom_keywords = load_keywords("symptoms.txt")

HTML_TEMPLATE = open("template.html", "r", encoding="utf-8").read()

# Words that can be used as a verb safely
safe_verb_context = {"aids", "supports", "helps", "promotes", "assists"}
prepositions = {"in", "with", "for", "to"}

@app.route("/", methods=["GET", "POST"])
def index():
    searched = ""
    result = ""
    is_compliant = True

    if request.method == "POST":
        claim = request.form.get("claim", "").strip().lower()
        searched = claim
        claim_words = set(re.findall(r"\b\w+\b", claim))

        red_flag_hit = red_flag_keywords & claim_words
        disease_hit = disease_keywords & claim_words
        symptom_hit = symptom_keywords & claim_words

        # Improved: Treat "aids" carefully when it's the only match in disease list and used as a verb
        aids_used_as_disease = "aids" in disease_hit and not re.search(r"\baids\b\s+(?:in|with|for|to)\b", claim)
        if aids_used_as_disease:
            disease_hit.remove("aids")  # keep it flagged
        elif "aids" in disease_hit:
            disease_hit.remove("aids")  # allow safe usage if contextually verb

        is_flagged = bool(red_flag_hit or disease_hit or symptom_hit)

        if is_flagged:
            result = "❌ Non-compliant: Claim appears to reference a drug-like benefit or symptom/disease."
            is_compliant = False
        else:
            result = "✅ Compliant: Claim appears to focus on general structure/function or wellness."
            is_compliant = True

    return render_template_string(HTML_TEMPLATE, searched=searched, result=result, is_compliant=is_compliant)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
