try:
    import shortcuteditor
    shortcuteditor.nuke_setup()
except Exception:
    import traceback
    traceback.print_exc()