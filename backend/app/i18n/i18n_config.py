import i18n
from pathlib import Path

def setup_i18n():
    print('vao day')
    locale_dir = Path(__file__).parent / "locales"
    print('locale_dir', locale_dir)
    i18n.load_path.append(str(locale_dir))
    i18n.set("locale", "vi")  # Ngôn ngữ mặc định
    i18n.set("fallback", "en")
    i18n.set("filename_format", "{locale}.yaml")
    i18n.set("format", "yaml")