"""Bagrat Motors = umbrella brand; Vulkanizacia.ge and Towing.ge are its sub-brands.

Builds on bagratmotors.ge only (the sub-sites are never touched):
  - 8 hub pages for services the sub-brands offer (ka/en/ru, unique text, "provided by" badge, sub-brand phone)
  - additive changes to existing pages: sub-brand badge, sub-brand phone on tyre/wheel pages (body + JSON-LD only,
    never <title>/meta), new links in the "other services" lists
  - homepage: new cards in the service groups, "our brands" section, Organization.subOrganization, offer catalogue
  - sitemap.xml and llms.txt blocks
Idempotent (marker blocks). Run:  python3 tools/build_hub.py && npm run build
"""
import json
import re
from datetime import date
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://bagratmotors.ge"
LANGS = ("ka", "en", "ru")
HOME = {"ka": "/", "en": "/en/", "ru": "/ru/"}
PREFIX = {"ka": "", "en": "/en", "ru": "/ru"}
LOCALE = {"ka": "ka_GE", "en": "en_US", "ru": "ru_RU"}

BRANDS = {
    "vulk": dict(name="Vulkanizacia.ge", url="https://vulkanizacia.ge", tel="+995591909013", tel_fmt="591 90 90 13", wa="995591909013"),
    "tow": dict(name="Towing.ge", url="https://towing.ge", tel="+995514908090", tel_fmt="514 90 80 90", wa="995514908090"),
}
GROUP = {  # breadcrumb parent per sub-brand (existing bagratmotors group pages)
    "vulk": {"ka": ("მოძრავი ვულკანიზაცია", "/services/vulkanizacia/"), "en": ("Mobile tyre service", "/en/services/vulcanization/"),
             "ru": ("Выездная вулканизация", "/ru/services/vulkanizaciya/")},
    "tow": {"ka": ("ევაკუატორი", "/services/evakuatori/"), "en": ("Towing", "/en/services/towing/"), "ru": ("Эвакуатор", "/ru/services/evakuator/")},
}

UI = {
    "ka": dict(home="მთავარი", services="სერვისები", contact="კონტაქტი", menu="მენიუ", call="დარეკვა", call_now="დაგვირეკეთ ახლავე",
               other="სხვა სერვისები", inc="რას მოიცავს სერვისი", faq="ხშირად დასმული კითხვები", contact_h="დაგვიკავშირდით",
               contact_p="ვმუშაობთ 24/7 — დაგვირეკეთ ნებისმიერ დროს.", phone="ტელეფონი", email="ელ. ფოსტა", location="მდებარეობა",
               loc_v="თბილისი, საქართველო", hours="სამუშაო საათები", lang="ენა", tag="24/7 · თბილისი", lang_full="ქართული",
               foot="ევაკუატორი, ვულკანიზაცია და მინი ექსკავატორი — თბილისში, 24/7.", copy="© 2026 Bagrat Motors · თბილისი", more="ვრცლად →",
               by="მომსახურებას ახორციელებს {b} — Bagrat Motors-ის ბრენდი.", by_btn="ვრცლად {b}-ზე →", by_label="Bagrat Motors-ის ბრენდი",
               brands_kicker="ჩვენი ბრენდები", brands_h="Bagrat Motors — ერთი კომპანია, ორი სპეციალიზებული ბრენდი",
               brands_p="ევაკუატორს და საგზაო დახმარებას Towing.ge ემსახურება, საბურავებსა და მანქანის მოვლას — Vulkanizacia.ge.",
               brand_desc={"vulk": "მოძრავი ვულკანიზაცია, საბურავები, ხუნდები, რეცხვა, ქიმწმენდა და ფარების პოლირება — ადგილზე, 24/7.",
                           "tow": "ევაკუატორი, ობობა ევაკუატორი, ავტოტრანსპორტირება და ფხიზელი მძღოლი — 24/7."},
               visit="საიტზე გადასვლა →"),
    "en": dict(home="Home", services="Services", contact="Contact", menu="Menu", call="Call", call_now="Call us now",
               other="Other services", inc="What's included", faq="Frequently asked questions", contact_h="Get in touch",
               contact_p="We work 24/7 — call us any time.", phone="Phone", email="Email", location="Location",
               loc_v="Tbilisi, Georgia", hours="Working hours", lang="Language", tag="24/7 · Tbilisi", lang_full="English",
               foot="Towing, mobile tyre service and mini-excavator — in Tbilisi, 24/7.", copy="© 2026 Bagrat Motors · Tbilisi", more="More →",
               by="This service is provided by {b}, a Bagrat Motors brand.", by_btn="More on {b} →", by_label="a Bagrat Motors brand",
               brands_kicker="Our brands", brands_h="Bagrat Motors — one company, two specialist brands",
               brands_p="Towing and roadside help are run by Towing.ge; tyres and car care by Vulkanizacia.ge.",
               brand_desc={"vulk": "Mobile tyre service, tyres, brakes, car wash, interior cleaning and headlight polishing — on site, 24/7.",
                           "tow": "Tow truck, spider tow truck, vehicle transport and sober driver — 24/7."},
               visit="Visit the website →"),
    "ru": dict(home="Главная", services="Услуги", contact="Контакты", menu="Меню", call="Позвонить", call_now="Позвоните прямо сейчас",
               other="Другие услуги", inc="Что входит в услугу", faq="Часто задаваемые вопросы", contact_h="Свяжитесь с нами",
               contact_p="Работаем 24/7 — звоните в любое время.", phone="Телефон", email="Эл. почта", location="Местоположение",
               loc_v="Тбилиси, Грузия", hours="Часы работы", lang="Язык", tag="24/7 · Тбилиси", lang_full="Русский",
               foot="Эвакуатор, выездная вулканизация и мини-экскаватор — в Тбилиси, 24/7.", copy="© 2026 Bagrat Motors · Тбилиси", more="Подробнее →",
               by="Услугу оказывает {b} — бренд Bagrat Motors.", by_btn="Подробнее на {b} →", by_label="бренд Bagrat Motors",
               brands_kicker="Наши бренды", brands_h="Bagrat Motors — одна компания, два специализированных бренда",
               brands_p="Эвакуатором и помощью на дороге занимается Towing.ge, шинами и уходом за машиной — Vulkanizacia.ge.",
               brand_desc={"vulk": "Выездная вулканизация, шины, тормозные колодки, мойка, химчистка и полировка фар — на месте, 24/7.",
                           "tow": "Эвакуатор, эвакуатор-паук, автоперевозка и трезвый водитель — 24/7."},
               visit="Перейти на сайт →"),
}

CHECK = '<svg class="h-5 w-5 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" aria-hidden="true"><path d="M20 6 9 17l-5-5"/></svg>'
PHONE_SVG = '<svg class="mr-1.5 inline-block h-[1em] w-[1em] align-[-0.125em]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3 19.5 19.5 0 0 1-6-6 19.8 19.8 0 0 1-3-8.6A2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.3 1.8.6 2.6a2 2 0 0 1-.5 2.1L8 9.6a16 16 0 0 0 6 6l1.2-1.2a2 2 0 0 1 2.1-.5c.8.3 1.7.5 2.6.6a2 2 0 0 1 1.7 2Z"/></svg>'
WA_SVG = '<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2a10 10 0 0 0-8.5 15.2L2 22l4.9-1.3A10 10 0 1 0 12 2Zm5.3 14.1c-.2.6-1.3 1.2-1.8 1.2-.5.1-1 .1-1.7-.1-.4-.1-.9-.3-1.6-.6-2.8-1.2-4.6-4-4.7-4.2-.1-.2-1.1-1.5-1.1-2.8s.7-2 .9-2.2c.2-.2.5-.3.7-.3h.5c.2 0 .4 0 .6.5l.8 1.9c.1.2.1.3 0 .5l-.4.6c-.2.2-.3.4-.1.7.2.3.8 1.3 1.7 2.1 1.2 1 2.1 1.4 2.4 1.5.2.1.4.1.6-.1l.7-.9c.2-.2.4-.2.6-.1l1.8.9c.3.1.4.2.5.3.1.2.1.6-.1 1.1Z"/></svg>'
VIBER_SVG = '<svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor"><path d="M12 3c-4.5 0-8 2.9-8 6.6 0 2 1 3.8 2.7 5v3l2.7-1.6c.8.2 1.7.3 2.6.3 4.5 0 8-2.9 8-6.6S16.5 3 12 3Z"/></svg>'
CALL_SVG = '<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3 19.5 19.5 0 0 1-6-6 19.8 19.8 0 0 1-3-8.6A2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.3 1.8.6 2.6a2 2 0 0 1-.5 2.1L8 9.6a16 16 0 0 0 6 6l1.2-1.2a2 2 0 0 1 2.1-.5c.8.3 1.7.5 2.6.6a2 2 0 0 1 1.7 2Z"/></svg>'

