import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

type Language = "en" | "te" | "sa";

const copy = {
  en: {
    nav: ["Home", "About", "Features", "Schools", "Resources", "Contact"],
    login: "Login",
    started: "Get started",
    language: "Language",
    eyebrow: "Charity Organisation · Education & Technology Services",
    hero: "Supporting Schools Through Education, Digital Solutions, Cloud & AI Services.",
    summary:
      "Balamukundam is a charity organisation founded with a commitment to education, cultural values and service to children and communities.",
    detail:
      "Along with our educational services, we provide software, digital solutions, cloud services and AI services to support school administrations and their day-to-day needs.",
    highlight:
      "Educational Services · School Software · Digital Solutions · Cloud Services · AI Services",
    explore: "Explore Balamukundam",
    contactTeam: "Contact our team",
    overview: "School overview",
    introLabel: "EDUCATION, SOFTWARE & TECHNOLOGY SERVICES",
    introTitle: "Education and Technology in the Service of Schools",
    intro: [
      "Balamukundam began with a commitment to help children learn our language, culture and values. Along with these educational services, we offer practical software and technology solutions that help schools manage their work and support their communities.",
      "From school software and digital solutions to cloud and AI services, Balamukundam supports school administrations with solutions that can adapt to their needs.",
    ],
    featuresLabel: "WHAT WE BUILD",
    featuresTitle: "Software That Supports Every Part of School Life",
    featuresLead:
      "Digital, cloud and AI solutions designed to support school administration, teaching, learning and day-to-day operations.",
    features: [
      [
        "Administration",
        "A clear place to manage users, students, teachers, classes and school information.",
      ],
      [
        "Teaching",
        "Help teachers manage classes, record attendance and share classwork and homework.",
      ],
      [
        "Student learning",
        "Give students one convenient place for lessons, homework and learning resources.",
      ],
      [
        "Registration",
        "Keep student and teacher registration details organised and easy to review.",
      ],
      [
        "Attendance",
        "Record class attendance quickly and keep an accurate history.",
      ],
      [
        "Homework",
        "Create, share and follow homework activities across each class.",
      ],
      [
        "Learning resources",
        "Bring lesson materials and useful educational links together.",
      ],
      [
        "Educational activities",
        "Make learning more engaging with resources and selected activities.",
      ],
    ],
    communityLabel: "DESIGNED FOR YOUR SCHOOL COMMUNITY",
    communityTitle: "Technology for Administrators, Teachers and Students.",
    roles: [
      [
        "Administrators",
        "Manage users, students, teachers, classes and overall school activities.",
      ],
      [
        "Teachers",
        "Manage classes, record attendance, assign homework and provide learning resources.",
      ],
      [
        "Students",
        "Follow lessons, complete homework, access resources and enjoy educational activities.",
      ],
    ],
    flow: ["Administrators", "Teachers", "Students"],
    flexibleLabel: "BUILT AROUND YOUR NEEDS",
    flexibleTitle: "Solutions for Different Kinds of Schools",
    flexibleLead:
      "Every school is different. Balamukundam supports a wide range of educational organisations and specialist learning programmes.",
    schools: [
      [
        "Academic schools",
        "Manage classes, attendance, homework and learning resources.",
      ],
      [
        "Language schools",
        "Support language learning with lessons, activities and resources.",
      ],
      [
        "Music schools",
        "Organise students, teachers, classes and learning activities.",
      ],
      [
        "Art schools",
        "Support creative education with flexible class and student management.",
      ],
      [
        "Specialist centres",
        "Adapt the platform to your school’s teaching and administration needs.",
      ],
    ],
    benefitsLabel: "OUR APPROACH",
    benefitsTitle: "Practical Software. Flexible Solutions. Ongoing Support.",
    benefits: [
      ["Simple", "Easy-to-understand dashboards and organised information."],
      [
        "Connected",
        "Bring administration, teaching and student activities together.",
      ],
      [
        "Flexible",
        "Suitable for different schools and educational programmes.",
      ],
      [
        "Engaging",
        "Support learning through homework, lessons, resources and activities.",
      ],
    ],
    readyLabel: "LET’S BUILD FOR YOUR SCHOOL",
    readyTitle:
      "Looking for Software, Digital, Cloud or AI Support for Your School?",
    readyText:
      "Whether your school administration needs software, digital solutions, cloud services, AI services or ongoing technology support, Balamukundam is here to serve and support your school.",
    adminContact: "Contact our school services team",
    findSchool: "Find your school",
  },
  te: {
    nav: [
      "హోమ్",
      "మా గురించి",
      "ఫీచర్లు",
      "పాఠశాలలు",
      "వనరులు",
      "సంప్రదించండి",
    ],
    login: "లాగిన్",
    started: "ప్రారంభించండి",
    language: "భాష",
    eyebrow: "ధార్మిక సంస్థ · విద్యా & సాంకేతిక సేవలు",
    hero: "విద్య, డిజిటల్ పరిష్కారాలు, క్లౌడ్ & AI సేవల ద్వారా పాఠశాలలకు సేవ చేస్తున్నాము.",
    summary:
      "బాలముకుందం మన చిన్నారులకు మన భాష, సంస్కృతి మరియు విలువలను నేర్పాలనే సంకల్పంతో ప్రారంభమైన ధార్మిక సంస్థ.",
    detail:
      "విద్యా సేవలతో పాటు, పాఠశాల పరిపాలనకు అవసరమైన సాఫ్ట్‌వేర్, డిజిటల్ పరిష్కారాలు, క్లౌడ్ సేవలు మరియు AI సేవలను అందిస్తూ పాఠశాలలకు సేవ చేస్తున్నాము.",
    highlight:
      "విద్యా సేవలు · పాఠశాల సాఫ్ట్‌వేర్ · డిజిటల్ పరిష్కారాలు · క్లౌడ్ సేవలు · AI సేవలు",
    explore: "బాలముకుందాన్ని అన్వేషించండి",
    contactTeam: "మా బృందాన్ని సంప్రదించండి",
    overview: "పాఠశాల అవలోకనం",
    introLabel: "విద్య, సాఫ్ట్‌వేర్ & సాంకేతిక సేవలు",
    introTitle: "పాఠశాలల సేవలో విద్య మరియు సాంకేతికత",
    intro: [
      "మన చిన్నారులకు మన భాష, సంస్కృతి మరియు విలువలను నేర్పాలనే సంకల్పంతో బాలముకుందం ప్రారంభమైంది. ఈ విద్యా సేవలతో పాటు, పాఠశాలల నిర్వహణకు మరియు వారి సమాజానికి మద్దతుగా ఉపయోగకరమైన సాఫ్ట్‌వేర్, డిజిటల్ పరిష్కారాలను అందిస్తున్నాము.",
      "పాఠశాల సాఫ్ట్‌వేర్, డిజిటల్ పరిష్కారాల నుంచి క్లౌడ్ మరియు AI సేవల వరకు, పాఠశాల పరిపాలన అవసరాలకు అనుగుణంగా బాలముకుందం సేవలను అందిస్తుంది.",
    ],
    featuresLabel: "మేము రూపొందించేవి",
    featuresTitle: "పాఠశాల జీవితంలోని ప్రతి భాగానికి తోడ్పడే సాఫ్ట్‌వేర్",
    featuresLead:
      "పాఠశాల పరిపాలన, బోధన, అభ్యాసం మరియు రోజువారీ కార్యకలాపాలకు మద్దతు ఇచ్చే డిజిటల్, క్లౌడ్ మరియు AI పరిష్కారాలు.",
    features: [
      [
        "నిర్వహణ",
        "వినియోగదారులు, విద్యార్థులు, ఉపాధ్యాయులు, తరగతులు మరియు పాఠశాల సమాచారాన్ని నిర్వహించడానికి ఒక స్పష్టమైన స్థలం.",
      ],
      [
        "బోధన",
        "ఉపాధ్యాయులు తరగతులను నిర్వహించడానికి, హాజరును నమోదు చేయడానికి, తరగతి పని మరియు హోమ్‌వర్క్ పంచుకోవడానికి సహాయం.",
      ],
      [
        "విద్యార్థి అభ్యాసం",
        "పాఠాలు, హోమ్‌వర్క్ మరియు అభ్యాస వనరుల కోసం విద్యార్థులకు ఒక అనుకూలమైన స్థలం.",
      ],
      [
        "నమోదు",
        "విద్యార్థి, ఉపాధ్యాయుల నమోదు వివరాలను క్రమబద్ధంగా, సమీక్షించడానికి సులభంగా ఉంచండి.",
      ],
      ["హాజరు", "తరగతి హాజరును త్వరగా నమోదు చేసి, ఖచ్చితమైన చరిత్రను ఉంచండి."],
      [
        "హోమ్‌వర్క్",
        "ప్రతి తరగతిలో హోమ్‌వర్క్ కార్యకలాపాలను సృష్టించండి, పంచుకోండి, అనుసరించండి.",
      ],
      [
        "అభ్యాస వనరులు",
        "పాఠ్య సామగ్రి, ఉపయోగకరమైన విద్యా లింకులను ఒకచోట చేర్చండి.",
      ],
      [
        "విద్యా కార్యకలాపాలు",
        "వనరులు, ఎంపిక చేసిన కార్యకలాపాల ద్వారా అభ్యాసాన్ని మరింత ఆకర్షణీయంగా చేయండి.",
      ],
    ],
    communityLabel: "మీ పాఠశాల సమాజం కోసం",
    communityTitle:
      "నిర్వాహకులు, ఉపాధ్యాయులు మరియు విద్యార్థుల కోసం టెక్నాలజీ.",
    roles: [
      [
        "నిర్వాహకులు",
        "వినియోగదారులు, విద్యార్థులు, ఉపాధ్యాయులు, తరగతులు, మొత్తం పాఠశాల కార్యకలాపాలను నిర్వహించండి.",
      ],
      [
        "ఉపాధ్యాయులు",
        "తరగతులను నిర్వహించండి, హాజరును నమోదు చేయండి, హోమ్‌వర్క్ ఇవ్వండి, అభ్యాస వనరులను అందించండి.",
      ],
      [
        "విద్యార్థులు",
        "పాఠాలను అనుసరించండి, హోమ్‌వర్క్ పూర్తి చేయండి, వనరులను పొందండి, విద్యా కార్యకలాపాలను ఆస్వాదించండి.",
      ],
    ],
    flow: ["నిర్వాహకులు", "ఉపాధ్యాయులు", "విద్యార్థులు"],
    flexibleLabel: "మీ అవసరాలకు అనుగుణంగా",
    flexibleTitle: "వివిధ రకాల పాఠశాలల కోసం పరిష్కారాలు",
    flexibleLead:
      "ప్రతి పాఠశాల భిన్నమైనది. బాలముకుందం విస్తృత విద్యా సంస్థలు, ప్రత్యేక అభ్యాస కార్యక్రమాలకు మద్దతు ఇస్తుంది.",
    schools: [
      [
        "విద్యా పాఠశాలలు",
        "తరగతులు, హాజరు, హోమ్‌వర్క్, అభ్యాస వనరులను నిర్వహించండి.",
      ],
      [
        "భాషా పాఠశాలలు",
        "పాఠాలు, కార్యకలాపాలు, వనరులతో భాషా అభ్యాసానికి మద్దతు ఇవ్వండి.",
      ],
      [
        "సంగీత పాఠశాలలు",
        "విద్యార్థులు, ఉపాధ్యాయులు, తరగతులు, అభ్యాస కార్యకలాపాలను నిర్వహించండి.",
      ],
      [
        "కళా పాఠశాలలు",
        "సౌకర్యవంతమైన తరగతి, విద్యార్థి నిర్వహణతో సృజనాత్మక విద్యకు మద్దతు ఇవ్వండి.",
      ],
      [
        "ప్రత్యేక కేంద్రాలు",
        "మీ పాఠశాల బోధన, నిర్వహణ అవసరాలకు వేదికను అనుకూలీకరించండి.",
      ],
    ],
    benefitsLabel: "మా విధానం",
    benefitsTitle: "ఉపయోగకరమైన సాఫ్ట్‌వేర్. అనువైన పరిష్కారాలు. నిరంతర మద్దతు.",
    benefits: [
      ["సరళమైనది", "సులభంగా అర్థమయ్యే డ్యాష్‌బోర్డులు, క్రమబద్ధమైన సమాచారం."],
      [
        "అనుసంధానితమైనది",
        "నిర్వహణ, బోధన, విద్యార్థి కార్యకలాపాలను ఒకచోట చేర్చండి.",
      ],
      ["సౌకర్యవంతమైనది", "విభిన్న పాఠశాలలు, విద్యా కార్యక్రమాలకు అనుకూలం."],
      [
        "ఆకర్షణీయమైనది",
        "హోమ్‌వర్క్, పాఠాలు, వనరులు, కార్యకలాపాల ద్వారా అభ్యాసానికి మద్దతు ఇవ్వండి.",
      ],
    ],
    readyLabel: "మీ పాఠశాల కోసం నిర్మిద్దాం",
    readyTitle:
      "మీ పాఠశాలకు సాఫ్ట్‌వేర్, డిజిటల్, క్లౌడ్ లేదా AI సేవలు కావాలా?",
    readyText:
      "మీ పాఠశాల పరిపాలనకు సాఫ్ట్‌వేర్, డిజిటల్ పరిష్కారాలు, క్లౌడ్ సేవలు, AI సేవలు లేదా నిరంతర సాంకేతిక మద్దతు అవసరమైనా, బాలముకుందం మీ పాఠశాలకు సేవ చేయడానికి మరియు మద్దతు ఇవ్వడానికి సిద్ధంగా ఉంది.",
    adminContact: "మా పాఠశాల సేవల బృందాన్ని సంప్రదించండి",
    findSchool: "మీ పాఠశాలను కనుగొనండి",
  },
  sa: {
    nav: [
      "मुखपृष्ठम्",
      "अस्माकम् विषये",
      "विशेषताः",
      "विद्यालयाः",
      "संसाधनानि",
      "सम्पर्कः",
    ],
    login: "प्रवेशः",
    started: "आरभत",
    language: "भाषा",
    eyebrow: "धार्मिक-संस्था · शैक्षणिक-तन्त्रज्ञानसेवाः",
    hero: "शिक्षया, डिजिटल-समाधानैः, क्लाउड्-सेवाभिः, AI-सेवाभिश्च विद्यालयानां सेवां कुर्मः।",
    summary:
      "बालमुकुन्दं बालकेभ्यः स्वभाषां संस्कृतिं च शिक्षयितुं सङ्कल्पेन प्रारब्धा धार्मिक-संस्था अस्ति।",
    detail:
      "शैक्षणिक-सेवाभिः सह विद्यालय-प्रशासनस्य आवश्यकतानुसारं सॉफ्टवेयर-सेवाः, डिजिटल-समाधानानि, क्लाउड्-सेवाः, AI-सेवाश्च प्रदद्मः।",
    highlight:
      "शैक्षणिक-सेवाः · विद्यालय-सॉफ्टवेयरम् · डिजिटल-समाधानानि · क्लाउड्-सेवाः · AI-सेवाः",
    explore: "बालमुकुन्दम् अन्विष्यताम्",
    contactTeam: "अस्माकं दलं सम्पर्कयत",
    overview: "विद्यालयस्य अवलोकनम्",
    introLabel: "शिक्षा, सॉफ्टवेयर-तन्त्रज्ञान-सेवाश्च",
    introTitle: "विद्यालयानां सेवायां शिक्षा तन्त्रज्ञानं च",
    intro: [
      "बालकेभ्यः स्वभाषां संस्कृतिं च शिक्षयितुं सङ्कल्पेन बालमुकुन्दं प्रारब्धम्। एताभिः शैक्षणिक-सेवाभिः सह विद्यालय-प्रशासनस्य समुदायस्य च समर्थनाय व्यावहारिकं सॉफ्टवेयरं डिजिटल-समाधानानि च प्रदद्मः।",
      "विद्यालय-सॉफ्टवेयरात् डिजिटल-समाधानेभ्यः क्लाउड्-सेवाभ्यः AI-सेवाभ्यश्च आरभ्य, विद्यालय-प्रशासनस्य आवश्यकतानुसारं बालमुकुन्दं सेवाः प्रददाति।",
    ],
    featuresLabel: "वयं यानि निर्मीमः",
    featuresTitle: "विद्यालयजीवनस्य सर्वेषां भागानां समर्थनाय सॉफ्टवेयरम्",
    featuresLead:
      "विद्यालय-प्रशासनस्य, पाठनस्य, अध्ययनस्य, दैनिक-कार्याणां च समर्थनाय निर्मितानि डिजिटल, क्लाउड्, AI-समाधानानि।",
    features: [
      [
        "प्रशासनम्",
        "प्रयोक्तॄन्, छात्रान्, अध्यापकान्, कक्ष्याः विद्यालय-विवराणि च प्रबन्धयितुं स्पष्टं स्थानम्।",
      ],
      [
        "पाठनम्",
        "अध्यापकान् कक्ष्याः प्रबन्धयितुं, उपस्थितिं लेखयितुं, कक्ष्या-कार्यं गृहकार्यं च साझां कर्तुं साहाय्यम्।",
      ],
      [
        "छात्र-अध्ययनम्",
        "पाठानां, गृहकार्यस्य, अध्ययन-संसाधनानां च कृते छात्रेभ्यः एकं सुविधाजनकं स्थानम्।",
      ],
      [
        "पञ्जीकरणम्",
        "छात्र-अध्यापक-पञ्जीकरण-विवराणि सुव्यवस्थितानि समीक्षितुं सरलानि च स्थापयत।",
      ],
      [
        "उपस्थितिः",
        "कक्ष्या-उपस्थितिं शीघ्रं लेखयत, यथार्थं इतिहासं च स्थापयत।",
      ],
      [
        "गृहकार्यम्",
        "प्रत्येक-कक्ष्यायां गृहकार्य-क्रियाः रचयत, साझां कुर्वन्तु, अनुसरत।",
      ],
      [
        "अध्ययन-संसाधनानि",
        "पाठ्य-सामग्री उपयोगी-शैक्षणिक-सम्पर्कांश्च एकत्र आनयत।",
      ],
      [
        "शैक्षणिक-क्रियाः",
        "संसाधनैः चयनित-क्रियाभिः च अध्ययनम् अधिकं रोचकं कुर्वन्तु।",
      ],
    ],
    communityLabel: "भवतः विद्यालय-समुदायाय",
    communityTitle: "प्रशासकेभ्यः, अध्यापकेभ्यः, छात्रेभ्यश्च तन्त्रज्ञानम्।",
    roles: [
      [
        "प्रशासकाः",
        "प्रयोक्तॄन्, छात्रान्, अध्यापकान्, कक्ष्याः समग्र-विद्यालय-क्रियाः च प्रबन्धयन्तु।",
      ],
      [
        "अध्यापकाः",
        "कक्ष्याः प्रबन्धयन्तु, उपस्थितिं लेखयन्तु, गृहकार्यं ददतु, अध्ययन-संसाधनानि च प्रददतु।",
      ],
      [
        "छात्राः",
        "पाठान् अनुसरन्तु, गृहकार्यं पूरयन्तु, संसाधनानि प्राप्नुवन्तु, शैक्षणिक-क्रियाः च अनुभवन्तु।",
      ],
    ],
    flow: ["प्रशासकाः", "अध्यापकाः", "छात्राः"],
    flexibleLabel: "भवतः आवश्यकतानुसारम्",
    flexibleTitle: "विविध-प्रकारस्य विद्यालयेभ्यः समाधानानि",
    flexibleLead:
      "प्रत्येकं विद्यालयं भिन्नम् अस्ति। बालमुकुन्दम् विविध-शैक्षणिक-संस्थानां विशेष-अध्ययन-कार्यक्रमाणां च समर्थनं करोति।",
    schools: [
      [
        "शैक्षणिक-विद्यालयाः",
        "कक्ष्याः, उपस्थितिः, गृहकार्यम्, अध्ययन-संसाधनानि च प्रबन्धयत।",
      ],
      [
        "भाषा-विद्यालयाः",
        "पाठैः, क्रियाभिः, संसाधनैः च भाषा-अध्ययनस्य समर्थनं कुर्वन्तु।",
      ],
      [
        "सङ्गीत-विद्यालयाः",
        "छात्रान्, अध्यापकान्, कक्ष्याः, अध्ययन-क्रियाः च व्यवस्थिताः कुर्वन्तु।",
      ],
      [
        "कला-विद्यालयाः",
        "लचीलेन कक्ष्या-छात्र-प्रबन्धनेन सृजनात्मक-शिक्षायाः समर्थनं कुर्वन्तु।",
      ],
      [
        "विशेष-केन्द्राणि",
        "भवतः विद्यालयस्य पाठन-प्रशासन-आवश्यकतानुसारं मञ्चम् अनुकूलयत।",
      ],
    ],
    benefitsLabel: "अस्माकं दृष्टिकोणः",
    benefitsTitle:
      "व्यावहारिकं सॉफ्टवेयरम्। लचीले समाधानानि। निरन्तरं समर्थनम्।",
    benefits: [
      ["सरलम्", "सुगम्य-डैशबोर्डाः सुव्यवस्थितं च विवरणम्।"],
      ["सम्बद्धम्", "प्रशासनं, पाठनं, छात्र-क्रियाः च एकत्र आनयत।"],
      ["लचीलेन", "विविध-विद्यालयानां शैक्षणिक-कार्यक्रमाणां च योग्यः।"],
      [
        "रोचकम्",
        "गृहकार्येण, पाठैः, संसाधनैः, क्रियाभिः च अध्ययनस्य समर्थनं कुर्वन्तु।",
      ],
    ],
    readyLabel: "भवतः विद्यालयाय निर्मीमः",
    readyTitle:
      "भवतः विद्यालयाय सॉफ्टवेयर, डिजिटल, क्लाउड्, AI-सेवा वा आवश्यकाः सन्ति?",
    readyText:
      "भवतः विद्यालय-प्रशासनाय सॉफ्टवेयर-सेवाः, डिजिटल-समाधानानि, क्लाउड्-सेवाः, AI-सेवाः अथवा निरन्तरं तन्त्रज्ञान-सहाय्यं आवश्यकं भवतु, बालमुकुन्दं भवतः विद्यालयस्य सेवां कर्तुं समर्थनं च दातुं सज्जम् अस्ति।",
    adminContact: "अस्माकं विद्यालय-सेवा-दलं सम्पर्कयत",
    findSchool: "भवतः विद्यालयं अन्विष्यताम्",
  },
} as const;

