import asyncio
import logging
from datetime import datetime, timezone

from sqlalchemy import select

from app.core.database import AsyncSessionLocal, init_db
from app.core.rbac import UserRole
from app.core.security import get_password_hash
from app.models.camera import Camera, CameraStatus
from app.models.crowd import CrowdObservation, CrowdTrend
from app.models.face_match import FaceMatchResult, FaceMatchStatus
from app.models.incident import Incident, IncidentEvent, IncidentSeverity, IncidentStatus, IncidentType
from app.models.lost_person import LostPersonCase, LostPersonReport, LostPersonStatus
from app.models.medical import MedicalAlert, MedicalAlertStatus, MedicalAlertType
from app.models.notification import Notification, NotificationType
from app.models.resource import Resource, ResourceAssignment, ResourceAssignmentStatus, ResourceAvailability, ResourceType
from app.models.route import Route, RouteStatus
from app.models.user import User
from app.models.zone import RiskLevel, Zone

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("varisetu.seed")

PEOPLE_DATA = [
            # 1-10: Seniors & Children (Critical/High Priority)
            {"name": "Maruti Kisan Shinde", "age": 68, "gender": "M", "cloth": "पांढरा कुर्ता, धोती, पांढरी टोपी, तुळशी माळ (White Kurta-Dhoti, Gandhi Topi, Tulsi Mala)", "loc": "Pandharpur Temple Chowk", "cam": "CAM-04", "prio": "HIGH", "status": LostPersonStatus.MATCH_FOUND, "caller": "Namdeo Shinde (Grandson)", "phone": "+91 98220 14455", "trans": "हॅलो कंट्रोल रूम, आमचे आजोबा मारुती शिंदे (वय ६८) वारीत वाखरी फाट्याजवळ गर्दीत सुटले आहेत. त्यांनी पांढरा सुती कुर्ता, धोती आणि पांढरी टोपी घातली आहे."},
            {"name": "Godavari Namdeo Jadhav", "age": 8, "gender": "F", "cloth": "पिवळा फ्रॉक, लाल हेअर रिबिन (Yellow floral frock, red hair ribbons)", "loc": "Pundalik Temple Steps", "cam": "CAM-04", "prio": "CRITICAL", "status": LostPersonStatus.MATCH_FOUND, "caller": "Sunita Jadhav (Mother)", "phone": "+91 94220 88912", "trans": "माझी लहान मुलगी गोदावरी जाधव (वय ८) पुंडलिक मंदिराच्या पायऱ्यांजवळ गर्दीत हरवली आहे. तिने पिवळा फ्रॉक घातला आहे."},
            {"name": "Anandita Ramesh Kulkarni", "age": 9, "gender": "F", "cloth": "पिवळा परकर पोलका, हिरव्या बांगड्या (Yellow traditional dress, green bangles)", "loc": "Wakhri Phata Rest Camp", "cam": "CAM-12", "prio": "CRITICAL", "status": LostPersonStatus.SEARCHING, "caller": "Ramesh Kulkarni (Father)", "phone": "+91 98220 19988", "trans": "माझी मुलगी आनंदिता वय ९ वर्षे वाखरी विश्राम शिबिराजवळ सुटली आहे. तिने पिवळा परकर पोलका घातला आहे."},
            {"name": "Dnyaneshwar Mahadev Gaikwad", "age": 72, "gender": "M", "cloth": "पांढरा खादी सदरा, लाल फेटा (White attire with red turban)", "loc": "Saswad Highway Checkpoint", "cam": "CAM-08", "prio": "NORMAL", "status": LostPersonStatus.REUNITED, "caller": "Sambhaji Gaikwad (Son)", "phone": "+91 98234 55112", "trans": "आमचे वडील ज्ञानेश्वर गायकवाड सासवड नाक्याजवळ दिंडीत पुढे निघून गेले होते."},
            {"name": "Janabai Tukaram Deshmukh", "age": 64, "gender": "F", "cloth": "जांभळी नऊवारी साडी, कपाळावर कुंकू (Purple Nauvari saree, large bindi)", "loc": "Alandi Corridor", "cam": "CAM-01", "prio": "HIGH", "status": LostPersonStatus.SEARCHING, "caller": "Tukaram Deshmukh (Husband)", "phone": "+91 97654 32100", "trans": "माझी पत्नी जनाबाई आळंदी घाटाजवळ पालखी प्रस्थानाच्या वेळी गर्दीत दिंडीपासून वेगळी झाली."},
            {"name": "Pandurang Eknath Chavan", "age": 75, "gender": "M", "cloth": "पांढरा कुर्ता, भगवी टोपी, हातात टाळ (White kurta, saffron cap, cymbals)", "loc": "Lonand Bypass", "cam": "CAM-08", "prio": "HIGH", "status": LostPersonStatus.SEARCHING, "caller": "Eknath Chavan (Son)", "phone": "+91 98901 23456", "trans": "वडिलांचे वय ७५ वर्षे असून लोणंद मुक्कामादरम्यान गर्दीत चुकले आहेत."},
            {"name": "Savitribai Babanrao Pawar", "age": 70, "gender": "F", "cloth": "हिरवी नऊवारी साडी, सोन्याची नथ (Green Nauvari saree, traditional nath)", "loc": "Taradgaon Ring Road", "cam": "CAM-08", "prio": "HIGH", "status": LostPersonStatus.SEARCHING, "caller": "Babanrao Pawar (Son)", "phone": "+91 94231 87654", "trans": "आई सावित्रीबाई पवार तरडगाव रिंग रोडजवळ दुपारच्या विसाव्याच्या वेळी हरवल्या आहेत."},
            {"name": "Eknath Sopan Bhosale", "age": 11, "gender": "M", "cloth": "भगवा कुर्ता, पांढरा पायजमा (Saffron kurta, white pajama)", "loc": "Bhalwani Camp", "cam": "CAM-12", "prio": "CRITICAL", "status": LostPersonStatus.SEARCHING, "caller": "Sopan Bhosale (Father)", "phone": "+91 98229 44332", "trans": "माझा मुलगा एकनाथ वय ११ भालवणी अन्नछत्राजवळ प्रसाद घेत असताना गर्दीत हरवला."},
            {"name": "Muktabai Khanderao More", "age": 58, "gender": "F", "cloth": "केशरी सुती साडी, खांद्यावर पिशवी (Orange cotton saree, cloth shoulder bag)", "loc": "Pandharpur North Gate", "cam": "CAM-04", "prio": "NORMAL", "status": LostPersonStatus.MATCH_FOUND, "caller": "Khanderao More (Husband)", "phone": "+91 97300 11223", "trans": "उत्तर दरवाजा जवळ मंदिराच्या रांगेत माझी पत्नी मुक्ताबाई वेगळी झाली आहे."},
            {"name": "Tukaram Narayan Wagh", "age": 82, "gender": "M", "cloth": "पांढरे धोतर, काळी कांबळी, हातात काठी (White dhoti, black woolen blanket, walking cane)", "loc": "Wakhri Phata", "cam": "CAM-12", "prio": "CRITICAL", "status": LostPersonStatus.SEARCHING, "caller": "Narayan Wagh (Son)", "phone": "+91 98811 77665", "trans": "आजोबा तुकाराम वाघ वय ८२ वर्षे यांना ऐकू कमी येते, वाखरी फाट्यावर हरवले आहेत."},
            
            # 11-25: Women & Senior Citizens
            {"name": "Rukminibai Sambhaji Kadam", "age": 62, "gender": "F", "cloth": "लाल काठाची पिवळी साडी (Yellow saree with red border)", "loc": "Chandrabhaga Ghat", "cam": "CAM-04", "prio": "HIGH", "status": LostPersonStatus.SEARCHING, "caller": "Sambhaji Kadam", "phone": "+91 94220 66554", "trans": "चंद्रभागा स्नानाच्या वेळी माझी आई गर्दीत सुटली आहे."},
            {"name": "Sambhaji Baburao Jagtap", "age": 67, "gender": "M", "cloth": "खादी कुर्ता, पांढरी टोपी, चष्मा (Khadi kurta, white cap, spectacles)", "loc": "Namdev Payatha", "cam": "CAM-04", "prio": "NORMAL", "status": LostPersonStatus.REUNITED, "caller": "Sachin Jagtap", "phone": "+91 98222 33445", "trans": "नामदेव पायरी जवळ आमचे काका भेटले आहेत, शोध पूर्ण झाला."},
            {"name": "Parvatibai Tanaji Thorat", "age": 69, "gender": "F", "cloth": "मोरपंखी निळी साडी (Peacock blue cotton saree)", "loc": "Saswad Rest Post", "cam": "CAM-08", "prio": "HIGH", "status": LostPersonStatus.SEARCHING, "caller": "Tanaji Thorat", "phone": "+91 98600 55443", "trans": "सासवड मुक्कामात साडीचा पदर सुटून गर्दीत पाठीमागे राहिली."},
            {"name": "Nivrutti Haribhau Salunkhe", "age": 71, "gender": "M", "cloth": "पांढरा सदरा, खांद्यावर भगवा शेला (White shirt, saffron stole on shoulder)", "loc": "Alandi Ghat Section", "cam": "CAM-01", "prio": "HIGH", "status": LostPersonStatus.SEARCHING, "caller": "Haribhau Salunkhe", "phone": "+91 97633 88990", "trans": "पालखीच्या पहिल्या टप्प्यात आळंदी येथे आमचे ज्येष्ठ वारकरी सहकारी हरवले."},
            {"name": "Shantabai Madhavrao Sawant", "age": 66, "gender": "F", "cloth": "तपकिरी सुती साडी, तुळशीचे रोप हातात (Brown saree, holding small Tulsi pot)", "loc": "Pandharpur Chowk", "cam": "CAM-04", "prio": "HIGH", "status": LostPersonStatus.MATCH_FOUND, "caller": "Madhavrao Sawant", "phone": "+91 98228 99887", "trans": "हातात तुळशी वृंदावन घेतलेल्या शांताबाई पंढरपूर चौकात हरवल्या."},
            {"name": "Mukund Babanrao Raut", "age": 55, "gender": "M", "cloth": "निळा कुर्ता, पांढरी पायजमा (Blue kurta, white pajama)", "loc": "Kurduvadi Junction", "cam": "CAM-12", "prio": "NORMAL", "status": LostPersonStatus.SEARCHING, "caller": "Vijay Raut", "phone": "+91 98909 11234", "trans": "कुर्डूवाडी फाट्यावर दिंडी क्रमांक १२ मधून वेगळे झाले."},
            {"name": "Kaushalya Vitthal Mane", "age": 73, "gender": "F", "cloth": "पांढरी सुती साडी, रुद्राक्ष माळ (White cotton saree, Rudraksha beads)", "loc": "Wakhri Ring Road", "cam": "CAM-12", "prio": "HIGH", "status": LostPersonStatus.SEARCHING, "caller": "Vitthal Mane", "phone": "+91 94223 44556", "trans": "वाखरी रिंग रोडवर रिंगण सोहळा पाहताना गर्दीत आई हरवली."},
            {"name": "Gajanan Laxman Tambe", "age": 60, "gender": "M", "cloth": "पांढरा कुर्ता, गळ्यात चिपळ्या (White kurta, wooden clappers around neck)", "loc": "Dehu Temple", "cam": "CAM-01", "prio": "NORMAL", "status": LostPersonStatus.REUNITED, "caller": "Prashant Tambe", "phone": "+91 98231 66778", "trans": "देहू मंदिराजवळ भाविक सुखरूप सापडले आहेत."},
            {"name": "Mandakini Sadashiv Mohite", "age": 63, "gender": "F", "cloth": "हिरवी चंद्रकळा साडी (Green traditional Chandrakala saree)", "loc": "Tarapur Phata", "cam": "CAM-12", "prio": "NORMAL", "status": LostPersonStatus.SEARCHING, "caller": "Sadashiv Mohite", "phone": "+91 97665 44332", "trans": "तारापूर फाटा येथे पाणी पिताना दिंडी पुढे निघून गेली."},
            {"name": "Santosh Raghunath Ghorpade", "age": 45, "gender": "M", "cloth": "भगवा सदरा, खाकी पॅन्ट, पाठीवर सॅक (Saffron shirt, khaki pants, backpack)", "loc": "Lonand Highway", "cam": "CAM-08", "prio": "LOW", "status": LostPersonStatus.SEARCHING, "caller": "Raghunath Ghorpade", "phone": "+91 98224 88776", "trans": "दिंडी सामान गाडीसोबत असलेला संतोष लोणंदजवळ संपर्कात नाही."},
            {"name": "Anusuyabai Uttamrao Nalawade", "age": 76, "gender": "F", "cloth": "राखाडी नऊवारी साडी, हातात काठी (Grey Nauvari saree, walking cane)", "loc": "Pandharpur Station", "cam": "CAM-04", "prio": "CRITICAL", "status": LostPersonStatus.SEARCHING, "caller": "Uttamrao Nalawade", "phone": "+91 94225 11990", "trans": "रेल्वे स्टेशन परिसरातून मंदिराकडे येताना आजोळच्या आई हरवल्या."},
            {"name": "Rameshwar Yashwant Ghodke", "age": 59, "gender": "M", "cloth": "पांढरा सदरा, भगवा शेला, विठ्ठल बॅज (White shirt, saffron stole, Vitthal badge)", "loc": "Solapur Bypass", "cam": "CAM-04", "prio": "NORMAL", "status": LostPersonStatus.SEARCHING, "caller": "Yashwant Ghodke", "phone": "+91 98902 44556", "trans": "सोलापूर बायपास नाक्यावर वाहनांच्या गर्दीत दिंडी सुटली."},
            {"name": "Pramila Vasant Khot", "age": 51, "gender": "F", "cloth": "गुलाबी सुती साडी, कपाळावर टिकली (Pink cotton saree)", "loc": "Bhalwani Shelter", "cam": "CAM-12", "prio": "NORMAL", "status": LostPersonStatus.SEARCHING, "caller": "Vasant Khot", "phone": "+91 97304 88221", "trans": "भालवणी मुक्कामात महिला मंडळातून वेगळ्या झाल्या."},
            {"name": "Baban Dattatray Nikam", "age": 70, "gender": "M", "cloth": "धोतर, पांढरी बंडी, कानावर मफलर (Dhoti, white vest, muffler on ears)", "loc": "Saswad Checkpoint", "cam": "CAM-08", "prio": "HIGH", "status": LostPersonStatus.SEARCHING, "caller": "Dattatray Nikam", "phone": "+91 98230 77112", "trans": "थंडीच्या वेळी सासवड घाटात विश्रांती घेताना पाठीमागे राहिले."},
            {"name": "Shakuntala Chandrakant Suryavanshi", "age": 65, "gender": "F", "cloth": "पिवळी काठपदराची साडी (Yellow traditional saree with zari border)", "loc": "Wakhri Confluence", "cam": "CAM-12", "prio": "HIGH", "status": LostPersonStatus.MATCH_FOUND, "caller": "Chandrakant Suryavanshi", "phone": "+91 94227 33441", "trans": "वाखरी येथे दोन्ही पालख्यांच्या संगमाच्या वेळी गर्दीत आई हरवली."},

            # 26-40: Children & Youths
            {"name": "Sai Sandeep Shelke", "age": 6, "gender": "M", "cloth": "छोटा भगवा कुर्ता, विठ्ठल मुकुट (Small saffron kurta, paper crown)", "loc": "Pundalik Steps", "cam": "CAM-04", "prio": "CRITICAL", "status": LostPersonStatus.SEARCHING, "caller": "Sandeep Shelke (Father)", "phone": "+91 98812 33441", "trans": "६ वर्षांचा लहान मुलगा साई पुंडलिक मंदिराच्या पायऱ्यांवरून निसटला."},
            {"name": "Aarohi Prashant Kale", "age": 5, "gender": "F", "cloth": "लाल फ्रॉक, पांढरे शूज (Red frock, white shoes)", "loc": "Alandi Main Gate", "cam": "CAM-01", "prio": "CRITICAL", "status": LostPersonStatus.SEARCHING, "caller": "Prashant Kale", "phone": "+91 97651 22334", "trans": "आळंदी मुख्य प्रवेशद्वाराजवळ ५ वर्षांची मुलगी गर्दीत हातातून सुटली."},
            {"name": "Omkar Ganesh Gite", "age": 14, "gender": "M", "cloth": "शालेय गणवेश, निळी पॅन्ट, पांढरा शर्ट (School uniform, blue pants, white shirt)", "loc": "Saswad Highway", "cam": "CAM-08", "prio": "HIGH", "status": LostPersonStatus.SEARCHING, "caller": "Ganesh Gite", "phone": "+91 98221 66550", "trans": "१४ वर्षांचा मुलगा स्वयंसेवक म्हणून काम करताना दिंडीतून चुकला."},
            {"name": "Tanvi Sachin Shirole", "age": 7, "gender": "F", "cloth": "हिरवा परकर पोलका, काळा दोरा गळ्यात (Green dress, black thread on neck)", "loc": "Pandharpur Chowk", "cam": "CAM-04", "prio": "CRITICAL", "status": LostPersonStatus.SEARCHING, "caller": "Sachin Shirole", "phone": "+91 94230 44556", "trans": "पंढरपूर चौकात गर्दी वाढल्याने ७ वर्षांची तन्वी हरवली आहे."},
            {"name": "Samarth Vishal Shingade", "age": 10, "gender": "M", "cloth": "पांढरा कुर्ता, डोक्यावर वारकरी टोपी (White kurta, pilgrim cap)", "loc": "Wakhri Rest Camp", "cam": "CAM-12", "prio": "CRITICAL", "status": LostPersonStatus.MATCH_FOUND, "caller": "Vishal Shingade", "phone": "+91 98905 66778", "trans": "वाखरी विश्राम शिबिरात जेवणाच्या रांगेत समर्थ चुकला."},
            {"name": "Vaishnavi Nitin Garje", "age": 12, "gender": "F", "cloth": "पिवळा ड्रेस, निळा दुपट्टा (Yellow salwar suit, blue dupatta)", "loc": "Lonand Halt", "cam": "CAM-08", "prio": "HIGH", "status": LostPersonStatus.SEARCHING, "caller": "Nitin Garje", "phone": "+91 97301 99887", "trans": "लोणंद मुक्कामात १२ वर्षांची वैष्णवी पाण्याचे पाऊच आणायला जाताना चुकली."},
            {"name": "Prathamesh Kiran Ghadge", "age": 15, "gender": "M", "cloth": "भगवा टीशर्ट, जिन्स (Saffron t-shirt, blue jeans)", "loc": "Taradgaon", "cam": "CAM-08", "prio": "NORMAL", "status": LostPersonStatus.SEARCHING, "caller": "Kiran Ghadge", "phone": "+91 98602 11445", "trans": "तरडगाव रिंगण सोहळ्यात प्रथमेश दिंडीपासून वेगळा झाला."},
            {"name": "Swara Deepak Gore", "age": 4, "gender": "F", "cloth": "गुलाबी फ्रॉक, हातात चांदीचे कडे (Pink frock, silver bangle)", "loc": "Pandharpur Ghat", "cam": "CAM-04", "prio": "CRITICAL", "status": LostPersonStatus.SEARCHING, "caller": "Deepak Gore", "phone": "+91 94226 77889", "trans": "४ वर्षांची स्वरा घाटावर आरती सुरू असताना हरवली, तातडीने मदत हवी."},
            {"name": "Aditya Santosh Hankare", "age": 16, "gender": "M", "cloth": "पांढरा सदरा, भगवी पताका हातात (White shirt, carrying saffron flag)", "loc": "Dehu Gaon", "cam": "CAM-01", "prio": "NORMAL", "status": LostPersonStatus.REUNITED, "caller": "Santosh Hankare", "phone": "+91 98233 44551", "trans": "देहू गावात पताका घेऊन जात असताना रस्ता चुकला होता, आता सापडला."},
            {"name": "Ananya Sunil Ingale", "age": 8, "gender": "F", "cloth": "जांभळा ड्रेस, पांढरी क्लिप (Purple dress, white hair clip)", "loc": "Wakhri Confluence", "cam": "CAM-12", "prio": "CRITICAL", "status": LostPersonStatus.SEARCHING, "caller": "Sunil Ingale", "phone": "+91 98906 33221", "trans": "वाखरी फाट्यावर पालखी दर्शनासाठी थांबले असताना अनन्य हरवली."},
            {"name": "Rohan Mahesh Jondhale", "age": 18, "gender": "M", "cloth": "वारकरी पांढरा पोशाख, मृदंग वादक (Warkari white dress, Mridang player)", "loc": "Alandi Corridor", "cam": "CAM-01", "prio": "LOW", "status": LostPersonStatus.SEARCHING, "caller": "Mahesh Jondhale", "phone": "+91 97657 88990", "trans": "आळंदी पालखी निघताना भजन मंडळातून रोहन पुढे निघून गेला."},
            {"name": "Shruti Vinod Kakade", "age": 13, "gender": "F", "cloth": "लाल कुर्ती, काळा लेगिंग्स (Red kurti, black leggings)", "loc": "Saswad Highway", "cam": "CAM-08", "prio": "HIGH", "status": LostPersonStatus.SEARCHING, "caller": "Vinod Kakade", "phone": "+91 94235 66778", "trans": "सासवडजवळ नाश्ता वाटप केंद्रावर श्रुती गर्दीत पाठीमागे राहिली."},
            {"name": "Atharva Rahul Londhe", "age": 9, "gender": "M", "cloth": "पिवळा टीशर्ट, खाकी शॉर्ट्स (Yellow t-shirt, khaki shorts)", "loc": "Pandharpur Perimeter", "cam": "CAM-04", "prio": "CRITICAL", "status": LostPersonStatus.SEARCHING, "caller": "Rahul Londhe", "phone": "+91 98227 11443", "trans": "पंढरपूर प्रवेशद्वारावर अथर्व आई-वडिलांच्या हातामधून सुटला."},
            {"name": "Janhavi Vikas Munde", "age": 11, "gender": "F", "cloth": "हिरवा परकर पोलका (Green traditional dress)", "loc": "Bhalwani Shelter", "cam": "CAM-12", "prio": "HIGH", "status": LostPersonStatus.SEARCHING, "caller": "Vikas Munde", "phone": "+91 98908 44552", "trans": "भालवणी येथे पाणी भरण्यासाठी गेली असता जान्हवी चुकली."},
            {"name": "Yash Pravin Pote", "age": 7, "gender": "M", "cloth": "भगवी टोपी, पांढरा सदरा (Saffron cap, white shirt)", "loc": "Taradgaon Camp", "cam": "CAM-08", "prio": "CRITICAL", "status": LostPersonStatus.SEARCHING, "caller": "Pravin Pote", "phone": "+91 97305 77112", "trans": "तरडगाव येथे ७ वर्षांचा यश गर्दीत हरवला आहे."},

            # 41-70: Middle-Aged & Senior Pilgrims (Diverse locations)
            {"name": "Vimal Dattatray Randive", "age": 57, "gender": "F", "cloth": "लाल सुती साडी, चष्मा (Red cotton saree, glasses)", "loc": "Pandharpur Chowk", "cam": "CAM-04", "prio": "NORMAL", "status": LostPersonStatus.SEARCHING, "caller": "Dattatray Randive", "phone": "+91 98604 88991", "trans": "चौकात दर्शनाची रांग लागली असताना विमल दिंडीतून वेगळी झाली."},
            {"name": "Sunanda Ashok Sanap", "age": 53, "gender": "F", "cloth": "पिवळी नऊवारी साडी (Yellow Nauvari saree)", "loc": "Alandi Corridor", "cam": "CAM-01", "prio": "HIGH", "status": LostPersonStatus.MATCH_FOUND, "caller": "Ashok Sanap", "phone": "+91 94228 11223", "trans": "आळंदी मंदिराजवळ दर्शनाला जाताना सुनंदा गर्दीत सुटल्या."},
            {"name": "Sulochana Ramdas Saste", "age": 61, "gender": "F", "cloth": "हिरवी साडी, गळ्यात तुळशीची माळ (Green saree, Tulsi mala)", "loc": "Wakhri Phata", "cam": "CAM-12", "prio": "HIGH", "status": LostPersonStatus.SEARCHING, "caller": "Ramdas Saste", "phone": "+91 98232 55667", "trans": "वाखरी फाट्यावर सुलोचना सास्ते दिंडीपासून लांब गेल्या आहेत."},
            {"name": "Suman Prabhakar Shewale", "age": 68, "gender": "F", "cloth": "केशरी साडी, पांढरा शेला (Orange saree, white shawl)", "loc": "Saswad Checkpoint", "cam": "CAM-08", "prio": "HIGH", "status": LostPersonStatus.SEARCHING, "caller": "Prabhakar Shewale", "phone": "+91 98903 77889", "trans": "सासवड नाक्यावर सुमनबाई विश्रांती घेत असताना दिंडी पुढे गेली."},
            {"name": "Chhaya Suresh Shingte", "age": 49, "gender": "F", "cloth": "निळी साडी, लाल ब्लाउज (Blue saree, red blouse)", "loc": "Lonand Bypass", "cam": "CAM-08", "prio": "NORMAL", "status": LostPersonStatus.REUNITED, "caller": "Suresh Shingte", "phone": "+91 97658 22110", "trans": "लोणंद येथे छायाबाई सापडल्या आहेत, कुटुंब एकत्र आले."},
            {"name": "Mangal Vijay Tarate", "age": 56, "gender": "F", "cloth": "जांभळी साडी, हातात पाण्याची बाटली (Purple saree, water bottle)", "loc": "Bhalwani", "cam": "CAM-12", "prio": "NORMAL", "status": LostPersonStatus.SEARCHING, "caller": "Vijay Tarate", "phone": "+91 94236 99881", "trans": "भालवणी मुक्कामात जेवणाच्या वेळी मंगल दिंडीतून चुकल्या."},
            {"name": "Vijaya Mohan Thorave", "age": 62, "gender": "F", "cloth": "तपकिरी साडी, कपाळावर गोपीचंदन (Brown saree, Gopichandan tilak)", "loc": "Pandharpur North Gate", "cam": "CAM-04", "prio": "HIGH", "status": LostPersonStatus.SEARCHING, "caller": "Mohan Thorave", "phone": "+91 98229 33221", "trans": "उत्तर दरवाजा जवळ विजयाबाई मंदिरात जाताना गर्दीत सुटल्या."},
            {"name": "Usha Sanjay Ughade", "age": 54, "gender": "F", "cloth": "गुलाबी नऊवारी साडी (Pink Nauvari saree)", "loc": "Chandrabhaga Ghat", "cam": "CAM-04", "prio": "NORMAL", "status": LostPersonStatus.SEARCHING, "caller": "Sanjay Ughade", "phone": "+91 98907 55443", "trans": "चंद्रभागा नदीच्या घाटावर स्नान करताना उषाबाई हरवल्या."},
            {"name": "Rekha Dilip Vanve", "age": 50, "gender": "F", "cloth": "राखाडी साडी, निळी शाल (Grey saree, blue shawl)", "loc": "Taradgaon", "cam": "CAM-08", "prio": "NORMAL", "status": LostPersonStatus.SEARCHING, "caller": "Dilip Vanve", "phone": "+91 97306 88771", "trans": "तरडगाव येथे रस्ता ओलांडताना रेखाबाई दिंडीपासून वेगळ्या झाल्या."},
            {"name": "Ashwini Prashant Waghmare", "age": 42, "gender": "F", "cloth": "पिवळी साडी, खांद्यावर पिशवी (Yellow saree, shoulder bag)", "loc": "Wakhri Confluence", "cam": "CAM-12", "prio": "NORMAL", "status": LostPersonStatus.MATCH_FOUND, "caller": "Prashant Waghmare", "phone": "+91 98605 11223", "trans": "वाखरी फाट्यावर पालखीच्या संगमावेळी अश्विनी हरवली."},
            {"name": "Archana Anil Zende", "age": 38, "gender": "F", "cloth": "हिरवा पंजाबी ड्रेस, लाल ओढणी (Green salwar suit, red dupatta)", "loc": "Alandi Corridor", "cam": "CAM-01", "prio": "LOW", "status": LostPersonStatus.SEARCHING, "caller": "Anil Zende", "phone": "+91 94229 44556", "trans": "आळंदी येथे मोबाईल बंद पडल्याने अर्चनाशी संपर्क होत नाही."},
            {"name": "Snehal Atul Jagdale", "age": 35, "gender": "F", "cloth": "केशरी कुर्ती, पांढरी लेगिंग्स (Saffron kurti, white leggings)", "loc": "Dehu Temple", "cam": "CAM-01", "prio": "LOW", "status": LostPersonStatus.REUNITED, "caller": "Atul Jagdale", "phone": "+91 98235 66778", "trans": "स्नेहल देहू मंदिराजवळ सुरक्षित सापडली आहे."},
            {"name": "Pallavi Nilesh Kute", "age": 44, "gender": "F", "cloth": "लाल साडी, सोन्याचे दागिने (Red saree, gold earrings)", "loc": "Pandharpur Chowk", "cam": "CAM-04", "prio": "NORMAL", "status": LostPersonStatus.SEARCHING, "caller": "Nilesh Kute", "phone": "+91 98904 88990", "trans": "पंढरपूर स्टेशन रोडवर पल्लवी दिंडीतून वेगळी झाली."},
            {"name": "Rohini Sagar Landge", "age": 41, "gender": "F", "cloth": "निळी नऊवारी साडी (Blue Nauvari saree)", "loc": "Saswad Checkpoint", "cam": "CAM-08", "prio": "NORMAL", "status": LostPersonStatus.SEARCHING, "caller": "Sagar Landge", "phone": "+91 97659 33445", "trans": "सासवड येथे मुक्कामाच्या वेळी रोहिणी हरवली आहे."},
            {"name": "Savita Nitin Mahajan", "age": 47, "gender": "F", "cloth": "मोरपंखी साडी, पांढरी टोपी (Peacock green saree, white Gandhi cap)", "loc": "Lonand Highway", "cam": "CAM-08", "prio": "NORMAL", "status": LostPersonStatus.SEARCHING, "caller": "Nitin Mahajan", "phone": "+91 94237 22119", "trans": "लोणंद येथे दिंडी पायी चालताना सविता पाठीमागे राहिली."},
            {"name": "Shobha Vijay Nimbalkar", "age": 52, "gender": "F", "cloth": "तपकिरी साडी, चष्मा (Brown saree, reading glasses)", "loc": "Bhalwani Camp", "cam": "CAM-12", "prio": "NORMAL", "status": LostPersonStatus.SEARCHING, "caller": "Vijay Nimbalkar", "phone": "+91 98236 44332", "trans": "भालवणी मुक्कामात शोभाताई मंडपातून बाहेर पडल्या व रस्ता चुकल्या."},
            {"name": "Meena Ajay Pandhare", "age": 46, "gender": "F", "cloth": "जांभळा ड्रेस, पिवळा दुपट्टा (Purple dress, yellow dupatta)", "loc": "Wakhri Phata", "cam": "CAM-12", "prio": "NORMAL", "status": LostPersonStatus.SEARCHING, "caller": "Ajay Pandhare", "phone": "+91 98901 66554", "trans": "वाखरी फाट्यावर मीनाताई दिंडी क्रमांक १५ मधून चुकल्या."},
            {"name": "Geeta Pravin Salve", "age": 40, "gender": "F", "cloth": "पिवळी सुती साडी (Yellow cotton saree)", "loc": "Pandharpur Ghat", "cam": "CAM-04", "prio": "NORMAL", "status": LostPersonStatus.SEARCHING, "caller": "Pravin Salve", "phone": "+91 97307 99881", "trans": "चंद्रभागा घाटावर गीतांजली साळवे हरवली आहे."},
            {"name": "Sindhubai Ramdas Shirote", "age": 74, "gender": "F", "cloth": "पांढरी सुती साडी, गळ्यात तुळशी माळ (White saree, Tulsi mala)", "loc": "Alandi Corridor", "cam": "CAM-01", "prio": "HIGH", "status": LostPersonStatus.SEARCHING, "caller": "Ramdas Shirote", "phone": "+91 98606 33221", "trans": "७४ वर्षांच्या सिंधुबाई आळंदी घाटावर हरवल्या आहेत."},
            {"name": "Sitabai Ganpat Tambade", "age": 78, "gender": "F", "cloth": "राखाडी नऊवारी साडी, काठी (Grey Nauvari saree, stick)", "loc": "Pandharpur Chowk", "cam": "CAM-04", "prio": "CRITICAL", "status": LostPersonStatus.MATCH_FOUND, "caller": "Ganpat Tambade", "phone": "+91 94221 55667", "trans": "सीताबाई तांबडे वय ७८ पंढरपूर चौकात हरवल्या असून त्वरित मदत हवी."},
            {"name": "Sushilabai Bhimrao Waghire", "age": 69, "gender": "F", "cloth": "हिरवी साडी, कपाळावर बुक्का (Green saree, holy Bukka tilak)", "loc": "Wakhri Confluence", "cam": "CAM-12", "prio": "HIGH", "status": LostPersonStatus.SEARCHING, "caller": "Bhimrao Waghire", "phone": "+91 98237 88990", "trans": "वाखरी फाट्यावर सुशीलाबाई गर्दीत सुटल्या."},
            {"name": "Tarabai Narayan Yewale", "age": 71, "gender": "F", "cloth": "केशरी साडी, चष्मा (Saffron saree, spectacles)", "loc": "Saswad Checkpoint", "cam": "CAM-08", "prio": "HIGH", "status": LostPersonStatus.SEARCHING, "caller": "Narayan Yewale", "phone": "+91 98902 11334", "trans": "सासवड येथे ताराबाई दिंडीपासून लांब गेल्या."},
            {"name": "Vatsalabai Sopanrao Adhalrao", "age": 73, "gender": "F", "cloth": "जांभळी नऊवारी साडी (Purple Nauvari saree)", "loc": "Dehu Temple", "cam": "CAM-01", "prio": "HIGH", "status": LostPersonStatus.REUNITED, "caller": "Sopanrao Adhalrao", "phone": "+91 97660 44556", "trans": "देहू येथे वत्सलाबाई सापडल्या आहेत."},
            {"name": "Anuradha Balasaheb Bankar", "age": 48, "gender": "F", "cloth": "लाल काठपदराची साडी (Red bordered traditional saree)", "loc": "Lonand Halt", "cam": "CAM-08", "prio": "NORMAL", "status": LostPersonStatus.SEARCHING, "caller": "Balasaheb Bankar", "phone": "+91 94238 77665", "trans": "लोणंद येथे अनुराधा बनकर दिंडीतून चुकल्या."},
            {"name": "Aruna Chandrakant Chikhale", "age": 55, "gender": "F", "cloth": "निळी सुती साडी (Blue cotton saree)", "loc": "Taradgaon Ring Road", "cam": "CAM-08", "prio": "NORMAL", "status": LostPersonStatus.SEARCHING, "caller": "Chandrakant Chikhale", "phone": "+91 98238 11223", "trans": "तरडगाव रिंग रोडवर अरुणा चिखले हरवल्या."},
            {"name": "Bharati Dnyaneshwar Darekar", "age": 52, "gender": "F", "cloth": "पिवळी साडी, खांद्यावर शेला (Yellow saree, shoulder shawl)", "loc": "Bhalwani Shelter", "cam": "CAM-12", "prio": "NORMAL", "status": LostPersonStatus.SEARCHING, "caller": "Dnyaneshwar Darekar", "phone": "+91 98903 55667", "trans": "भालवणी मुक्कामात भारती दरेकर चुकल्या."},
            {"name": "Deepali Eknath Dhumal", "age": 39, "gender": "F", "cloth": "गुलाबी ड्रेस, काळी ओढणी (Pink dress, black dupatta)", "loc": "Wakhri Phata", "cam": "CAM-12", "prio": "NORMAL", "status": LostPersonStatus.MATCH_FOUND, "caller": "Eknath Dhumal", "phone": "+91 97308 22119", "trans": "वाखरी फाट्यावर दीपाली धुमाळ हरवली आहे."},
            {"name": "Jayashree Gajanan Gaikwad", "age": 43, "gender": "F", "cloth": "हिरवा ड्रेस (Green dress)", "loc": "Pandharpur Chowk", "cam": "CAM-04", "prio": "NORMAL", "status": LostPersonStatus.SEARCHING, "caller": "Gajanan Gaikwad", "phone": "+91 98607 66554", "trans": "पंढरपूर चौकात जयश्री गायकवाड हरवली आहे."},
            {"name": "Jyoti Haribhau Gore", "age": 37, "gender": "F", "cloth": "केशरी पंजाबी ड्रेस (Saffron salwar suit)", "loc": "Alandi Corridor", "cam": "CAM-01", "prio": "LOW", "status": LostPersonStatus.SEARCHING, "caller": "Haribhau Gore", "phone": "+91 94222 99881", "trans": "आळंदी घाटावर ज्योती गोरे गर्दीत पुढे निघून गेली."},
            {"name": "Kalpana Jagannath Hingane", "age": 51, "gender": "F", "cloth": "जांभळी साडी (Purple saree)", "loc": "Saswad Checkpoint", "cam": "CAM-08", "prio": "NORMAL", "status": LostPersonStatus.SEARCHING, "caller": "Jagannath Hingane", "phone": "+91 98239 33221", "trans": "सासवड येथे कल्पना हिंगणे हरवली आहे."},

            # 71-100: Senior Men & Warkaris (Dindi flag bearers, taal players)
            {"name": "Kavita Kisan Jadhav", "age": 45, "gender": "F", "cloth": "पिवळा ड्रेस (Yellow dress)", "loc": "Dehu Temple", "cam": "CAM-01", "prio": "LOW", "status": LostPersonStatus.REUNITED, "caller": "Kisan Jadhav", "phone": "+91 98904 77889", "trans": "देहू मंदिरात कविता जाधव सापडली आहे."},
            {"name": "Lata Laxman Kadam", "age": 58, "gender": "F", "cloth": "लाल साडी, पांढरी शाल (Red saree, white shawl)", "loc": "Wakhri Confluence", "cam": "CAM-12", "prio": "HIGH", "status": LostPersonStatus.SEARCHING, "caller": "Laxman Kadam", "phone": "+91 97661 11223", "trans": "वाखरी फाट्यावर लता कदम हरवली आहे."},
            {"name": "Manisha Madhavrao Kale", "age": 40, "gender": "F", "cloth": "निळा ड्रेस, चष्मा (Blue dress, glasses)", "loc": "Pandharpur Station", "cam": "CAM-04", "prio": "NORMAL", "status": LostPersonStatus.SEARCHING, "caller": "Madhavrao Kale", "phone": "+91 94239 44332", "trans": "पंढरपूर स्टेशनवर मनीषा काळे चुकली आहे."},
            {"name": "Nirmala Namdeo Khade", "age": 60, "gender": "F", "cloth": "हिरवी नऊवारी साडी (Green Nauvari saree)", "loc": "Taradgaon", "cam": "CAM-08", "prio": "HIGH", "status": LostPersonStatus.SEARCHING, "caller": "Namdeo Khade", "phone": "+91 98240 66554", "trans": "तरडगाव येथे निर्मला खाडे हरवली आहे."},
            {"name": "Pratibha Nivrutti Kokare", "age": 49, "gender": "F", "cloth": "गुलाबी साडी (Pink saree)", "loc": "Lonand Halt", "cam": "CAM-08", "prio": "NORMAL", "status": LostPersonStatus.SEARCHING, "caller": "Nivrutti Kokare", "phone": "+91 98905 99887", "trans": "लोणंद येथे प्रतिभा कोकरे हरवली आहे."},
            {"name": "Radhabai Pandurang Kumbhar", "age": 75, "gender": "F", "cloth": "पांढरी साडी, तुळशी माळ (White saree, Tulsi mala)", "loc": "Bhalwani Shelter", "cam": "CAM-12", "prio": "CRITICAL", "status": LostPersonStatus.SEARCHING, "caller": "Pandurang Kumbhar", "phone": "+91 97309 44332", "trans": "भालवणी येथे राधाबाई कुंभार वय ७५ हरवल्या आहेत."},
            {"name": "Ranjana Raghunath Lande", "age": 53, "gender": "F", "cloth": "राखाडी साडी (Grey saree)", "loc": "Chandrabhaga Ghat", "cam": "CAM-04", "prio": "NORMAL", "status": LostPersonStatus.MATCH_FOUND, "caller": "Raghunath Lande", "phone": "+91 98608 11990", "trans": "चंद्रभागा घाटावर रंजना लांडे हरवली आहे."},
            {"name": "Sarojini Ramesh Madane", "age": 63, "gender": "F", "cloth": "तपकिरी साडी (Brown saree)", "loc": "Alandi Corridor", "cam": "CAM-01", "prio": "HIGH", "status": LostPersonStatus.SEARCHING, "caller": "Ramesh Madane", "phone": "+91 94223 88776", "trans": "आळंदी घाटावर सरोजिनी मदने हरवली आहे."},
            {"name": "Taramati Santosh Maske", "age": 59, "gender": "F", "cloth": "पिवळी काठपदराची साडी (Yellow bordered saree)", "loc": "Saswad Checkpoint", "cam": "CAM-08", "prio": "NORMAL", "status": LostPersonStatus.SEARCHING, "caller": "Santosh Maske", "phone": "+91 98241 33221", "trans": "सासवड येथे ताराबाई मसके हरवली आहे."},
            {"name": "Urmila Tanaji More", "age": 44, "gender": "F", "cloth": "केशरी ड्रेस (Saffron dress)", "loc": "Wakhri Phata", "cam": "CAM-12", "prio": "NORMAL", "status": LostPersonStatus.SEARCHING, "caller": "Tanaji More", "phone": "+91 98906 77889", "trans": "वाखरी फाट्यावर उर्मिला मोरे हरवली आहे."},
            {"name": "Bhagwan Pandharinath Garje", "age": 67, "gender": "M", "cloth": "धोती-कुर्ता, पांढरी टोपी (Dhoti-kurta, white cap)", "loc": "Pandharpur Chowk", "cam": "CAM-04", "prio": "HIGH", "status": LostPersonStatus.SEARCHING, "caller": "Pandharinath Garje", "phone": "+91 97662 44556", "trans": "पंढरपूर चौकात भगवान गर्जे हरवले आहेत."},
            {"name": "Chandrakant Raosaheb Ghadge", "age": 71, "gender": "M", "cloth": "पांढरा सदरा, भगवा फेटा (White shirt, saffron turban)", "loc": "Wakhri Confluence", "cam": "CAM-12", "prio": "HIGH", "status": LostPersonStatus.MATCH_FOUND, "caller": "Raosaheb Ghadge", "phone": "+91 94240 11223", "trans": "वाखरी येथे चंद्रकांत घाडगे गर्दीत चुकले आहेत."},
            {"name": "Devidas Sarjerao Gore", "age": 65, "gender": "M", "cloth": "खादी सदरा, चष्मा, काठी (Khadi shirt, glasses, stick)", "loc": "Dehu Temple", "cam": "CAM-01", "prio": "NORMAL", "status": LostPersonStatus.REUNITED, "caller": "Sarjerao Gore", "phone": "+91 98242 88990", "trans": "देहू मंदिराजवळ देविदास गोरे सापडले आहेत."},
            {"name": "Ganesh Shankarrao Hankare", "age": 58, "gender": "M", "cloth": "पांढरा कुर्ता, गळ्यात टाळ (White kurta, cymbals)", "loc": "Saswad Checkpoint", "cam": "CAM-08", "prio": "NORMAL", "status": LostPersonStatus.SEARCHING, "caller": "Shankarrao Hankare", "phone": "+91 98907 22119", "trans": "सासवड नाक्यावर गणेश हंकारे हरवले आहेत."},
            {"name": "Hiraman Shivaji Ingale", "age": 73, "gender": "M", "cloth": "धोतर, बंडी, पांढरी टोपी (Dhoti, vest, Gandhi topi)", "loc": "Alandi Corridor", "cam": "CAM-01", "prio": "HIGH", "status": LostPersonStatus.SEARCHING, "caller": "Shivaji Ingale", "phone": "+91 97310 66554", "trans": "आळंदी येथे हिरामन इंगळे वय ७३ हरवले आहेत."},
            {"name": "Jagtap Bhau Somnath", "age": 62, "gender": "M", "cloth": "पांढरा पोशाख, तुळशी माळ (White dress, Tulsi mala)", "loc": "Lonand Halt", "cam": "CAM-08", "prio": "NORMAL", "status": LostPersonStatus.SEARCHING, "caller": "Somnath Jagtap", "phone": "+91 98609 33221", "trans": "लोणंद येथे जगताप भाऊ हरवले आहेत."},
            {"name": "Kashinath Subhash Jondhale", "age": 69, "gender": "M", "cloth": "खादी कुर्ता, भगवी टोपी (Khadi kurta, saffron cap)", "loc": "Taradgaon", "cam": "CAM-08", "prio": "HIGH", "status": LostPersonStatus.SEARCHING, "caller": "Subhash Jondhale", "phone": "+91 94224 55667", "trans": "तरडगाव येथे काशिनाथ जोंधळे हरवले आहेत."},
            {"name": "Limbaji Sudam Kakade", "age": 80, "gender": "M", "cloth": "पांढरे धोतर, कांबळी, काठी (White dhoti, blanket, walking cane)", "loc": "Bhalwani Shelter", "cam": "CAM-12", "prio": "CRITICAL", "status": LostPersonStatus.SEARCHING, "caller": "Sudam Kakade", "phone": "+91 98243 11990", "trans": "८० वर्षांचे लिंबाजी काकडे भालवणी येथे हरवले आहेत."},
            {"name": "Mahadev Suresh Londhe", "age": 66, "gender": "M", "cloth": "पांढरा सदरा, चष्मा (White shirt, spectacles)", "loc": "Pandharpur Station", "cam": "CAM-04", "prio": "NORMAL", "status": LostPersonStatus.SEARCHING, "caller": "Suresh Londhe", "phone": "+91 98908 66554", "trans": "पंढरपूर स्टेशनवर महादेव लोंढे हरवले आहेत."},
            {"name": "Nana Tanaji Munde", "age": 64, "gender": "M", "cloth": "पांढरा कुर्ता, भगवा शेला (White kurta, saffron stole)", "loc": "Wakhri Phata", "cam": "CAM-12", "prio": "NORMAL", "status": LostPersonStatus.MATCH_FOUND, "caller": "Tanaji Munde", "phone": "+91 97663 88990", "trans": "वाखरी फाट्यावर नाना मुंडे हरवले आहेत."},
            {"name": "Pandhari Uttam Pote", "age": 57, "gender": "M", "cloth": "पांढरा सदरा, डोक्यावर टोपी (White shirt, cap)", "loc": "Chandrabhaga Ghat", "cam": "CAM-04", "prio": "NORMAL", "status": LostPersonStatus.SEARCHING, "caller": "Uttam Pote", "phone": "+91 94241 33221", "trans": "चंद्रभागा घाटावर पंढरी पोते हरवले आहेत."},
            {"name": "Ramchandra Vasant Randive", "age": 72, "gender": "M", "cloth": "धोती, कुर्ता, तुळशी माळ (Dhoti, kurta, Tulsi mala)", "loc": "Saswad Checkpoint", "cam": "CAM-08", "prio": "HIGH", "status": LostPersonStatus.SEARCHING, "caller": "Vasant Randive", "phone": "+91 98244 77889", "trans": "सासवड येथे रामचंद्र रणदिवे हरवले आहेत."},
            {"name": "Raosaheb Yashwant Sanap", "age": 68, "gender": "M", "cloth": "पांढरा खादी सदरा (White khadi shirt)", "loc": "Alandi Corridor", "cam": "CAM-01", "prio": "HIGH", "status": LostPersonStatus.SEARCHING, "caller": "Yashwant Sanap", "phone": "+91 98909 11223", "trans": "आळंदी येथे रावसाहेब सानप हरवले आहेत."},
            {"name": "Sarjerao Anant Saste", "age": 61, "gender": "M", "cloth": "भगवा कुर्ता, पांढरी टोपी (Saffron kurta, white cap)", "loc": "Dehu Temple", "cam": "CAM-01", "prio": "LOW", "status": LostPersonStatus.REUNITED, "caller": "Anant Saste", "phone": "+91 97311 55667", "trans": "देहू येथे सर्जेराव सास्ते सापडले आहेत."},
            {"name": "Shankarrao Baban Shewale", "age": 75, "gender": "M", "cloth": "धोतर, बंडी, हातात काठी (Dhoti, vest, walking stick)", "loc": "Pandharpur Chowk", "cam": "CAM-04", "prio": "HIGH", "status": LostPersonStatus.SEARCHING, "caller": "Baban Shewale", "phone": "+91 98610 88990", "trans": "पंढरपूर चौकात शंकरराव शेवाळे हरवले आहेत."},
            {"name": "Shivaji Dnyaneshwar Shingte", "age": 63, "gender": "M", "cloth": "पांढरा पोशाख, गळ्यात टाळ (White attire, cymbals)", "loc": "Wakhri Confluence", "cam": "CAM-12", "prio": "NORMAL", "status": LostPersonStatus.SEARCHING, "caller": "Dnyaneshwar Shingte", "phone": "+91 94225 22119", "trans": "वाखरी फाट्यावर शिवाजी शिंगटे हरवले आहेत."},
            {"name": "Somnath Eknath Tarate", "age": 59, "gender": "M", "cloth": "खादी कुर्ता, पांढरी टोपी (Khadi kurta, white cap)", "loc": "Lonand Halt", "cam": "CAM-08", "prio": "NORMAL", "status": LostPersonStatus.SEARCHING, "caller": "Eknath Tarate", "phone": "+91 98245 44332", "trans": "लोणंद येथे सोमनाथ तराटे हरवले आहेत."},
            {"name": "Subhash Gajanan Thorave", "age": 66, "gender": "M", "cloth": "पांढरा सदरा, चष्मा (White shirt, reading glasses)", "loc": "Taradgaon", "cam": "CAM-08", "prio": "HIGH", "status": LostPersonStatus.SEARCHING, "caller": "Gajanan Thorave", "phone": "+91 98910 77881", "trans": "तरडगाव येथे सुभाष थोरावे हरवले आहेत."},
            {"name": "Sudam Haribhau Ughade", "age": 77, "gender": "M", "cloth": "पांढरे धोतर, कांबळी, तुळशी माळ (Dhoti, blanket, Tulsi mala)", "loc": "Bhalwani Shelter", "cam": "CAM-12", "prio": "CRITICAL", "status": LostPersonStatus.SEARCHING, "caller": "Haribhau Ughade", "phone": "+91 97664 11223", "trans": "भालवणी येथे सुदाम उघाडे वय ७७ हरवले आहेत."},
            {"name": "Suresh Jagannath Vanve", "age": 60, "gender": "M", "cloth": "पांढरा सदरा, भगवा फेटा (White shirt, saffron turban)", "loc": "Pandharpur North Gate", "cam": "CAM-04", "prio": "NORMAL", "status": LostPersonStatus.MATCH_FOUND, "caller": "Jagannath Vanve", "phone": "+91 94242 66554", "trans": "उत्तर दरवाजा जवळ सुरेश वनवे हरवले आहेत."}
        ]