# ------------------------------------------------------------------ the 8 hub services (unique text — never copied from the sub-sites)
V, T_ = "vulk", "tow"
VSUB = lambda slug: {"ka": f"/services/{slug}/", "en": f"/services/{slug}/index-en.html", "ru": f"/services/{slug}/index-ru.html"}
HUB = [
    dict(key="brakes", brand=V, img="brakes", sub=VSUB("khundebis-shecvla"),
         slug=dict(ka="khundebis-shecvla", en="brake-pad-replacement", ru="zamena-tormoznyh-kolodok"),
         icon='<circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="2.5"/><path d="M16 5.5a7.5 7.5 0 0 1 2.5 6.5"/>',
         ka=dict(title="ხუნდების შეცვლა გამოძახებით თბილისში | Bagrat Motors", h1="ხუნდების შეცვლა გამოძახებით",
                 desc="ხუნდების შეცვლა გამოძახებით თბილისში — Bagrat Motors-ის ბრენდი Vulkanizacia.ge მოვა თქვენთან: წინა და უკანა ხუნდები, დისკები და სენსორი, 24/7.",
                 kw="ხუნდების შეცვლა, ხუნდების შეცვლა გამოძახებით, ხუნდების შეცვლა ადგილზე, სამუხრუჭე ხუნდების შეცვლა, Bagrat Motors",
                 lead="Bagrat Motors-ის გუნდი ხუნდებს თქვენს ეზოში ან ავტოსადგომზე შეცვლის — სერვისში მისვლა და რიგში ლოდინი აღარ გჭირდებათ.",
                 card="წინა და უკანა ხუნდები, დისკები და ცვეთის სენსორი — ადგილზე.",
                 inc=["წინა და უკანა ხუნდების შეცვლა", "სამუხრუჭე დისკების შეცვლა", "ცვეთის სენსორის შეცვლა", "ხუნდები თქვენი მანქანისთვის — ან თქვენი შეძენილი"],
                 sec=[("რატომ არ უნდა გადადოთ", "გაცვეთილი ხუნდი ზრდის დამუხრუჭების მანძილს და ზიანს აყენებს დისკს — მერე უკვე ორივეს შეცვლა გიწევთ. ჭრიალი, ნიშანი დაფაზე ან პედლის ვიბრაცია იმის ნიშანია, რომ შემოწმების დროა."),
                      ("ფასი", "ფასი დამოკიდებულია მარკასა და მოდელზე. დაგვირეკეთ, გვითხარით მანქანის მონაცემები და ფასს წინასწარ შეგითანხმებთ.")],
                 faq=[("ხუნდებს თქვენ მოიტანთ?", "დიახ — შევარჩევთ თქვენი მანქანისთვის, ან დაგიყენებთ თქვენ მიერ შეძენილს."),
                      ("რამდენ ხანში მოხვალთ?", "თბილისში ჩვეულებრივ 20–30 წუთში."), ("ღამითაც მუშაობთ?", "დიახ, 24/7.")]),
         en=dict(title="Brake pad replacement on site in Tbilisi | Bagrat Motors", h1="Brake pad replacement on site",
                 desc="Brake pad replacement at your place in Tbilisi — Bagrat Motors' brand Vulkanizacia.ge comes to you: front and rear pads, discs and wear sensors, 24/7.",
                 kw="brake pad replacement Tbilisi, mobile brake repair, brake pads Tbilisi, Bagrat Motors",
                 lead="The Bagrat Motors team replaces your brake pads in your yard or car park — no workshop visit, no queue.",
                 card="Front and rear pads, discs and wear sensors — on site.",
                 inc=["Front and rear brake pads", "Brake disc replacement", "Wear sensor replacement", "Pads for your car — or the ones you bought"],
                 sec=[("Why not to wait", "A worn pad lengthens the braking distance and damages the disc — then you pay for both. Squeaking, a dashboard warning light or a vibrating pedal mean it's time for a check."),
                      ("Price", "The price depends on the make and model. Call us with your car's details and we agree the price in advance.")],
                 faq=[("Do you bring the pads?", "Yes — we pick pads for your car, or fit the ones you bought."),
                      ("How fast do you arrive?", "Usually within 20–30 minutes in Tbilisi."), ("Do you work at night?", "Yes, 24/7.")]),
         ru=dict(title="Замена тормозных колодок с выездом в Тбилиси | Bagrat Motors", h1="Замена тормозных колодок с выездом",
                 desc="Замена тормозных колодок с выездом в Тбилиси — бренд Bagrat Motors Vulkanizacia.ge приедет к вам: передние и задние колодки, диски и датчик износа, 24/7.",
                 kw="замена тормозных колодок с выездом, замена колодок Тбилиси, тормозные колодки Тбилиси, Bagrat Motors",
                 lead="Команда Bagrat Motors заменит колодки у вас во дворе или на парковке — без поездки в сервис и очередей.",
                 card="Передние и задние колодки, диски и датчик износа — на месте.",
                 inc=["Передние и задние колодки", "Замена тормозных дисков", "Замена датчика износа", "Колодки под вашу машину — или ваши"],
                 sec=[("Почему не стоит откладывать", "Изношенная колодка увеличивает тормозной путь и портит диск — и тогда менять приходится и то и другое. Скрип, индикатор на панели или вибрация педали — пора на проверку."),
                      ("Цена", "Цена зависит от марки и модели. Позвоните, назовите данные машины — согласуем цену заранее.")],
                 faq=[("Вы привозите колодки?", "Да — подберём под вашу машину или установим купленные вами."),
                      ("Как быстро приедете?", "По Тбилиси обычно за 20–30 минут."), ("Работаете ночью?", "Да, 24/7.")])),
    dict(key="wash", brand=V, img="car-wash", sub=VSUB("mankanis-recxva"),
         slug=dict(ka="mankanis-recxva", en="car-wash-at-home", ru="moyka-mashiny-na-domu"),
         icon='<path d="M12 3.5c-2.6 3.3-4.5 6-4.5 8.4a4.5 4.5 0 0 0 9 0c0-2.4-1.9-5.1-4.5-8.4Z"/><path d="M4 21h16"/>',
         ka=dict(title="მანქანის რეცხვა ადგილზე თბილისში | Bagrat Motors", h1="მანქანის რეცხვა ადგილზე",
                 desc="მანქანის რეცხვა ადგილზე თბილისში — Bagrat Motors-ის ბრენდი Vulkanizacia.ge მანქანას გარეცხავს სახლთან ან ოფისთან, საკუთარი წყლითა და დენით, 24/7.",
                 kw="მანქანის რეცხვა ადგილზე, მანქანის რეცხვა გამოძახებით, მობილური სამრეცხაო, მანქანის რეცხვა თბილისი, Bagrat Motors",
                 lead="მანქანა ეზოში დგას, დრო კი არ გაქვთ? Bagrat Motors-ის გუნდი მოვა და იქვე გარეცხავს — ონკანი და დენი არ გჭირდებათ.",
                 card="გარეცხვა სახლთან ან ოფისთან — წყალი და დენი ჩვენზეა.",
                 inc=["ძარის რეცხვა გარედან", "დისკებისა და საბურავების რეცხვა", "სალონის მტვერსასრუტით დასუფთავება და მინები", "ძრავის რეცხვა — სურვილისამებრ"],
                 sec=[("ვისთვის არის", "მოსახერხებელია მათთვის, ვისაც სამრეცხაოში რიგისთვის დრო არ აქვს — ოჯახის მანქანისთვის, ოფისის ავტოპარკისთვის ან მანქანის გაყიდვის წინ."),
                      ("ფასი", "ფასი დამოკიდებულია მანქანის ზომასა და იმაზე, რას მოიცავს რეცხვა. დაგვირეკეთ ან მოგვწერეთ — წინასწარ შეგითანხმებთ.")],
                 faq=[("წყალი და დენი უნდა მოგცეთ?", "არა, ყველაფერი თან მოგვაქვს."),
                      ("რამდენიმე მანქანას ერთად რეცხავთ?", "დიახ — ოჯახის ან კომპანიის რამდენიმე მანქანას ერთ ვიზიტზე."), ("ღამითაც მოდიხართ?", "დიახ, ვმუშაობთ 24/7.")]),
         en=dict(title="Car wash at your home in Tbilisi | Bagrat Motors", h1="Car wash at your home",
                 desc="Car wash at your home or office in Tbilisi — Bagrat Motors' brand Vulkanizacia.ge brings its own water and power, 24/7.",
                 kw="car wash at home Tbilisi, mobile car wash Tbilisi, car wash Tbilisi, Bagrat Motors",
                 lead="Car parked at home and no time for a car wash? The Bagrat Motors team comes and washes it right there — no tap or socket needed.",
                 card="Washed at home or at the office — water and power on us.",
                 inc=["Exterior body wash", "Wheels and tyres", "Interior vacuum and windows", "Engine wash — on request"],
                 sec=[("Who it's for", "Handy if you have no time to queue at a car wash — for the family car, an office fleet or before selling a car."),
                      ("Price", "It depends on the car size and what the wash includes. Call or message us — we agree the price in advance.")],
                 faq=[("Do I need to provide water or power?", "No, we bring everything."),
                      ("Can you wash several cars at once?", "Yes — several family or company cars in one visit."), ("Do you come at night?", "Yes, we work 24/7.")]),
         ru=dict(title="Мойка машины на дому в Тбилиси | Bagrat Motors", h1="Мойка машины на дому",
                 desc="Мойка машины на дому или у офиса в Тбилиси — бренд Bagrat Motors Vulkanizacia.ge привозит свою воду и электричество, 24/7.",
                 kw="мойка машины на дому, мойка авто на выезд, выездная мойка Тбилиси, мойка Тбилиси, Bagrat Motors",
                 lead="Машина стоит во дворе, а времени нет? Команда Bagrat Motors приедет и помоет её прямо там — кран и розетка не нужны.",
                 card="Мойка у дома или офиса — вода и электричество наши.",
                 inc=["Мойка кузова", "Мойка колёс и дисков", "Пылесос салона и стёкла", "Мойка двигателя — по желанию"],
                 sec=[("Для кого", "Удобно, если нет времени стоять в очереди на мойке, — для семейной машины, офисного автопарка или перед продажей авто."),
                      ("Цена", "Зависит от размера машины и состава мойки. Позвоните или напишите — согласуем заранее.")],
                 faq=[("Нужно ли давать воду или электричество?", "Нет, всё привозим с собой."),
                      ("Моете несколько машин сразу?", "Да — несколько машин семьи или компании за один выезд."), ("Приезжаете ночью?", "Да, работаем 24/7.")])),
    dict(key="interior", brand=V, img="car-interior", sub=VSUB("mankanis-qimwmenda"),
         slug=dict(ka="mankanis-qimwmenda", en="car-interior-cleaning", ru="himchistka-salona"),
         icon='<path d="M5 18v-6a3 3 0 0 1 3-3h2a3 3 0 0 1 3 3v6"/><path d="M4 18h10"/><path d="M17 4v4M15 6h4M19 12v3M17.5 13.5h3"/>',
         ka=dict(title="მანქანის სალონის ქიმწმენდა თბილისში | Bagrat Motors", h1="მანქანის სალონის ქიმწმენდა",
                 desc="მანქანის სალონის ქიმწმენდა თბილისში ორთქლით — Bagrat Motors-ის ბრენდი Vulkanizacia.ge მოვა თქვენთან: სავარძლები, ჭერი, ნოხები და ტყავი, 24/7.",
                 kw="მანქანის სალონის ქიმწმენდა, სალონის ქიმწმენდა, მანქანის ქიმწმენდა ორთქლით, მანქანის ქიმწმენდა გამოძახებით, Bagrat Motors",
                 lead="ლაქები სავარძლებზე, სუნი ან ზამთრის ტალახი — Bagrat Motors-ის გუნდი სალონს ორთქლით გაწმენდს იქ, სადაც მანქანა დგას.",
                 card="სავარძლები, ჭერი, ნოხები და ტყავი — ორთქლით, ადგილზე.",
                 inc=["ქსოვილისა და ტყავის სავარძლები", "ჭერისა და კარების წმენდა", "ნოხები და იატაკი", "პანელი და საჭე"],
                 sec=[("ორთქლის უპირატესობა", "ორთქლი ღრმად ხსნის ჭუჭყს და სალონს ზედმეტად არ ასველებს, ამიტომ მანქანის გამოყენებას მალევე შეძლებთ."),
                      ("ფასი", "ფასი დამოკიდებულია მანქანის ზომასა და სალონის მდგომარეობაზე. გამოგვიგზავნეთ ფოტო WhatsApp-ზე — ფასს წინასწარ გეტყვით.")],
                 faq=[("ტყავის სალონს წმენდთ?", "დიახ, ტყავისთვის შესაფერისი საშუალებით."),
                      ("რამდენ ხანს გრძელდება?", "სრულ ქიმწმენდას რამდენიმე საათი სჭირდება."), ("ღამითაც მოდიხართ?", "დიახ, 24/7.")]),
         en=dict(title="Car interior steam cleaning in Tbilisi | Bagrat Motors", h1="Car interior steam cleaning",
                 desc="Car interior steam cleaning in Tbilisi — Bagrat Motors' brand Vulkanizacia.ge comes to you: seats, ceiling, mats and leather, 24/7.",
                 kw="car interior cleaning Tbilisi, steam car cleaning, car detailing Tbilisi, Bagrat Motors",
                 lead="Stains on the seats, a smell or winter mud — the Bagrat Motors team steam cleans the interior wherever the car is parked.",
                 card="Seats, ceiling, mats and leather — steam cleaned on site.",
                 inc=["Fabric and leather seats", "Ceiling and door panels", "Mats and floor", "Dashboard and steering wheel"],
                 sec=[("Why steam", "Steam lifts dirt deep down without soaking the interior, so you can use the car again soon."),
                      ("Price", "It depends on the car size and the condition of the interior. Send a photo on WhatsApp and we'll tell you the price in advance.")],
                 faq=[("Do you clean leather?", "Yes, with a product suitable for leather."),
                      ("How long does it take?", "A full interior clean takes a few hours."), ("Do you come at night?", "Yes, 24/7.")]),
         ru=dict(title="Химчистка салона автомобиля в Тбилиси | Bagrat Motors", h1="Химчистка салона автомобиля",
                 desc="Химчистка салона автомобиля паром в Тбилиси — бренд Bagrat Motors Vulkanizacia.ge приедет к вам: сиденья, потолок, коврики и кожа, 24/7.",
                 kw="химчистка салона автомобиля, химчистка салона Тбилиси, химчистка салона паром, химчистка авто с выездом, Bagrat Motors",
                 lead="Пятна на сиденьях, запах или зимняя грязь — команда Bagrat Motors почистит салон паром там, где стоит машина.",
                 card="Сиденья, потолок, коврики и кожа — паром, на месте.",
                 inc=["Тканевые и кожаные сиденья", "Потолок и обивка дверей", "Коврики и пол", "Панель и руль"],
                 sec=[("Почему паром", "Пар глубоко удаляет грязь и не мочит салон, поэтому машиной можно пользоваться вскоре после чистки."),
                      ("Цена", "Зависит от размера машины и состояния салона. Пришлите фото в WhatsApp — скажем цену заранее.")],
                 faq=[("Чистите кожаный салон?", "Да, подходящим для кожи средством."),
                      ("Сколько длится?", "Полная химчистка занимает несколько часов."), ("Приезжаете ночью?", "Да, 24/7.")])),
    dict(key="lights", brand=V, img="headlights", sub=VSUB("parebis-polireba"),
         slug=dict(ka="parebis-polireba", en="headlight-polishing", ru="polirovka-far"),
         icon='<path d="M9 18h6M10 21h4"/><path d="M12 3a6 6 0 0 0-3.5 10.9c.6.5 1 1.2 1 2V16h5v-.1c0-.8.4-1.5 1-2A6 6 0 0 0 12 3Z"/>',
         ka=dict(title="ფარების პოლირება ორთქლით და ნათურების შეცვლა | Bagrat Motors", h1="ფარების პოლირება და ნათურების შეცვლა",
                 desc="ფარების პოლირება ორთქლით ან ხელით და მანქანის ნათურების შეცვლა თბილისში — Bagrat Motors-ის ბრენდი Vulkanizacia.ge, ადგილზე, 24/7.",
                 kw="ფარების პოლირება ორთქლით, ფარების პოლირება, ნათურის შეცვლა, მანქანის ნათურები h4 h7 h11, Bagrat Motors",
                 lead="მკრთალი, გაყვითლებული ფარები ღამით გზას ცუდად ანათებს. Bagrat Motors-ის გუნდი ფარებს ადგილზე გააპრიალებს და დამწვარ ნათურასაც შეცვლის.",
                 card="ფარების პოლირება ორთქლით ან ხელით, ნათურების შეცვლა.",
                 inc=["ფარების პოლირება ორთქლით", "ხელით პოლირება მსუბუქად დაბინდულ ფარებზე", "ნათურები H1, H4, H7, H11 და ლედ", "გაბარიტისა და სანისლე ფარის ნათურები"],
                 sec=[("მეთოდის არჩევა", "ძლიერ გაყვითლებულ ფარს ორთქლით ვაპრიალებთ, მსუბუქად დაბინდულს — ხელით. მეთოდს ადგილზე, ფარის მდგომარეობის მიხედვით ვარჩევთ."),
                      ("ფასი", "გამოგვიგზავნეთ ფარების ფოტო WhatsApp-ზე — ფასს წინასწარ გეტყვით.")],
                 faq=[("ნათურას მოიტანთ?", "დიახ — ან დაგიყენებთ თქვენსას."),
                      ("ტექდათვალიერებამდე ღირს?", "დიახ — გამჭვირვალე ფარები და მუშა ნათურები ტექდათვალიერებისთვის მნიშვნელოვანია."), ("ღამითაც მოდიხართ?", "დიახ, 24/7.")]),
         en=dict(title="Headlight polishing and bulb replacement in Tbilisi | Bagrat Motors", h1="Headlight polishing and bulb replacement",
                 desc="Headlight polishing with steam or by hand and car bulb replacement in Tbilisi — Bagrat Motors' brand Vulkanizacia.ge, on site, 24/7.",
                 kw="headlight polishing Tbilisi, headlight restoration, car bulb replacement, H4 H7 H11 bulbs, Bagrat Motors",
                 lead="Dull, yellowed headlights light the road poorly at night. The Bagrat Motors team polishes them on site and replaces a dead bulb too.",
                 card="Headlight polishing with steam or by hand, bulb replacement.",
                 inc=["Steam headlight polishing", "Hand polishing for lightly clouded headlights", "H1, H4, H7, H11 and LED bulbs", "Side light and fog light bulbs"],
                 sec=[("Choosing the method", "Badly yellowed headlights are steam polished, lightly clouded ones by hand. We choose on site, based on the headlight's condition."),
                      ("Price", "Send a photo of the headlights on WhatsApp and we'll tell you the price in advance.")],
                 faq=[("Do you bring the bulb?", "Yes — or we fit yours."),
                      ("Is it worth doing before a technical inspection?", "Yes — clear headlights and working bulbs matter for the inspection."), ("Do you come at night?", "Yes, 24/7.")]),
         ru=dict(title="Полировка фар паром в Тбилиси | Bagrat Motors", h1="Полировка фар и замена ламп",
                 desc="Полировка фар паром или вручную и замена ламп в Тбилиси — бренд Bagrat Motors Vulkanizacia.ge, на месте, 24/7.",
                 kw="полировка фар паром, полировка фар Тбилиси, замена ламп в фарах, лампы H4 H7 H11, Bagrat Motors",
                 lead="Тусклые, пожелтевшие фары плохо освещают дорогу ночью. Команда Bagrat Motors отполирует их на месте и заменит перегоревшую лампу.",
                 card="Полировка фар паром или вручную, замена ламп.",
                 inc=["Полировка фар паром", "Ручная полировка слегка помутневших фар", "Лампы H1, H4, H7, H11 и светодиодные", "Лампы габаритов и противотуманок"],
                 sec=[("Выбор метода", "Сильно пожелтевшие фары полируем паром, слегка помутневшие — вручную. Метод выбираем на месте по состоянию фары."),
                      ("Цена", "Пришлите фото фар в WhatsApp — скажем цену заранее.")],
                 faq=[("Привезёте лампу?", "Да — или установим вашу."),
                      ("Стоит ли делать перед техосмотром?", "Да — прозрачные фары и рабочие лампы важны для техосмотра."), ("Приезжаете ночью?", "Да, 24/7.")])),
    dict(key="tpms", brand=V, img="van-rear", sub=VSUB("saburavis-wnevis-sensori"),
         slug=dict(ka="saburavis-wnevis-sensori", en="tpms-sensor-replacement", ru="zamena-datchika-davleniya-shin"),
         icon='<path d="M5 12.5a9.5 9.5 0 0 1 14 0M8 15.5a5.5 5.5 0 0 1 8 0"/><circle cx="12" cy="19" r="1"/>',
         ka=dict(title="საბურავის ბლუთუზის შეცვლა და დაპროგრამება | Bagrat Motors", h1="საბურავის ბლუთუზის შეცვლა და დაპროგრამება",
                 desc="საბურავის ბლუთუზის (წნევის სენსორის) შემოწმება, შეცვლა და დაპროგრამება თბილისში — Bagrat Motors-ის ბრენდი Vulkanizacia.ge. დამოკიდებულია მარკასა და მოდელზე.",
                 kw="საბურავის ბლუთუზი, საბურავის ბლუთუზის შეცვლა, საბურავის ბლუთუზის დაპროგრამება, საბურავის სენსორის შეცვლა, Bagrat Motors",
                 lead="დაფაზე წნევის ნიშანი არ ქრება? საბურავის ბლუთუზი — წნევის სენსორი — შესაძლოა დაზიანდა ან ბატარეა დაუჯდა. შევამოწმებთ, შევცვლით და დავაპროგრამებთ.",
                 card="წნევის სენსორის შემოწმება, შეცვლა და დაპროგრამება.",
                 inc=["ბლუთუზის (სენსორის) შემოწმება", "დაზიანებული სენსორის შეცვლა", "ახალი სენსორის დაპროგრამება", "სენსორის ფრთხილად მოხსნა საბურავის შეცვლისას"],
                 sec=[("მნიშვნელოვანია", "შესაძლებლობა დამოკიდებულია ავტომობილის მარკაზე, მოდელსა და წელზე. დარეკვისას გვითხარით მანქანის მონაცემები — გეტყვით, შეგვიძლია თუ არა დახმარება."),
                      ("რატომ ანთია ნიშანი", "ხშირად მიზეზი დაბალი წნევაა, ამიტომ ჯერ წნევა შეამოწმეთ. თუ წნევა ნორმაშია, სავარაუდოდ სენსორის ან მისი დაპროგრამების პრობლემაა.")],
                 faq=[("ყველა მანქანაზე ცვლით?", "არა ყოველთვის — დამოკიდებულია მარკაზე, მოდელსა და წელზე."),
                      ("რა არის საბურავის ბლუთუზი?", "ასე ხშირად უწოდებენ საბურავის წნევის სენსორს (TPMS), რომელიც წნევას უკაბელოდ გადასცემს მანქანას."),
                      ("რა ღირს?", "ფასი დამოკიდებულია მანქანასა და სენსორზე — დაგვირეკეთ.")]),
         en=dict(title="TPMS sensor replacement in Tbilisi | Bagrat Motors", h1="TPMS sensor replacement and programming",
                 desc="TPMS (tire pressure sensor) check, replacement and programming in Tbilisi — Bagrat Motors' brand Vulkanizacia.ge. Depends on make and model.",
                 kw="TPMS sensor replacement Tbilisi, tire pressure sensor, TPMS programming, Bagrat Motors",
                 lead="Tire pressure light won't go off? The pressure sensor may be damaged or its battery dead. We check, replace and program it.",
                 card="Pressure sensor check, replacement and programming.",
                 inc=["Sensor check", "Replacing a damaged sensor", "Programming a new sensor", "Careful removal during a tire change"],
                 sec=[("Important", "It depends on the car's make, model and year. Tell us your car's details when you call and we'll say whether we can help."),
                      ("Why the light is on", "Often the cause is low pressure, so check the pressure first. If it's fine, the sensor or its programming is the likely problem.")],
                 faq=[("Can you do it on any car?", "Not always — it depends on the make, model and year."),
                      ("What is a TPMS sensor?", "A sensor in the wheel that measures tire pressure and sends it wirelessly to the car — in Georgia it's often called the tire “bluetooth”."),
                      ("How much does it cost?", "It depends on the car and the sensor — call us.")]),
         ru=dict(title="Замена датчика давления шин в Тбилиси | Bagrat Motors", h1="Замена и программирование датчиков давления шин",
                 desc="Проверка, замена и программирование датчиков давления шин (TPMS) в Тбилиси — бренд Bagrat Motors Vulkanizacia.ge. Зависит от марки и модели.",
                 kw="замена датчика давления шин, датчик давления шин Тбилиси, прописать датчики давления, TPMS, Bagrat Motors",
                 lead="Не гаснет индикатор давления? Датчик мог повредиться или разрядиться. Проверим, заменим и пропишем.",
                 card="Проверка, замена и программирование датчиков давления.",
                 inc=["Проверка датчика", "Замена повреждённого датчика", "Программирование нового датчика", "Аккуратный демонтаж при замене шин"],
                 sec=[("Важно", "Зависит от марки, модели и года машины. Назовите данные автомобиля при звонке — скажем, сможем ли помочь."),
                      ("Почему горит индикатор", "Часто причина — низкое давление, поэтому сначала проверьте его. Если давление в норме, проблема, скорее всего, в датчике или его программировании.")],
                 faq=[("Меняете на любой машине?", "Не всегда — зависит от марки, модели и года."),
                      ("Что такое датчик TPMS?", "Датчик в колесе, который измеряет давление и по радиоканалу передаёт его в машину; в Грузии его часто называют «блютуз» шины."),
                      ("Сколько стоит?", "Зависит от машины и датчика — позвоните.")])),
    dict(key="seasonal", brand=V, img="tyres-gallery-3", sub=VSUB("sezonuri-saburavebis-shecvla"),
         slug=dict(ka="sezonuri-saburavebis-shecvla", en="seasonal-tire-change", ru="sezonnaya-zamena-shin"),
         icon='<circle cx="12" cy="12" r="9"/><path d="M12 7v10M7.7 9.5l8.6 5M7.7 14.5l8.6-5"/>',
         ka=dict(title="ზამთრის საბურავების შეცვლა ადგილზე თბილისში | Bagrat Motors", h1="ზამთრის საბურავების შეცვლა ადგილზე",
                 desc="ზამთრის და ზაფხულის საბურავების შეცვლა ადგილზე თბილისში — Bagrat Motors-ის ბრენდი Vulkanizacia.ge: მონტაჟი, ბალანსირება და წნევა, 24/7.",
                 kw="ზამთრის საბურავების შეცვლა, საბურავების შეცვლა ადგილზე, საბურავების შეცვლა გამოძახებით, საბურავების შეცვლა 24 7, Bagrat Motors",
                 lead="სეზონის დადგომისას საბურავების შესაცვლელად რიგში დგომა აღარ გჭირდებათ — Bagrat Motors-ის გუნდი საბურავებს სახლთან ან ოფისთან შეგიცვლით.",
                 card="ზამთრის და ზაფხულის საბურავები — ადგილზე, ბალანსირებით.",
                 inc=["საბურავების გადაცმა დისკებზე", "ბორბლების ბალანსირება", "წნევის შემოწმება", "ახალი ან მეორადი საბურავის მოტანა"],
                 sec=[("როდის შევცვალოთ", "ზამთრის საბურავებს ჩვეულებრივ მაშინ აყენებენ, როცა საშუალო ტემპერატურა 7°C-ზე დაბლა ეცემა, ზაფხულის საბურავებს კი — როცა ტემპერატურა სტაბილურად 7°C-ზე მაღლა დგება."),
                      ("საბურავები გჭირდებათ?", "თუ ახალი ან მეორადი საბურავები გჭირდებათ, თქვენს ზომაში მოგიტანთ და იქვე დაგიყენებთ.")],
                 faq=[("საბურავები დისკებზე უნდა იყოს?", "არა — საბურავს დისკზე ადგილზე გადავაცვამთ და დავაბალანსებთ."),
                      ("ბალანსირება შედის?", "დიახ, საბურავის გადაცმისას ბორბლებს ვაბალანსებთ."), ("ღამითაც მოდიხართ?", "დიახ, 24/7.")]),
         en=dict(title="Seasonal tire change at home in Tbilisi | Bagrat Motors", h1="Seasonal tire change at home",
                 desc="Winter and summer tire change at your home in Tbilisi — Bagrat Motors' brand Vulkanizacia.ge: fitting, balancing and pressure check, 24/7.",
                 kw="seasonal tire change Tbilisi, tire change at home, winter tires Tbilisi, Bagrat Motors",
                 lead="No more queues when the season changes — the Bagrat Motors team swaps your tires at home or at the office.",
                 card="Winter and summer tires — on site, with balancing.",
                 inc=["Fitting tires on rims", "Wheel balancing", "Pressure check", "New or used tires delivered"],
                 sec=[("When to change", "Winter tires usually go on when the average temperature drops below 7°C, summer tires when it stays above that."),
                      ("Need tires?", "If you need new or used tires, we bring them in your size and fit them on the spot.")],
                 faq=[("Do my tires need to be on rims?", "No — we fit the tires onto the rims on site and balance them."),
                      ("Is balancing included?", "Yes, we balance the wheels when fitting tires."), ("Do you come at night?", "Yes, 24/7.")]),
         ru=dict(title="Сезонная замена шин с выездом в Тбилиси | Bagrat Motors", h1="Сезонная замена шин с выездом",
                 desc="Сезонная замена шин с выездом в Тбилиси — бренд Bagrat Motors Vulkanizacia.ge: шиномонтаж, балансировка и проверка давления, 24/7.",
                 kw="сезонная замена шин, замена шин с выездом, шиномонтаж на выезде Тбилиси, зимние шины Тбилиси, Bagrat Motors",
                 lead="Не нужно стоять в очереди в сезон — команда Bagrat Motors поменяет шины у дома или у офиса.",
                 card="Зимние и летние шины — на месте, с балансировкой.",
                 inc=["Шиномонтаж на диски", "Балансировка колёс", "Проверка давления", "Привезём новые или б/у шины"],
                 sec=[("Когда менять", "Зимние шины обычно ставят, когда средняя температура опускается ниже 7°C, летние — когда держится выше."),
                      ("Нужны шины?", "Если нужны новые или б/у шины, привезём вашего размера и установим на месте.")],
                 faq=[("Шины должны быть на дисках?", "Нет — смонтируем шины на диски на месте и отбалансируем."),
                      ("Балансировка входит?", "Да, при шиномонтаже балансируем колёса."), ("Приезжаете ночью?", "Да, 24/7.")])),
    dict(key="tyres", brand=V, img="tyres-gallery-1", sub={"ka": "/saburavebi/", "en": "/tyres/", "ru": "/shiny/"},
         slug=dict(ka="saburavebi", en="buy-tires", ru="kupit-shiny"),
         icon='<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="4"/>',
         ka=dict(title="საბურავების ყიდვა თბილისში — ახალი და მეორადი | Bagrat Motors", h1="საბურავების ყიდვა თბილისში",
                 desc="საბურავების ყიდვა თბილისში — ახალი და მეორადი, ზამთრის და ზაფხულის, R13-დან R20-მდე. Bagrat Motors-ის ბრენდი Vulkanizacia.ge მოგიტანთ და დაგიყენებთ.",
                 kw="საბურავების ყიდვა თბილისში, საბურავები, მეორადი საბურავები, ახალი საბურავები, საბურავების მაღაზია თბილისში, Bagrat Motors",
                 lead="ახალი და მეორადი საბურავები ყველა პოპულარულ ზომაში. გვითხარით ზომა — Bagrat Motors-ის გუნდი საბურავებს მოგიტანთ, დაგიყენებთ და დააბალანსებს.",
                 card="ახალი და მეორადი, ზამთრის და ზაფხულის — R13-დან R20-მდე.",
                 inc=["ახალი საბურავები", "მეორადი საბურავები ევროპიდან, იაპონიიდან და ჩინეთიდან", "ზამთრის, ზაფხულის და ყველა სეზონის", "მიტანა, მონტაჟი და ბალანსირება"],
                 sec=[("როგორ შევუკვეთოთ", "ზომა საბურავის გვერდზეა დაწერილი, მაგალითად 205/55 R16. გამოგვიგზავნეთ ფოტო ან ზომა WhatsApp-ზე — გეტყვით, რა გვაქვს და რა ღირს."),
                      ("სრული კატალოგი", "ყველა ზომა და ზომის ფილტრი იხილეთ Vulkanizacia.ge-ის საბურავების კატალოგში.")],
                 faq=[("მეორადი საბურავები საიდანაა?", "ევროპიდან, იაპონიიდან და ჩინეთიდან."),
                      ("საბურავებს დაგვიყენებთ?", "დიახ — მოგიტანთ, დაგიყენებთ და დავაბალანსებთ ადგილზე."),
                      ("რა ღირს საბურავები?", "ფასი დამოკიდებულია ზომაზე, სეზონსა და იმაზე, ახალია თუ მეორადი — დაგვირეკეთ ან მოგვწერეთ.")]),
         en=dict(title="Buy tires in Tbilisi — new and used | Bagrat Motors", h1="Buy tires in Tbilisi",
                 desc="Buy tires in Tbilisi — new and used, winter and summer, R13 to R20. Bagrat Motors' brand Vulkanizacia.ge delivers and fits them.",
                 kw="buy tires Tbilisi, tires Tbilisi, used tires Tbilisi, tire shop Tbilisi, Bagrat Motors",
                 lead="New and used tires in all popular sizes. Tell us your size — the Bagrat Motors team brings, fits and balances them.",
                 card="New and used, winter and summer — R13 to R20.",
                 inc=["New tires", "Used tires from Europe, Japan and China", "Winter, summer and all-season", "Delivery, fitting and balancing"],
                 sec=[("How to order", "The size is written on the tire sidewall, for example 205/55 R16. Send a photo or the size on WhatsApp — we'll tell you what we have and the price."),
                      ("Full catalogue", "See every size and the size filter in the Vulkanizacia.ge tire catalogue.")],
                 faq=[("Where are the used tires from?", "Europe, Japan and China."),
                      ("Do you fit them?", "Yes — we bring, fit and balance them on site."),
                      ("How much do tires cost?", "It depends on the size, season and whether new or used — call or message us.")]),
         ru=dict(title="Купить шины в Тбилиси — новые и б/у | Bagrat Motors", h1="Купить шины в Тбилиси",
                 desc="Купить шины в Тбилиси — новые и б/у, зимние и летние, от R13 до R20. Бренд Bagrat Motors Vulkanizacia.ge привезёт и установит.",
                 kw="купить шины в Тбилиси, шины Тбилиси, б/у шины Тбилиси, зимние шины Тбилиси, Bagrat Motors",
                 lead="Новые и б/у шины всех популярных размеров. Назовите размер — команда Bagrat Motors привезёт, установит и отбалансирует.",
                 card="Новые и б/у, зимние и летние — от R13 до R20.",
                 inc=["Новые шины", "Б/у шины из Европы, Японии и Китая", "Зимние, летние и всесезонные", "Доставка, монтаж и балансировка"],
                 sec=[("Как заказать", "Размер указан на боковине шины, например 205/55 R16. Пришлите фото или размер в WhatsApp — скажем, что есть и сколько стоит."),
                      ("Полный каталог", "Все размеры и фильтр по размеру — в каталоге шин Vulkanizacia.ge.")],
                 faq=[("Откуда б/у шины?", "Из Европы, Японии и Китая."), ("Установите?", "Да — привезём, установим и отбалансируем на месте."),
                      ("Сколько стоят шины?", "Зависит от размера, сезона и того, новые или б/у, — позвоните или напишите.")])),
    dict(key="driver", brand=T_, img="towing", sub={"ka": "/services/mdzgvolis-servisi/", "en": "/services/mdzgvolis-servisi/index-en.html", "ru": "/services/mdzgvolis-servisi/index-ru.html"},
         slug=dict(ka="mdzgholis-servisi", en="sober-driver", ru="trezvyy-voditel"),
         icon='<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="2"/><path d="M12 14v7M10.2 11 3.5 9.5M13.8 11l6.7-1.5"/>',
         ka=dict(title="მძღოლი გამოძახებით თბილისში — ფხიზელი მძღოლი | Bagrat Motors", h1="მძღოლი გამოძახებით",
                 desc="მძღოლი გამოძახებით თბილისში — ფხიზელი და პირადი მძღოლი 24/7. Bagrat Motors-ის ბრენდი Towing.ge: მძღოლი მართავს თქვენს მანქანას.",
                 kw="მძღოლი გამოძახებით, ფხიზელი მძღოლი, მძღოლის გამოძახება თბილისში, მძღოლის სერვისი, პირადი მძღოლი, Bagrat Motors",
                 lead="საჭესთან ჯდომა არ შეგიძლიათ ან არ გსურთ? Bagrat Motors-ის მძღოლი მოვა და თქვენივე მანქანით მიგიყვანთ იქ, სადაც გჭირდებათ — დღე და ღამე.",
                 card="ფხიზელი და პირადი მძღოლი — თქვენი მანქანით, 24/7.",
                 inc=["ფხიზელი მძღოლი — წვეულების ან რესტორნის შემდეგ", "პირადი მძღოლი საქმიანი შეხვედრებისთვის", "მგზავრობა ქალაქში და ქალაქგარეთ", "მძღოლი მართავს თქვენს მანქანას"],
                 sec=[("როგორ მუშაობს", "დაგვირეკეთ, გვითხარით მისამართი და დანიშნულება. მძღოლი მოვა, დაჯდება თქვენი მანქანის საჭესთან და უსაფრთხოდ მიგიყვანთ."),
                      ("ფასი", "ფასი დამოკიდებულია მანძილსა და დროზე — დარეკვისას წინასწარ შეგითანხმებთ.")],
                 faq=[("ჩემივე მანქანით?", "დიახ, ჩვენი მძღოლი მართავს თქვენს მანქანას."), ("ღამითაც მუშაობთ?", "დიახ, 24/7."),
                      ("რამდენ ხანში მოვა მძღოლი?", "დამოკიდებულია ადგილსა და დროზე — დარეკვისას გეტყვით.")]),
         en=dict(title="Sober driver in Tbilisi — driver on call | Bagrat Motors", h1="Sober driver on call",
                 desc="Sober driver and personal driver on call in Tbilisi, 24/7. Bagrat Motors' brand Towing.ge: our driver drives your own car.",
                 kw="sober driver Tbilisi, designated driver Tbilisi, driver on call, personal driver Tbilisi, Bagrat Motors",
                 lead="Can't or don't want to drive? A Bagrat Motors driver comes and takes you where you need to go in your own car — day and night.",
                 card="Sober and personal driver — in your own car, 24/7.",
                 inc=["Sober driver — after a party or a restaurant", "Personal driver for business meetings", "Trips in the city and out of town", "Our driver drives your car"],
                 sec=[("How it works", "Call us with the address and destination. The driver arrives, takes the wheel of your car and gets you there safely."),
                      ("Price", "It depends on distance and time — we agree it in advance when you call.")],
                 faq=[("In my own car?", "Yes, our driver drives your car."), ("Do you work at night?", "Yes, 24/7."),
                      ("How fast does the driver arrive?", "It depends on the place and time — we'll tell you when you call.")]),
         ru=dict(title="Трезвый водитель в Тбилиси | Bagrat Motors", h1="Трезвый водитель по вызову",
                 desc="Трезвый водитель и личный водитель по вызову в Тбилиси, 24/7. Бренд Bagrat Motors Towing.ge: наш водитель поведёт вашу машину.",
                 kw="трезвый водитель Тбилиси, водитель по вызову, личный водитель Тбилиси, Bagrat Motors",
                 lead="Не можете или не хотите садиться за руль? Водитель Bagrat Motors приедет и отвезёт вас на вашей же машине — днём и ночью.",
                 card="Трезвый и личный водитель — на вашей машине, 24/7.",
                 inc=["Трезвый водитель — после праздника или ресторана", "Личный водитель для деловых встреч", "Поездки по городу и за город", "Водитель ведёт вашу машину"],
                 sec=[("Как это работает", "Позвоните, назовите адрес и куда ехать. Водитель приедет, сядет за руль вашей машины и безопасно довезёт вас."),
                      ("Цена", "Зависит от расстояния и времени — согласуем заранее при звонке.")],
                 faq=[("На моей машине?", "Да, наш водитель ведёт вашу машину."), ("Работаете ночью?", "Да, 24/7."),
                      ("Как быстро приедет водитель?", "Зависит от места и времени — скажем при звонке.")])),
]