const languageNames: Record<Language, string> = {
  en: "English",
  te: "తెలుగు",
  sa: "संस्कृतम्",
};

export default function PlatformHomePage() {
  const [menuOpen, setMenuOpen] = useState(false);
  const [language, setLanguage] = useState<Language>(
    () => (localStorage.getItem("bmk-language") as Language) || "en",
  );
  const closeMenu = () => setMenuOpen(false);
  const t = copy[language];

  useEffect(() => {
    localStorage.setItem("bmk-language", language);
    document.documentElement.lang =
      language === "te" ? "te" : language === "sa" ? "sa" : "en";
    document.documentElement.dataset.language = language;
  }, [language]);

  return (
    <div className="platform-page">
      <header className="platform-header">
        <Link className="platform-header-brand" to="/" onClick={closeMenu}>
          <img src="/logo.svg" alt="Balamukundam" width={46} height={46} />
          <span>Bālamukundam</span>
        </Link>
        <button
          className="platform-menu-toggle"
          type="button"
          aria-label={language === "en" ? "Toggle navigation menu" : t.nav[0]}
          aria-expanded={menuOpen}
          onClick={() => setMenuOpen((open) => !open)}
        >
          <span />
          <span />
          <span />
        </button>
        <nav
          className={`platform-nav ${menuOpen ? "open" : ""}`}
          aria-label="Platform navigation"
        >
          <a href="#home" onClick={closeMenu}>
            {t.nav[0]}
          </a>
          <a href="#about" onClick={closeMenu}>
            {t.nav[1]}
          </a>
          <a href="#features" onClick={closeMenu}>
            {t.nav[2]}
          </a>
          <Link to={`/schools?lang=${language}`} onClick={closeMenu}>
            {t.nav[3]}
          </Link>
          <a href="#contact" onClick={closeMenu}>
            {t.nav[5]}
          </a>
          <label className="platform-language">
            <span>{t.language}</span>
            <select
              value={language}
              onChange={(event) => setLanguage(event.target.value as Language)}
              aria-label={t.language}
            >
              {(Object.keys(languageNames) as Language[]).map((code) => (
                <option key={code} value={code}>
                  {languageNames[code]}
                </option>
              ))}
            </select>
          </label>
        </nav>
      </header>

      <main>
        <section className="platform-home-hero" id="home">
          <div className="platform-hero-copy">
            <p className="platform-eyebrow">{t.eyebrow}</p>
            <h1>{t.hero}</h1>
            <p className="platform-hero-summary">{t.summary}</p>
            <p className="platform-hero-detail">{t.detail}</p>
            <p className="platform-highlight">{t.highlight}</p>
            <div className="platform-actions">
              <Link
                className="platform-primary-action"
                to={`/schools?lang=${language}`}
              >
                {t.explore}
              </Link>
              <a className="platform-secondary-action" href="#contact">
                {t.contactTeam}
              </a>
            </div>
          </div>
          <div
            className="platform-hero-art"
            aria-label="Balamukundam learning platform"
          >
            <img src="/logo.svg" alt="" className="platform-hero-logo" />
            <div className="platform-dashboard-preview">
              <div className="preview-top">
                <span />
                <span />
                <span />
              </div>
              <div className="preview-body">
                <div className="preview-sidebar">
                  <i />
                  <i />
                  <i />
                  <i />
                </div>
                <div className="preview-content">
                  <b>{t.overview}</b>
                  <div className="preview-stat-row">
                    <span />
                    <span />
                    <span />
                  </div>
                  <div className="preview-lines">
                    <i />
                    <i />
                    <i />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="platform-section platform-introduction" id="about">
          <div>
            <p className="platform-section-label">{t.introLabel}</p>
            <h2>{t.introTitle}</h2>
          </div>
          <div className="platform-prose">
            <p>{t.intro[0]}</p>
            <p>{t.intro[1]}</p>
          </div>
        </section>

        <section className="platform-section" id="features">
          <div className="platform-section-heading centered">
            <p className="platform-section-label">{t.featuresLabel}</p>
            <h2>{t.featuresTitle}</h2>
            <p>{t.featuresLead}</p>
          </div>
          <div className="platform-feature-grid">
            {t.features.map(([title, description], index) => (
              <article className="platform-feature-card" key={title}>
                <span className="platform-feature-number">
                  {String(index + 1).padStart(2, "0")}
                </span>
                <h3>{title}</h3>
                <p>{description}</p>
              </article>
            ))}
          </div>
        </section>

        <section className="platform-section platform-role-section">
          <div className="platform-section-heading centered">
            <p className="platform-section-label">{t.communityLabel}</p>
            <h2>{t.communityTitle}</h2>
          </div>
          <div className="platform-role-grid">
            {t.roles.map(([title, description], index) => (
              <article key={title}>
                <span>{String(index + 1).padStart(2, "0")}</span>
                <h3>{title}</h3>
                <p>{description}</p>
              </article>
            ))}
          </div>
          <p className="platform-community-flow">
            {t.flow[0]} <b>→</b> {t.flow[1]} <b>→</b> {t.flow[2]}
          </p>
        </section>

        <section className="platform-section platform-school-section">
          <div className="platform-section-heading">
            <p className="platform-section-label">{t.flexibleLabel}</p>
            <h2>{t.flexibleTitle}</h2>
            <p>{t.flexibleLead}</p>
          </div>
          <div className="platform-school-grid">
            {t.schools.map(([title, description]) => (
              <article key={title}>
                <h3>{title}</h3>
                <p>{description}</p>
              </article>
            ))}
          </div>
        </section>

        <section className="platform-section platform-benefits" id="resources">
          <div className="platform-section-heading">
            <p className="platform-section-label">{t.benefitsLabel}</p>
            <h2>{t.benefitsTitle}</h2>
          </div>
          <div className="platform-benefit-grid">
            {t.benefits.map(([title, description]) => (
              <article key={title}>
                <h3>{title}</h3>
                <p>{description}</p>
              </article>
            ))}
          </div>
        </section>

        <section className="platform-contact" id="contact">
          <div>
            <p className="platform-section-label">{t.readyLabel}</p>
            <h2>{t.readyTitle}</h2>
            <p>{t.readyText}</p>
          </div>
          <address className="platform-contact-details">
            <span>{t.adminContact}</span>
            <div className="platform-contact-numbers">
              <a href="tel:+447415862152">+44 7415 862152</a>
              <a href="tel:+447872644407">+44 7872 644407</a>
              <a href="tel:+447812994964">+44 7812 994964</a>
              <a href="tel:+447809564959">+44 7809 564959</a>
            </div>
          </address>
        </section>
      </main>

      <footer className="platform-footer">
        <span>© {new Date().getFullYear()} Balamukundam</span>
        <Link to={`/schools?lang=${language}`}>{t.findSchool}</Link>
      </footer>
    </div>
  );
}
