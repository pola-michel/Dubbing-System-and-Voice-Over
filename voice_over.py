import subprocess

# Define your variables
text = """بدلاً من العودة إلى المنزل، ماذا لو كان بإمكانك استخدام هاتفك الذكي لمعرفة حالة مكيف الهواء لديك؟
حتى وقت قريب، كان الوصول إلى الإنترنت محدودًا عبر أجهزة مثل سطح المكتب أو الجهاز اللوحي أو الهاتف الذكي.
ولكن الآن، مع إنترنت الأشياء، يمكن توصيل جميع الأجهزة تقريبًا بالإنترنت ومراقبتها عن بُعد.
يمكن ربط الأجهزة المنزلية مثل مكيف الهواء، وجرس الباب، وأجهزة ضبط الحرارة، وأجهزة الكشف عن الدخان، وسخانات المياه، وأجهزة الإنذار الأمنية ببعضها البعض لمشاركة البيانات مع المستخدم عبر تطبيق الهاتف المحمول.
"""

sentences = text.split('\n')

model_name = "tts_models/multilingual/multi-dataset/xtts_v2"
speaker_wav = "tones/male.mp3"
language_idx = "ar"
out_path = "voice_over1.wav"

# Construct the command with variables
command = f"tts --text \"{sentences}\" --model_name \"{model_name}\" --speaker_wav \"{speaker_wav}\" --language_idx \"{language_idx}\" --out_path \"{out_path}\""

# Execute the command
subprocess.run(command, shell=True)