# existing bagratmotors pages delivered by a sub-brand (Georgian slugs; en/ru found through hreflang)
EXISTING = {"vulkanizacia": V, "saburavis-sheketeba": V, "saburavis-montaji": V, "saburavis-shecvla-gzaze": T_, "balansireba": V,
            "diskis-dadugheba": V, "diskis-gasworeba": V, "evakuatori": T_, "oboba-evakuatori": T_, "avtotransportireba": T_}
PHONE_TO_VULK = {"vulkanizacia", "saburavis-sheketeba", "saburavis-montaji", "balansireba", "diskis-dadugheba", "diskis-gasworeba"}


def url(h, lang):
    return f"{PREFIX[lang]}/services/{h['slug'][lang]}/"


def sub_href(h, lang):
    return BRANDS[h["brand"]]["url"] + h["sub"][lang]


def read(rel):
    return (ROOT / rel.lstrip("/")).read_text(encoding="utf-8")


def file_of(u):
    u = u.replace(SITE, "").lstrip("/")
    return ROOT / (u + "index.html" if (u == "" or u.endswith("/")) else u)


def group_links(lang, brand):
    """(href, name) of the existing cards in the homepage group of this sub-brand."""
    s = read(HOME[lang] + "index.html") if lang != "ka" else read("index.html")
    head = GROUP[brand][lang][1]
    i = s.index(f'<a href="{head}" class="mb-5')
    j = s.index('\n    </div>', i)
    return re.findall(r'<a href="(/[^"]+)" class="group[^"]*">.*?<h4[^>]*>([^<]+)</h4>', s[i:j], re.S)


