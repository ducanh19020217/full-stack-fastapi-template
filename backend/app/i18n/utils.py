from app.i18n import i18n_config
import i18n

def translate(key: str, lang: str = "vi", **kwargs) -> str:
    i18n.set("locales", lang)
    i18n.set("fallback", "en")
    value = i18n.t(key)
    if not value or key in value:
        print(f"[i18n] ⚠️ Không tìm thấy key: {key} trong ngôn ngữ {lang}")
    return value
