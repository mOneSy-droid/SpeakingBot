# University partnership / education consulting speech uchun tayyorlangan kontent
# 4 haftalik dastur: har hafta yangi mavzu ustida ishlaymiz

VOCAB_WEEKS = {
    1: [  # Hafta 1: Tanishtiruv va umumiy partnership so'zlari
        {"word": "partnership", "translation": "hamkorlik", "example": "We are here to discuss a potential partnership between our organizations."},
        {"word": "collaboration", "translation": "hamkorlik, birgalikda ishlash", "example": "This collaboration would benefit students from both countries."},
        {"word": "memorandum of understanding (MoU)", "translation": "hamkorlik memorandumi", "example": "We would like to propose signing a memorandum of understanding."},
        {"word": "stakeholder", "translation": "manfaatdor tomon", "example": "All stakeholders will benefit from this agreement."},
        {"word": "delegation", "translation": "delegatsiya", "example": "Our delegation is honored to visit your campus today."},
        {"word": "on behalf of", "translation": "nomidan", "example": "I am speaking on behalf of EduVisa Consulting."},
        {"word": "outreach", "translation": "aloqa o'rnatish, tashqi faoliyat", "example": "Our outreach program connects students with international universities."},
        {"word": "mutual benefit", "translation": "o'zaro manfaat", "example": "This agreement is designed for mutual benefit."},
    ],
    2: [  # Hafta 2: Ta'lim tizimi va dastur so'zlari
        {"word": "curriculum", "translation": "o'quv dasturi", "example": "The curriculum is designed to meet international standards."},
        {"word": "accreditation", "translation": "akkreditatsiya", "example": "The program holds full accreditation from the ministry of education."},
        {"word": "scholarship", "translation": "stipendiya", "example": "We are seeking scholarship opportunities for our students."},
        {"word": "tuition fee", "translation": "o'qish to'lovi", "example": "The tuition fee covers accommodation as well."},
        {"word": "admission criteria", "translation": "qabul mezonlari", "example": "Could you clarify the admission criteria for international applicants?"},
        {"word": "exchange program", "translation": "almashinuv dasturi", "example": "We hope to establish a student exchange program."},
        {"word": "enrollment", "translation": "ro'yxatdan o'tish", "example": "Enrollment numbers have grown steadily over the past year."},
        {"word": "faculty", "translation": "professor-o'qituvchilar tarkibi", "example": "Your faculty has an excellent international reputation."},
    ],
    3: [  # Hafta 3: Biznes va muzokara so'zlari
        {"word": "proposal", "translation": "taklif", "example": "Let me walk you through our proposal in detail."},
        {"word": "framework", "translation": "asos, doira", "example": "This framework outlines the responsibilities of each party."},
        {"word": "feasibility", "translation": "amalga oshirish imkoniyati", "example": "We have already studied the feasibility of this project."},
        {"word": "timeline", "translation": "vaqt jadvali", "example": "Our proposed timeline spans the next twelve months."},
        {"word": "milestone", "translation": "muhim bosqich", "example": "The first milestone would be signing the agreement by September."},
        {"word": "logistics", "translation": "logistika", "example": "We will handle all logistics for student placement."},
        {"word": "compliance", "translation": "talablarga muvofiqlik", "example": "All documents are in full compliance with local regulations."},
        {"word": "track record", "translation": "faoliyat tarixi, tajriba", "example": "We have a strong track record of placing students successfully."},
    ],
    4: [  # Hafta 4: Yakuniy so'zlar va yopilish
        {"word": "envision", "translation": "tasavvur qilmoq, ko'z oldiga keltirmoq", "example": "We envision this partnership growing over the coming years."},
        {"word": "commitment", "translation": "sodiqlik, majburiyat", "example": "Our commitment is to support every student until graduation."},
        {"word": "long-term", "translation": "uzoq muddatli", "example": "We are looking for a long-term relationship, not a one-time project."},
        {"word": "in conclusion", "translation": "xulosa qilib aytganda", "example": "In conclusion, we believe this partnership serves both institutions well."},
        {"word": "appreciate", "translation": "qadrlamoq", "example": "We truly appreciate the time you have given us today."},
        {"word": "follow up", "translation": "keyingi qadam, davom ettirish", "example": "We will follow up with a written proposal next week."},
        {"word": "look forward to", "translation": "intiqlik bilan kutmoq", "example": "We look forward to hearing your feedback."},
        {"word": "on the same page", "translation": "bir fikrda bo'lish", "example": "I want to make sure we are on the same page before we proceed."},
    ],
}

STRUCTURES = [
    {
        "pattern": "We are delighted / pleased to ___",
        "explanation": "Rasmiy taqdimotni boshlash uchun ishlatiladi.",
        "example": "We are delighted to introduce our organization to you today.",
    },
    {
        "pattern": "This partnership would enable ___ to ___",
        "explanation": "Hamkorlikning natijasini tushuntirish uchun.",
        "example": "This partnership would enable our students to access world-class education.",
    },
    {
        "pattern": "Looking ahead, we envision ___",
        "explanation": "Kelajakdagi rejalarni tasvirlash uchun.",
        "example": "Looking ahead, we envision sending fifty students annually.",
    },
    {
        "pattern": "In terms of numbers, ___",
        "explanation": "Statistik ma'lumot keltirishdan oldin ishlatiladi.",
        "example": "In terms of numbers, we placed over 200 students last year.",
    },
    {
        "pattern": "To address your question, ___",
        "explanation": "Savolga javob berishni boshlash uchun (rasmiy).",
        "example": "To address your question, our fee structure is fully transparent.",
    },
    {
        "pattern": "What sets us apart is ___",
        "explanation": "Raqobatchilardan farqni ta'kidlash uchun.",
        "example": "What sets us apart is our personalized approach to every student.",
    },
    {
        "pattern": "We would be happy to ___",
        "explanation": "Taklif yoki yordam bildirish uchun muloyim shakl.",
        "example": "We would be happy to arrange a follow-up meeting.",
    },
    {
        "pattern": "If I may add, ___",
        "explanation": "Suhbat davomida qo'shimcha fikr bildirish uchun.",
        "example": "If I may add, this program has been very successful in Dubai as well.",
    },
    {
        "pattern": "That's a great question. ___",
        "explanation": "Kutilmagan savolga vaqt olish va hurmat bildirish uchun.",
        "example": "That's a great question. Let me explain how our screening process works.",
    },
    {
        "pattern": "In conclusion, ___",
        "explanation": "Nutqni yakunlash uchun.",
        "example": "In conclusion, we believe this is a mutually beneficial opportunity.",
    },
]

QA_TOPIC_HINT = (
    "a partnership meeting between an education consulting company from Uzbekistan "
    "(EduVisa Consulting) and a university in Malaysia, discussing student recruitment, "
    "scholarships, and long-term collaboration"
)

SPEAKING_PROMPTS = [
    "Introduce yourself and your organization in under one minute.",
    "Explain why this partnership would benefit both the university and Uzbek students.",
    "Describe your organization's track record in placing students abroad.",
    "Explain how scholarship opportunities would work for your students.",
    "Summarize the key numbers (students, universities, success rate) of your work so far.",
    "Explain what makes your organization different from other consulting agencies.",
    "Describe your vision for this partnership over the next three years.",
    "Give a one-minute closing statement thanking the panel and expressing hope for collaboration.",
]