async def seed_lost_persons_internal(db, cam_map):
    from sqlalchemy import text
    fallback_cam_id = list(cam_map.values())[0] if cam_map else None

    # Delete existing
    await db.execute(text("DELETE FROM face_match_results"))
    await db.execute(text("DELETE FROM lost_person_reports"))
    await db.execute(text("DELETE FROM lost_person_cases"))
    await db.flush()

    lost_cases = []
    for idx, p in enumerate(PEOPLE_DATA, 1):
        case_num = f"#LF-{idx:03d}"
        res_time = datetime.now(timezone.utc) if p["status"] == LostPersonStatus.REUNITED else None
        
        c = LostPersonCase(
            case_number=case_num,
            name=p["name"],
            age=p["age"],
            gender=p["gender"],
            clothing_description=p["cloth"],
            last_seen_location=p["loc"],
            last_seen_camera_id=cam_map.get(p["cam"], fallback_cam_id),
            priority=p["prio"],
            status=p["status"],
            resolved_at=res_time,
            is_demo=True
        )
        lost_cases.append(c)

    db.add_all(lost_cases)
    await db.flush()

    reports = []
    matches = []
    for idx, (c, p) in enumerate(zip(lost_cases, PEOPLE_DATA), 1):
        rep = LostPersonReport(
            case_id=c.id,
            caller_name=p["caller"],
            caller_phone=p["phone"],
            transcript=p["trans"],
            language="mr",
            asr_confidence=round(0.92 + (idx % 8) * 0.01, 2)
        )
        reports.append(rep)

        if p["status"] == LostPersonStatus.MATCH_FOUND:
            m = FaceMatchResult(
                case_id=c.id,
                camera_id=cam_map.get(p["cam"], fallback_cam_id),
                frame_reference=f"frame_cctv_{idx:03d}.jpg",
                similarity_score=round(0.88 + (idx % 10) * 0.01, 2),
                confidence=round(0.93 + (idx % 6) * 0.01, 2),
                status=FaceMatchStatus.PENDING_VERIFICATION
            )
            matches.append(m)

    db.add_all(reports)
    db.add_all(matches)
    await db.flush()


