import streamlit as st
import swisseph as swe
import matplotlib.pyplot as plt
import hashlib

from datetime import date, datetime, timezone, timedelta
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError


# =========================================================
# PAGE SETTINGS
# =========================================================

st.set_page_config(
    page_title="Astro_KD",
    page_icon="🔮",
    layout="centered"
)


# =========================================================
# SAFE CSS
# CSS ONLY - NO VISIBLE HTML CONTENT
# =========================================================

st.markdown(
    """
    <style>

    .stApp {
        background:
            radial-gradient(
                circle at top,
                #281758 0%,
                #140d31 40%,
                #080714 100%
            );
    }

    .block-container {
        max-width: 900px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    h1 {
        color: #f6d778 !important;
        text-align: center;
    }

    h2 {
        color: #f5d98b !important;
    }

    h3 {
        color: #ead49a !important;
    }

    p {
        color: #eee8f5;
    }

    label {
        color: #f5df9e !important;
        font-weight: 600 !important;
    }

    div.stButton > button {
        width: 100%;
        background: linear-gradient(
            90deg,
            #c9973e,
            #f6d778,
            #c9973e
        );
        color: #160d2d;
        border: none;
        border-radius: 12px;
        font-size: 18px;
        font-weight: 800;
        padding: 0.75rem;
    }

    div.stButton > button:hover {
        color: #160d2d;
        border: none;
        box-shadow: 0px 6px 20px rgba(246,215,120,0.25);
    }

    div[data-testid="stMetric"] {
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(246,215,120,0.25);
        padding: 18px;
        border-radius: 16px;
    }

    div[data-testid="stAlert"] {
        border-radius: 12px;
    }

    hr {
        border-color: rgba(246,215,120,0.20);
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# ASTROLOGY DATA
# =========================================================

RASHIS = [
    "Mesha",
    "Vrishabha",
    "Mithuna",
    "Karka",
    "Simha",
    "Kanya",
    "Tula",
    "Vrishchika",
    "Dhanu",
    "Makara",
    "Kumbha",
    "Meena"
]


RASHI_ENGLISH = [
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces"
]


RASHI_HINDI = [
    "मेष",
    "वृषभ",
    "मिथुन",
    "कर्क",
    "सिंह",
    "कन्या",
    "तुला",
    "वृश्चिक",
    "धनु",
    "मकर",
    "कुंभ",
    "मीन"
]


RASHI_SYMBOLS = [
    "♈",
    "♉",
    "♊",
    "♋",
    "♌",
    "♍",
    "♎",
    "♏",
    "♐",
    "♑",
    "♒",
    "♓"
]


PLANETS = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mars": swe.MARS,
    "Mercury": swe.MERCURY,
    "Jupiter": swe.JUPITER,
    "Venus": swe.VENUS,
    "Saturn": swe.SATURN
}


# =========================================================
# DAILY ASTROLOGY CONTENT
# =========================================================

LUCKY_COLOURS_EN = [
    "Red",
    "Orange",
    "Yellow",
    "Green",
    "Sky Blue",
    "Royal Blue",
    "Purple",
    "White",
    "Golden",
    "Pink",
    "Turquoise",
    "Cream"
]


LUCKY_COLOURS_HI = [
    "लाल",
    "नारंगी",
    "पीला",
    "हरा",
    "आसमानी नीला",
    "गहरा नीला",
    "बैंगनी",
    "सफेद",
    "सुनहरा",
    "गुलाबी",
    "फिरोज़ी",
    "क्रीम"
]


# =========================================================
# RASHI-SPECIFIC BASE MESSAGES
# =========================================================

RASHI_BASE_EN = [

    # Mesha
    "Your natural drive may be strong today. Use your energy thoughtfully rather than rushing into every situation.",

    # Vrishabha
    "A steady and practical approach may work in your favour today. Give important matters enough time.",

    # Mithuna
    "Communication and new ideas may play an important role today. Stay focused so that scattered thoughts do not reduce productivity.",

    # Karka
    "Personal priorities and emotional matters may require attention today. Balance sensitivity with practical thinking.",

    # Simha
    "Confidence can help you move important matters forward today. Use leadership with patience and avoid unnecessary ego conflicts.",

    # Kanya
    "Planning, organisation and attention to detail may help you considerably today. Avoid overthinking small matters.",

    # Tula
    "Balance will be important today. Consider different perspectives before making an important choice.",

    # Vrishchika
    "Your concentration may be strong today. Direct your energy toward meaningful priorities rather than unnecessary conflicts.",

    # Dhanu
    "Learning, planning or exploring a new possibility may attract your attention today. Keep expectations realistic.",

    # Makara
    "Discipline and patience can help you make steady progress today. Focus on long-term value rather than quick results.",

    # Kumbha
    "A different perspective may help you find an interesting solution today. Remain open to useful ideas from others.",

    # Meena
    "Intuition may influence your thinking today. Balance your feelings with practical information before making decisions."
]


RASHI_BASE_HI = [

    "आज आपकी ऊर्जा मजबूत रह सकती है। जल्दबाज़ी करने के बजाय अपनी ऊर्जा को सही दिशा में लगाएँ।",

    "आज स्थिर और व्यावहारिक दृष्टिकोण आपके लिए लाभदायक हो सकता है। महत्वपूर्ण मामलों को पर्याप्त समय दें।",

    "आज बातचीत और नए विचार महत्वपूर्ण भूमिका निभा सकते हैं। कई विचारों के बीच अपने मुख्य लक्ष्य पर ध्यान बनाए रखें।",

    "आज व्यक्तिगत और भावनात्मक विषयों पर ध्यान देने की आवश्यकता हो सकती है। भावनाओं और व्यावहारिक सोच में संतुलन रखें।",

    "आज आपका आत्मविश्वास महत्वपूर्ण कार्यों को आगे बढ़ाने में मदद कर सकता है। नेतृत्व करें, लेकिन धैर्य बनाए रखें।",

    "आज योजना, व्यवस्था और छोटी बातों पर ध्यान देना लाभदायक हो सकता है। आवश्यकता से अधिक सोचने से बचें।",

    "आज संतुलन बनाए रखना महत्वपूर्ण रहेगा। कोई महत्वपूर्ण निर्णय लेने से पहले अलग-अलग पहलुओं पर विचार करें।",

    "आज आपकी एकाग्रता मजबूत रह सकती है। अपनी ऊर्जा को महत्वपूर्ण कार्यों में लगाएँ और अनावश्यक विवाद से बचें।",

    "आज कुछ नया सीखने, योजना बनाने या नई संभावना पर विचार करने का मन हो सकता है। अपेक्षाएँ व्यावहारिक रखें।",

    "आज अनुशासन और धैर्य आपको लगातार आगे बढ़ने में मदद कर सकते हैं। तुरंत परिणाम के बजाय लंबे समय के लाभ पर ध्यान दें।",

    "आज अलग दृष्टिकोण किसी समस्या का नया समाधान दे सकता है। दूसरों के उपयोगी विचारों के लिए खुले रहें।",

    "आज आपकी अंतर्ज्ञान शक्ति सक्रिय रह सकती है। महत्वपूर्ण निर्णय में भावना के साथ व्यावहारिक जानकारी को भी महत्व दें।"
]


CAREER_EN = [
    "Complete important pending work before taking on additional responsibilities.",
    "A professional discussion could become useful. Communicate your ideas clearly.",
    "Review financial commitments carefully and avoid unnecessary expenditure.",
    "Your consistency may receive attention. Concentrate on quality rather than speed.",
    "An existing problem may become easier when approached from a different angle.",
    "Prioritise your most valuable task and minimise distractions."
]


CAREER_HI = [
    "नई जिम्मेदारियाँ लेने से पहले महत्वपूर्ण लंबित कार्य पूरे करने पर ध्यान दें।",
    "कार्यस्थल पर कोई बातचीत उपयोगी साबित हो सकती है। अपने विचार स्पष्ट रूप से रखें।",
    "आर्थिक निर्णय सावधानी से लें और अनावश्यक खर्च से बचें।",
    "आपकी निरंतरता पर ध्यान दिया जा सकता है। गति से अधिक काम की गुणवत्ता पर ध्यान दें।",
    "किसी पुरानी समस्या को नए दृष्टिकोण से देखने पर समाधान मिल सकता है।",
    "आज सबसे महत्वपूर्ण कार्य को प्राथमिकता दें और ध्यान भटकाने वाली चीज़ों से बचें।"
]


LOVE_EN = [
    "Honest communication can help strengthen an important relationship.",
    "Spend meaningful time with family and avoid unnecessary arguments.",
    "Listening carefully may be more valuable than immediately giving an answer.",
    "A small gesture of appreciation could improve someone's day.",
    "Do not allow a minor misunderstanding to become a larger issue.",
    "Patience and empathy can make personal conversations more productive."
]


LOVE_HI = [
    "ईमानदार बातचीत किसी महत्वपूर्ण रिश्ते को मजबूत करने में मदद कर सकती है।",
    "परिवार के साथ अच्छा समय बिताएँ और अनावश्यक बहस से बचें।",
    "तुरंत जवाब देने के बजाय सामने वाले की बात ध्यान से सुनना अधिक उपयोगी हो सकता है।",
    "आपकी छोटी-सी सराहना किसी अपने का दिन बेहतर बना सकती है।",
    "छोटी गलतफहमी को बड़ा मुद्दा न बनने दें।",
    "धैर्य और समझदारी व्यक्तिगत बातचीत को बेहतर बना सकती है।"
]


HEALTH_EN = [
    "Maintain a balanced routine and give yourself adequate rest.",
    "Avoid an overloaded schedule and take short breaks when needed.",
    "Regular movement and proper hydration can support your daily routine.",
    "Pay attention to sleep and avoid unnecessary mental overload.",
    "A calmer pace may help you maintain better focus throughout the day.",
    "Make time to disconnect from screens and unnecessary distractions."
]


HEALTH_HI = [
    "अपनी दिनचर्या संतुलित रखें और पर्याप्त आराम को महत्व दें।",
    "दिन को आवश्यकता से अधिक व्यस्त न करें और जरूरत पड़ने पर छोटा ब्रेक लें।",
    "नियमित शारीरिक गतिविधि और पर्याप्त पानी आपकी दिनचर्या को बेहतर रख सकते हैं।",
    "नींद पर ध्यान दें और अनावश्यक मानसिक दबाव से बचें।",
    "थोड़ी शांत गति पूरे दिन बेहतर एकाग्रता बनाए रखने में मदद कर सकती है।",
    "कुछ समय स्क्रीन और अनावश्यक व्यवधानों से दूर रहने का प्रयास करें।"
]


ADVICE_EN = [
    "Patience can be more powerful than speed today.",
    "Focus on what is within your control.",
    "Finish what you have already started.",
    "Think carefully, then act confidently.",
    "Protect your time and use it intentionally.",
    "Do not let temporary emotions control an important decision.",
    "Consistency matters more than one perfect day."
]


ADVICE_HI = [
    "आज गति से अधिक धैर्य आपके काम आ सकता है।",
    "उन चीज़ों पर ध्यान दें जो आपके नियंत्रण में हैं।",
    "जो काम शुरू कर चुके हैं, पहले उसे पूरा करने का प्रयास करें।",
    "पहले अच्छी तरह सोचें और फिर आत्मविश्वास से कदम उठाएँ।",
    "अपने समय को महत्व दें और उसका सही उपयोग करें।",
    "क्षणिक भावनाओं के आधार पर महत्वपूर्ण निर्णय लेने से बचें।",
    "एक परफेक्ट दिन से अधिक महत्वपूर्ण निरंतरता है।"
]


# =========================================================
# LOCATION LOOKUP
# =========================================================

@st.cache_data
def get_coordinates(place):

    geolocator = Nominatim(
        user_agent="astro_kd_vedic_astrology_app"
    )

    try:

        location = geolocator.geocode(
            place,
            timeout=10
        )

        if location:

            return {
                "address": location.address,
                "latitude": location.latitude,
                "longitude": location.longitude
            }

    except (
        GeocoderTimedOut,
        GeocoderServiceError
    ):

        return None

    return None


# =========================================================
# BIRTH CHART CALCULATION
# =========================================================

def calculate_chart(
    dob,
    birth_time,
    latitude,
    longitude
):

    # -----------------------------------------------------
    # IMPORTANT:
    # Current Astro_KD version assumes birth time is IST.
    # Suitable for Indian birthplaces.
    # -----------------------------------------------------

    ist = timezone(
        timedelta(
            hours=5,
            minutes=30
        )
    )


    birth_local = datetime(
        dob.year,
        dob.month,
        dob.day,
        birth_time.hour,
        birth_time.minute,
        birth_time.second,
        tzinfo=ist
    )


    birth_utc = birth_local.astimezone(
        timezone.utc
    )


    decimal_hour = (
        birth_utc.hour
        + birth_utc.minute / 60
        + birth_utc.second / 3600
    )


    jd = swe.julday(
        birth_utc.year,
        birth_utc.month,
        birth_utc.day,
        decimal_hour
    )


    # Lahiri Ayanamsha

    swe.set_sid_mode(
        swe.SIDM_LAHIRI
    )


    flags = (
        swe.FLG_SWIEPH
        | swe.FLG_SIDEREAL
    )


    # =====================================================
    # LAGNA
    # =====================================================

    cusps, ascmc = swe.houses_ex(
        jd,
        latitude,
        longitude,
        b'P',
        swe.FLG_SIDEREAL
    )


    lagna_longitude = (
        ascmc[0] % 360
    )


    lagna_index = int(
        lagna_longitude // 30
    )


    # =====================================================
    # PLANETS
    # =====================================================

    planet_positions = {}

    moon_sign_index = None


    for planet_name, planet_id in PLANETS.items():

        planet_data, _ = swe.calc_ut(
            jd,
            planet_id,
            flags
        )


        longitude_value = (
            planet_data[0] % 360
        )


        sign_index = int(
            longitude_value // 30
        )


        # Whole-sign house mapping

        house = (
            (sign_index - lagna_index) % 12
        ) + 1


        planet_positions[planet_name] = {
            "longitude": longitude_value,
            "sign_index": sign_index,
            "house": house
        }


        if planet_name == "Moon":

            moon_sign_index = (
                sign_index
            )


    # =====================================================
    # RAHU
    # =====================================================

    rahu_data, _ = swe.calc_ut(
        jd,
        swe.MEAN_NODE,
        flags
    )


    rahu_longitude = (
        rahu_data[0] % 360
    )


    rahu_sign_index = int(
        rahu_longitude // 30
    )


    rahu_house = (
        (rahu_sign_index - lagna_index) % 12
    ) + 1


    planet_positions["Rahu"] = {
        "longitude": rahu_longitude,
        "sign_index": rahu_sign_index,
        "house": rahu_house
    }


    # =====================================================
    # KETU
    # =====================================================

    ketu_longitude = (
        rahu_longitude + 180
    ) % 360


    ketu_sign_index = int(
        ketu_longitude // 30
    )


    ketu_house = (
        (ketu_sign_index - lagna_index) % 12
    ) + 1


    planet_positions["Ketu"] = {
        "longitude": ketu_longitude,
        "sign_index": ketu_sign_index,
        "house": ketu_house
    }


    return {
        "lagna_index": lagna_index,
        "lagna_longitude": lagna_longitude,
        "moon_sign_index": moon_sign_index,
        "planets": planet_positions
    }


# =========================================================
# DETERMINISTIC DAILY SYSTEM
# =========================================================

def deterministic_index(
    rashi_index,
    current_date,
    category,
    length
):

    seed = (
        f"{current_date.isoformat()}-"
        f"{rashi_index}-"
        f"{category}"
    )


    hash_value = hashlib.sha256(
        seed.encode()
    ).hexdigest()


    number = int(
        hash_value[:12],
        16
    )


    return number % length


# =========================================================
# DAILY RASHIFAL
# =========================================================

def get_daily_rashifal(
    rashi_index,
    current_date,
    language
):

    career_index = deterministic_index(
        rashi_index,
        current_date,
        "career",
        len(CAREER_EN)
    )

    love_index = deterministic_index(
        rashi_index,
        current_date,
        "love",
        len(LOVE_EN)
    )

    health_index = deterministic_index(
        rashi_index,
        current_date,
        "health",
        len(HEALTH_EN)
    )

    advice_index = deterministic_index(
        rashi_index,
        current_date,
        "advice",
        len(ADVICE_EN)
    )

    colour_index = deterministic_index(
        rashi_index,
        current_date,
        "colour",
        len(LUCKY_COLOURS_EN)
    )

    lucky_number = (
        deterministic_index(
            rashi_index,
            current_date,
            "number",
            9
        )
        + 1
    )


    if language == "हिन्दी":

        return {
            "overall": RASHI_BASE_HI[rashi_index],
            "career": CAREER_HI[career_index],
            "relationship": LOVE_HI[love_index],
            "wellbeing": HEALTH_HI[health_index],
            "advice": ADVICE_HI[advice_index],
            "colour": LUCKY_COLOURS_HI[colour_index],
            "number": lucky_number
        }


    return {
        "overall": RASHI_BASE_EN[rashi_index],
        "career": CAREER_EN[career_index],
        "relationship": LOVE_EN[love_index],
        "wellbeing": HEALTH_EN[health_index],
        "advice": ADVICE_EN[advice_index],
        "colour": LUCKY_COLOURS_EN[colour_index],
        "number": lucky_number
    }


# =========================================================
# DRAW KUNDLI
# =========================================================

def draw_kundli(chart):

    lagna_index = chart["lagna_index"]

    # -----------------------------------------------------
    # Build the 12 houses
    # -----------------------------------------------------

    houses = {}

    for house in range(1, 13):

        sign_index = (
            lagna_index + house - 1
        ) % 12

        planets_here = []

        for planet_name, planet_data in chart["planets"].items():

            if planet_data["house"] == house:
                planets_here.append(planet_name)

        houses[house] = {
            "sign_index": sign_index,
            "sign": RASHIS[sign_index],
            "symbol": RASHI_SYMBOLS[sign_index],
            "planets": planets_here
        }


    # -----------------------------------------------------
    # Short planet labels
    # -----------------------------------------------------

    planet_short = {
        "Sun": "Su",
        "Moon": "Mo",
        "Mars": "Ma",
        "Mercury": "Me",
        "Jupiter": "Ju",
        "Venus": "Ve",
        "Saturn": "Sa",
        "Rahu": "Ra",
        "Ketu": "Ke"
    }


    # -----------------------------------------------------
    # Chart colours
    # -----------------------------------------------------

    background = "#120B2E"
    gold = "#E7C568"
    light_gold = "#F7E5A5"
    planet_text = "#FFFFFF"
    secondary_text = "#BDB4D2"


    # -----------------------------------------------------
    # Create chart
    # -----------------------------------------------------

    fig, ax = plt.subplots(
        figsize=(8, 8),
        facecolor=background
    )

    ax.set_facecolor(background)

    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)

    ax.set_aspect("equal")
    ax.axis("off")


    # -----------------------------------------------------
    # Outer border
    # -----------------------------------------------------

    ax.plot(
        [0, 10, 10, 0, 0],
        [0, 0, 10, 10, 0],
        linewidth=2.5,
        color=gold
    )


    # -----------------------------------------------------
    # Main diamond
    # -----------------------------------------------------

    ax.plot(
        [5, 10, 5, 0, 5],
        [10, 5, 0, 5, 10],
        linewidth=2.2,
        color=gold
    )


    # -----------------------------------------------------
    # Corner diagonals
    # -----------------------------------------------------

    ax.plot(
        [0, 5],
        [10, 5],
        linewidth=1.4,
        color=gold
    )

    ax.plot(
        [10, 5],
        [10, 5],
        linewidth=1.4,
        color=gold
    )

    ax.plot(
        [0, 5],
        [0, 5],
        linewidth=1.4,
        color=gold
    )

    ax.plot(
        [10, 5],
        [0, 5],
        linewidth=1.4,
        color=gold
    )


    # -----------------------------------------------------
    # House positions
    # -----------------------------------------------------

    positions = {

        1: (5, 8.25),
        2: (2.65, 8.45),
        3: (1.45, 7.25),

        4: (1.65, 5),
        5: (1.45, 2.75),
        6: (2.65, 1.55),

        7: (5, 1.75),
        8: (7.35, 1.55),
        9: (8.55, 2.75),

        10: (8.35, 5),
        11: (8.55, 7.25),
        12: (7.35, 8.45)
    }


    # -----------------------------------------------------
    # Draw house information
    # -----------------------------------------------------

    for house_number, house_data in houses.items():

        x, y = positions[house_number]

        # House number

        ax.text(
            x,
            y + 0.58,
            str(house_number),
            ha="center",
            va="center",
            fontsize=7,
            color=secondary_text
        )


        # Zodiac symbol + Rashi

        rashi_label = (
            f"{house_data['symbol']} "
            f"{house_data['sign']}"
        )

        ax.text(
            x,
            y + 0.15,
            rashi_label,
            ha="center",
            va="center",
            fontsize=9,
            color=light_gold,
            fontweight="bold"
        )


        # Planets

        if house_data["planets"]:

            short_planets = [
                planet_short.get(
                    planet,
                    planet
                )
                for planet in house_data["planets"]
            ]

            planet_label = " • ".join(
                short_planets
            )

            # Split crowded houses

            if len(short_planets) >= 3:

                midpoint = (
                    len(short_planets) + 1
                ) // 2

                line1 = " • ".join(
                    short_planets[:midpoint]
                )

                line2 = " • ".join(
                    short_planets[midpoint:]
                )

                planet_label = (
                    line1
                    + "\n"
                    + line2
                )


            ax.text(
                x,
                y - 0.38,
                planet_label,
                ha="center",
                va="center",
                fontsize=8,
                color=planet_text,
                fontweight="bold"
            )


    # -----------------------------------------------------
    # Lagna indicator
    # -----------------------------------------------------

    ax.text(
        5,
        9.50,
        "▲ LAGNA",
        ha="center",
        va="center",
        fontsize=10,
        color=gold,
        fontweight="bold"
    )


    # -----------------------------------------------------
    # Center branding
    # -----------------------------------------------------

    ax.text(
        5,
        5.18,
        "ॐ",
        ha="center",
        va="center",
        fontsize=25,
        color=gold,
        fontweight="bold"
    )


    ax.text(
        5,
        4.72,
        "Astro_KD",
        ha="center",
        va="center",
        fontsize=10,
        color=light_gold,
        fontweight="bold"
    )


    # -----------------------------------------------------
    # Premium title
    # -----------------------------------------------------

    ax.text(
        5,
        10.35,
        "VEDIC BIRTH CHART",
        ha="center",
        va="center",
        fontsize=13,
        color=gold,
        fontweight="bold"
    )


    # -----------------------------------------------------
    # Clean spacing
    # -----------------------------------------------------

    plt.tight_layout(
        pad=1.5
    )

    return fig


# =========================================================
# WEBSITE HEADER
# =========================================================

st.title(
    "🔮 Astro_KD"
)


st.markdown(
    "### 🕉️ Vedic Astrology • Kundli • Daily Rashifal"
)


st.caption(
    "Ancient Wisdom • Modern Experience"
)


st.divider()


st.header(
    "✨ Discover Your Stars"
)


st.write(
    "Enter your birth details to generate your personal "
    "Vedic Kundli and today's astrology guide."
)


# =========================================================
# INPUT FORM
# =========================================================

name = st.text_input(
    "👤 Name",
    placeholder="Enter your name"
)


dob = st.date_input(
    "🎂 Date of Birth",
    min_value=date(
        1940,
        1,
        1
    ),
    max_value=date.today(),
    value=date(
        1950,
        11,
        11
    )
)


birth_time = st.time_input(
    "🕐 Exact Birth Time",
    value=datetime.strptime(
        "12:00",
        "%H:%M"
    ).time()
)


birth_place = st.text_input(
    "📍 Birth Place",
    value="Aligarh, Uttar Pradesh, India"
)

language = st.selectbox(
    "🌐 Rashifal Language",
    [
        "English",
        "हिन्दी"
    ]
)


st.write("")


# =========================================================
# GENERATE BUTTON
# =========================================================

generate = st.button(
    "🔮 Generate My Kundli",
    type="primary",
    use_container_width=True
)


# =========================================================
# RESULTS
# =========================================================

if generate:

    if not name:

        st.warning(
            "Please enter your name."
        )


    elif not birth_place:

        st.warning(
            "Please enter your birthplace."
        )


    else:

        with st.spinner(
            "✨ Preparing your Vedic Kundli..."
        ):

            location = get_coordinates(
                birth_place
            )


        if location is None:

            st.error(
                "Birthplace could not be found. "
                "Please enter City, State, Country."
            )


        else:

            chart = calculate_chart(
                dob,
                birth_time,
                location["latitude"],
                location["longitude"]
            )


            moon_index = (
                chart["moon_sign_index"]
            )


            lagna_index = (
                chart["lagna_index"]
            )


            today = date.today()


            rashifal = get_daily_rashifal(
    		moon_index,
    		today,
    		language
	    )


            # =================================================
            # GREETING
            # =================================================

            st.divider()


            st.success(
                f"🙏 Namaste {name}"
            )


            st.caption(
                "Your Vedic astrology profile is ready."
            )


            # =================================================
            # KUNDLI
            # =================================================

            st.header(
                "🕉️ Your Kundli / Birth Chart"
            )


            fig = draw_kundli(
                chart
            )


            st.pyplot(
                fig
            )


            plt.close(
                fig
            )


            col1, col2 = st.columns(
                2
            )


            with col1:

                st.metric(
                    "⬆️ Lagna",
                    (
                        f"{RASHI_SYMBOLS[lagna_index]} "
                        f"{RASHIS[lagna_index]}"
                    )
                )


                st.caption(
                    RASHI_ENGLISH[
                        lagna_index
                    ]
                )


            with col2:

                st.metric(
                    "🌙 Janma Rashi",
                    (
                        f"{RASHI_SYMBOLS[moon_index]} "
                        f"{RASHIS[moon_index]}"
                    )
                )


                st.caption(
                    RASHI_ENGLISH[
                        moon_index
                    ]
                )


            st.caption(
                "Vedic Sidereal Astrology • Lahiri Ayanamsha"
            )


            # =================================================
            # DAILY RASHIFAL
            # =================================================

            st.divider()


            st.header(
                "🔮 आज का राशिफल"
            )


            st.subheader(
                "Today's Rashifal"
            )


            st.caption(
                today.strftime(
                    "%d %B %Y"
                )
            )


            st.markdown(
                f"## "
                f"{RASHI_SYMBOLS[moon_index]} "
                f"{RASHI_HINDI[moon_index]} राशि"
            )


            st.subheader(
                "🌟 Overall"
            )


            st.write(
                rashifal[
                    "overall"
                ]
            )


            st.subheader(
                "💼 Career & Money"
            )


            st.write(
                rashifal[
                    "career"
                ]
            )


            st.subheader(
                "❤️ Love & Family"
            )


            st.write(
                rashifal[
                    "relationship"
                ]
            )


            st.subheader(
                "🧘 Wellbeing"
            )


            st.write(
                rashifal[
                    "wellbeing"
                ]
            )


            st.subheader(
                "🙏 Today's Advice"
            )


            st.write(
                rashifal[
                    "advice"
                ]
            )


            # =================================================
            # LUCKY GUIDE
            # =================================================

            st.divider()


            st.header(
                "✨ Today's Lucky Guide"
            )


            lucky_col1, lucky_col2 = st.columns(
                2
            )


            with lucky_col1:

                st.metric(
                    "🎨 Lucky Colour",
                    rashifal[
                        "colour"
                    ]
                )


            with lucky_col2:

                st.metric(
                    "🔢 Lucky Number",
                    rashifal[
                        "number"
                    ]
                )


            st.write("")


            st.info(
                "Daily Rashifal, Lucky Colour and Lucky Number "
                "are traditional astrology-style interpretations "
                "for general guidance and entertainment."
            )


# =========================================================
# FOOTER
# =========================================================

st.divider()


st.markdown(
    "### 🔮 Astro_KD"
)


st.caption(
    "Ancient Wisdom • Modern Experience"
)