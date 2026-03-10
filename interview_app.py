import streamlit as st
from openai import OpenAI
import json

# =========================
# OpenAI client
# =========================
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# =========================
# Vragenlijst
# =========================
vragen = [
    "Wie ben je?",
    "Wat doe je graag?",
    "Wat wil je professioneel bereiken?",
    "Wat wil je financieel bereiken?",
    "Wat motiveert jou om een bedrijf te bouwen of mee te laten groeien?",
    "Welke rol neem jij meestal spontaan op in een team?",
    "Wat is een professionele beslissing waar je achteraf trots op bent?",
    "Wat is een fout die je professioneel hebt gemaakt en wat heb je eruit geleerd?",
    "Hoe neem je beslissingen wanneer je niet alle informatie hebt?",
    "Wat betekent risico voor jou in een zakelijke context?",
    "Een klant koopt een AI project van €10k en vraagt een extra aanpassing die ons €1k kost. Hoe ga je hiermee om?",
    "Een softwareproject van €200k loopt vertraging op door een fout in het team. Hoe pak je dit aan?",
    "Een bouwproject heeft onverwacht €30k extra kosten. Hoe communiceer je dit naar de klant?",
    "Een hardwareproduct dat €500k ontwikkeling kost blijkt minder vraag te hebben dan verwacht. Wat doe je?",
    "Een aandeelhouder wil plots agressiever groeien terwijl het team stabiliteit wil. Hoe ga je hiermee om?",
    "Hoe bepaal jij of een investering de moeite waard is?",
    "We maken na jaar 1 een winst van €150k. Wat zou jij doen met dat geld?",
    "Hoe kijk je naar het verschil tussen winst nemen en herinvesteren?",
    "Hoe zou jij een nieuw product of dienst naar de markt brengen?",
    "Wat is volgens jou belangrijker: een goed product of goede marketing?",
    "Stel dat je een nieuw bedrijf start met €50k budget. Waar besteed je het eerst aan?",
    "Hoe overtuig je een klant om met ons te werken in plaats van met een concurrent?",
    "Stel dat je een product moet verkopen waar niemand specifiek naar vraagt. Hoe pak je dat aan?",
    "Hoe ga je om met conflicten binnen een team?",
    "Waarom denk je dat jij een waardevolle partner of collega kan zijn?",
    "Wat is voor jouw de financiële grens om de overstap te maken naar een zaak? brutto en/of netto en eventuele voorwaarden"
]

# =========================
# System prompt
# =========================
system_prompt = """
Je bent een slimme en kritische interviewer.
Doel:
een kandidaat evalueren op persoonlijkheid, business inzicht,
besluitvorming, sales en strategisch denken.

Regels:
- Stel 1 relevante vervolg vraag gebaseerd op het antwoord.
- De vervolg vraag moet logisch aansluiten op het antwoord.
- Als de vraag persoonlijk is, stel persoonlijke vervolgvragen.
- Als de vraag business gerelateerd is, stel strategische vervolgvragen.
"""

# =========================
# Streamlit state initialisatie
# =========================
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": system_prompt}]

if "vraag_index" not in st.session_state:
    st.session_state.vraag_index = 0

if "fase" not in st.session_state:
    st.session_state.fase = "vraag"  # fases: vraag / followup

st.title("AI Interview Tool")
st.write(f"Vraag {st.session_state.vraag_index + 1} van {len(vragen)}")

# =========================
# Interview flow
# =========================
if st.session_state.vraag_index < len(vragen):
    vraag = vragen[st.session_state.vraag_index]

    # Hoofdvraag fase
    if st.session_state.fase == "vraag":
        st.subheader("Hoofdvraag")
        st.write(vraag)
        antwoord = st.text_area("Jouw antwoord", key="hoofdvraag_input")

        if st.button("Verstuur antwoord"):
            st.session_state.messages.append({"role": "assistant", "content": vraag})
            st.session_state.messages.append({"role": "user", "content": antwoord})

            # AI genereert vervolg vraag
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=st.session_state.messages
            )
            followup = response.choices[0].message.content
            st.session_state.followup = followup
            st.session_state.fase = "followup"

    # Vervolgvraag fase
    elif st.session_state.fase == "followup":
        st.subheader("AI vervolg vraag")
        st.write(st.session_state.followup)
        followup_antwoord = st.text_area("Antwoord op vervolg vraag", key="followup_input")

        if st.button("Verstuur vervolg antwoord"):
            st.session_state.messages.append({"role": "assistant", "content": st.session_state.followup})
            st.session_state.messages.append({"role": "user", "content": followup_antwoord})

            # volgende vraag
            st.session_state.vraag_index += 1
            st.session_state.fase = "vraag"
            st.experimental_rerun()

# =========================
# Interview afgerond
# =========================
else:
    st.success("Interview afgerond!")

    analysis = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=st.session_state.messages + [{
            "role": "user",
            "content": """
Analyseer deze kandidaat en geef een conclusie over:

- persoonlijkheid
- business inzicht
- risico inschatting
- leiderschap
- sales en marketing inzicht
- algemene geschiktheid als partner of manager

Geef een duidelijke maar beknopte analyse.
"""
        }]
    )

    conclusie = analysis.choices[0].message.content
    st.subheader("Analyse kandidaat")
    st.write(conclusie)

    # Opslaan in JSON
    data = {
        "conversation": st.session_state.messages,
        "analysis": conclusie
    }
    with open("interview_result.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


    st.success("Resultaat opgeslagen in interview_result.json")