async def seed_database(force_lost_cases: bool = False):
    async with AsyncSessionLocal() as db:
        # Check if users already exist
        existing_user = (await db.execute(select(User).limit(1))).scalar_one_or_none()
        existing_lost = (await db.execute(select(LostPersonCase))).scalars().all()
        
        if existing_user:
            if len(existing_lost) >= 100 and not force_lost_cases:
                logger.info("Database already seeded with 100+ cases. Skipping...")
                return
            logger.info("Database initialized previously. Refreshing 100 Lost Persons dataset...")
            cams = (await db.execute(select(Camera))).scalars().all()
            cam_map = {c.camera_code: c.id for c in cams}
            await seed_lost_persons_internal(db, cam_map)
            await db.commit()
            logger.info("Successfully refreshed 100 Lost Persons dataset!")
            return
            logger.info("Seeding users...")
            users = [
                User(
                    name="Command Center Controller",
                    email="control.room@mahapolice.gov.in",
                    phone="+91-9822001122",
                    password_hash=get_password_hash("varisetu2026"),
                    role=UserRole.ADMIN,
                    department="Maharashtra Police IT Cell",
                    is_active=True
                ),
                User(
                    name="Inspector R. K. Patil",
                    email="police.officer@mahapolice.gov.in",
                    phone="+91-9822003344",
                    password_hash=get_password_hash("varisetu2026"),
                    role=UserRole.POLICE,
                    department="Pandharpur Traffic Division",
                    is_active=True
                ),
                User(
                    name="Dr. Shubhada Deshmukh",
                    email="medical.team@varisetu.org",
                    phone="+91-9822005566",
                    password_hash=get_password_hash("varisetu2026"),
                    role=UserRole.MEDICAL,
                    department="Emergency Health Services",
                    is_active=True
                )
            ]
            db.add_all(users)
            await db.flush()

        # Zones & Cameras Map
        existing_zones = (await db.execute(select(Zone))).scalars().all()
        if not existing_zones:
            logger.info("Seeding zones...")
            zones = [
                Zone(name="Pandharpur Chowk", description="Main temple entry plaza bottleneck", latitude=17.6777, longitude=75.3276, capacity=60000, risk_level=RiskLevel.CRITICAL),
                Zone(name="Wakhri Phata", description="Major highway diversion and camp junction", latitude=17.7280, longitude=75.2950, capacity=45000, risk_level=RiskLevel.HIGH),
                Zone(name="Vakhri Naka", description="Bridge approach choke point", latitude=17.7500, longitude=75.2700, capacity=35000, risk_level=RiskLevel.HIGH),
                Zone(name="Saswad Highway Stop", description="Intermediate resting shelter", latitude=18.3440, longitude=74.0305, capacity=25000, risk_level=RiskLevel.MODERATE),
                Zone(name="Tarapur Phata", description="Bypass junction for supply convoys", latitude=17.8000, longitude=75.1500, capacity=20000, risk_level=RiskLevel.LOW),
                Zone(name="Alandi Corridor", description="Procession starting ghats", latitude=18.6772, longitude=73.8967, capacity=50000, risk_level=RiskLevel.LOW),
            ]
            db.add_all(zones)
            await db.flush()
            zone_map = {z.name: z.id for z in zones}
        else:
            zone_map = {z.name: z.id for z in existing_zones}

        existing_cams = (await db.execute(select(Camera))).scalars().all()
        if not existing_cams:
            logger.info("Seeding cameras...")
            cameras = [
                Camera(camera_code="CAM-01", name="Alandi Ghat Section Cam 01", zone_id=zone_map.get("Alandi Corridor"), latitude=18.6772, longitude=73.8967, status=CameraStatus.ONLINE),
                Camera(camera_code="CAM-04", name="Pandharpur Temple Chowk Cam 04", zone_id=zone_map.get("Pandharpur Chowk"), latitude=17.6777, longitude=75.3276, status=CameraStatus.ONLINE),
                Camera(camera_code="CAM-08", name="Saswad Highway Checkpoint Cam 08", zone_id=zone_map.get("Saswad Highway Stop"), latitude=18.3440, longitude=74.0305, status=CameraStatus.ONLINE),
                Camera(camera_code="CAM-12", name="Wakhri Phata Junction Cam 12", zone_id=zone_map.get("Wakhri Phata"), latitude=17.7280, longitude=75.2950, status=CameraStatus.ONLINE),
            ]
            db.add_all(cameras)
            await db.flush()
            cam_map = {c.camera_code: c.id for c in cameras}
        else:
            cam_map = {c.camera_code: c.id for c in existing_cams}

        logger.info("Seeding crowd observations...")
        observations = [
            CrowdObservation(camera_id=cam_map["CAM-04"], zone_id=zone_map["Pandharpur Chowk"], density_percentage=94.0, people_count=2850, movement_direction="SOUTH", trend=CrowdTrend.RISING, risk_level=RiskLevel.CRITICAL, source="DEMO"),
            CrowdObservation(camera_id=cam_map["CAM-12"], zone_id=zone_map["Wakhri Phata"], density_percentage=88.0, people_count=1420, movement_direction="EAST", trend=CrowdTrend.RISING, risk_level=RiskLevel.HIGH, source="DEMO"),
            CrowdObservation(camera_id=cam_map["CAM-08"], zone_id=zone_map["Saswad Highway Stop"], density_percentage=62.0, people_count=890, movement_direction="SOUTH", trend=CrowdTrend.EASING, risk_level=RiskLevel.MODERATE, source="DEMO"),
            CrowdObservation(camera_id=cam_map["CAM-01"], zone_id=zone_map["Alandi Corridor"], density_percentage=35.0, people_count=410, movement_direction="SOUTH", trend=CrowdTrend.STABLE, risk_level=RiskLevel.LOW, source="DEMO"),
            CrowdObservation(zone_id=zone_map["Vakhri Naka"], density_percentage=74.0, people_count=1100, trend=CrowdTrend.STABLE, risk_level=RiskLevel.HIGH, source="DEMO"),
            CrowdObservation(zone_id=zone_map["Tarapur Phata"], density_percentage=28.0, people_count=320, trend=CrowdTrend.FALLING, risk_level=RiskLevel.LOW, source="DEMO"),
        ]
        db.add_all(observations)

        logger.info("Seeding incidents & events...")
        incidents = [
            Incident(
                incident_number="INC-2026-0825-001",
                type=IncidentType.CROWD,
                severity=IncidentSeverity.HIGH,
                status=IncidentStatus.OPEN,
                source="CCTV_AI",
                zone_id=zone_map["Wakhri Phata"],
                camera_id=cam_map["CAM-12"],
                latitude=17.7280,
                longitude=75.2950,
                title="Crowd density surge detected at Wakhri Phata (88%)",
                description="Pedestrian flow bottleneck causing slow movement. Recommendation: Divert queue to North Ring Road.",
                is_demo=True
            ),
            Incident(
                incident_number="INC-2026-0825-002",
                type=IncidentType.ROAD_BLOCK,
                severity=IncidentSeverity.MEDIUM,
                status=IncidentStatus.IN_PROGRESS,
                source="OPERATOR",
                zone_id=zone_map["Saswad Highway Stop"],
                latitude=18.3440,
                longitude=74.0305,
                title="Solapur Highway Diversion Gate 2 opened",
                description="Traffic diverted to secondary bypass for VIP procession escort.",
                is_demo=True
            )
        ]
        db.add_all(incidents)
        await db.flush()

        events = [
            IncidentEvent(incident_id=incidents[0].id, event_type="CROWD_PEAK", message="CAM-12 Wakhri Phata: Density peak detected (88%)"),
            IncidentEvent(incident_id=incidents[1].id, event_type="ROUTE_DIVERTED", message="Solapur Highway Diversion Gate 2 opened for traffic relief")
        ]
        db.add_all(events)

        logger.info("Seeding 100 diverse lost person cases...")
        await seed_lost_persons_internal(db, cam_map)

        logger.info("Seeding medical alerts...")
        medical_alerts = [
            MedicalAlert(
                alert_code="MED-101",
                type=MedicalAlertType.FALL,
                severity=IncidentSeverity.HIGH,
                zone_id=zone_map["Wakhri Phata"],
                camera_id=cam_map["CAM-12"],
                latitude=17.7280,
                longitude=75.2950,
                description="FALL DETECTED / FAINTING PILGRIM (Wakhri Phata Km 184) - Dispatching First Responder",
                status=MedicalAlertStatus.ACTIVE,
                assigned_volunteer_name="Team Bravo (V. R. Kadam)",
                is_demo=True
            ),
            MedicalAlert(
                alert_code="MED-102",
                type=MedicalAlertType.HEAT_EXHAUSTION,
                severity=IncidentSeverity.HIGH,
                zone_id=zone_map["Pandharpur Chowk"],
                camera_id=cam_map["CAM-04"],
                latitude=17.6777,
                longitude=75.3276,
                description="CROWD HEAT EXHAUSTION RISK (SECTOR 5) - Ambient Temp 34°C, High Humidity",
                status=MedicalAlertStatus.ACTIVE,
                assigned_volunteer_name="Medical Van #MV-02",
                is_demo=True
            ),
            MedicalAlert(
                alert_code="MED-098",
                type=MedicalAlertType.DEHYDRATION,
                severity=IncidentSeverity.MEDIUM,
                zone_id=zone_map["Saswad Highway Stop"],
                latitude=18.3440,
                longitude=74.0305,
                description="DEHYDRATION ASSIST & REHYDRATION (RESOLVED) - Pilgrim treated with ORSL salt packets",
                status=MedicalAlertStatus.RESOLVED,
                assigned_volunteer_name="Red Cross Volunteer Post #3",
                resolved_at=datetime.now(timezone.utc),
                is_demo=True
            )
        ]
        db.add_all(medical_alerts)

        logger.info("Seeding resources & vehicles...")
        resources = [
            Resource(resource_code="WT-09", name="10,000L Water Tanker #09", resource_type=ResourceType.WATER_TANKER, capacity=10000, status_tag="OPTIMAL", availability=ResourceAvailability.AVAILABLE, latitude=17.7280, longitude=75.2950, zone_id=zone_map["Wakhri Phata"], location_description="Wakhri Station Standby"),
            Resource(resource_code="WT-04", name="10,000L Water Tanker #04", resource_type=ResourceType.WATER_TANKER, capacity=10000, status_tag="DEPLOYED", availability=ResourceAvailability.ASSIGNED, latitude=17.6777, longitude=75.3276, zone_id=zone_map["Pandharpur Chowk"], location_description="Temple Gate North"),
            Resource(resource_code="WT-12", name="10,000L Water Tanker #12", resource_type=ResourceType.WATER_TANKER, capacity=10000, status_tag="OPTIMAL", availability=ResourceAvailability.AVAILABLE, latitude=18.3440, longitude=74.0305, zone_id=zone_map["Saswad Highway Stop"], location_description="Saswad Rest Post"),
            Resource(resource_code="MV-02", name="Mobile Medical Van #02 (Ambulance)", resource_type=ResourceType.MEDICAL_VAN, capacity=4, status_tag="ACTIVE", availability=ResourceAvailability.ASSIGNED, latitude=17.7280, longitude=75.2950, zone_id=zone_map["Wakhri Phata"], location_description="Wakhri Sector 4 Base"),
            Resource(resource_code="MV-05", name="Emergency Ambulance #05", resource_type=ResourceType.AMBULANCE, capacity=2, status_tag="STANDBY", availability=ResourceAvailability.AVAILABLE, latitude=17.6777, longitude=75.3276, zone_id=zone_map["Pandharpur Chowk"], location_description="Pandharpur Civil Hospital"),
            Resource(resource_code="PS-14", name="Police Patrol Squad #14", resource_type=ResourceType.POLICE_SQUAD, capacity=8, status_tag="ACTIVE", availability=ResourceAvailability.ON_SCENE, latitude=17.7280, longitude=75.2950, zone_id=zone_map["Wakhri Phata"], location_description="Wakhri Bottleneck Patrol"),
            Resource(resource_code="VT-08", name="Dindi Volunteer Stewards (Squad 8)", resource_type=ResourceType.VOLUNTEER_TEAM, capacity=25, status_tag="ACTIVE", availability=ResourceAvailability.AVAILABLE, latitude=17.6777, longitude=75.3276, zone_id=zone_map["Pandharpur Chowk"], location_description="Chhatrapati Shivaji Chowk"),
        ]
        db.add_all(resources)

        logger.info("Seeding routes...")
        routes = [
            Route(name="NH-9 Solapur Highway Junction", description="Primary vehicle thoroughfare", status=RouteStatus.DIVERTED, priority="PRIMARY", latitude_start=17.7280, longitude_start=75.2950, latitude_end=17.6777, longitude_end=75.3276),
            Route(name="Pune-Saswad Pilgrimage Road", description="Dedicated pedestrian corridor for Palkhi procession", status=RouteStatus.PILGRIMS_ONLY, priority="PRIMARY", latitude_start=18.6772, longitude_start=73.8967, latitude_end=18.3440, longitude_end=74.0305),
            Route(name="Wakhri Phata Inner Access Road", description="Narrow passage near temporary tents", status=RouteStatus.CLOSED, priority="SECONDARY", latitude_start=17.7280, longitude_start=75.2950, latitude_end=17.7500, longitude_end=75.2700),
            Route(name="Pandharpur Temple Ring Road", description="Reserved exclusively for ambulances and police emergency vehicles", status=RouteStatus.EMERGENCY_ACCESS, priority="PRIMARY", latitude_start=17.6777, longitude_start=75.3276, latitude_end=17.6850, longitude_end=75.3400),
        ]
        db.add_all(routes)

        logger.info("Seeding notifications...")
        notifications = [
            Notification(type=NotificationType.CROWD, title="Crowd Congestion Warning", message="Density at Wakhri Phata crossed 85%. Automated queue diversion suggested.", priority="HIGH"),
            Notification(type=NotificationType.MEDICAL, title="Medical Emergency Dispatched", message="Ambulance MV-02 dispatched to Sector 4 for fainting pilgrim.", priority="HIGH"),
            Notification(type=NotificationType.LOST_PERSON, title="AI Face Match Candidate", message="Candidate match with 89% similarity found on CAM-04 for #LF-802.", priority="NORMAL"),
        ]
        db.add_all(notifications)

        logger.info("Seeding Yatra / Palkhi live state...")
        from app.models.yatra import Yatra, YatraStatus, YatraTrack
        from app.models.announcement import PublicAnnouncement, AnnouncementStatus

        yatra = Yatra(
            name="Sant Tukaram Maharaj Palkhi",
            type="PALKHI",
            status=YatraStatus.LIVE,
            current_latitude=17.7280,
            current_longitude=75.2950,
            current_speed=2.8,
            current_heading=145.0,
            current_accuracy=5.0,
            active_tracker_id="PALKHI-TUKARAM-01"
        )
        db.add(yatra)
        await db.flush()

        track_pts = [
            YatraTrack(yatra_id=yatra.id, tracker_id="PALKHI-TUKARAM-01", latitude=18.0400, longitude=74.1900, speed_kmph=3.0, heading=140.0, source="GPS_DEVICE", sequence_number=1),
            YatraTrack(yatra_id=yatra.id, tracker_id="PALKHI-TUKARAM-01", latitude=17.8900, longitude=75.0200, speed_kmph=2.9, heading=142.0, source="GPS_DEVICE", sequence_number=2),
            YatraTrack(yatra_id=yatra.id, tracker_id="PALKHI-TUKARAM-01", latitude=17.7280, longitude=75.2950, speed_kmph=2.8, heading=145.0, source="GPS_DEVICE", sequence_number=3),
        ]
        db.add_all(track_pts)

        logger.info("Seeding Public Announcements...")
        announcements = [
            PublicAnnouncement(
                message_mr="सर्व वारकऱ्यांना नम्र विनंती: वाखरी फाटा येथे गर्दी जास्त असल्याने कृपया पर्यायी पायी मार्गाचा वापर करावा.",
                message_en="All pilgrims are requested to use the designated pedestrian bypass route due to high crowd density at Wakhri Phata.",
                priority="HIGH",
                status=AnnouncementStatus.BROADCAST,
                broadcast_at=datetime.now(timezone.utc)
            ),
            PublicAnnouncement(
                message_mr="विनामूल्य ओआरएसएल (ORSL) आणि पाणी वाटप केंद्र क्र. ४ वर उपलब्ध आहे.",
                message_en="Free ORSL rehydration sachets and drinking water available at Hub No. 4.",
                priority="NORMAL",
                status=AnnouncementStatus.APPROVED
            )
        ]
        db.add_all(announcements)

        await db.commit()
        logger.info("Database seeding completed successfully!")


if __name__ == "__main__":
    asyncio.run(seed_database())


