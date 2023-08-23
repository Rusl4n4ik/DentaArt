fill_info1 = <b>Ma'lumotlarni to'ldirish 1/2📝</b>\nIltimos, to'liq ismingizni kiriting <b>(familiya Ism Ota ism)</b>
fill_info2 = <b>Ma'lumotlarni to'ldirish 2/2📝</b>\n 📞 Endi, iltimos, telefon raqamingizni kiriting. Biz faqat siz bilan bog'lanish uchun uni ishlatamiz.
fill_info_error1 = ⚠️ Ko'rsatib o'taylik, ismingizni noto'g'ri formatda kiritdingiz. Iltimos, ismingizni to'liq formatda (familiya Ism Ota ism) kiritishingizni tekshiring. Qayta urinib ko'ring:
fill_info_error2 = ⚠️ Noto'g'ri telefon raqami formati. Telefon raqamini '+998XXXXXXXXX' formatida kiriting.
loading = Ma'lumot yuklanmoqda...
info = 🏥 <b>Denta Art</b> - bu to'liq xizmat ko'rsatadigan so'nggi zamon stamatologiya klinika. <b>Manzil va aloqalarimiz:</b> <i> Samarqand sh. Fitrat ko'chasi, 47,</i> <u>+998902706390</u>.\n<b>Direktor:</b> Anvar Sodullaev\n<b>Ish vaqti:</b> Soat 8:00 dan 18:00 gacha
loading_price = Narxlarni yuklash...
price_info = 💵 "Denta Art" stamatologiyasi narxi:
cabinet = Shaxsiy kabinet
cabinet1 = <b>Sizning ismingiz:</b> {$name}\n<b>Sizning telefon raqamingiz:</b> {$num}\n👤 Shaxsiy kabinetda Siz o'z o'zingiz haqingizdagi ma'lumotlarni yangilay olasiz <b>(O'zingiz haqida)</b> yoki "✏Mening yozib olishlarim" tugmasi orqali. \n\n\n<b><i>O'zgartirishni istagan joyingizni tanlang:</i></b>\nAgar o'zgarishlar bo'lmasa, avvalgi sahifaga qayting, "🔙Orqaga" tugmasidan foydalaning
cabinet2 =
greeting = 👋Telegram bot stamatologiyasi <b>Denta Art</b>ga xush kelibsiz! Bu yerda Siz stamatologga yozilish uchun ro'yxatdan o'tishingiz mumkin. Quyidagi menyudan Siz uchun qaysi bo'limni tanlashingiz mumkin ❓Agar bot bilan ishlash haqida savollar bo'lsa, quyida ko'rsatilgan ko'rsatmalar bilan tanishing yoki <u>+998902706390</u> raqamiga murojaat qiling.
enter_name = 📝 Iltimos, yangi ismingizni kiriting, formatda 'Familiya Ism Ota ism'
enter_num = Yangi telefon raqamingizni '+998XXXXXXXXX' formatida kiriting.
name_update = ✅ <i>Sizning ismingiz muvaffaqiyatli yangilandi!</i>
name_update_error = ⚠️ Ko'rsatib o'taylik, ismingizni noto'g'ri formatda kiritdingiz. Iltimos, ismingizni to'liq formatda (familiya Ism Ota ism) kiritishingizni tekshiring. Qayta urinib ko'ring:
num_update = ⚠️ Telefon raqamini noto'g'ri formatda kiritdingiz. Telefon raqamini '+998XXXXXXXXX' formatida kiriting.
num_update_error = ⚠️ <i>Kiritilgan telefon raqami noto'g'ri formatda. Telefon raqamini </i> '+998XXXXXXXXX' <i>formatda kiriting.\nMisol uchun, <u>'+998902706390'.</u> Qayta urinib ko'ring:</i>
month_names = [
        "Yanvar", "Fevral", "Mart", "Aprel", "May", "Iyun",
        "Iyul", "Avgust", "Sentabr", "Oktabr", "Noyabr", "Dekabr"
    ]