def brand_block(lang, brand, href):
    U, B = UI[lang], BRANDS[brand]
    strong = f'<strong class="font-semibold text-brand-400">{B["name"]}</strong>'
    return (f'<div class="mb-8 flex flex-col gap-3 rounded-2xl bg-zinc-900 p-5 ring-1 ring-brand/30 sm:flex-row sm:items-center sm:justify-between">'
            f'<p class="text-sm text-zinc-300">{U["by"].format(b=strong)}</p>'
            f'<a href="{href}" class="shrink-0 rounded-xl bg-zinc-950 px-4 py-2.5 text-center text-sm font-semibold text-zinc-100 ring-1 ring-zinc-700 hover:ring-brand/60">{U["by_btn"].format(b=B["name"])}</a></div>')


def lang_switch(urls, lang, short):
    lab = {"ka": "ქა" if short else "ქართული", "en": "EN", "ru": "RU"}
    out = []
    for l in LANGS:
        if short:
            cls = "rounded px-2 py-1 font-semibold text-brand-400" if l == lang else "rounded px-2 py-1 text-zinc-400 hover:bg-zinc-800"
        else:
            cls = "rounded bg-zinc-900 px-3 py-1.5 font-semibold text-brand-400" if l == lang else "rounded px-3 py-1.5 text-zinc-400"
        out.append(f'<a href="{urls[l]}" class="{cls}">{lab[l]}</a>')
    return "\n        ".join(out)


