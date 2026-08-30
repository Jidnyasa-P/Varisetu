/* ==================== VariSetu i18n Engine ====================
   Lightweight EN/MR toggle. Add data-i18n="key" to any element's
   text, or data-i18n-placeholder="key" for input placeholders.
   Default language on first load = English.
================================================================= */

const VARISETU_TRANSLATIONS = {
  en: {
    officerLogin: "Officer Login",
    publicPortalBtn: "Public Pilgrim Portal & Helplines",
    commandCenterAccess: "COMMAND CENTER ACCESS",
    emailLabel: "Official Email / Officer ID",
    passwordLabel: "Password",
    signIn: "SIGN IN",
    restrictedNote: "Authorised Personnel Only • Access Monitored",
    brandTaglinePublic: "Public Pilgrim Service Portal",
    brandSubtitle: "Government of Maharashtra • Shri Kshetra Pandharpur Ashadhi Wari",
    palkhiStatus: "PALKHI: APPROACHING WAKHRI",
    heroTitle: "Sant Tukaram Maharaj & Sant Dnyaneshwar Maharaj Palkhi Sohala 2026",
    heroLive: "Live Location: Wakhri Phata Junction (Km 184) • Moving smoothly towards Pandharpur Shrine",
    heroCount: "Estimated Pilgrim Count",
    routeMapTitle: "PILGRIMAGE ROUTE & HALT STATIONS MAP",
    routeMapStops: "Alandi → Saswad → Lonand → Wakhri → Pandharpur",
    weatherTitle: "PILGRIM HEALTH & HYDRATION ADVISORY",
    weatherAdvisory: "Advisory: Drink plenty of water. Free ORSL salt sachets & medical assistance are available at all 24 water points and 16 medical tents stationed along the highway.",
    helplineTitle: "EMERGENCY & HELPLINE NUMBERS",
    helplineActive: "24x7 ACTIVE",
    policeControl: "Police Control Room",
    ambulanceLabel: "Ambulance & Medical Emergency",
    lostFoundBooth: "Lost & Found Pilgrim Assistance Booth",
    tollFree: "Toll Free",
    vitthalDesk: "Shri Vitthal Mandir Samiti Control Desk",
    callNow: "CALL NOW",
    reportMissingTitle: "REPORT MISSING FAMILY MEMBER",
    reportMissingDesc: "Separated from your family or group in the crowd? Submit details and photos directly for instant AI matching across state CCTV cameras.",
    submitMissingBtn: "Submit Missing Person Report"
  },
  mr: {
    officerLogin: "अधिकारी लॉगिन",
    publicPortalBtn: "सार्वजनिक वारकरी पोर्टल व हेल्पलाइन",
    commandCenterAccess: "नियंत्रण कक्ष प्रवेश",
    emailLabel: "अधिकृत ईमेल / अधिकारी आयडी",
    passwordLabel: "पासवर्ड",
    signIn: "लॉगिन करा",
    restrictedNote: "केवळ अधिकृत कर्मचाऱ्यांसाठी • प्रवेशावर नजर ठेवली जाते",
    brandTaglinePublic: "सार्वजनिक वारकरी सेवा पोर्टल",
    brandSubtitle: "महाराष्ट्र शासन • श्री क्षेत्र पंढरपूर आषाढी वारी सोहळा",
    palkhiStatus: "पालखी: वाखरीकडे येत आहे",
    heroTitle: "संत तुकाराम महाराज व संत ज्ञानेश्वर महाराज पालखी सोहळा २०२६",
    heroLive: "सद्य स्थान: वाखरी फाटा जंक्शन (कि.मी. १८४) • पंढरपूरकडे सुरळीत वाटचाल",
    heroCount: "अंदाजे वारकरी संख्या",
    routeMapTitle: "वारी मार्ग व मुक्काम स्थानके नकाशा",
    routeMapStops: "आळंदी → सासवड → लोणंद → वाखरी → पंढरपूर",
    weatherTitle: "वारकरी आरोग्य व जलसंधारण सूचना",
    weatherAdvisory: "सूचना: भरपूर पाणी प्या. महामार्गावरील सर्व २४ पाणपोई व १६ वैद्यकीय केंद्रांवर मोफत ओआरएसएल पाकिटे व वैद्यकीय मदत उपलब्ध आहे.",
    helplineTitle: "आपत्कालीन व हेल्पलाइन क्रमांक",
    helplineActive: "२४x७ कार्यरत",
    policeControl: "पोलीस नियंत्रण कक्ष",
    ambulanceLabel: "रुग्णवाहिका व वैद्यकीय आपत्कालीन सेवा",
    lostFoundBooth: "हरवले-सापडले वारकरी मदत केंद्र",
    tollFree: "टोल फ्री",
    vitthalDesk: "श्री विठ्ठल मंदिर समिती नियंत्रण कक्ष",
    callNow: "आता कॉल करा",
    reportMissingTitle: "कुटुंबातील हरवलेल्या व्यक्तीची तक्रार नोंदवा",
    reportMissingDesc: "गर्दीत कुटुंबापासून किंवा गटापासून विभक्त झालात का? राज्यभरातील सीसीटीव्ही कॅमेऱ्यांद्वारे तात्काळ एआय शोधासाठी तपशील व छायाचित्रे सादर करा.",
    submitMissingBtn: "हरवलेल्या व्यक्तीची तक्रार नोंदवा"
  }
};

function applyLanguage(lang) {
  const dict = VARISETU_TRANSLATIONS[lang] || VARISETU_TRANSLATIONS.en;

  document.querySelectorAll("[data-i18n]").forEach((el) => {
    const key = el.getAttribute("data-i18n");
    if (dict[key] !== undefined) el.textContent = dict[key];
  });

  document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => {
    const key = el.getAttribute("data-i18n-placeholder");
    if (dict[key] !== undefined) el.setAttribute("placeholder", dict[key]);
  });

  document.documentElement.setAttribute("lang", lang === "mr" ? "mr" : "en");

  document.querySelectorAll(".lang-toggle-btn").forEach((btn) => {
    btn.textContent = lang === "mr" ? "English" : "मराठी";
    btn.setAttribute("data-current-lang", lang);
  });

  localStorage.setItem("varisetu_lang", lang);
}

function toggleLanguage() {
  const current = localStorage.getItem("varisetu_lang") || "en";
  applyLanguage(current === "en" ? "mr" : "en");
}

document.addEventListener("DOMContentLoaded", () => {
  // Default on load = English, unless the user previously chose Marathi.
  const saved = localStorage.getItem("varisetu_lang") || "en";
  applyLanguage(saved);

  document.querySelectorAll(".lang-toggle-btn").forEach((btn) => {
    btn.addEventListener("click", toggleLanguage);
  });
});
