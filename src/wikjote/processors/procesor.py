from htmlobject import HTMLObject


class Processor:
    def __init__(self, target_object: HTMLObject, section_type: None | str = None):
        self.object = target_object
        self.section_type = section_type

    def run(self):
        return None