def hub_page(h, lang):
    U, d, B = UI[lang], h[lang], BRANDS[h["brand"]]
    urls = {l: url(h, l) for l in LANGS}
    me = SITE + urls[lang]
    gname, ghref = GROUP[h["brand"]][lang]
    img = f"{SITE}/assets/{h['img']}.jpg"
    siblings = [(u, n) for u, n in group_links(lang, h["brand"])] + [(url(x, lang), x[lang]["h1"]) for x in HUB if x["brand"] == h["brand"] and x is not h]
    siblings = [(u, n) for u, n in siblings if u != urls[lang]]
    graph = [
        {"@type": "Service", "serviceType": d["h1"], "name": f"{d['h1']} — Bagrat Motors", "url": me, "image": img, "description": d["desc"],
         "areaServed": {"@type": "City", "name": "Tbilisi"},
         "provider": {"@type": "LocalBusiness", "name": B["name"], "url": B["url"] + "/", "telephone": B["tel"],
                      "parentOrganization": {"@type": "Organization", "@id": f"{SITE}/#org", "name": "Bagrat Motors", "url": SITE + "/"}},
         "brand": {"@type": "Brand", "name": B["name"]}},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": U["home"], "item": SITE + HOME[lang]},
            {"@type": "ListItem", "position": 2, "name": gname, "item": SITE + ghref},
            {"@type": "ListItem", "position": 3, "name": d["h1"], "item": me}]},
        {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in d["faq"]]},
    ]
    alts = "\n".join(f'<link rel="alternate" hreflang="{l}" href="{SITE}{urls[l]}" />' for l in LANGS) + f'\n<link rel="alternate" hreflang="x-default" href="{SITE}{urls["ka"]}" />'
    locs = "\n".join(f'<meta property="og:locale:alternate" content="{LOCALE[l]}" />' for l in LANGS if l != lang)
    lis = "\n".join(f'        <li class="flex gap-2 rounded-xl bg-zinc-900 p-4 ring-1 ring-zinc-800"><span class="text-brand-400">{CHECK}</span> {escape(x)}</li>' for x in d["inc"])
    secs = "\n".join(f'      <h2 class="mt-10 font-head text-2xl font-bold">{escape(t)}</h2>\n      <p class="mt-3 text-zinc-300">{escape(p)}</p>' for t, p in d["sec"])
    faqs = "\n".join(f'''          <details class="group rounded-2xl bg-zinc-900 p-5 ring-1 ring-zinc-800">
            <summary class="flex cursor-pointer items-center justify-between font-semibold">{escape(q)}<span class="text-brand-400 transition group-open:rotate-45">+</span></summary>
            <p class="mt-3 text-zinc-400">{escape(a)}</p>
          </details>''' for q, a in d["faq"])
    side = "\n".join(f'          <li><a href="{u}" class="hover:text-white">→ {escape(n)}</a></li>' for u, n in siblings)
    home = HOME[lang]
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{escape(d['title'])}</title>
<meta name="description" content="{escape(d['desc'])}" />
<meta name="keywords" content="{escape(d['kw'])}" />
<meta name="robots" content="index, follow" />
<meta name="theme-color" content="#09090b" />
<meta name="geo.region" content="GE-TB" />
<meta name="geo.placename" content="Tbilisi" />
<meta name="ICBM" content="41.7151, 44.8271" />
<link rel="canonical" href="{me}" />
{alts}
<meta property="og:type" content="website" />
<meta property="og:site_name" content="Bagrat Motors" />
<meta property="og:title" content="{escape(d['title'])}" />
<meta property="og:description" content="{escape(d['desc'])}" />
<meta property="og:url" content="{me}" />
<meta property="og:image" content="{img}" />
<meta property="og:locale" content="{LOCALE[lang]}" />
{locs}
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="{escape(d['title'])}" />
<meta name="twitter:description" content="{escape(d['desc'])}" />
<meta name="twitter:image" content="{img}" />
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml" />
<link rel="preload" href="/assets/fonts/manrope-800-latin.woff2" as="font" type="font/woff2" crossorigin />
<link rel="preload" href="/assets/fonts/noto-sans-georgian-700-georgian.woff2" as="font" type="font/woff2" crossorigin />
<link rel="preload" as="image" href="/assets/{h['img']}.webp" fetchpriority="high" />
<link href="/assets/styles.css" rel="stylesheet" />
<!-- google -->
<script type="application/ld+json">
{json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=2)}
</script>
</head>
<body class="bg-zinc-950 text-zinc-100 font-sans antialiased">