choose_time = 🕘 Vaqtni tanlash
back = 🔙Orqaga
appointment = 📅 Qabulga yozilish
appointment1 = 📅 Qabulga yozilish uchun sizga qulay bo'lgan kunni tanlang. E'tibor bering, o'tgan kunlar tanlash uchun mavjud emas.\nKalendardan foydalaning va avval kunni belgilang. <b>Kunni tik bo'lgan bo'lsa, tugmani bosing</b> "🕘 Vaqtni tanlash:"
appointment_day = Kunni tanlang:
appointment2 = <b>Siz kuni tanladingiz</b>: {$selected_day} {$uzbek_month_names[selected_month - 1]} {$selected_year}\nEndi, qabul qilish uchun kerakli bo'lgan vaqtni tanlang:
appointment3 = 📝 Iltimos, qisqa <b>kasallik alomatlari</b> yoki <b>yozib olish maqsadingizni</b> qisqacha tavsiflang. Bu bizni sizning tashrifingizga yaxshi tayyorgarlik ko'rsatishga yordam beradi.
appointment4 =
day_error = Xatolik! Kun tanlanmadi.
time_error = Xatolik! Vaqt haqiqiy emas.
confirmation-message =
    📝 Qabulni tasdiqlash stamatologiyasi <b>Denta Art</b>\n
    <b>Ismingiz</b>: { $name }\n
    <b>Telefon raqamingiz</b>: { $phnum }\n
    <b>Qabul san'ati</b>: { $appointment_date }\n
    <b>Qabul vaqti</b>: { $appointment_time_str }\n
    <b>Kasallik alomatlari/yozib olish maqsadi</b>: { $reason }\n\n\n
    <i>Iltimos, taqdim etilgan ma'lumotni tekshiring. Hammasi to'g'ri bo'lsa, '✅ Qabulni tasdiqlash' tugmasini bosing. Agar o'zgarishlarni kiritishni istasangiz, orqaga qaytishing</i>
confirmation_message2 = ✅ Sizning qabul yozingiz muvaffaqiyatli tasdiqlandi!\nSizni kutamiz <b>{$appointment_date} {$appointment_time_str}</b>. Agar savollar yoki rejalaringizda o'zgarishlar bo'lsa, iltimos, oldindan bizga murojaat qiling. "<b>Denta Art</b>" stamatologiyasini tanlaganingiz uchun rahmat! 🦷\n\nQabulni bekor qilish uchun bosh menuda "Shaxsiy kabinet" => "Mening qabul yozib olishlarim" bo'limiga o'ting
notification-message =
    <b>🔔 Denta Art stamatologiyasi atrofidan eslatma</b>!\n\n
    Bir soat ichida, { $appointment_time_str },
    sizga stamatologga kelish uchun murojaat qilinadi. Iltimos, vaqtingizni to'g'ri kelishingizni harakat qiling.\n
    <b>Manzil:</b> Samarqand sh. Fitrat ko'chasi, 47.\n
    <b>Kasallik alomatlari</b>: { $reason }\n
    Agar savollar yoki rejalaringizda o'zgarishlar bo'lsa, iltimos, <u>+998902706390</u> raqamiga murojaat qiling
notification-message =
    <b>🔔 Denta Art stamatologiyasi atrofidan eslatma</b>!\n\n
    Ertaga, { $appointment_date }, { $appointment_time_str }
    sizga stamatologga kelish uchun murojaat qilinadi.\n
    <b>Manzil:</b> Samarqand sh. Fitrat ko'chasi, 47.\n
    <b>Kasallik alomatlari</b>: { $reason }\n
    Agar savollar yoki rejalaringizda o'zgarishlar bo'lsa, iltimos, <u>+998902706390</u> raqamiga murojaat qiling
my_app = 📅 <b>Sizning qabullar</b>:\n
show_canceled = Bekor qilingan qabullarni ko'rsatish
show_current = Joriy qabullarni ko'rsatish
app_choose = <b><i>Qabul haqida ma'lumotni ko'rish yoki bekor qilish uchun kerakli qabulni tanlang</i></b>:
no_app = Sizda qabul yo'q.
appointment_info = 📋 Qabul haqida ma'lumot:\n<b>Qabul san'ati</b>: {$appointment_date}\n<b>Qabul vaqti</b>: {$appointment_time_str}\n<b>Kasallik alomatlari/yozib olish maqsadi</b>: {$appointment_reason}\n\n\n
appointment_info1 = <b>Bekor qilish uchun, quyidagi tugmani foydalaning:</b>\n❌ Qabulni bekor qilish
wrong_app = Noto'g'ri qabul raqami.
cancel-confirmation = Siz tanlagan kunda { $selected_day } { $selected_month } { $selected_year } yil { $selected_hour }:{ $selected_minute }. Ushbu qabulni bekor qilmoqchimisiz?
cancellation-reason-prompt = 📝 <b>Iltimos, qabulni bekor qilish sababini kiriting</b>:\nUshbu xizmat sifatini yaxshilashga yordam bering.
cannot-delete-cancelled-appointment = Siz bekor qilinayotgan qabullarni qayta o'chira olmaysiz.
appointment-cancelled-successfully = Sizning qabul san'atingiz { $appointment_date } { $appointment_month } { $appointment_year } yil, { $appointment_time } da bekor qilindi.  Taqdim etgan ma'lumotingiz uchun rahmat! Agar boshqa rejalaringiz yoki savollar yuzaga kelsa,
error-occurred-cancelling-appointment = Qabulni bekor qilishda xatolik yuz berdi.
error-occurred = Xatolik yuz berdi. Iltimos, qayta urinib ko'ring