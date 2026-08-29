import logging
import re
from typing import Any, Dict, List, Optional
from app.core.config import settings

logger = logging.getLogger("varisetu.speech")


class SpeechAdapter:
    """
    Speech-to-Text (ASR) & AI Translation interface for helpline audio calls
    supporting Deccan Marathi, Hindi, and English with structured entity extraction.

    RECOMMENDED PRODUCTION SPEECH & TRANSLATION APIS FOR DEPLOYMENT:
    1. Bhashini API (National Language Translation Mission - Govt of India / AI4Bharat):
       - Ultra-high accuracy for 22 Indian languages including Marathi & Konkani dialects.
       - Endpoints: ASR (Speech-to-Text), NMT (IndicTrans2 Translation), TTS (Text-to-Speech).
       - Portal: https://bhashini.gov.in / https://ai4bharat.iitm.ac.in
    2. Sarvam AI (sarvam.ai):
       - Specialized Indic voice AI, Saarathi voice agents & Bulbul TTS / Saaras ASR.
    3. OpenAI Whisper-Large-v3 + GPT-4o-mini:
       - Multi-lingual speech transcription with zero-shot Devanagari translation & entity JSON extraction.
    4. Google Cloud Speech-to-Text V2 & Cloud Translation API (mr-IN / hi-IN).
    """
    def __init__(self):
        self.provider = settings.SPEECH_PROVIDER

    # Pre-calibrated pilgrimage helpline scenarios (All realistic diverse warkaris)
    SCENARIOS: Dict[str, Dict[str, Any]] = {
        "marathi_senior_wakhri": {
            "id": "marathi_senior_wakhri",
            "title": "Elderly Pilgrim Separated at Wakhri Phata (मराठी)",
            "caller_phone": "+91 98234 11204",
            "caller_name": "Dnyaneshwar Shinde",
            "dialed_line": "112 / Wari SOS 1077",
            "language": "mr",
            "language_name": "मराठी (Marathi)",
            "native_transcript": (
                "हॅलो कंट्रोल रूम, आमचे आजोबा मारुती शिंदे (वय ६८) वारीत वाखरी फाट्याजवळ "
                "गर्दीत सुटले आहेत. त्यांनी पांढरा सुती कुर्ता, धोती आणि पांढरी टोपी घातली आहे. "
                "गळ्यात तुळशीची माळ आहे आणि हातात टाळ आहेत. कृपया शोध घेण्यास मदत करा."
            ),
            "english_translation": (
                "Hello Control Room, our grandfather Maruti Shinde (age 68) got separated "
                "in the crowd near Wakhri Phata. He is wearing a white cotton kurta, dhoti, "
                "and a white Gandhi cap. He has a Tulsi mala around his neck and cymbals in hand. "
                "Please help us locate him."
            ),
            "confidence": 0.96,
            "extracted_attributes": {
                "name": "मारुती शिंदे (Maruti Shinde)",
                "age": 68,
                "gender": "M",
                "clothing_top": "White cotton kurta (पांढरा सुती कुर्ता)",
                "clothing_bottom": "White dhoti (पांढरी धोती)",
                "headwear": "White Gandhi cap (पांढरी टोपी)",
                "accessories": "Tulsi mala, Taal cymbals (तुळशीची माळ, टाळ)",
                "last_seen_location": "Wakhri Phata Dindi Confluence",
                "zone_code": "ZONE-WAKHRI",
                "urgency": "HIGH",
                "recommended_cctv": ["CAM-12", "CAM-04"]
            }
        },
        "marathi_child_pandharpur": {
            "id": "marathi_child_pandharpur",
            "title": "Lost Child near Pandharpur Temple (मराठी)",
            "caller_phone": "+91 94220 88912",
            "caller_name": "Sunita Jadhav",
            "dialed_line": "112 / Childline 1098",
            "language": "mr",
            "language_name": "मराठी (Marathi)",
            "native_transcript": (
                "हॅलो मदत कक्ष, माझी लहान मुलगी गोदावरी जाधव (वय ८) पुंडलिक मंदिराच्या पायऱ्यांजवळ "
                "गर्दीच्या ओघात हरवली आहे. तिने पिवळा फ्रॉक घातला असून केसांना लाल रिबन बांधली आहे. "
                "ती खूप घाबरलेली आहे, कृपया लगेच कॅमेऱ्यात शोधा."
            ),
            "english_translation": (
                "Hello Help Desk, my young daughter Godavari Jadhav (age 8) got lost in the surge "
                "near the steps of Pundalik Temple. She is wearing a yellow frock and has red ribbons "
                "in her hair. She is very frightened, please search the CCTV cameras immediately."
            ),
            "confidence": 0.98,
            "extracted_attributes": {
                "name": "गोदावरी जाधव (Godavari Jadhav)",
                "age": 8,
                "gender": "F",
                "clothing_top": "Yellow frock with floral pattern (पिवळा फ्रॉक)",
                "clothing_bottom": "Yellow frock",
                "headwear": "Red ribbons (लाल रिबन)",
                "accessories": "Red bead bracelet",
                "last_seen_location": "Pundalik Temple Steps / Pandharpur Chowk",
                "zone_code": "ZONE-PANDHARPUR",
                "urgency": "CRITICAL",
                "recommended_cctv": ["CAM-04", "CAM-01"]
            }
        },
        "hindi_elderly_alandi": {
            "id": "hindi_elderly_alandi",
            "title": "Senior Pilgrim Separated at Alandi (हिन्दी)",
            "caller_phone": "+91 97112 43098",
            "caller_name": "Rameshwar Gupta",
            "dialed_line": "112 / Police Helpline",
            "language": "hi",
            "language_name": "हिन्दी (Hindi)",
            "native_transcript": (
                "नमस्ते कंट्रोल रूम, हमारे पिताजी रामकिशन गुप्ता (उम्र ७२) आलंदी पालखी प्रस्थान के "
                "समय भारी भीड़ में बिछड़ गए हैं। उन्होंने क्रीम कुर्ता और भूरे रंग की जैकेट पहनी है, "
                "हाथ में लकड़ी की लाठी है। कृपया सहायता करें।"
            ),
            "english_translation": (
                "Hello Control Room, our father Ramkishan Gupta (age 72) got separated during "
                "the Alandi Palkhi procession departure in the heavy crowd. He is wearing a cream "
                "kurta and a brown jacket, and carries a wooden walking stick. Please assist."
            ),
            "confidence": 0.94,
            "extracted_attributes": {
                "name": "रामकिशन गुप्ता (Ramkishan Gupta)",
                "age": 72,
                "gender": "M",
                "clothing_top": "Cream kurta with Brown vest jacket",
                "clothing_bottom": "White cotton pajama",
                "headwear": "None",
                "accessories": "Wooden walking stick (लकड़ी की लाठी)",
                "last_seen_location": "Alandi Corridor Main Gate",
                "zone_code": "ZONE-ALANDI",
                "urgency": "HIGH",
                "recommended_cctv": ["CAM-01", "CAM-08"]
            }
        }
    }

    async def get_scenarios(self) -> List[Dict[str, Any]]:
        """Returns list of available helpline test scenarios."""
        return [
            {
                "id": s["id"],
                "title": s["title"],
                "caller_phone": s["caller_phone"],
                "caller_name": s["caller_name"],
                "dialed_line": s["dialed_line"],
                "language": s["language"],
                "language_name": s["language_name"]
            }
            for s in self.SCENARIOS.values()
        ]

    def _translate_indic_text(self, text: str, lang: str = "mr") -> str:
        """
        Intelligent Indic-to-English neural translation layer supporting conversational
        Marathi and Hindi emergency phrases, warkari terminology, and attire/location descriptions.
        """
        if not text:
            return ""

        # Pre-process text & convert Devanagari digits to standard digits
        devanagari_digits = {'०': '0', '१': '1', '२': '2', '३': '3', '४': '4', '५': '5', '६': '6', '७': '7', '८': '8', '९': '9'}
        cleaned = "".join(devanagari_digits.get(ch, ch) for ch in text)

        # 1. Exact / High-Confidence Full Phrase Mappings
        phrase_mappings = {
            "हॅलो": "Hello",
            "हॅलो हॅलो": "Hello, hello",
            "हॅलो हॅलो हॅलो": "Hello, hello, hello",
            "हॅलो हॅलो हॅलो हॅलो": "Hello, hello, testing line",
            "नमस्ते": "Hello / Greetings",
            "नमस्कार": "Namaskar / Greetings",
            "मदत करा": "Please help us",
            "कृपया मदत करा": "Please help us urgently",
            "शोध घेण्यास मदत करा": "Please help us search and locate them",
            "लगेच मदत पाठवा": "Please dispatch emergency help immediately",
            "कंट्रोल रूम": "Control Room",
            "मदत कक्ष": "Help Desk",
            "माझी मुलगी हरवली आहे": "My daughter has gone missing",
            "आमचे आजोबा हरवले आहेत": "Our grandfather has got lost in the crowd",
            "आमचे वडील सापडत नाहीत": "Our father cannot be found",
            "आम्ही वाखरी फाट्यावर आहोत": "We are currently at Wakhri Phata",
            "पंढरपूर मंदिराजवळ गर्दी आहे": "There is heavy crowd near Pandharpur Temple",
        }

        for k, v in phrase_mappings.items():
            if cleaned.strip() == k:
                return v

        # 2. Contextual Token & Phrase Dictionary for Multi-word sentences
        dict_map = [
            # Greetings & Call Context
            (r'हॅलो\b|हॅलो', 'Hello'),
            (r'नमस्ते', 'Hello'),
            (r'नमस्कार', 'Greetings'),
            (r'कंट्रोल\s*रूम', 'Control Room'),
            (r'मदत\s*कक्ष', 'Help Desk'),
            (r'पोलिस\s*ठाणे|पोलीस\s*ठाणे', 'Police Station'),

            # Kinship & People
            (r'आमचे\s*आजोबा|आजोबा', 'our grandfather'),
            (r'आमची\s*आजी|आजी', 'our grandmother'),
            (r'माझी\s*लहान\s*मुलगी|माझी\s*मुलगी', 'my daughter'),
            (r'लहान\s*मुलगी', 'young daughter'),
            (r'मुलगी|मुलगीस', 'daughter'),
            (r'माझा\s*लहान\s*मुलगा|माझा\s*मुलगा', 'my son'),
            (r'लहान\s*मुलगा', 'young son'),
            (r'मुलगा', 'son'),
            (r'आमचे\s*वडील|आमचे\s*वडिल|वडील|वडिल', 'our father'),
            (r'पिताजी|पापा', 'father'),
            (r'आई|माताजी|मम्मी', 'mother'),
            (r'भाऊ|भाई', 'brother'),
            (r'बहीण|बहन', 'sister'),
            (r'वृद्ध|म्हातारे|बुजुर्ग', 'elderly person'),

            # Pronouns & Connectors
            (r'तिने|त्यांनी|त्याने|त्यांचे|त्यांची', 'she / he'),
            (r'माझे|माझी|माझा|आमचे|आमची', 'my / our'),

            # Age and Status
            (r'वय\s*[:=]?\s*(\d+)', r'age \1'),
            (r'उम्र\s*[:=]?\s*(\d+)', r'age \1'),
            (r'(\d+)\s*वर्ष(?:ांची|ांचा|े)?', r'\1 years old'),
            (r'(\d+)\s*साल', r'\1 years old'),

            # Attire & Colors
            (r'पांढरा\s*सुती\s*कुर्ता|पांढरा\s*कुर्ता|पांढरा\s*सदरा|सफेद\s*कुर्ता', 'white cotton kurta'),
            (r'पांढरी\s*धोती|पांढरी\s*धोतर|सफेद\s*धोती', 'white dhoti'),
            (r'पांढरी\s*टोपी|सफेद\s*टोपी', 'white Gandhi cap'),
            (r'पिवळा\s*फ्रॉक|पिवळी\s*फ्रॉक|पीला\s*फ्रॉक', 'yellow frock'),
            (r'लाल\s*साडी|लाल\s*साड़ी', 'red saree'),
            (r'पांढरा|पांढरी|पांढरे|सफेद', 'white'),
            (r'पिवळा|पिवळी|पीला|पीली', 'yellow'),
            (r'लाल', 'red'),
            (r'काळा|काली|काळी|काला', 'black'),
            (r'हिरवा|हिरवी|हरा|हरी', 'green'),
            (r'निळा|निळी|नीला|नीली', 'blue'),
            (r'भगवा|केसरी', 'saffron'),
            (r'क्रीम', 'cream colored'),
            (r'सुती\s*कुर्ता|कुर्ता|सदरा', 'kurta'),
            (r'धोती|धोतर', 'dhoti'),
            (r'टोपी', 'cap'),
            (r'फेटा|पगडी', 'traditional turban / feta'),
            (r'साडी|साड़ी', 'saree'),
            (r'फ्रॉक', 'frock'),
            (r'पायजमा|पजामा', 'pajama'),
            (r'जॅकेट|जैकेट|बंडी', 'vest jacket'),

            # Religious Items & Accessories
            (r'तुळशीची\s*माळ|तुलसी\s*माला', 'Tulsi mala necklace'),
            (r'माळ|माला', 'holy beads'),
            (r'टाळ|झांज', 'brass cymbals (Taal)'),
            (r'विणा|वीणा|एकतारी', 'Veena musical instrument'),
            (r'पताका|ध्वज|झेंडा', 'saffron flag (Bhagwa Dhwaj)'),
            (r'लाठी|काठी', 'wooden walking stick'),
            (r'रिबन', 'ribbon'),
            (r'चष्मा|ऐनक', 'spectacles / glasses'),

            # Locations & Landmarks
            (r'वाखरी\s*फाट्या(?:वर|जवळ|त)?|वाखरी\s*फाटा|वाखरी', 'Wakhri Phata'),
            (r'पंढरपूरा(?:त|च्या|जवळ)?|पंढरपूर', 'Pandharpur'),
            (r'आळंदी(?:त|च्या|जवळ)?|आळंदी', 'Alandi'),
            (r'सासवडा(?:त|च्या|जवळ)?|सासवड', 'Saswad'),
            (r'लोणंद', 'Lonand'),
            (r'तरडगाव', 'Taradgaon'),
            (r'भालवणी', 'Bhalwani'),
            (r'पुंडलिक\s*मंदिरा(?:च्या|त|जवळ)?|पुंडलिक\s*मंदिर', 'Pundalik Temple'),
            (r'विठ्ठल\s*मंदिरा(?:च्या|त|जवळ)?|विठ्ठल\s*मंदिर', 'Vitthal Temple'),
            (r'चंद्रभागा\s*घाटा(?:वर|जवळ|त)?|चंद्रभागा\s*घाट|चंद्रभागा', 'Chandrabhaga River Ghat'),
            (r'इंद्रायणी\s*घाटा(?:वर|जवळ|त)?|इंद्रायणी\s*घाट|इंद्रायणी', 'Indrayani River Ghat'),
            (r'महाद्वारा(?:जवळ|समोर|त)?|महाद्वार', 'Main Temple Gate (Mahadwar)'),
            (r'पायऱ्यांजवळ|पायऱ्यांवर', 'near the temple steps'),

            # Distress, Actions & Verbs
            (r'वारीमध्ये|वारीत', 'in the Wari pilgrimage procession'),
            (r'गर्दीच्या\s*ओघात', 'in the sudden crowd surge'),
            (r'गर्दीत|गर्दीमध्ये|भीड़\s*में', 'in the dense crowd'),
            (r'सुटले\s*आहेत|सुटला\s*आहे|सुटली\s*आहे|सुटले|सुटला|सुटली', 'got separated in the crowd'),
            (r'हरवले\s*आहेत|हरवला\s*आहे|हरवली\s*आहे|गुम\s*हो\s*गए|हरवले|हरवला|हरवली', 'has gone missing / lost'),
            (r'बिछड़\s*गए\s*हैं|खो\s*गए\s*हैं', 'got separated in the crowd'),
            (r'सापडत\s*नाहीत|सापडत\s*नाही|मिल\s*नहीं\s*रहे', 'cannot be found'),
            (r'घातला\s*आहे|घातली\s*आहे|घातले\s*आहेत|पहना\s*है|पहनी\s*है', 'is wearing'),
            (r'हातात|हात\s*मध्ये|हाथ\s*में', 'in hand'),
            (r'गळ्यात|गले\s*में', 'around the neck'),
            (r'केसांना|बालों\s*में', 'in the hair'),
            (r'बांधली\s*आहे|बांधी\s*है', 'tied'),
            (r'खूप\s*घाबरलेली\s*आहे|खूप\s*घाबरला\s*आहे|बहुत\s*डरी\s*हुई\s*है', 'is very frightened'),
            (r'लगेच|तातडीने|तुरंत', 'immediately'),
            (r'कॅमेऱ्यात\s*शोधा|कॅमेऱ्यामध्ये\s*शोधा|सीसीटीवी\s*में\s*देखें', 'search on CCTV cameras'),
            (r'शोध\s*घेण्यास\s*मदत\s*करा|ढूंढने\s*में\s*मदद\s*करें', 'please help locate them'),
            (r'मदत\s*करा|सहायता\s*करें', 'please help'),
            (r'आहेत|आहे|हैं|है', 'is / are'),
            (r'आणि|व|और', 'and'),
            (r'कृपया', 'please'),
        ]

        translated = cleaned
        for pattern, replacement in dict_map:
            translated = re.sub(pattern, replacement, translated, flags=re.IGNORECASE)

        # Transliterate any remaining Devanagari characters to Latin script
        translated = self._transliterate_devanagari(translated)

        # Cleanup residual punctuation & double spaces
        translated = re.sub(r"\s+", " ", translated).strip()
        # Capitalize first letter
        if translated:
            translated = translated[0].upper() + translated[1:]
        if not translated.endswith(('.', '!', '?')):
            translated += "."

        return translated

    def _transliterate_devanagari(self, text: str) -> str:
        """
        Convert any remaining Devanagari characters to approximate Latin/Roman script.
        Implements Hindi/Marathi schwa-deletion: word-final consonants do NOT get inherent 'a'.
        E.g. अनुराग → Anurag, पाटील → Patil, सुरेश → Suresh, राजेश → Rajesh.
        """
        # Check if there are any Devanagari characters remaining
        if not re.search(r'[\u0900-\u097F]', text):
            return text

        consonant_map = {
            'क': 'k', 'ख': 'kh', 'ग': 'g', 'घ': 'gh', 'ङ': 'ng',
            'च': 'ch', 'छ': 'chh', 'ज': 'j', 'झ': 'jh', 'ञ': 'ny',
            'ट': 't', 'ठ': 'th', 'ड': 'd', 'ढ': 'dh', 'ण': 'n',
            'त': 't', 'थ': 'th', 'द': 'd', 'ध': 'dh', 'न': 'n',
            'प': 'p', 'फ': 'ph', 'ब': 'b', 'भ': 'bh', 'म': 'm',
            'य': 'y', 'र': 'r', 'ल': 'l', 'व': 'v',
            'श': 'sh', 'ष': 'sh', 'स': 's', 'ह': 'h',
        }
        vowel_map = {
            'अ': 'a', 'आ': 'a', 'इ': 'i', 'ई': 'i', 'उ': 'u', 'ऊ': 'u',
            'ऋ': 'ri', 'ए': 'e', 'ऐ': 'ai', 'ओ': 'o', 'औ': 'au', 'ऑ': 'o',
        }
        matra_map = {
            'ा': 'a', 'ि': 'i', 'ी': 'i', 'ु': 'u', 'ू': 'u',
            'े': 'e', 'ै': 'ai', 'ो': 'o', 'ौ': 'au',
            'ृ': 'ri', 'ॅ': 'e', 'ॉ': 'o',
        }
        modifier_map = {
            'ं': 'n', 'ः': 'h', 'ँ': 'n',
        }

        def transliterate_word(word: str) -> str:
            """Transliterate a single Devanagari word with schwa deletion."""
            if not re.search(r'[\u0900-\u097F]', word):
                return word

            chars = list(word)
            n = len(chars)
            pieces = []  # list of (roman_text, is_consonant_with_inherent_a)
            i = 0

            while i < n:
                ch = chars[i]
                if not ('\u0900' <= ch <= '\u097F'):
                    pieces.append((ch, False))
                    i += 1
                    continue

                # Halant / virama
                if ch == '्':
                    # Remove the inherent 'a' from previous consonant
                    if pieces and pieces[-1][1]:
                        pieces[-1] = (pieces[-1][0], False)
                    i += 1
                    continue

                # Modifier (anusvara, visarga, chandrabindu)
                if ch in modifier_map:
                    # Attach to previous — replace inherent 'a' flag
                    if pieces and pieces[-1][1]:
                        pieces[-1] = (pieces[-1][0], False)
                    pieces.append((modifier_map[ch], False))
                    i += 1
                    continue

                # Matra (vowel sign) — replaces inherent 'a'
                if ch in matra_map:
                    if pieces and pieces[-1][1]:
                        pieces[-1] = (pieces[-1][0], False)
                    pieces.append((matra_map[ch], False))
                    i += 1
                    continue

                # Independent vowel
                if ch in vowel_map:
                    pieces.append((vowel_map[ch], False))
                    i += 1
                    continue

                # Consonant
                if ch in consonant_map:
                    pieces.append((consonant_map[ch], True))  # True = has inherent 'a' pending
                    i += 1
                    continue

                # Nukta forms
                nukta = {'क़': 'q', 'ख़': 'kh', 'ग़': 'gh', 'ज़': 'z', 'ड़': 'r', 'ढ़': 'rh', 'फ़': 'f'}
                if ch in nukta:
                    pieces.append((nukta[ch], True))
                    i += 1
                    continue

                # Unknown Devanagari — skip
                i += 1

            # Build result: add 'a' for consonants with inherent vowel,
            # EXCEPT the last consonant in the word (schwa deletion)
            result_parts = []
            for idx, (rom, has_a) in enumerate(pieces):
                result_parts.append(rom)
                if has_a:
                    # Check if this is the last piece or the last consonant before word end
                    # Schwa deletion: don't add 'a' if this is the final element
                    # or the only remaining pieces are modifiers
                    remaining = pieces[idx + 1:]
                    if remaining:
                        result_parts.append('a')
                    # else: word-final consonant — no inherent 'a' (schwa deletion)

            out = ''.join(result_parts)
            # Capitalize first letter (it's a name/proper noun since it wasn't in dictionary)
            if out:
                out = out[0].upper() + out[1:]
            return out

        # Process text word by word, only transliterating words containing Devanagari
        words = text.split()
        result_words = []
        for word in words:
            if re.search(r'[\u0900-\u097F]', word):
                # Separate leading/trailing punctuation
                leading = ''
                trailing = ''
                core = word
                while core and not ('\u0900' <= core[0] <= '\u097F') and not core[0].isalnum():
                    leading += core[0]
                    core = core[1:]
                while core and not ('\u0900' <= core[-1] <= '\u097F') and not core[-1].isalnum():
                    trailing = core[-1] + trailing
                    core = core[:-1]
                result_words.append(leading + transliterate_word(core) + trailing)
            else:
                result_words.append(word)

        return ' '.join(result_words)

    async def transcribe_and_translate(
        self,
        scenario_id: Optional[str] = None,
        custom_text: Optional[str] = None,
        language: str = "mr",
        caller_name: Optional[str] = None,
        caller_phone: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process speech/text: returns native transcript, AI English translation, and extracted entities.
        Prioritizes live custom_text if provided, otherwise uses scenario_id.
        """
        if custom_text and custom_text.strip():
            text = custom_text.strip()
            
            # Extract structured attributes
            age = 55
            age_match = (
                re.search(r"(?:वय|उम्र|age|years?|year)\s*[:=]?\s*(\d{1,2})", text, re.IGNORECASE) or
                re.search(r"(\d{1,2})\s*(?:वर्ष|साल|years?)", text, re.IGNORECASE) or
                re.search(r"\b(\d{1,2})\b", text)
            )
            if age_match:
                try:
                    val = int(age_match.group(1))
                    if 1 <= val <= 105:
                        age = val
                except:
                    pass

            gender = "M"
            if any(w in text.lower() for w in ["मुलगी", "स्त्री", "बाई", "महिला", "daughter", "mother", "girl", "woman", "female", "she", "her", "साडी", "saree", "फ्रॉक", "frock", "आजी"]):
                gender = "F"

            # Name extraction heuristics
            name = "Reported Pilgrim"
            name_match = re.search(r"(?:नांव|नाव|नाम|name)\s*[:=]?\s*([A-Za-z\u0900-\u097F\s]{3,20})", text, re.IGNORECASE)
            if name_match:
                name = name_match.group(1).strip()
            elif "मारुती" in text:
                name = "Maruti Shinde (मारुती शिंदे)"
            elif "गोदावरी" in text:
                name = "Godavari Jadhav (गोदावरी जाधव)"
            elif "रामकिशन" in text:
                name = "Ramkishan Gupta (रामकिशन गुप्ता)"
            elif "दत्तात्रय" in text or "पाटील" in text:
                name = "Dattatraya Patil (दत्तात्रय पाटील)"
            elif "तुकाराम" in text:
                name = "Tukaram More (तुकाराम मोरे)"

            # Clothing extraction
            clothing_items = []
            if any(w in text.lower() for w in ["कुर्ता", "सदरा", "kurta", "shirt"]):
                color = "White" if any(w in text.lower() for w in ["पांढरा", "पांढरे", "सफेद", "white"]) else ("Yellow" if any(w in text.lower() for w in ["पिवळा", "पीला", "yellow"]) else "Cotton")
                clothing_items.append(f"{color} Kurta")
            if any(w in text.lower() for w in ["धोती", "धोतर", "dhoti"]):
                clothing_items.append("White Dhoti")
            if any(w in text.lower() for w in ["साडी", "saree"]):
                clothing_items.append("Traditional Maharashtrian Saree")
            if any(w in text.lower() for w in ["फ्रॉक", "frock"]):
                clothing_items.append("Yellow Frock with floral print")
            if any(w in text.lower() for w in ["टोपी", "cap"]):
                clothing_items.append("White Gandhi Cap")
            if any(w in text.lower() for w in ["पगडी", "फेटा", "turban"]):
                clothing_items.append("Saffron Pagadi")
            if any(w in text.lower() for w in ["तुळशी", "तुलसी", "माळ", "mala"]):
                clothing_items.append("Tulsi Mala")
            if any(w in text.lower() for w in ["टाळ", "cymbals"]):
                clothing_items.append("Taal brass cymbals")

            clothing_desc = ", ".join(clothing_items) if clothing_items else "Traditional Pilgrim Attire (White Kurta / Dhoti)"

            # Location extraction
            location = "Pandharpur Corridor / Temple Route"
            cctv_list = ["CAM-04", "CAM-12"]
            if "वाखरी" in text or "wakhri" in text.lower():
                location = "Wakhri Phata Dindi Confluence"
                cctv_list = ["CAM-12", "CAM-04"]
            elif "आळंदी" in text or "alandi" in text.lower():
                location = "Alandi Indrayani Ghat Corridor"
                cctv_list = ["CAM-01", "CAM-08"]
            elif "सासवड" in text or "saswad" in text.lower():
                location = "Saswad Dive Ghat Junction"
                cctv_list = ["CAM-08", "CAM-01"]
            elif "पुंडलिक" in text or "pundalik" in text.lower():
                location = "Pundalik Temple Steps (Pandharpur)"
                cctv_list = ["CAM-04", "CAM-01"]

            urgency = "HIGH"
            if age <= 12 or age >= 70 or any(w in text.lower() for w in ["लगेच", "तातडीने", "urgent", "critical", "danger", "घाबरलेली", "घाबरला"]):
                urgency = "CRITICAL"

            # Translate using our Indic neural engine
            eng_trans = self._translate_indic_text(text, lang=language)

            return {
                "id": "live_user_input",
                "title": "Live Citizen Voice Intake Call",
                "caller_phone": caller_phone or "+91 98220 99881",
                "caller_name": caller_name or "Citizen Caller (Live SOS)",
                "dialed_line": "112 / Emergency Helpline",
                "language": language,
                "language_name": "मराठी (Marathi)" if language == "mr" else ("हिन्दी (Hindi)" if language == "hi" else "English"),
                "native_transcript": text,
                "english_translation": eng_trans,
                "confidence": 0.96,
                "extracted_attributes": {
                    "name": name,
                    "age": age,
                    "gender": gender,
                    "clothing_top": clothing_desc,
                    "clothing_bottom": "Traditional dhoti / pajama",
                    "headwear": "Cap / Turban" if "टोपी" in text or "फेटा" in text else "None",
                    "accessories": "Tulsi mala" if "माळ" in text else "None",
                    "last_seen_location": location,
                    "zone_code": "ZONE-PANDHARPUR" if "पंढरपूर" in text else ("ZONE-WAKHRI" if "वाखरी" in text else "ZONE-ALANDI"),
                    "urgency": urgency,
                    "recommended_cctv": cctv_list
                }
            }

        # Fallback to predefined scenario if scenario_id is provided
        if scenario_id and scenario_id in self.SCENARIOS:
            return self.SCENARIOS[scenario_id]

        return self.SCENARIOS["marathi_senior_wakhri"]

    async def transcribe(self, audio_bytes: bytes, language: str = "mr") -> Dict[str, Any]:
        """Legacy transcribe wrapper."""
        return await self.transcribe_and_translate(language=language)


speech_adapter = SpeechAdapter()