<header class="sticky top-0 z-40 border-b border-zinc-800/80 bg-zinc-950/80 backdrop-blur">
  <div class="mx-auto flex max-w-6xl items-center justify-between gap-4 px-4 py-3">
    <a href="{home}" class="flex items-center gap-2">
      <span class="grid h-9 w-9 place-items-center rounded-lg bg-brand font-head text-sm font-extrabold text-zinc-950">BM</span>
      <span class="font-head text-lg font-extrabold tracking-tight text-white">Bagrat <span class="text-brand">Motors</span></span>
    </a>
    <nav class="hidden items-center gap-6 text-sm text-zinc-300 md:flex">
      <a href="{home}" class="hover:text-white">{U['home']}</a>
      <a href="{home}#services" class="hover:text-white">{U['services']}</a>
      <a href="#faq" class="hover:text-white">FAQ</a>
      <a href="#contact" class="hover:text-white">{U['contact']}</a>
    </nav>
    <div class="flex items-center gap-3">
      <div class="hidden items-center gap-1 rounded-lg bg-zinc-900 p-1 text-xs sm:flex">
        {lang_switch(urls, lang, True)}
      </div>
      <a href="tel:{B['tel']}" class="hidden rounded-lg bg-brand px-4 py-2 text-sm font-semibold text-zinc-950 hover:bg-brand-600 sm:inline-block">{PHONE_SVG}{B['tel_fmt']}</a>
      <button id="navBtn" aria-label="{U['menu']}" class="grid h-9 w-9 place-items-center rounded-lg bg-zinc-900 md:hidden"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M4 7h16M4 12h16M4 17h16"/></svg></button>
    </div>
  </div>
  <div id="navMenu" class="hidden border-t border-zinc-800 bg-zinc-950 px-4 py-3 md:hidden">
    <div class="flex flex-col gap-3 text-sm text-zinc-300">
      <a href="{home}" class="hover:text-white">{U['home']}</a>
      <a href="{home}#services" class="hover:text-white">{U['services']}</a>
      <a href="#faq" class="hover:text-white">FAQ</a>
      <a href="#contact" class="hover:text-white">{U['contact']}</a>
      <div class="flex items-center gap-1 pt-1 text-xs">
        {lang_switch(urls, lang, False)}
      </div>
    </div>
  </div>
