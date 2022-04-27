import aqt


def get_dialog_class_or_none(name):
    try:
        return aqt.dialogs._dialogs[name][0]
    except KeyError:
        return None


def get_dialog_instance_or_none(name):
    return aqt.dialogs._dialogs[name][1]