</header>

<main>
<section class="relative overflow-hidden">
  <picture>
    <source srcset="/assets/{h['img']}.webp" type="image/webp" />
    <img src="/assets/{h['img']}.jpg" alt="{escape(d['h1'])} — Bagrat Motors" class="absolute inset-0 h-full w-full object-cover" />
  </picture>
  <div class="absolute inset-0 bg-gradient-to-b from-zinc-950/85 via-zinc-950/85 to-zinc-950"></div>
  <div class="relative mx-auto max-w-6xl px-4 py-20 sm:py-28">
    <nav class="mb-4 text-sm text-zinc-400">
      <a href="{home}" class="hover:text-white">{U['home']}</a> <span class="mx-1">/</span>
      <a href="{ghref}" class="hover:text-white">{gname}</a> <span class="mx-1">/</span>
      <span class="text-zinc-200">{escape(d['h1'])}</span>
    </nav>
    <span class="rounded-full bg-brand/15 px-3 py-1 text-xs font-medium text-brand-400 ring-1 ring-brand/30">{U['tag']} · {B['name']}</span>
    <h1 class="mt-4 font-head text-4xl font-extrabold leading-tight sm:text-5xl">{escape(d['h1'])}</h1>
    <p class="mt-4 max-w-2xl text-lg text-zinc-300">{escape(d['lead'])}</p>
    <div class="mt-8 flex flex-wrap gap-3">
      <a href="tel:{B['tel']}" class="rounded-xl bg-brand px-6 py-3 font-semibold text-zinc-950 hover:bg-brand-600">{PHONE_SVG}{U['call']} {B['tel_fmt']}</a>
      <a href="https://wa.me/{B['wa']}" class="rounded-xl bg-[#15803d] px-6 py-3 font-semibold text-white">WhatsApp</a>
    </div>
  </div>
</section>

<section class="mx-auto max-w-6xl px-4 py-16">
  <div class="grid gap-10 lg:grid-cols-3">
    <article class="lg:col-span-2">
      {brand_block(lang, h['brand'], sub_href(h, lang))}
      <h2 class="font-head text-2xl font-bold">{U['inc']}</h2>
      <ul class="mt-6 grid gap-3 sm:grid-cols-2">
{lis}
      </ul>
{secs}

      <div id="faq" class="mt-12">
        <h2 class="font-head text-2xl font-bold">{U['faq']}</h2>
        <div class="mt-4 space-y-3">
{faqs}
        </div>
      </div>
    </article>

    <aside class="lg:sticky lg:top-24 lg:h-fit">
      <div class="rounded-2xl bg-gradient-to-br from-brand/15 to-zinc-900 p-6 ring-1 ring-brand/20">
        <div class="text-sm text-zinc-300">{U['call_now']}</div>
        <a href="tel:{B['tel']}" class="mt-1 block font-head text-2xl font-extrabold text-white">{B['tel_fmt']}</a>
        <div class="mt-4 flex flex-col gap-2">
          <a href="tel:{B['tel']}" class="rounded-xl bg-brand px-4 py-2.5 text-center text-sm font-semibold text-zinc-950 hover:bg-brand-600">{PHONE_SVG}{U['call']}</a>
          <a href="https://wa.me/{B['wa']}" class="rounded-xl bg-[#15803d] px-4 py-2.5 text-center text-sm font-semibold text-white">WhatsApp</a>
          <a href="viber://chat?number=%2B{B['wa']}" class="rounded-xl bg-[#6d28d9] px-4 py-2.5 text-center text-sm font-semibold text-white">Viber</a>
        </div>
      </div>
      <div class="mt-4 rounded-2xl bg-zinc-900 p-6 ring-1 ring-zinc-800">
        <div class="text-sm font-semibold text-zinc-200">{U['other']}</div>
        <ul class="mt-3 space-y-2 text-sm text-zinc-400">
{side}
          <li class="pt-1"><a href="{ghref}" class="font-semibold text-brand-400 hover:text-white">↑ {gname}</a></li>
        </ul>
      </div>
    </aside>
  </div>
</section>

<section id="contact" class="border-t border-zinc-800">
  <div class="mx-auto max-w-6xl px-4 py-16">
    <div class="rounded-3xl bg-gradient-to-br from-brand/15 to-zinc-900 p-8 ring-1 ring-brand/20 sm:p-12">
      <h2 class="font-head text-3xl font-bold">{U['contact_h']}</h2>
      <p class="mt-3 text-zinc-300">{U['contact_p']}</p>
      <div class="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <a href="tel:{B['tel']}" class="rounded-2xl bg-zinc-950/40 p-5 ring-1 ring-zinc-700 hover:ring-brand/50"><div class="text-sm text-zinc-400">{U['phone']}</div><div class="mt-1 font-semibold">{B['tel_fmt']}</div></a>
        <a href="mailto:info@bagratmotors.ge" class="rounded-2xl bg-zinc-950/40 p-5 ring-1 ring-zinc-700 hover:ring-brand/50"><div class="text-sm text-zinc-400">{U['email']}</div><div class="mt-1 font-semibold">info@bagratmotors.ge</div></a>
        <div class="rounded-2xl bg-zinc-950/40 p-5 ring-1 ring-zinc-700"><div class="text-sm text-zinc-400">{U['location']}</div><div class="mt-1 font-semibold">{U['loc_v']}</div></div>
        <div class="rounded-2xl bg-zinc-950/40 p-5 ring-1 ring-zinc-700"><div class="text-sm text-zinc-400">{U['hours']}</div><div class="mt-1 font-semibold">24/7</div></div>
      </div>
    </div>
  </div>
</section>
</main>

<footer class="border-t border-zinc-800 bg-zinc-950">
  <div class="mx-auto grid max-w-6xl gap-8 px-4 py-12 sm:grid-cols-2 lg:grid-cols-4">
    <div>
      <div class="flex items-center gap-2">
        <span class="grid h-8 w-8 place-items-center rounded-lg bg-brand text-xs font-extrabold text-zinc-950">BM</span>
        <span class="font-head font-extrabold text-white">Bagrat <span class="text-brand">Motors</span></span>
      </div>
      <p class="mt-3 text-sm text-zinc-400">{U['foot']}</p>
    </div>
    <div>
      <div class="text-sm font-semibold text-zinc-200">{U['services']}</div>
      <ul class="mt-3 space-y-2 text-sm text-zinc-400">
        <li><a href="{ghref}" class="hover:text-white">{gname}</a></li>
        <li><a href="{home}#services" class="hover:text-white">{U['services']}</a></li>
      </ul>
    </div>
    <div>
      <div class="text-sm font-semibold text-zinc-200">{U['contact']}</div>
      <ul class="mt-3 space-y-2 text-sm text-zinc-400">
        <li><a href="tel:{B['tel']}" class="hover:text-white">{PHONE_SVG}{B['tel_fmt']}</a></li>
        <li><a href="mailto:info@bagratmotors.ge" class="hover:text-white">info@bagratmotors.ge</a></li>
      </ul>
    </div>
    <div>
      <div class="text-sm font-semibold text-zinc-200">{U['lang']}</div>
      <div class="mt-3 flex items-center gap-1 text-xs">
        {lang_switch(urls, lang, False)}
      </div>
    </div>
  </div>
  <div class="border-t border-zinc-800/70 py-5 text-center text-xs text-zinc-400">{U['copy']}</div>
</footer>

<div class="fixed bottom-5 right-5 z-50 flex flex-col gap-3">
  <a href="https://wa.me/{B['wa']}" aria-label="WhatsApp" class="grid h-12 w-12 place-items-center rounded-full bg-[#25D366] text-white shadow-lg">{WA_SVG}</a>
  <a href="viber://chat?number=%2B{B['wa']}" aria-label="Viber" class="grid h-12 w-12 place-items-center rounded-full bg-[#7360f2] text-white shadow-lg">{VIBER_SVG}</a>
  <a href="tel:{B['tel']}" aria-label="{U['call']}" class="call-pulse grid h-14 w-14 place-items-center rounded-full bg-brand text-zinc-950 shadow-lg">{CALL_SVG}</a>
</div>

<script>
  document.getElementById("navBtn").addEventListener("click", function () {{
    document.getElementById("navMenu").classList.toggle("hidden");
  }});
</script>
</body>
</html>
"""


def build_hubs():
    for h in HUB:
        for lang in LANGS:
            out = file_of(url(h, lang))
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(hub_page(h, lang), encoding="utf-8")


# ------------------------------------------------------------------ existing pages (additive)
def existing_files():
    """{ka_slug: {lang: Path}} via each Georgian page's hreflang."""
    out = {}
    for slug in EXISTING:
        s = read(f"services/{slug}/index.html")
        alts = dict(re.findall(r'hreflang="(ka|en|ru)" href="([^"]+)"', s))
        out[slug] = {l: file_of(alts[l]) for l in LANGS}
    return out


def patch_existing():
    hubs_by_brand = {b: [h for h in HUB if h["brand"] == b] for b in BRANDS}
    for slug, files in existing_files().items():
        brand = EXISTING[slug]
        for lang, p in files.items():
            s = p.read_text(encoding="utf-8")
            # 1) sub-brand badge at the top of the article (marker block)
            target = BRANDS[brand]["url"] + "/"
            block = "<!-- brand:start -->" + brand_block(lang, brand, target) + "<!-- brand:end -->"
            if "<!-- brand:start -->" in s:
                s = re.sub(r"<!-- brand:start -->.*?<!-- brand:end -->", lambda m: block, s, flags=re.S)
            else:
                s = s.replace('<article class="lg:col-span-2">', '<article class="lg:col-span-2">\n      ' + block, 1)
            # 2) sub-brand phone on tyre/wheel pages: body + JSON-LD only (title/meta untouched)
            if slug in PHONE_TO_VULK:
                head, body = s.split("</head>", 1)
                head = re.sub(r'("telephone":\s*")\+995514908090(")', r"\1+995591909013\2", head)
                for a, b in (("+995514908090", "+995591909013"), ("%2B995514908090", "%2B995591909013"), ("995514908090", "995591909013"), ("514 90 80 90", "591 90 90 13")):
                    body = body.replace(a, b)
                s = head + "</head>" + body
            # 3) new hub pages in the "other services" list
            m = re.search(r'(<ul class="mt-3 space-y-2 text-sm text-zinc-400">)(.*?)(\n\s*<li class="pt-1">)', s, re.S)
            if m:
                add = "".join(f'\n          <li><a href="{url(h, lang)}" class="hover:text-white">→ {escape(h[lang]["h1"])}</a></li>'
                              for h in hubs_by_brand[brand] if f'href="{url(h, lang)}"' not in m.group(2))
                if add:
                    s = s[:m.end(2)] + add + s[m.end(2):]
            p.write_text(s, encoding="utf-8")


# ------------------------------------------------------------------ homepages
def card(h, lang):
    d = h[lang]
    return f'''
        <a href="{url(h, lang)}" class="group flex flex-col overflow-hidden rounded-2xl bg-zinc-900 ring-1 ring-zinc-800 transition hover:-translate-y-0.5 hover:ring-brand/50">
          <div class="flex h-28 items-center justify-center bg-gradient-to-br from-zinc-800/50 to-zinc-900">
            <span class="grid h-16 w-16 place-items-center rounded-2xl bg-brand/10 text-brand ring-1 ring-brand/20 transition group-hover:bg-brand/20">
              <svg class="h-8 w-8" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{h["icon"]}</svg>
            </span>
          </div>
          <div class="flex flex-1 flex-col p-5">
            <h4 class="font-head text-lg font-bold">{escape(d["h1"])}</h4>
            <p class="mt-2 flex-1 text-sm text-zinc-400">{escape(d["card"])}</p>
            <span class="mt-4 inline-flex items-center gap-1 text-sm font-semibold text-brand-400">{UI[lang]["more"]}</span>
          </div>
        </a>'''


def brands_section(lang):
    U = UI[lang]
    cards = ""
    for b in ("vulk", "tow"):
        B = BRANDS[b]
        cards += f'''
      <div class="flex flex-col rounded-2xl bg-zinc-900 p-6 ring-1 ring-zinc-800">
        <div class="font-head text-2xl font-extrabold text-white">{B["name"]}</div>
        <div class="mt-1 text-xs font-semibold uppercase tracking-wider text-brand-400">{U["by_label"]}</div>
        <p class="mt-3 flex-1 text-sm text-zinc-400">{U["brand_desc"][b]}</p>
        <div class="mt-5 flex flex-wrap gap-2">
          <a href="tel:{B["tel"]}" class="rounded-xl bg-brand px-4 py-2.5 text-sm font-semibold text-zinc-950 hover:bg-brand-600">{PHONE_SVG}{B["tel_fmt"]}</a>
          <a href="{B["url"]}/" class="rounded-xl bg-zinc-950 px-4 py-2.5 text-sm font-semibold text-zinc-100 ring-1 ring-zinc-700 hover:ring-brand/60">{U["visit"]}</a>
        </div>
      </div>'''
    return f'''
<section id="brands" class="mx-auto max-w-6xl px-4 py-16 sm:py-20">
  <div class="mb-10 max-w-2xl">
    <p class="text-sm font-semibold uppercase tracking-wider text-brand-400">{U["brands_kicker"]}</p>
    <h2 class="mt-2 font-head text-3xl font-bold sm:text-4xl">{U["brands_h"]}</h2>
    <p class="mt-3 text-zinc-400">{U["brands_p"]}</p>
  </div>
  <div class="grid gap-6 sm:grid-cols-2">{cards}
  </div>
</section>
'''


def sync_block(s, start, end, block, anchor, before=True):
    if start in s:
        return re.sub(re.escape(start) + r".*?" + re.escape(end), lambda m: start + block + end, s, flags=re.S)
    i = s.index(anchor)
    return s[:i] + start + block + end + s[i:] if before else s[:i + len(anchor)] + start + block + end + s[i + len(anchor):]


def patch_homepages():
    for lang in LANGS:
        p = ROOT / ("index.html" if lang == "ka" else f"{lang}/index.html")
        s = p.read_text(encoding="utf-8")
        for b in BRANDS:
            head = GROUP[b][lang][1]
            i = s.index(f'<a href="{head}" class="mb-5')
            j = s.index("\n      </div>\n    </div>", i)          # end of that group's card grid
            cards = "".join(card(h, lang) for h in HUB if h["brand"] == b)
            mk_s, mk_e = f"<!-- hub-{b}:start -->", f"<!-- hub-{b}:end -->"
            if mk_s in s:
                s = re.sub(re.escape(mk_s) + r".*?" + re.escape(mk_e), lambda m: mk_s + cards + "\n        " + mk_e, s, flags=re.S)
            else:
                s = s[:j] + "\n        " + mk_s + cards + "\n        " + mk_e + s[j:]
        s = sync_block(s, "<!-- brands:start -->", "<!-- brands:end -->", brands_section(lang), '<section id="why"')
        # schema: sub-brands + offer catalogue
        m = re.search(r'(<script type="application/ld\+json">\s*)(\{.*?\})(\s*</script>)', s, re.S)
        data = json.loads(m.group(2))
        for node in data.get("@graph", []):
            if node.get("@type") == "Organization":
                node["subOrganization"] = [{"@type": "Organization", "name": B["name"], "url": B["url"] + "/", "telephone": B["tel"]} for B in BRANDS.values()]
            cat = node.get("hasOfferCatalog")
            if cat:
                have = {o.get("itemOffered", {}).get("url") for o in cat.get("itemListElement", [])}
                for h in HUB:
                    u = SITE + url(h, lang)
                    if u not in have:
                        cat["itemListElement"].append({"@type": "Offer", "itemOffered": {"@type": "Service", "name": h[lang]["h1"], "url": u}})
        s = s[:m.start(2)] + json.dumps(data, ensure_ascii=False, indent=2) + s[m.end(2):]
        p.write_text(s, encoding="utf-8")


# ------------------------------------------------------------------ sitemap + llms
def sync_sitemap_llms():
    today = date.today().isoformat()
    block = "\n  <!-- Sub-brand hub pages (Vulkanizacia.ge, Towing.ge) -->\n"
    for h in HUB:
        for lang in LANGS:
            alts = "".join(f'\n    <xhtml:link rel="alternate" hreflang="{l}" href="{SITE}{url(h, l)}"/>' for l in LANGS)
            alts += f'\n    <xhtml:link rel="alternate" hreflang="x-default" href="{SITE}{url(h, "ka")}"/>'
            block += (f"  <url>\n    <loc>{SITE}{url(h, lang)}</loc>\n    <lastmod>{today}</lastmod>\n    <changefreq>monthly</changefreq>\n"
                      f"    <priority>{'0.8' if lang == 'ka' else '0.7'}</priority>{alts}\n  </url>\n")
    p = ROOT / "sitemap.xml"
    s = p.read_text(encoding="utf-8")
    old = re.search(r"<!-- hub:start -->.*?<!-- hub:end -->", s, re.S)
    if old:   # keep lastmod stable when nothing changed (idempotent)
        prev = dict(re.findall(r"<loc>([^<]+)</loc>\s*<lastmod>([^<]+)</lastmod>", old.group(0)))
        block = re.sub(r"<loc>([^<]+)</loc>\n    <lastmod>[^<]+</lastmod>", lambda m: f"<loc>{m.group(1)}</loc>\n    <lastmod>{prev.get(m.group(1), today)}</lastmod>", block)
    s = sync_block(s, "<!-- hub:start -->", "<!-- hub:end -->", block + "  ", "</urlset>")
    p.write_text(s, encoding="utf-8")
    llm = ("\n## Brands of Bagrat Motors\n"
           "- Vulkanizacia.ge — mobile tyre service, tyres, brakes, car wash, interior cleaning, headlight polishing (phone +995 591 90 90 13): https://vulkanizacia.ge/\n"
           "- Towing.ge — tow truck, spider tow truck, vehicle transport, sober driver (phone +995 514 90 80 90): https://towing.ge/\n"
           "\n## More services (provided by the brands)\n"
           + "".join(f"- [{h['en']['h1']}]({SITE}{url(h, 'en')}) · ka {SITE}{url(h, 'ka')} · ru {SITE}{url(h, 'ru')} — {BRANDS[h['brand']]['name']}\n" for h in HUB))
    p = ROOT / "llms.txt"
    s = p.read_text(encoding="utf-8")
    s = sync_block(s, "<!-- hub:start -->", "<!-- hub:end -->", llm, "\n## Languages")
    p.write_text(s, encoding="utf-8")


def main():
    build_hubs()
    patch_existing()
    patch_homepages()
    sync_sitemap_llms()
    print(f"hub: {len(HUB) * 3} pages; patched {len(EXISTING) * 3} existing pages + 3 homepages")


if __name__ == "__main__":
    main()
